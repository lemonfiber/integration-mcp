# Copyright (c) 2026 NightWorksIO
"""Azure DNS, by a service principal allowed to change the zone's records."""

from http import HTTPMethod
from typing import TYPE_CHECKING, Final, cast

from lemonfiber_mcp.certificates.dns.api import Api, Asking, Document, Leased
from lemonfiber_mcp.certificates.dns.provider import (
    ProviderError,
    Timing,
    candidates,
    needed,
    relative,
    secret,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

LOGIN: Final = "https://login.microsoftonline.com"
PROVIDER: Final = "Azure DNS"
LOGIN_PROVIDER: Final = "Microsoft Entra"
MANAGEMENT: Final = "https://management.azure.com"
TENANT_ID: Final = "AZURE_TENANT_ID"
CLIENT_ID: Final = "AZURE_CLIENT_ID"
CLIENT_CREDENTIAL_FILE: Final = "AZURE_CLIENT_SECRET_FILE"
SUBSCRIPTION_ID: Final = "AZURE_SUBSCRIPTION_ID"
RESOURCE_GROUP: Final = "AZURE_RESOURCE_GROUP"
SCOPE: Final = "https://management.azure.com/.default"
VERSION: Final = {"api-version": "2018-05-01"}
TTL: Final = 60


class AzureDns:
    """TXT records written through Azure Resource Manager, the record set holding every value at once."""

    timing = Timing(propagation=120.0, interval=4.0)

    def __init__(self, tenant: str, client: str, client_secret: str, subscription: str, group: str) -> None:
        """Hold the service principal and where its zones are."""
        self._login = (tenant, client, client_secret)
        self._zones = (
            f"/subscriptions/{subscription}/resourceGroups/{group}/providers/Microsoft.Network/dnsZones"
        )
        self._leased = Leased(PROVIDER, MANAGEMENT, self._token)

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> AzureDns:
        """Return the provider its settings describe."""
        return cls(
            needed(environment, TENANT_ID),
            needed(environment, CLIENT_ID),
            secret(environment, CLIENT_CREDENTIAL_FILE),
            needed(environment, SUBSCRIPTION_ID),
            needed(environment, RESOURCE_GROUP),
        )

    def _token(self) -> Document:
        tenant, client, client_secret = self._login
        form = {
            "grant_type": "client_credentials",
            "client_id": client,
            "client_secret": client_secret,
            "scope": SCOPE,
        }
        return Api(LOGIN_PROVIDER, LOGIN).document(
            HTTPMethod.POST,
            f"/{tenant}/oauth2/v2.0/token",
            Asking(form=form),
        )

    def _asked(self) -> Api:
        return self._leased.api()

    def _record(self, name: str) -> str:
        held = cast(
            "list[Document]",
            self._asked().document(HTTPMethod.GET, self._zones, Asking(params=VERSION))["value"],
        )
        zones = {str(zone["name"]) for zone in held}
        for candidate in candidates(name):
            if candidate in zones:
                return f"{self._zones}/{candidate}/TXT/{relative(name, candidate)}"
        msg = f"Azure DNS holds no zone for {name}."
        raise ProviderError(msg)

    def _values(self, record: str) -> list[list[str]]:
        held = self._asked().found(HTTPMethod.GET, record, Asking(params=VERSION))
        entries = [] if held is None else cast("list[Document]", held["properties"]["TXTRecords"])
        return [cast("list[str]", entry["value"]) for entry in entries]

    def _set(self, record: str, values: list[list[str]]) -> None:
        if values:
            body = {"properties": {"TTL": TTL, "TXTRecords": [{"value": value} for value in values]}}
            self._asked().document(HTTPMethod.PUT, record, Asking(params=VERSION, body=body))
        else:
            self._asked().send(HTTPMethod.DELETE, record, Asking(params=VERSION))

    def present(self, name: str, value: str) -> None:
        """Add the value to the name's TXT record set."""
        record = self._record(name)
        self._set(record, [*self._values(record), [value]])

    def cleanup(self, name: str, value: str) -> None:
        """Take the value out of the name's TXT record set."""
        record = self._record(name)
        self._set(record, [held for held in self._values(record) if held != [value]])
