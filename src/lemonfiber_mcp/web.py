# Copyright (c) 2026 NightWorksIO
"""The HTTP mode: Streamable HTTP over TLS, each request answered with the key it brought.

The server holds no credential of its own. A request carries the person's
integration key as `Authorization: Bearer`, and is refused before the protocol
sees it without one. That key reaches the stack for that request alone, through
a client opened for it and closed after it; what is known of the key between
requests is held by its digest, never the key itself, so a refused key stays
refused and is not sent again. `/health` answers without a key and with
nothing about the stack, and in `private-ca` the root is served at `/root.pem`.
"""

import contextvars
import hashlib
import logging
from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from lemonfiber import AsyncClient, Credential
from starlette.responses import JSONResponse, Response

from lemonfiber_mcp import serving, settings
from lemonfiber_mcp.connection import Connection, Held

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator

    from lemonfiber import Address
    from starlette.types import ASGIApp, Receive, Scope, Send

    from lemonfiber_mcp.certificates.manager import Certificates
    from lemonfiber_mcp.withheld import Withholding

LISTEN: Final = "LEMONFIBER_LISTEN"
PATH: Final = "/mcp"
HEALTH: Final = "/health"
ROOT: Final = "/root.pem"
BEARER: Final = "bearer"
"""The `Authorization` scheme a key is carried in, read in any letter case."""
HELD_KEYS: Final = 1024
"""How many keys' digests are remembered at once, the least lately used let go first."""
UNAUTHORISED: Final = 401
NOT_FOUND: Final = 404
REFUSED_WITHOUT_A_KEY: Final = (
    "Every request carries the person's integration key, as `Authorization: Bearer <key>`. "
    "This server holds none of its own."
)
PEM: Final = "application/x-pem-file"

logger = logging.getLogger(__name__)

current: contextvars.ContextVar[Connection] = contextvars.ContextVar("current")
"""The connection the request being answered opened with its own key."""


def digest_of(key: str) -> str:
    """Return what a key is held by: its SHA-256 digest, so the pool keeps no key."""
    return hashlib.sha256(key.encode()).hexdigest()


class Pool:
    """What is known of each key lately seen, by the key's digest, a bounded number at once."""

    def __init__(self, size: int = HELD_KEYS) -> None:
        """Hold nothing yet, and at most `size` keys' digests."""
        self._size = size
        self._held: OrderedDict[str, Held] = OrderedDict()

    def held(self, key: str) -> Held:
        """Return what is known of a key, by its digest, starting afresh for one not lately seen."""
        digest = digest_of(key)
        held = self._held.pop(digest, None) or Held()
        self._held[digest] = held
        while len(self._held) > self._size:
            self._held.popitem(last=False)
        return held

    def __len__(self) -> int:
        """Return how many keys' digests are held."""
        return len(self._held)

    def __contains__(self, key: object) -> bool:
        """Tell whether what is known of a key is held."""
        return isinstance(key, str) and digest_of(key) in self._held

    def __iter__(self) -> Iterator[str]:
        """Return the digests held, the least lately used first."""
        return iter(list(self._held))


def bearer(scope: Scope) -> str | None:
    """Return the integration key a request carries as `Authorization: Bearer`, or None where it carries none."""
    for name, value in scope.get("headers", []):
        if name.lower() == b"authorization":
            scheme, _, carried = value.decode("latin-1").strip().partition(" ")
            key = carried.strip()
            return key if scheme.lower() == BEARER and settings.KEY_SHAPE.fullmatch(key) else None
    return None


def opened() -> Connection:
    """Return the connection the request being answered opened with its own key."""
    return current.get()


@dataclass(frozen=True, slots=True)
class Gate:
    """The way in: `/health` and the root answered here, every other request only with a key."""

    app: ASGIApp
    address: Address
    withholding: Withholding
    pool: Pool
    certificates: Certificates
    root: pathlib.Path | None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """Answer one ASGI event, handing it to the protocol where it carried a key."""
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        path = scope["path"]
        if path == HEALTH:
            status, body = self.certificates.health()
            await JSONResponse(body, status_code=status)(scope, receive, send)
            return
        if path == ROOT:
            answer = (
                Response(self.root.read_bytes(), media_type=PEM)
                if self.root is not None and self.root.is_file()
                else Response(status_code=NOT_FOUND)
            )
            await answer(scope, receive, send)
            return
        key = bearer(scope)
        if key is None:
            refused = JSONResponse(
                {"error": REFUSED_WITHOUT_A_KEY},
                status_code=UNAUTHORISED,
                headers={"WWW-Authenticate": "Bearer"},
            )
            await refused(scope, receive, send)
            return
        async with AsyncClient(self.address, Credential(key)) as client:
            token = current.set(Connection(client, self.withholding, self.pool.held(key)))
            try:
                await self.app(scope, receive, send)
            finally:
                current.reset(token)


def protocol(withholding: Withholding, version: str, host: str) -> ASGIApp:
    """Return the protocol's stateless Streamable HTTP, answered from each request's own connection."""
    server = serving.build(opened, withholding, version)
    return server.streamable_http_app(
        streamable_http_path=PATH,
        json_response=True,
        stateless_http=True,
        host=host,
    )
