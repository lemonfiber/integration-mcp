# Copyright (c) 2026 NightWorksIO
"""Cloudflare, by an API token allowed to edit the zone's DNS."""

from typing import TYPE_CHECKING, Final, cast

from lemonfiber_mcp.certificates.dns.api import Api, Asking, Document
from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, candidates, secret

if TYPE_CHECKING:
    from collections.abc import Mapping

ENDPOINT: Final = "https://api.cloudflare.com/client/v4"
CREDENTIAL_FILE: Final = "CLOUDFLARE_DNS_API_TOKEN_FILE"
TTL: Final = 120


class Cloudflare:
    """TXT records written through Cloudflare's API."""

    timing = Timing()

    def __init__(self, token: str) -> None:
        """Hold the API token."""
        self._api = Api("Cloudflare", ENDPOINT, {"Authorization": f"Bearer {token}"})

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> Cloudflare:
        """Return the provider its settings describe."""
        return cls(secret(environment, CREDENTIAL_FILE))

    def _results(self, path: str, params: Mapping[str, str]) -> list[Document]:
        return cast("list[Document]", self._api.document("GET", path, Asking(params=params))["result"])

    def _zone(self, name: str) -> str:
        for candidate in candidates(name):
            found = self._results("/zones", {"name": candidate})
            if found:
                return str(found[0]["id"])
        msg = f"Cloudflare holds no zone for {name}."
        raise ProviderError(msg)

    def present(self, name: str, value: str) -> None:
        """Write the TXT record."""
        record = {"type": "TXT", "name": name.rstrip("."), "content": value, "ttl": TTL}
        self._api.document("POST", f"/zones/{self._zone(name)}/dns_records", Asking(body=record))

    def cleanup(self, name: str, value: str) -> None:
        """Remove the TXT record."""
        zone = self._zone(name)
        asked = {"type": "TXT", "name": name.rstrip("."), "content": value}
        for record in self._results(f"/zones/{zone}/dns_records", asked):
            self._api.document("DELETE", f"/zones/{zone}/dns_records/{record['id']}")
