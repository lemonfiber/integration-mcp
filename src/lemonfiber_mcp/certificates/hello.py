# Copyright (c) 2026 NightWorksIO
"""What a TLS ClientHello asks for, read before the handshake: the name it is for and the protocols it offers.

Only what decides how a connection is answered is read: the server name
indication and the application protocols. A ClientHello not yet whole is
`INCOMPLETE`, so the caller waits for more; one that is not a ClientHello, or
cannot be read, comes to nothing asked, and the connection is answered as
any other.
"""

from dataclasses import dataclass
from typing import Final

HANDSHAKE: Final = 22
CLIENT_HELLO: Final = 1
SERVER_NAME: Final = 0
APPLICATION_PROTOCOLS: Final = 16
HOST_NAME: Final = 0
RECORD_HEADER: Final = 5
HANDSHAKE_HEADER: Final = 4
RANDOM: Final = 32
VERSION: Final = 2


@dataclass(frozen=True, slots=True)
class Hello:
    """What a ClientHello asks for: the server name, and the application protocols in the client's order."""

    server_name: str | None
    protocols: tuple[str, ...]


NOTHING_ASKED: Final = Hello(None, ())
"""What a connection that is not a readable ClientHello asks for."""


class Incomplete:
    """A ClientHello that has not all arrived."""


INCOMPLETE: Final = Incomplete()


class Reader:
    """Bytes read in order, each read refused past the end."""

    def __init__(self, data: bytes) -> None:
        """Start at the beginning of `data`."""
        self._data = data
        self._at = 0

    def take(self, count: int) -> bytes:
        """Return the next `count` bytes, raising `ValueError` where fewer are left."""
        if self._at + count > len(self._data):
            msg = "past the end"
            raise ValueError(msg)
        taken = self._data[self._at : self._at + count]
        self._at += count
        return taken

    def take_all(self) -> bytes:
        """Return every byte left."""
        return self.take(self.left)

    def number(self, size: int) -> int:
        """Return the next big-endian number of `size` bytes."""
        return int.from_bytes(self.take(size))

    def vector(self, size: int) -> Reader:
        """Return a reader of the next vector, whose length is given in `size` bytes."""
        return Reader(self.take(self.number(size)))

    @property
    def left(self) -> int:
        """Return how many bytes are left."""
        return len(self._data) - self._at


def server_name(extension: Reader) -> str | None:
    """Return the host name a server name extension carries, or None where it carries none."""
    names = extension.vector(2)
    while names.left:
        kind = names.number(1)
        name = names.vector(2).take_all()
        if kind == HOST_NAME:
            return name.decode("ascii").lower()
    return None


def protocols(extension: Reader) -> tuple[str, ...]:
    """Return the application protocols an extension offers, in the client's order."""
    offered = extension.vector(2)
    found: list[str] = []
    while offered.left:
        # Each protocol is taken off before it is decoded, so every pass shortens what is left.
        protocol = offered.vector(1).take_all()
        found.append(protocol.decode("ascii"))
    return tuple(found)


def read(data: bytes) -> Hello | Incomplete:
    """Return what the first record of a connection asks for, `INCOMPLETE` where it has not all arrived."""
    if len(data) < RECORD_HEADER:
        return INCOMPLETE
    record = Reader(data)
    if record.number(1) != HANDSHAKE:
        return NOTHING_ASKED
    record.take(VERSION)
    length = record.number(2)
    if record.left < length:
        return INCOMPLETE
    try:
        return hello(Reader(record.take(length)))
    except ValueError, UnicodeDecodeError:
        return NOTHING_ASKED


def hello(handshake: Reader) -> Hello:
    """Return what a handshake message asks for, raising `ValueError` where it is not a whole ClientHello."""
    if handshake.number(1) != CLIENT_HELLO:
        return NOTHING_ASKED
    body = handshake.vector(3)
    body.take(VERSION + RANDOM)
    body.vector(1)
    body.vector(2)
    body.vector(1)
    name: str | None = None
    offered: tuple[str, ...] = ()
    extensions = body.vector(2) if body.left else Reader(b"")
    while extensions.left:
        kind = extensions.number(2)
        extension = extensions.vector(2)
        if kind == SERVER_NAME:
            name = server_name(extension)
        elif kind == APPLICATION_PROTOCOLS:
            offered = protocols(extension)
    return Hello(name, offered)
