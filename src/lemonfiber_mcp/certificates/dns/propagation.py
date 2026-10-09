# Copyright (c) 2026 NightWorksIO
"""Where a challenge's record is written, and whether every authoritative server answers with it yet.

A `_acme-challenge` name delegated by CNAME is followed to where it points.
Before the authority is told to look, the zone's authoritative servers are
asked directly, each of them, until every one answers with the value.
"""

import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, cast

import dns.exception
import dns.message
import dns.query
import dns.rdatatype
import dns.resolver

if TYPE_CHECKING:
    from collections.abc import Callable

    from dns.rdtypes.ANY.CNAME import CNAME
    from dns.rdtypes.ANY.NS import NS
    from dns.rdtypes.ANY.TXT import TXT

    from lemonfiber_mcp.certificates.dns.provider import Timing

CHALLENGE_LABEL: Final = "_acme-challenge"
MOST_CNAMES: Final = 8
"""The longest chain of CNAMEs followed before the name is taken as it is."""
QUERY_TIMEOUT: Final = 5.0
PORT: Final = 53

type Server = tuple[str, int]
"""An authoritative server: its address, and the port it answers on."""


def challenge_name(name: str) -> str:
    """Return the name a challenge's TXT record is looked up at, for a name the certificate covers."""
    return f"{CHALLENGE_LABEL}.{name.rstrip('.')}."


def delegated(name: str, resolver: dns.resolver.Resolver) -> str:
    """Return where a name's CNAMEs lead, the name itself where it has none."""
    current = name
    for _ in range(MOST_CNAMES):
        try:
            answer = resolver.resolve(current, dns.rdatatype.CNAME)
        except dns.exception.DNSException:
            return current
        current = str(cast("CNAME", answer[0]).target)
    return current


def authoritative(name: str, resolver: dns.resolver.Resolver) -> list[Server]:
    """Return every authoritative server of the zone a name sits in."""
    zone = dns.resolver.zone_for_name(name, resolver=resolver)
    servers: list[Server] = []
    for record in resolver.resolve(zone, dns.rdatatype.NS):
        host = str(cast("NS", record).target)
        for kind in (dns.rdatatype.A, dns.rdatatype.AAAA):
            try:
                servers.extend((str(address), PORT) for address in resolver.resolve(host, kind))
            except dns.exception.DNSException:
                continue
    return servers


def answers_with(server: Server, name: str, value: str) -> bool:
    """Tell whether a server answers a name's TXT lookup with the value."""
    query = dns.message.make_query(name, dns.rdatatype.TXT)
    try:
        response = dns.query.udp(query, server[0], timeout=QUERY_TIMEOUT, port=server[1])
    except dns.exception.DNSException, OSError:
        return False
    held: list[TXT] = []
    for answer in response.answer:
        if answer.rdtype == dns.rdatatype.TXT:
            held.extend(cast("list[TXT]", list(answer)))
    return any(b"".join(record.strings) == value.encode() for record in held)


@dataclass(frozen=True, slots=True)
class Waiting:
    """How the wait for a record is spent: sleeping, and reading the time."""

    sleep: Callable[[float], None] = time.sleep
    clock: Callable[[], float] = time.monotonic


def seen_everywhere(name: str, value: str, servers: list[Server], timing: Timing, waiting: Waiting) -> bool:
    """Wait until every server answers with the value, and tell whether they did before the provider's time ran out."""
    until = waiting.clock() + timing.propagation
    while not all(answers_with(server, name, value) for server in servers):
        if waiting.clock() >= until:
            return False
        waiting.sleep(timing.interval)
    return True
