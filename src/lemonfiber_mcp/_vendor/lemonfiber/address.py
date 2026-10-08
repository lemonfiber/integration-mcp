# Copyright (c) 2026 NightWorksIO
"""Where a stack is: on this machine, or anywhere a certificate pin vouches for."""

import asyncio
import ipaddress
import re
import socket
import urllib.parse
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, override

from lemonfiber.problems import AddressRefusedError

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

type Resolver = Callable[[str], Sequence[str]]
"""Turns a host name into every address it resolves to."""

SCHEMES: Final = frozenset({"http", "https"})
"""The schemes lemonfiber is reached over."""

ENCRYPTED: Final = "https"
"""The scheme a pin is checked over."""

PORTS: Final = {"http": 80, "https": 443}
"""The port each scheme names by naming none."""

SEPARATOR: Final = "/"
"""What separates the segments of a path."""

NAME: Final = re.compile(r"[a-z0-9_]([a-z0-9_-]*[a-z0-9_])?(\.[a-z0-9_]([a-z0-9_-]*[a-z0-9_])?)*\.?")
"""A host name: labels of letters, digits, hyphens and underscores, as the address's lowercased host spells one."""

PIN: Final = re.compile(r"^[0-9a-f]{64}$")
"""A certificate pin's one written form: SHA-256 over the certificate's DER encoding, lower-case hex."""


class CertificatePin:
    """The digest of the one certificate a stack is permitted to present."""

    __slots__ = ("_hex",)

    def __init__(self, digest: str) -> None:
        """Take a pin from pairing material, refusing anything but a certificate's SHA-256 digest."""
        written = digest.strip().lower()
        if not PIN.match(written):
            msg = (
                "A certificate pin is the SHA-256 digest of the stack's certificate, written as "
                "64 hexadecimal characters; what was given is not one."
            )
            raise AddressRefusedError(msg)
        self._hex = written

    @property
    def hex(self) -> str:
        """Return the digest as 64 lower-case hexadecimal characters."""
        return self._hex

    @property
    def digest(self) -> bytes:
        """Return the digest as the 32 bytes it is."""
        return bytes.fromhex(self._hex)

    @override
    def __eq__(self, other: object) -> bool:
        return isinstance(other, CertificatePin) and other.hex == self._hex

    @override
    def __hash__(self) -> int:
        return hash(self._hex)

    @override
    def __repr__(self) -> str:
        return f"CertificatePin({self._hex!r})"


def resolve(host: str) -> list[str]:
    """Return every address the system resolver gives a host name."""
    try:
        found = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except OSError:
        return []
    return [str(info[4][0]) for info in found]


def is_loopback(address: str) -> bool:
    """Tell whether a literal address, IPv4-mapped ones included, is one on this machine."""
    try:
        return ipaddress.ip_address(address).is_loopback
    except ValueError:
        return False


def is_literal(host: str) -> bool:
    """Tell whether a host is written as an address rather than as a name."""
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return False
    return True


def bracketed(host: str) -> str:
    """Write a host as a URL's authority carries it: an IPv6 address in brackets."""
    return f"[{host}]" if ":" in host else host


@dataclass(frozen=True, slots=True)
class Route:
    """One way to a stack: where a connection is made, and the name the stack is asked for there."""

    host: str
    """The host a connection is made to."""
    base: str
    """The address every path is joined onto, over this route."""
    named: str | None = None
    """The host name given, where `host` is an address that name resolved to when it was given."""
    authority: str | None = None
    """What the `Host` header carries, where `host` is not what the address named."""

    def url(self, path: str) -> str:
        """Return the address of a path on this stack, over this route."""
        return f"{self.base}{path}"

    def headers(self) -> dict[str, str]:
        """Return the `Host` header naming the stack as it was given, where this route reaches it by address."""
        return {} if self.authority is None else {"Host": self.authority}


def split(url: str) -> tuple[urllib.parse.SplitResult, str, str, int | None]:
    """Return an address's parts, scheme, host and port, refusing what is not an address lemonfiber prints."""
    parts = urllib.parse.urlsplit(url.strip())
    scheme = parts.scheme.lower()
    if scheme not in SCHEMES:
        msg = f"lemonfiber is reached over http or https, and {url!r} names neither."
        raise AddressRefusedError(msg)
    if parts.username is not None or parts.password is not None or parts.query or parts.fragment:
        msg = "That address carries more than an address: a credential, a query or a fragment."
        raise AddressRefusedError(msg)
    host = parts.hostname
    try:
        port = parts.port
    except ValueError:
        port = 0
    if not host or port == 0 or not (is_literal(host) or NAME.fullmatch(host)):
        msg = f"{url!r} is not an address."
        raise AddressRefusedError(msg)
    return parts, scheme, host, port


def vouched_for(host: str, scheme: str, pin: CertificatePin | None, resolver: Resolver) -> list[str]:
    """Return the addresses a host is reached at, refusing one neither a pin nor this machine vouches for."""
    if pin is not None and scheme != ENCRYPTED:
        msg = "A pinned address is reached over https: a pin is checked against the certificate TLS presents."
        raise AddressRefusedError(msg)
    reached = [host] if pin is not None or is_literal(host) else resolved_once(host, resolver)
    if pin is None and not (reached and all(is_loopback(one) for one in reached)):
        msg = (
            f"{host} is not on this machine, and a stack anywhere else is reached only with its "
            "certificate pin, given with the address."
        )
        raise AddressRefusedError(msg)
    return reached


class Address:
    """A stack's base address, and the pin it is held to where it is not on this machine.

    A loopback address needs no pin. Any other address needs one, and an
    address and its pin are given together, so there is no way to name a stack
    off this machine without one. A named host is accepted unpinned only where
    every address it resolves to is loopback.
    """

    __slots__ = ("_base", "_host", "_pin", "_port", "_prefix", "_routes", "_scheme")

    def __init__(
        self,
        url: str,
        *,
        pin: str | CertificatePin | None = None,
        resolver: Resolver = resolve,
    ) -> None:
        """Read a base address as lemonfiber printed it, refusing one the pin does not vouch for."""
        parts, scheme, host, port = split(url)
        held = pin if isinstance(pin, CertificatePin) or pin is None else CertificatePin(pin)
        reached = vouched_for(host, scheme, held, resolver)
        self._scheme = scheme
        self._host = host
        self._port = port if port is not None else PORTS[scheme]
        self._pin = held
        self._prefix = parts.path.rstrip(SEPARATOR)
        authority = f"{bracketed(host)}:{self._port}"
        self._base = f"{scheme}://{authority}{self._prefix}"
        self._routes = tuple(
            Route(host, self._base)
            if one == host
            else Route(one, f"{scheme}://{bracketed(one)}:{self._port}{self._prefix}", host, authority)
            for one in reached
        )

    @classmethod
    async def resolved(cls, url: str, *, pin: str | CertificatePin | None = None) -> Address:
        """Read a base address as `Address` does, resolving a host name without blocking the event loop."""
        host = urllib.parse.urlsplit(url.strip()).hostname
        if pin is not None or not host or is_literal(host):
            return cls(url, pin=pin)
        try:
            infos = await asyncio.get_running_loop().getaddrinfo(host, None, type=socket.SOCK_STREAM)
        except OSError:
            infos = []
        found = [str(info[4][0]) for info in infos]
        return cls(url, resolver=lambda _: found)

    @property
    def base(self) -> str:
        """Return the address every path is joined onto, with its port written out."""
        return self._base

    @property
    def scheme(self) -> str:
        """Return `http` or `https`."""
        return self._scheme

    @property
    def host(self) -> str:
        """Return the host, as a name or a literal address."""
        return self._host

    @property
    def port(self) -> int:
        """Return the port, the scheme's own where the address named none."""
        return self._port

    @property
    def prefix(self) -> str:
        """Return the path every request's path is written beneath, empty where the address named none."""
        return self._prefix

    @property
    def pin(self) -> CertificatePin | None:
        """Return the certificate this address is held to, where it is held to one."""
        return self._pin

    @property
    def routes(self) -> tuple[Route, ...]:
        """Return every way to the stack, in the order they are tried.

        A host name given without a pin was resolved when the address was given,
        and was accepted because every address it resolved to is loopback; those
        addresses are where connections go, each asking for the stack by its
        name, so a name that later resolves elsewhere reaches nothing new. A
        literal address, or any address held to a pin, is its own one route.
        """
        return self._routes

    def url(self, path: str) -> str:
        """Return the address of a path on this stack."""
        return f"{self._base}{path}"

    @override
    def __repr__(self) -> str:
        return f"Address({self._base!r}, pin={self._pin!r})"


def resolved_once(host: str, resolver: Resolver) -> list[str]:
    """Return every address a name resolves to, once each, in the order the resolver gave them."""
    return list(dict.fromkeys(resolver(host)))
