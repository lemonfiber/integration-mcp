# Copyright (c) 2026 NightWorksIO
"""A DNS server of the operator's own, updated as RFC 2136 sets out and signed with a TSIG key."""

from typing import TYPE_CHECKING, Final

import dns.exception
import dns.message
import dns.name
import dns.query
import dns.rcode
import dns.rdatatype
import dns.tsigkeyring
import dns.update

from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, candidates, needed, secret
from lemonfiber_mcp.certificates.settings import TlsSettingsError

if TYPE_CHECKING:
    from collections.abc import Mapping

NAMESERVER: Final = "RFC2136_NAMESERVER"
TSIG_KEY: Final = "RFC2136_TSIG_KEY"
TSIG_ALGORITHM: Final = "RFC2136_TSIG_ALGORITHM"
TSIG_CREDENTIAL_FILE: Final = "RFC2136_TSIG_SECRET_FILE"
DEFAULT_ALGORITHM: Final = "hmac-sha256."
PORT: Final = 53
TTL: Final = 60
TIMEOUT_SECONDS: Final = 10.0


def nameserver_of(written: str) -> tuple[str, int]:
    """Return the server and port a setting names: `host`, `host:port`, an IPv6 address, or `[address]:port`."""
    if written.startswith("["):
        address, _, port = written[1:].partition("]")
        return address, int(port.removeprefix(":") or PORT)
    if written.count(":") == 1:
        host, _, port = written.partition(":")
        return host, int(port)
    return written, PORT


class Rfc2136:
    """TXT records written by dynamic update to the operator's own DNS server."""

    timing = Timing(propagation=60.0, interval=2.0)

    def __init__(self, server: tuple[str, int], key: str, algorithm: str, key_secret: str) -> None:
        """Hold the server and the TSIG key updates are signed with."""
        self._server = server
        self._algorithm = dns.name.from_text(algorithm)
        try:
            self._keyring = dns.tsigkeyring.from_text({key: key_secret})
        except ValueError, dns.exception.DNSException:
            msg = f"{TSIG_CREDENTIAL_FILE} does not hold a TSIG secret in base64."
            raise TlsSettingsError(msg) from None

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> Rfc2136:
        """Return the provider its settings describe."""
        return cls(
            nameserver_of(needed(environment, NAMESERVER)),
            needed(environment, TSIG_KEY),
            environment.get(TSIG_ALGORITHM, "").strip() or DEFAULT_ALGORITHM,
            secret(environment, TSIG_CREDENTIAL_FILE),
        )

    def _zone(self, name: str) -> str:
        for candidate in candidates(name):
            query = dns.message.make_query(f"{candidate}.", dns.rdatatype.SOA)
            try:
                response = dns.query.udp(
                    query,
                    self._server[0],
                    timeout=TIMEOUT_SECONDS,
                    port=self._server[1],
                )
            except dns.exception.DNSException, OSError:
                continue
            if any(answer.rdtype == dns.rdatatype.SOA for answer in response.answer):
                return f"{candidate}."
        msg = f"The DNS server at {self._server[0]} holds no zone for {name}."
        raise ProviderError(msg)

    def _update(self, name: str) -> dns.update.UpdateMessage:
        """Return an update to the zone a name sits in, signed with the key."""
        return dns.update.UpdateMessage(self._zone(name), keyring=self._keyring, keyalgorithm=self._algorithm)

    def _sent(self, update: dns.update.UpdateMessage) -> None:
        try:
            response = dns.query.tcp(update, self._server[0], timeout=TIMEOUT_SECONDS, port=self._server[1])
        except (dns.exception.DNSException, OSError, EOFError) as failed:
            msg = f"The DNS server at {self._server[0]} could not be updated: {type(failed).__name__}."
            raise ProviderError(msg) from None
        if response.rcode() != dns.rcode.NOERROR:
            msg = f"The DNS server at {self._server[0]} refused the update: {dns.rcode.to_text(response.rcode())}."
            raise ProviderError(msg)

    def present(self, name: str, value: str) -> None:
        """Add the TXT record."""
        update = self._update(name)
        update.add(name, TTL, dns.rdatatype.TXT, f'"{value}"')
        self._sent(update)

    def cleanup(self, name: str, value: str) -> None:
        """Delete the TXT record."""
        update = self._update(name)
        update.delete(name, dns.rdatatype.TXT, f'"{value}"')
        self._sent(update)
