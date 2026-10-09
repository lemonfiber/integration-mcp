# Copyright (c) 2026 NightWorksIO
"""deSEC, by a token."""

from http import HTTPMethod
from typing import TYPE_CHECKING, Final, cast

from lemonfiber_mcp.certificates.dns.api import AUTHORIZATION, Api, Asking
from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, relative, secret

if TYPE_CHECKING:
    from collections.abc import Mapping

ENDPOINT: Final = "https://desec.io/api/v1"
PROVIDER: Final = "deSEC"
CREDENTIAL_FILE: Final = "DESEC_TOKEN_FILE"
TTL: Final = 3600
"""The shortest a record's lifetime deSEC takes."""


class Desec:
    """TXT records written through deSEC's API, the record set holding every value at once."""

    timing = Timing(propagation=120.0, interval=4.0)

    def __init__(self, token: str) -> None:
        """Hold the token."""
        self._api = Api(PROVIDER, ENDPOINT, {AUTHORIZATION: f"Token {token}"})

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> Desec:
        """Return the provider its settings describe."""
        return cls(secret(environment, CREDENTIAL_FILE))

    def _held(self, name: str) -> tuple[str, str, list[str]]:
        found = self._api.listing(
            HTTPMethod.GET,
            "/domains/",
            Asking(params={"owns_qname": name.rstrip(".")}),
        )
        if not found:
            msg = f"deSEC holds no domain for {name}."
            raise ProviderError(msg)
        zone = str(found[0]["name"])
        written = relative(name, zone)
        held = self._api.found(HTTPMethod.GET, f"/domains/{zone}/rrsets/{written}/TXT/")
        return zone, written.removeprefix("@"), [] if held is None else cast("list[str]", held["records"])

    def _set(self, zone: str, subname: str, records: list[str]) -> None:
        rrset = [{"subname": subname, "type": "TXT", "ttl": TTL, "records": records}]
        self._api.send(HTTPMethod.PATCH, f"/domains/{zone}/rrsets/", Asking(body=rrset))

    def present(self, name: str, value: str) -> None:
        """Add the value to the name's TXT record set."""
        zone, subname, records = self._held(name)
        self._set(zone, subname, [*records, f'"{value}"'])

    def cleanup(self, name: str, value: str) -> None:
        """Take the value out of the name's TXT record set."""
        zone, subname, records = self._held(name)
        self._set(zone, subname, [record for record in records if record != f'"{value}"'])
