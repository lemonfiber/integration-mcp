# Copyright (c) 2026 NightWorksIO
"""A provider's HTTP API, asked with its credential, refusing by status and never repeating what was sent."""

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Final, cast

import requests

from lemonfiber_mcp.certificates.dns.provider import TIMEOUT_SECONDS, ProviderError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from http import HTTPMethod

NOT_FOUND: Final = 404
REFUSED_FROM: Final = 400
AUTHORIZATION: Final = "Authorization"
LIFETIME: Final = 3600.0
"""How long an access token lasts where its answer does not say."""
EARLY: Final = 300.0
"""How long before an access token ends it is asked for again."""

type Document = dict[str, Any]
"""A JSON object an API answers with."""


@dataclass(frozen=True, slots=True)
class Asking:
    """What a request carries beyond its method and path: a query, a JSON body, a form, raw bytes, headers."""

    params: Mapping[str, str] | None = None
    body: Document | list[Document] | None = None
    form: Mapping[str, str] | None = None
    raw: bytes | None = None
    headers: Mapping[str, str] | None = None


NOTHING: Final = Asking()


def bearer(token: str) -> dict[str, str]:
    """Return the header a bearer token is sent in."""
    return {AUTHORIZATION: f"Bearer {token}"}


class Api:
    """One provider's API, at its address, with the headers that carry its credential."""

    def __init__(self, provider: str, base: str, headers: Mapping[str, str] | None = None) -> None:
        """Hold the provider's name, where its API is, and the headers every request carries."""
        self._provider = provider
        self._base = base.rstrip("/")
        self._session = requests.Session()
        self._session.headers.update(headers or {})

    def _refused(self, method: HTTPMethod, path: str, status: int) -> ProviderError:
        return ProviderError(f"The {self._provider} API answered {status} to {method} {path}.")

    def send(self, method: HTTPMethod, path: str, asking: Asking = NOTHING) -> requests.Response:
        """Return what a request answers, refusing a refusal by its status and the path, never what was sent."""
        try:
            response = self._session.request(
                method,
                f"{self._base}{path}",
                params=asking.params,
                json=asking.body,
                data=asking.form if asking.raw is None else asking.raw,
                headers=asking.headers,
                timeout=TIMEOUT_SECONDS,
            )
        except requests.RequestException as unreachable:
            msg = f"The {self._provider} API could not be reached: {type(unreachable).__name__}."
            raise ProviderError(msg) from None
        if response.status_code >= REFUSED_FROM and response.status_code != NOT_FOUND:
            raise self._refused(method, path, response.status_code)
        return response

    def found(self, method: HTTPMethod, path: str, asking: Asking = NOTHING) -> Document | None:
        """Return the JSON object a request answers with, or None where it answered `404`."""
        response = self.send(method, path, asking)
        if response.status_code == NOT_FOUND:
            return None
        return cast("Document", response.json()) if response.content else {}

    def document(self, method: HTTPMethod, path: str, asking: Asking = NOTHING) -> Document:
        """Return the JSON object a request answers with, refusing a `404`."""
        answered = self.found(method, path, asking)
        if answered is None:
            raise self._refused(method, path, NOT_FOUND)
        return answered

    def listing(self, method: HTTPMethod, path: str, asking: Asking = NOTHING) -> list[Document]:
        """Return the JSON list a request answers with, refusing a `404`."""
        response = self.send(method, path, asking)
        if response.status_code == NOT_FOUND:
            raise self._refused(method, path, NOT_FOUND)
        return cast("list[Document]", response.json())

    def text(self, method: HTTPMethod, path: str, asking: Asking = NOTHING) -> str:
        """Return the text a request answers with, refusing a `404`."""
        response = self.send(method, path, asking)
        if response.status_code == NOT_FOUND:
            raise self._refused(method, path, NOT_FOUND)
        return response.text


def monotonic() -> float:
    """Return a time that only moves forward, in seconds."""
    return time.monotonic()


class Leased:
    """An API reached with a short-lived access token, asked for again before it ends."""

    def __init__(self, provider: str, base: str, ask: Callable[[], Document]) -> None:
        """Hold the provider's name, where its API is, and how a token is asked for."""
        self._provider = provider
        self._base = base
        self._ask = ask
        self._held: tuple[Api, float] | None = None
        """The API with the token held, and when it is asked for again."""

    def api(self) -> Api:
        """Return the API with a token that has not ended, asking for one where none is held or it is ending."""
        now = monotonic()
        if self._held is None or now >= self._held[1]:
            answered = self._ask()
            until = now + float(answered.get("expires_in", LIFETIME)) - EARLY
            self._held = (Api(self._provider, self._base, bearer(str(answered["access_token"]))), until)
        return self._held[0]
