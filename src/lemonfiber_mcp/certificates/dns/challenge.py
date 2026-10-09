# Copyright (c) 2026 NightWorksIO
"""A DNS-01 answer: its record written through the provider where the name's CNAMEs lead, and waited for."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import dns.exception
import dns.resolver

from lemonfiber_mcp.certificates.dns.propagation import (
    Server,
    Waiting,
    authoritative,
    challenge_name,
    delegated,
    seen_everywhere,
)
from lemonfiber_mcp.certificates.modes import CertificateError

if TYPE_CHECKING:
    from collections.abc import Callable

    from lemonfiber_mcp.certificates.dns.provider import Provider


@dataclass(frozen=True, slots=True)
class Dns01:
    """How DNS-01 is answered: the provider, how names are looked up, where a zone's servers are, and how a wait is spent."""

    provider: Provider
    resolver: Callable[[], dns.resolver.Resolver] = dns.resolver.Resolver
    servers: Callable[[str, dns.resolver.Resolver], list[Server]] = authoritative
    waiting: Waiting = field(default_factory=Waiting)

    def where(self, name: str) -> str:
        """Return where the record for a name is written: its challenge name, or where that name's CNAMEs lead."""
        try:
            resolver = self.resolver()
        except dns.exception.DNSException as failed:
            msg = f"Names could not be looked up to answer DNS-01 for {name}: {type(failed).__name__}."
            raise CertificateError(msg) from None
        return delegated(challenge_name(name), resolver)

    def wait_for(self, name: str, value: str) -> None:
        """Wait until every authoritative server of the record's zone answers with its value, refusing where none does in time."""
        try:
            servers = self.servers(name, self.resolver())
        except dns.exception.DNSException as failed:
            msg = f"The authoritative servers of {name} could not be found: {type(failed).__name__}."
            raise CertificateError(msg) from None
        if not servers:
            msg = f"No authoritative server of {name} has an address to ask."
            raise CertificateError(msg)
        if not seen_everywhere(name, value, servers, self.provider.timing, self.waiting):
            seconds = round(self.provider.timing.propagation)
            msg = f"The record at {name} was not answered by every authoritative server within {seconds} seconds."
            raise CertificateError(msg)
