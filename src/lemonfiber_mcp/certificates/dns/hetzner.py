# Copyright (c) 2026 NightWorksIO
"""Hetzner DNS, through the Hetzner Cloud API, by an API token."""

import time
from http import HTTPMethod
from typing import TYPE_CHECKING, Final, cast

from lemonfiber_mcp.certificates.dns.api import Api, Asking, Document, bearer
from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, candidates, relative, secret

if TYPE_CHECKING:
    from collections.abc import Mapping

ENDPOINT: Final = "https://api.hetzner.cloud/v1"
PROVIDER: Final = "Hetzner"
CREDENTIAL_FILE: Final = "HETZNER_API_TOKEN_FILE"
TTL: Final = 60
RUNNING: Final = "running"
SUCCEEDED: Final = "success"
ACTION_CHECKS: Final = 30
ACTION_INTERVAL: Final = 1.0
"""How often, and how many times, an action the API answers with is looked at until it ends."""


class Hetzner:
    """TXT records added to and removed from a zone's record set through the Hetzner Cloud API."""

    timing = Timing()

    def __init__(self, token: str) -> None:
        """Hold the API token."""
        self._api = Api(PROVIDER, ENDPOINT, bearer(token))

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> Hetzner:
        """Return the provider its settings describe."""
        return cls(secret(environment, CREDENTIAL_FILE))

    def _zone(self, name: str) -> str:
        for candidate in candidates(name):
            found = cast(
                "list[Document]",
                self._api.document(HTTPMethod.GET, "/zones", Asking(params={"name": candidate}))["zones"],
            )
            if found:
                return candidate
        msg = f"Hetzner holds no zone for {name}."
        raise ProviderError(msg)

    def _changed(self, name: str, value: str, action: str, ttl: int | None) -> None:
        zone = self._zone(name)
        body: Document = {"records": [{"value": f'"{value}"'}]}
        if ttl is not None:
            body["ttl"] = ttl
        path = f"/zones/{zone}/rrsets/{relative(name, zone)}/TXT/actions/{action}"
        started = cast("Document", self._api.document(HTTPMethod.POST, path, Asking(body=body))["action"])
        self._ended(int(started["id"]), str(started["status"]))

    def _ended(self, action: int, status: str) -> None:
        """Wait for an action to end, refusing one that ends in an error or does not end in time."""
        for _ in range(ACTION_CHECKS):
            if status != RUNNING:
                break
            time.sleep(ACTION_INTERVAL)
            status = str(self._api.document(HTTPMethod.GET, f"/actions/{action}")["action"]["status"])
        if status != SUCCEEDED:
            msg = f"The Hetzner action {action} ended as {status}."
            raise ProviderError(msg)

    def present(self, name: str, value: str) -> None:
        """Add the value to the name's TXT record set, making it where there is none."""
        self._changed(name, value, "add_records", TTL)

    def cleanup(self, name: str, value: str) -> None:
        """Remove the value from the name's TXT record set."""
        self._changed(name, value, "remove_records", None)
