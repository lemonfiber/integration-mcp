# Copyright (c) 2026 NightWorksIO
"""The `acme` mode: a certificate from any RFC 8555 authority, renewed when the authority says or a third is left.

The account key is the server's own, one per authority, kept beside the
account's address. Each order is answered by the challenge the settings
choose. Until the first certificate is issued the server serves one standing
in, which no client trusts and the health answer counts as not ready. A failed
attempt is tried again after a minute, doubling to six hours with jitter, and
never sooner than the authority asked.
"""

import datetime
import hashlib
import json
import logging
import random
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, cast

from acme import client, errors, messages
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from josepy.jwk import JWK, JWKEC

from lemonfiber_mcp.certificates import making, state
from lemonfiber_mcp.certificates.acme_protocol import FAILURES, Network, Presenting, said_of
from lemonfiber_mcp.certificates.acme_settings import EAB_HMAC_FILE, EAB_KID
from lemonfiber_mcp.certificates.modes import (
    CHAIN,
    KEY,
    RENEWAL,
    CertificateError,
    Served,
    kept_leaf,
    leaf_dir,
)
from lemonfiber_mcp.certificates.settings import KeyType, Mode

if TYPE_CHECKING:
    import pathlib

    from lemonfiber_mcp.certificates.acme_settings import Acme
    from lemonfiber_mcp.certificates.alpn import Challenges
    from lemonfiber_mcp.certificates.dns.challenge import Dns01
    from lemonfiber_mcp.certificates.settings import Tls

ACCOUNT: Final = "account"
ACCOUNT_KEY: Final = "key.pem"
ACCOUNT_RECORD: Final = "account.json"
STANDING_IN: Final = "standing-in"
"""Where the certificate standing in until the first is issued is kept, beside the state's own."""
ORDER_TIMEOUT: Final = datetime.timedelta(minutes=3)
"""How long an order is waited on before it counts as failed."""
FIRST_RETRY: Final = datetime.timedelta(minutes=1)
LAST_RETRY: Final = datetime.timedelta(hours=6)
JITTER: Final = 0.1
"""How far either way a wait before trying again is moved, as a share of it, so servers do not all ask at once."""
RENEWED_WITH: Final = 1 / 3
"""How much of a certificate's lifetime is left when it is renewed, where the authority says nothing."""

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class Waiting:
    """When a failed attempt is tried again, and how long the wait before it was."""

    until: datetime.datetime
    wait: datetime.timedelta


def utc(moment: datetime.datetime) -> datetime.datetime:
    """Return a moment in UTC, one without a zone read as this machine's local time."""
    return moment.astimezone(datetime.UTC)


def local_deadline(now: datetime.datetime) -> datetime.datetime:
    """Return when an order stops being waited on, in this machine's local time without a zone, as the client reads it."""
    return (now + ORDER_TIMEOUT).astimezone().replace(tzinfo=None)


def csr_of(names: tuple[str, ...], key: making.PrivateKey) -> bytes:
    """Return a certificate request for these names, signed by the certificate's key."""
    request = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(making.named(names[0]))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(name) for name in names]), critical=False)
        .sign(key, hashes.SHA256())
    )
    return request.public_bytes(serialization.Encoding.PEM)


class AcmeSource:
    """The certificate an ACME authority issues for the server's names, renewed as the authority says."""

    mode = Mode.ACME

    def __init__(
        self,
        tls: Tls,
        settings: Acme,
        pending: Challenges,
        rng: random.Random | None = None,
        dns: Dns01 | None = None,
    ) -> None:
        """Hold the settings, where the account and the certificate are kept, and the pending TLS-ALPN-01 answers."""
        self._tls = tls
        self._settings = settings
        self._pending = pending
        self._dns = dns
        self._names = tuple(str(name) for name in tls.names)
        self._leaf_dir = leaf_dir(tls)
        self._account_dir = tls.state / ACCOUNT / hashlib.sha256(settings.directory.encode()).hexdigest()
        self._rng = random.SystemRandom() if rng is None else rng
        self._waiting: Waiting | None = None
        self._asked: datetime.datetime | None = None
        self._due: datetime.datetime | None = None
        self._ask_again: datetime.datetime | None = None
        self._standing_in: Served | None = None

    @property
    def renewal(self) -> pathlib.Path:
        """Return where the record of renewal is kept."""
        return self._leaf_dir / RENEWAL

    @property
    def waiting_until(self) -> datetime.datetime | None:
        """Return when a failed attempt is tried again, or None where the last attempt did not fail."""
        return None if self._waiting is None else self._waiting.until

    def announced(self) -> list[str]:
        """Return nothing beyond the mode: the authority's terms are logged once, when an account is registered."""
        return []

    def first(self, now: datetime.datetime) -> Served:
        """Return the kept certificate where it still serves, and one standing in where it does not.

        The directory is asked once here, so a start against an authority that
        requires a binding, without one, is refused, naming the two settings.
        """
        try:
            required = self._client().external_account_required()
        except FAILURES as unreachable:
            logger.warning("The ACME directory could not be asked: %s", said_of(unreachable))
            required = False
        if required and self._settings.binding is None:
            msg = f"The ACME directory requires an external account: set {EAB_KID} and {EAB_HMAC_FILE}."
            raise CertificateError(msg)
        return self._kept(now) or self._stand_in(now)

    def due(self, served: Served, /) -> datetime.datetime | None:
        """Return when the certificate is renewed: when the authority said, or once a third of its lifetime is left."""
        if served.standing_in:
            return None
        lifetime = served.leaf.not_valid_after_utc - served.leaf.not_valid_before_utc
        return self._due or served.leaf.not_valid_after_utc - lifetime * RENEWED_WITH

    def obtain(self, now: datetime.datetime) -> Served:
        """Return the certificate to serve now: the kept one until it is due, and a new one ordered when it is."""
        kept = self._kept(now)
        if kept is not None:
            self._asked_for_renewal(kept, now)
            if now < cast("datetime.datetime", self.due(kept)):
                return kept
        if self._waiting is not None and now < self._waiting.until:
            return kept or self._stand_in(now)
        self._asked = None
        try:
            served = self._ordered(now)
        except CertificateError:
            self._waited(now)
            raise
        self._waiting = None
        return served

    def _kept(self, now: datetime.datetime) -> Served | None:
        kept = kept_leaf(self._leaf_dir, self._tls.names, now)
        return None if kept is None else Served(self._leaf_dir / CHAIN, self._leaf_dir / KEY, kept[0])

    def _stand_in(self, now: datetime.datetime) -> Served:
        """Return the certificate standing in until the first is issued, made once, kept nowhere."""
        if self._standing_in is None:
            held = self._tls.state / STANDING_IN / self._tls.first
            key = making.generated(KeyType.EC_P256)
            state.write(held / CHAIN, making.certificate_pem(making.pinned(self._tls.names, key, now)))
            state.write(held / KEY, making.key_pem(key))
            leaf = x509.load_pem_x509_certificate((held / CHAIN).read_bytes())
            self._standing_in = Served(held / CHAIN, held / KEY, leaf, standing_in=True)
        return self._standing_in

    def _waited(self, now: datetime.datetime) -> None:
        wait = FIRST_RETRY if self._waiting is None else min(self._waiting.wait * 2, LAST_RETRY)
        until = now + wait * (1 + self._rng.uniform(-JITTER, JITTER))
        self._waiting = Waiting(until if self._asked is None else max(until, self._asked), wait)

    def _asked_for_renewal(self, kept: Served, now: datetime.datetime) -> None:
        """Ask the authority when to renew the kept certificate, where it is time to ask again."""
        if self._ask_again is not None and now < self._ask_again:
            return
        try:
            suggested, again = self._client().renewal_time(making.certificate_pem(kept.leaf))
        except FAILURES:
            self._ask_again = now + FIRST_RETRY
            return
        self._due = None if suggested is None else utc(suggested)
        self._ask_again = utc(again)

    def _account_key(self) -> JWK:
        path = self._account_dir / ACCOUNT_KEY
        if not path.is_file():
            state.write(path, making.key_pem(ec.generate_private_key(ec.SECP256R1())))
        key = serialization.load_pem_private_key(path.read_bytes(), password=None)
        return JWKEC(key=cast("ec.EllipticCurvePrivateKey", key))

    def _client(self) -> client.ClientV2:
        network = Network(self._account_key(), self._settings.roots)
        return client.ClientV2(client.ClientV2.get_directory(self._settings.directory, network), network)

    def _registered(self, acme: client.ClientV2) -> None:
        record = self._account_dir / ACCOUNT_RECORD
        if record.is_file():
            known = cast("dict[str, str]", json.loads(record.read_text(encoding="utf-8")))
            acme.net.account = messages.RegistrationResource(uri=known["url"], body=messages.Registration())
            return
        binding = self._settings.binding
        bound = (
            None
            if binding is None
            else messages.ExternalAccountBinding.from_data(
                account_public_key=cast("JWK", acme.net.key).public_key(),
                kid=binding.kid,
                hmac_key=binding.hmac_key(),
                directory=acme.directory,
            )
        )
        contact = () if self._settings.contact is None else (self._settings.contact,)
        asked = messages.NewRegistration.from_data(
            contact=contact,
            terms_of_service_agreed=True,
            external_account_binding=bound,
        )
        try:
            url = str(acme.new_account(asked).uri)
        except errors.ConflictError as existing:
            url = str(existing.location)
            acme.net.account = messages.RegistrationResource(uri=url, body=messages.Registration())
        state.write(record, json.dumps({"url": url, "contact": list(contact)}).encode())
        terms = cast("Any", acme.directory).meta.terms_of_service
        logger.info("An ACME account is registered, agreeing to the authority's terms: %s", terms)

    def _ordered(self, now: datetime.datetime) -> Served:
        acme: client.ClientV2 | None = None
        key = making.generated(self._tls.key_type)
        try:
            acme = self._client()
            self._registered(acme)
            order = acme.new_order(csr_of(self._names, key))
            with Presenting(self._settings.challenge, self._pending, acme, order, self._dns):
                finished = acme.poll_and_finalize(order, deadline=local_deadline(now))
        except FAILURES as failed:
            self._asked = None if acme is None else cast("Network", acme.net).retry_after
            raise CertificateError(said_of(failed)) from None
        state.write(self._leaf_dir / KEY, making.key_pem(key))
        state.write(self._leaf_dir / CHAIN, str(cast("Any", finished).fullchain_pem).encode())
        self._due, self._ask_again = None, None
        leaf = x509.load_pem_x509_certificate((self._leaf_dir / CHAIN).read_bytes())
        served = Served(self._leaf_dir / CHAIN, self._leaf_dir / KEY, leaf)
        self._asked_for_renewal(served, now)
        return served
