# Copyright (c) 2026 NightWorksIO
"""DigitalOcean, by a personal access token with write access."""

from http import HTTPMethod
from typing import TYPE_CHECKING, Final, cast

from lemonfiber_mcp.certificates.dns.api import Api, Asking, Document, bearer
from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, candidates, relative, secret

if TYPE_CHECKING:
    from collections.abc import Mapping

ENDPOINT: Final = "https://api.digitalocean.com/v2"
PROVIDER: Final = "DigitalOcean"
CREDENTIAL_FILE: Final = "DO_AUTH_TOKEN_FILE"
TTL: Final = 30


class DigitalOcean:
    """TXT records written through DigitalOcean's API."""

    timing = Timing(propagation=60.0, interval=5.0)

    def __init__(self, token: str) -> None:
        """Hold the access token."""
        self._api = Api(PROVIDER, ENDPOINT, bearer(token))

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> DigitalOcean:
        """Return the provider its settings describe."""
        return cls(secret(environment, CREDENTIAL_FILE))

    def _zone(self, name: str) -> str:
        for candidate in candidates(name):
            if self._api.found(HTTPMethod.GET, f"/domains/{candidate}") is not None:
                return candidate
        msg = f"DigitalOcean holds no domain for {name}."
        raise ProviderError(msg)

    def present(self, name: str, value: str) -> None:
        """Write the TXT record."""
        zone = self._zone(name)
        record = {"type": "TXT", "name": relative(name, zone), "data": value, "ttl": TTL}
        self._api.document(HTTPMethod.POST, f"/domains/{zone}/records", Asking(body=record))

    def cleanup(self, name: str, value: str) -> None:
        """Remove the TXT record."""
        zone = self._zone(name)
        asked = Asking(params={"type": "TXT", "name": name.rstrip(".")})
        held = cast(
            "list[Document]",
            self._api.document(HTTPMethod.GET, f"/domains/{zone}/records", asked)["domain_records"],
        )
        for record in held:
            if record["data"] == value:
                self._api.send(HTTPMethod.DELETE, f"/domains/{zone}/records/{record['id']}")
