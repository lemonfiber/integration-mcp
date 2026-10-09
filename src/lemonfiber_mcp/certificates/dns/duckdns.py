# Copyright (c) 2026 NightWorksIO
"""Duck DNS, by the account's token; one TXT record a domain."""

from typing import TYPE_CHECKING, Final

from lemonfiber_mcp.certificates.dns.api import Api, Asking
from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, secret

if TYPE_CHECKING:
    from collections.abc import Mapping

ENDPOINT: Final = "https://www.duckdns.org"
CREDENTIAL_FILE: Final = "DUCKDNS_TOKEN_FILE"
ZONE: Final = ".duckdns.org"
DONE: Final = "OK"


class DuckDns:
    """The TXT record of a Duck DNS domain, set and cleared."""

    timing = Timing(propagation=120.0, interval=5.0)

    def __init__(self, token: str) -> None:
        """Hold the token."""
        self._token = token
        self._api = Api("Duck DNS", ENDPOINT)

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> DuckDns:
        """Return the provider its settings describe."""
        return cls(secret(environment, CREDENTIAL_FILE))

    def _update(self, name: str, asked: Mapping[str, str]) -> None:
        bare = name.rstrip(".")
        if not bare.endswith(ZONE):
            msg = f"{name} is not a Duck DNS name."
            raise ProviderError(msg)
        domain = bare.removesuffix(ZONE).split(".")[-1]
        params = {"domains": domain, "token": self._token, **asked}
        if self._api.text("GET", "/update", Asking(params=params)).strip() != DONE:
            msg = "Duck DNS refused the update."
            raise ProviderError(msg)

    def present(self, name: str, value: str) -> None:
        """Set the domain's TXT record."""
        self._update(name, {"txt": value})

    def cleanup(self, name: str, value: str) -> None:
        """Clear the domain's TXT record."""
        self._update(name, {"txt": value, "clear": "true"})
