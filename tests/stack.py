# Copyright (c) 2026 NightWorksIO
"""A stand-in stack: a real TLS server on loopback, with a certificate a pin names, answering as a test tells it.

Each path is answered from replies a test queues, in turn, the last one from
then on, and every request that arrives is recorded with its headers, query and
body, so a test can say what reached the stack and what never did.
"""

import asyncio
import hashlib
import json
import ssl
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Final, Self

import trustme
from aiohttp import web

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping
    from types import TracebackType

API_VERSION: Final = 1
LOOPBACK: Final = "127.0.0.1"
LET_GO: Final = "Error on transport creation for incoming connection"
"""What the event loop says when a client lets a connection go while the stand-in is still accepting it."""


def envelope(kind: str, data: object, version: int = API_VERSION) -> dict[str, object]:
    """Return an envelope as lemonfiber writes one."""
    return {"api_version": version, "kind": kind, "data": data}


def problem(code: str, summary: str, detail: str | None = None) -> dict[str, object]:
    """Return an `error` envelope carrying one problem."""
    data: dict[str, object] = {
        "code": code,
        "severity": "error",
        "state": "actionable",
        "summary": summary,
        "meaning": "",
        "remedies": [],
    }
    if detail is not None:
        data["detail"] = detail
    return envelope("error", data)


@dataclass(frozen=True)
class Reply:
    """One answer: a status, a body, and the headers beside it."""

    status: int = 200
    body: object = None
    headers: Mapping[str, str] = field(default_factory=dict[str, str])
    raw: bytes | None = None
    """Bytes sent as they are, with `content_type`, in place of a JSON body."""
    content_type: str = "application/json"

    def response(self) -> web.Response:
        """Return the answer as aiohttp sends it."""
        if self.raw is not None:
            return web.Response(
                status=self.status,
                body=self.raw,
                content_type=self.content_type,
                headers=self.headers,
            )
        if isinstance(self.body, str):
            return web.Response(status=self.status, text=self.body, headers=self.headers)
        return web.Response(
            status=self.status,
            body=json.dumps(self.body).encode(),
            content_type="application/json",
            headers=self.headers,
        )


@dataclass(frozen=True)
class Arrival:
    """One request as it reached the stand-in."""

    method: str
    path: str
    headers: Mapping[str, str]
    query: Mapping[str, list[str]]
    body: object


class Stack:
    """A loopback TLS server answering each path with the replies it was given, in order, the last from then on."""

    def __init__(self) -> None:
        """Make a certificate of the stand-in's own, and the pin that names it."""
        self.arrived: list[Arrival] = []
        self._replies: dict[str, list[Reply]] = {}
        authority = trustme.CA()
        issued = authority.issue_cert(LOOPBACK, "localhost")
        self._context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        with issued.private_key_and_cert_chain_pem.tempfile() as path:
            self._context.load_cert_chain(path)
        der = ssl.PEM_cert_to_DER_cert(issued.cert_chain_pems[0].bytes().decode())
        self.pin = hashlib.sha256(der).hexdigest()
        self.port = 0
        self._runner: web.AppRunner | None = None
        self._handler: Callable[[asyncio.AbstractEventLoop, dict[str, Any]], object] | None = None

    @property
    def url(self) -> str:
        """Return the address the stand-in serves at."""
        return f"https://{LOOPBACK}:{self.port}"

    def reply(self, path: str, *replies: Reply) -> None:
        """Answer a path with these replies in turn, the last one from then on."""
        self._replies[path] = list(replies)

    def asked(self, path: str) -> list[Arrival]:
        """Return every request that arrived for a path, in order."""
        return [arrival for arrival in self.arrived if arrival.path == path]

    async def _handle(self, request: web.Request) -> web.StreamResponse:
        raw = await request.read()
        body: object = json.loads(raw) if raw else None
        query: dict[str, list[str]] = {}
        for name, value in request.query.items():
            query.setdefault(name, []).append(value)
        self.arrived.append(Arrival(request.method, request.path, dict(request.headers), query, body))
        queued = self._replies.get(request.path)
        if not queued:
            return web.Response(status=599, text="the stand-in was not told how to answer this")
        reply = queued.pop(0) if len(queued) > 1 else queued[0]
        return reply.response()

    def _accepting(self, loop: asyncio.AbstractEventLoop, context: dict[str, Any]) -> None:
        """Pass on every failure the event loop reports but a client letting go of a connection being accepted."""
        if str(context.get("message", "")).startswith(LET_GO) and isinstance(
            context.get("exception"),
            ConnectionError | ssl.SSLError,
        ):
            return
        if self._handler is None:
            loop.default_exception_handler(context)
        else:
            self._handler(loop, context)

    async def __aenter__(self) -> Self:
        """Start serving."""
        loop = asyncio.get_running_loop()
        self._handler = loop.get_exception_handler()
        loop.set_exception_handler(self._accepting)
        application = web.Application()
        application.router.add_route("*", "/{tail:.*}", self._handle)
        self._runner = web.AppRunner(application, access_log=None, shutdown_timeout=0.1)
        await self._runner.setup()
        site = web.TCPSite(self._runner, LOOPBACK, 0, ssl_context=self._context)
        await site.start()
        self.port = int(self._runner.addresses[0][1])
        return self

    async def __aexit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Stop serving."""
        if self._runner is not None:
            await self._runner.cleanup()
        asyncio.get_running_loop().set_exception_handler(self._handler)
