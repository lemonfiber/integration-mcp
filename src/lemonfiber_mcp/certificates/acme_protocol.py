# Copyright (c) 2026 NightWorksIO
"""The EFF's `acme` client, as this server speaks through it: typed where the library reads its fields at run time.

TLS-ALPN-01 (RFC 8737) is registered as a challenge the library reads, since it
no longer ships one. The network keeps the last `Retry-After` an authority
answered a refusal with, so a failed attempt is never tried again sooner. An
order's authorizations are answered by the chosen challenge for as long as it
is pending, and withdrawn after.
"""

import datetime
import logging
from typing import TYPE_CHECKING, Any, Final, cast, override

import requests
from acme import challenges, client, errors, messages
from josepy.jwa import ES256

from lemonfiber_mcp.certificates import http01
from lemonfiber_mcp.certificates.acme_settings import Challenge
from lemonfiber_mcp.certificates.modes import CertificateError

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Callable

    from josepy.jwk import JWK

    from lemonfiber_mcp.certificates.alpn import Challenges
    from lemonfiber_mcp.certificates.dns.challenge import Dns01

USER_AGENT: Final = "lemonfiber-mcp"
logger = logging.getLogger(__name__)
REFUSED_FROM: Final = 400
"""The lowest status an authority refuses with."""
HTTP_DATE: Final = "%a, %d %b %Y %H:%M:%S GMT"
FAILURES: Final = (errors.Error, messages.Error, requests.RequestException, OSError)
"""Everything speaking to an authority can fail with, short of a bug."""


@challenges.ChallengeResponse.register
class TlsAlpn01Response(challenges.KeyAuthorizationChallengeResponse):
    """The answer to a TLS-ALPN-01 challenge: the key authorization, shown in the handshake."""

    typ = "tls-alpn-01"


@challenges.Challenge.register
class TlsAlpn01(challenges.KeyAuthorizationChallenge):
    """A TLS-ALPN-01 challenge."""

    response_cls = TlsAlpn01Response
    typ = response_cls.typ

    @override
    def validation(self, account_key: JWK, **unused_kwargs: Any) -> str:
        """Return the key authorization the challenge certificate carries the digest of."""
        return self.key_authorization(account_key)


def later_of(asked: str, now: datetime.datetime) -> datetime.datetime | None:
    """Return when a `Retry-After` header asks to be asked again, after seconds or at a time; None where unread."""
    written = asked.strip()
    if written.isdigit():
        return now + datetime.timedelta(seconds=int(written))
    try:
        return datetime.datetime.strptime(written, HTTP_DATE).replace(tzinfo=datetime.UTC)
    except ValueError:
        return None


class Network(client.ClientNetwork):
    """The client's network, keeping when the authority last asked to be left alone until."""

    def __init__(self, key: JWK, roots: pathlib.Path | None) -> None:
        """Speak as the account key, checking the directory's TLS against `roots` where given."""
        super().__init__(key, alg=ES256, user_agent=USER_AGENT)
        if roots is not None:
            # The client hands this to `requests` as `verify`, which takes a bundle's path as well as a yes or no.
            self.verify_ssl = cast("Any", str(roots))
        self.retry_after: datetime.datetime | None = None

    @override
    def _send_request(self, method: str, url: str, *args: Any, **kwargs: Any) -> requests.Response:
        response = super()._send_request(method, url, *args, **kwargs)
        asked = response.headers.get("Retry-After")
        if response.status_code >= REFUSED_FROM and asked is not None:
            self.retry_after = later_of(asked, datetime.datetime.now(datetime.UTC))
        return response


def authorizations_of(order: messages.OrderResource) -> tuple[messages.AuthorizationResource, ...]:
    """Return an order's authorizations."""
    return tuple(cast("Any", order).authorizations)


def name_of(authorization: messages.AuthorizationResource) -> str:
    """Return the name an authorization is for."""
    return str(cast("Any", authorization).body.identifier.value)


def offered_of(authorization: messages.AuthorizationResource) -> tuple[messages.ChallengeBody, ...]:
    """Return the challenges an authorization may be answered by."""
    return tuple(cast("Any", authorization).body.challenges)


def valid(authorization: messages.AuthorizationResource) -> bool:
    """Tell whether an authorization is already valid, as an authority that reuses one answers it."""
    return cast("Any", authorization).body.status == messages.STATUS_VALID


def kind_of(body: messages.ChallengeBody) -> str:
    """Return a challenge's kind, as RFC 8555 spells it."""
    return str(cast("Any", body).chall.typ)


def problems_of(failed: errors.ValidationError) -> list[str]:
    """Return each failed authorization's name and the authority's problem type for it."""
    return [
        f"{name_of(authorization)}: {cast('Any', body).error.typ}"
        for authorization in failed.failed_authzrs
        for body in offered_of(authorization)
        if cast("Any", body).error is not None
    ]


def said_of(failed: BaseException) -> str:
    """Return what failed in an order, with the authority's problem type and detail where it gave them."""
    if isinstance(failed, messages.Error):
        return f"The ACME authority refused: {failed.typ}: {failed.detail}"
    if isinstance(failed, errors.ValidationError):
        return f"The ACME authority could not validate {', '.join(problems_of(failed))}."
    return f"The ACME authority could not be reached or answered unexpectedly: {type(failed).__name__}."


class Presenting:
    """Each authorization of an order answered by the chosen challenge, for as long as the order is pending."""

    def __init__(
        self,
        chosen: Challenge,
        pending: Challenges,
        acme: client.ClientV2,
        order: messages.OrderResource,
        dns: Dns01 | None = None,
    ) -> None:
        """Hold the challenge kind, where TLS-ALPN-01 answers are kept, how DNS-01 is answered, the client and the order."""
        self._chosen = chosen
        self._pending = pending
        self._dns = dns
        self._acme = acme
        self._order = order
        self._withdrawn: list[Callable[[], None]] = []

    def __enter__(self) -> None:
        """Present every answer, then tell the authority to look; withdraw what was presented where that fails."""
        try:
            self._present()
        except BaseException:
            self.__exit__()
            raise

    def _present(self) -> None:
        key = cast("JWK", self._acme.net.key)
        answers: list[tuple[messages.ChallengeBody, challenges.ChallengeResponse]] = []
        tokens: dict[str, str] = {}
        records: list[tuple[str, str]] = []
        for authorization in authorizations_of(self._order):
            if valid(authorization):
                continue
            name = name_of(authorization)
            offered = [body for body in offered_of(authorization) if kind_of(body) == self._chosen.value]
            if not offered:
                msg = f"The ACME authority offers no {self._chosen.value} challenge for {name}."
                raise CertificateError(msg)
            chall = cast("challenges.KeyAuthorizationChallenge", cast("Any", offered[0]).chall)
            response, validation = cast(
                "tuple[challenges.ChallengeResponse, str]",
                chall.response_and_validation(key),
            )
            if self._chosen is Challenge.TLS_ALPN_01:
                self._pending.present(name, validation)
                self._withdrawn.append(lambda withdrawn=name: self._pending.withdraw(withdrawn))
            elif self._chosen is Challenge.HTTP_01:
                tokens[cast("challenges.HTTP01", chall).path] = validation
            else:
                records.append(self._written(name, validation))
            answers.append((offered[0], response))
        if tokens:
            port = http01.Responder(tokens)
            port.open()
            self._withdrawn.append(port.close)
        for written in records:
            cast("Dns01", self._dns).wait_for(*written)
        for body, response in answers:
            self._acme.answer_challenge(body, response)

    def _written(self, name: str, value: str) -> tuple[str, str]:
        """Write a DNS-01 record through the provider, and return where it was written and its value."""
        dns = cast("Dns01", self._dns)
        where = dns.where(name)
        dns.provider.present(where, value)
        self._withdrawn.append(lambda: dns.provider.cleanup(where, value))
        return where, value

    def __exit__(self, *_: object) -> None:
        """Withdraw every answer and close port 80 where it was opened, logging a withdrawal that fails."""
        for withdrawn in reversed(self._withdrawn):
            try:
                withdrawn()
            except CertificateError as failed:
                logger.warning("An answer could not be withdrawn: %s", failed)
        self._withdrawn.clear()
