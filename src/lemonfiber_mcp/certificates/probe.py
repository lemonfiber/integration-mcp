# Copyright (c) 2026 NightWorksIO
"""Ask the server's own health answer, over its own TLS, trusting only the certificates it keeps.

The image's health check runs this beside the server. The connection trusts
the certificates in the chain the server keeps and nothing else, any of them as
an anchor, and checks the presented certificate for a name it covers: the
probe holds the server to what it keeps, as a pin does, with the validator's
own checks of time and name.
"""

import http.client
import ipaddress
import ssl
from typing import TYPE_CHECKING, Final, override

from lemonfiber_mcp.certificates import making
from lemonfiber_mcp.certificates.modes import chain_of

if TYPE_CHECKING:
    import pathlib

    from cryptography import x509

TIMEOUT_SECONDS: Final = 10.0
HEALTHY: Final = 200
ANYWHERE: Final[dict[ipaddress.IPv4Address | ipaddress.IPv6Address, str]] = {
    ipaddress.IPv4Address(0): "127.0.0.1",
    ipaddress.IPv6Address(0): "::1",
}
"""Where a server listening on every address is reached from beside it."""
WILDCARD: Final = "*."
STANDING_IN: Final = "health."
"""The label a wildcard name is checked with, being no name a connection can ask for."""


class Kept(http.client.HTTPSConnection):
    """An HTTPS connection trusting only the kept certificates, and checking the presented one for a name."""

    def __init__(self, host: str, port: int, chain: pathlib.Path, name: str) -> None:
        """Hold where the server is, the certificates to trust, and the name to check the certificate for."""
        trusted = ssl.create_default_context(cafile=chain)
        trusted.verify_flags |= ssl.VERIFY_X509_PARTIAL_CHAIN
        super().__init__(host, port, timeout=TIMEOUT_SECONDS, context=trusted)
        self._trusted = trusted
        self._name = name

    @override
    def connect(self) -> None:
        """Connect to the address, and check the certificate for the name rather than the address."""
        http.client.HTTPConnection.connect(self)
        self.sock = self._trusted.wrap_socket(self.sock, server_hostname=self._name)


def reached(host: str) -> str:
    """Return the address a server listening at `host` is reached at from beside it."""
    try:
        written = ipaddress.ip_address(host)
    except ValueError:
        return host
    return ANYWHERE.get(written, str(written))


def named(leaf: x509.Certificate) -> str | None:
    """Return a name the certificate covers to check it for, a wildcard's with a label standing in, or None."""
    names = sorted(str(name) for name in making.covered(leaf))
    exact = [name for name in names if not name.startswith(WILDCARD)]
    if exact:
        return exact[0]
    return STANDING_IN + names[0].removeprefix(WILDCARD) if names else None


def healthy(host: str, port: int, chain: pathlib.Path) -> bool:
    """Tell whether the server at a port answers its health as healthy, presenting a certificate `chain` vouches for.

    A chain that cannot be read, or whose certificate covers no name, is no
    certificate to hold the server to, so the server is not healthy.
    """
    try:
        name = named(chain_of(chain)[0])
        if name is None:
            return False
        connection = Kept(reached(host), port, chain, name)
    except OSError, ValueError:
        return False
    try:
        connection.request("GET", "/health")
        return connection.getresponse().status == HEALTHY
    except OSError, http.client.HTTPException:
        return False
    finally:
        connection.close()
