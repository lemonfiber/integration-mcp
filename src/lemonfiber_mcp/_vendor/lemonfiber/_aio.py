# Copyright (c) 2026 NightWorksIO
"""The asynchronous client, on aiohttp.

A pinned address is reached with an `aiohttp.Fingerprint` on every request:
aiohttp compares the certificate's SHA-256 digest with it once the handshake
completes and before a byte of the request is written, and refuses the
connection where they differ. It is given per request rather than to a
connector, so it holds on a session the caller supplied, whatever that session's
connector was built with; an unpinned https address is given a verifying
context per request for the same reason.
"""

import asyncio
import ssl
from typing import TYPE_CHECKING, Final, Self

import aiohttp

from lemonfiber._protocol import operation
from lemonfiber._protocol.calls import DEFAULT_TIMEOUT, Answer, Call, declared_over, received, with_credential
from lemonfiber._protocol.following import DEFAULT_EVERY, job_name, next_wait
from lemonfiber._protocol.refusals import CERTIFICATE_REFUSED, NOT_ANSWERING, opening_refusal
from lemonfiber._protocol.retry import Attempts
from lemonfiber.jobs import Ended, Finished, Running
from lemonfiber.problems import (
    CertificateRefusedError,
    ConfigurationError,
    LemonfiberError,
    UnreachableError,
)
from lemonfiber.reads import HELD_ID_BACKDROP, HELD_ID_POSTER
from lemonfiber.stream import FIRST_WAIT, OPENED, RECONNECTS_ALLOWED, SILENCE_ALLOWED, Break, Following

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, AsyncIterator, Callable, Mapping, Sequence
    from types import TracebackType

    from lemonfiber._generated import Envelope, JobEnvelope, LogEnvelope
    from lemonfiber._protocol.calls import Json, Query
    from lemonfiber.address import Address, Route
    from lemonfiber.capabilities import CapabilitySet
    from lemonfiber.credential import Credential, Session
    from lemonfiber.files import BundleFile, Picture
    from lemonfiber.jobs import JobStanding
    from lemonfiber.reads import Read
    from lemonfiber.stream import Arrival, Live, Stale


type TlsSetting = aiohttp.Fingerprint | ssl.SSLContext | bool

NOT_PROXIED: Final = "The session given would send through a proxy, and a credential goes to the stack alone, so nothing was sent."
"""Why a request a caller's session would send through a proxy is refused."""


async def unproxied(
    request: aiohttp.ClientRequest,
    handler: aiohttp.ClientHandlerType,
) -> aiohttp.ClientResponse:
    """Send a request straight to the stack, refusing one the session would send through a proxy.

    A session the caller gave may carry a proxy of its own, or read one from the
    environment; either would hand the credential to the proxy, in the clear over
    http. This runs once aiohttp has chosen the proxy and before anything is
    sent, and as the request's only middleware it also keeps the session's own
    middlewares from ever seeing the credential.
    """
    if request.proxy is not None:
        raise ConfigurationError(NOT_PROXIED)
    return await handler(request)


STRAIGHT: Final = (unproxied,)
"""The middlewares every request is sent through: this one, in place of any the session holds."""


def tls_for(address: Address) -> TlsSetting:
    """Return what every request to an address is checked with: its pin, a verifying context, or nothing."""
    if address.pin is not None:
        return aiohttp.Fingerprint(address.pin.digest)
    if address.scheme == "https":
        return ssl.create_default_context()
    return True


def checked(session: aiohttp.ClientSession) -> aiohttp.ClientSession:
    """Return a caller's session, refusing one whose connector would not check a pin."""
    if not isinstance(session.connector, aiohttp.TCPConnector):
        msg = "A session given to the client connects over TCP, so the certificate pin can be checked."
        raise ConfigurationError(msg)
    return session


async def attempt(
    session: aiohttp.ClientSession,
    route: Route,
    tls: TlsSetting,
    call: Call,
    limit: aiohttp.ClientTimeout,
) -> Answer | None:
    """Send one call over one route, or return nothing where no connection could be made there.

    A route that reaches a named stack by an address it resolved to names the
    stack in the TLS handshake, and the certificate is checked against that name.
    A failure is raised once aiohttp's error is let go, since that error holds
    the request's headers, credential included, and would ride along as the
    failure's cause.
    """
    try:
        async with session.request(
            call.method,
            route.url(call.path),
            data=call.body,
            headers={**call.headers, **route.headers()},
            ssl=tls,
            server_hostname=route.named,
            middlewares=STRAIGHT,
            allow_redirects=False,
            raise_for_status=False,
            timeout=limit,
        ) as response:
            body = (
                await response.read()
                if call.most is None
                else await capped(response.headers, response.content, call.most)
            )
    except aiohttp.ServerFingerprintMismatch, aiohttp.ClientSSLError:
        failure: LemonfiberError = CertificateRefusedError(CERTIFICATE_REFUSED)
    except aiohttp.ClientConnectorError:
        return None
    except aiohttp.ClientError, TimeoutError:
        failure = UnreachableError(NOT_ANSWERING)
    else:
        return received(response.status, response.headers, body)
    raise failure


async def capped(headers: Mapping[str, str], content: aiohttp.StreamReader, most: int) -> bytes:
    """Return at most one byte past `most` of an answer's body, and none of one whose headers declare more.

    What is left unread is aiohttp's to deal with: a connection whose answer was not
    read to its end is closed when the answer is let go, not kept for the next request.
    """
    if declared_over(headers, most):
        return b""
    kept = bytearray()
    while len(kept) <= most and (chunk := await content.read(most + 1 - len(kept))):
        kept += chunk
    return bytes(kept)


async def exchange(
    session: aiohttp.ClientSession,
    address: Address,
    tls: TlsSetting,
    call: Call,
    limit: aiohttp.ClientTimeout,
) -> Answer:
    """Send one call over the first route a connection can be made on, following no redirect.

    A route is passed over only where no connection could be made, so nothing
    was sent; once a connection is made, its outcome is the call's.
    """
    for route in address.routes:
        answer = await attempt(session, route, tls, call, limit)
        if answer is not None:
            return answer
    raise UnreachableError(NOT_ANSWERING)


async def asked(
    session: aiohttp.ClientSession,
    address: Address,
    tls: TlsSetting,
    call: Call,
    attempts: Attempts,
) -> Answer:
    """Send a call, and send a read again after a passing failure, as `attempts` allows.

    The last attempt's outcome is the call's: its answer, or the failure that
    nothing answered.
    """
    loop = asyncio.get_running_loop()
    while True:
        outcome: Answer | UnreachableError
        limit = aiohttp.ClientTimeout(total=attempts.left(loop.time()))
        try:
            outcome = await exchange(session, address, tls, call, limit)
        except UnreachableError as unanswered:
            outcome = unanswered
        pause = attempts.pause(outcome if isinstance(outcome, Answer) else None, loop.time())
        if pause is None:
            break
        await asyncio.sleep(pause)
    if isinstance(outcome, UnreachableError):
        raise outcome
    return outcome


class AsyncClient:
    """Talks to one stack, asynchronously, with one credential.

    Give it the `aiohttp.ClientSession` the application already holds, as Home
    Assistant gives an integration its own; a client given none opens one and
    closes it in `aclose`. A session it was given is never closed by it.
    """

    def __init__(
        self,
        address: Address,
        credential: Credential,
        *,
        session: aiohttp.ClientSession | None = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Hold an address, a credential and the session to send through; nothing is sent until a call is made."""
        self._address = address
        self._credential = credential
        self._given = None if session is None else checked(session)
        self._owned: aiohttp.ClientSession | None = None
        self._tls = tls_for(address)
        self._timeout = timeout

    @property
    def address(self) -> Address:
        """Return where this client sends, and the pin it holds that address to."""
        return self._address

    def _session(self) -> aiohttp.ClientSession:
        if self._given is not None:
            return self._given
        if self._owned is None:
            self._owned = aiohttp.ClientSession()
        return self._owned

    async def _run[T](self, operated: operation.Operation[T]) -> T:
        call = with_credential(operated.call, self._credential)
        attempts = Attempts(operated.again, self._timeout, asyncio.get_running_loop().time())
        return operated.read(await asked(self._session(), self._address, self._tls, call, attempts))

    async def read(self, read: Read, query: Query | None = None) -> Envelope:
        """Ask for what a command prints under `--json`."""
        return await self._run(operation.reading(read, query))

    async def capabilities(self) -> CapabilitySet:
        """Ask what the stack can do, for the credential this client holds, as it stands now."""
        return await self._run(operation.capabilities())

    async def logs(
        self,
        *,
        services: Sequence[str] = (),
        forms: Sequence[str] = (),
        tail: int | None = None,
    ) -> list[LogEnvelope]:
        """Ask for what the services have been saying, a `log` envelope a line.

        `services` and `forms` narrow to those named; `tail` is how many of the
        latest lines to answer with. Each left out is left to lemonfiber, as the
        command leaves a flag it was not given.
        """
        return await self._run(operation.logs(services, forms, tail))

    async def bundle(self, name: str) -> BundleFile:
        """Fetch one support bundle this run wrote, by name, as the bytes it is."""
        return await self._run(operation.bundle(name))

    async def poster(self, title: str, query: Query | None = None) -> Picture:
        """Fetch a title's poster, by the id its shelf lists it under, as the raster image it is.

        `query` takes `member` and `defaults`, as the title read does. A title outside
        the member's limits is `PLAY-2`, and one with no poster is `PLAY-9`.
        """
        return await self._run(operation.picture(HELD_ID_POSTER, title, query))

    async def backdrop(self, title: str, query: Query | None = None) -> Picture:
        """Fetch a title's backdrop, as `poster` fetches its poster."""
        return await self._run(operation.picture(HELD_ID_BACKDROP, title, query))

    async def act(self, action: str, arguments: Mapping[str, Json] | None = None) -> Envelope:
        """Tell lemonfiber to do something the command line could also do. Sent once, never retried."""
        return await self._run(operation.action(action, arguments))

    async def job(self, job: str) -> JobStanding:
        """Ask where the work a name stands for got to."""
        return await self._run(operation.job(job))

    async def release(self, job: str) -> JobStanding:
        """Let a name go, ending the work it stands for, and say where it now stands."""
        return await self._run(operation.release(job))

    async def follow(
        self,
        job: str | JobEnvelope,
        *,
        every: float = DEFAULT_EVERY,
        within: float | None = None,
    ) -> Finished | Ended:
        """Ask where work stands every `every` seconds until it is no longer going.

        Raises `StillRunningError` once `within` seconds have passed with it still going.
        """
        name = job_name(job)
        loop = asyncio.get_running_loop()
        started = loop.time()
        standing = await self.job(name)
        while isinstance(standing, Running):
            await asyncio.sleep(next_wait(name, started, loop.time(), every, within))
            standing = await self.job(name)
        return standing

    def events(
        self,
        *,
        silence: float = SILENCE_ALLOWED,
        reconnects: int = RECONNECTS_ALLOWED,
        first_wait: float = FIRST_WAIT,
    ) -> AsyncStream:
        """Follow the live stream: what arrives, what has gone stale across a gap, and each gap itself.

        Silence longer than `silence` seconds is a broken stream. A broken stream
        is reopened from the last event it carried, waiting `first_wait` seconds
        and twice as long after each failure, and `StreamLostError` is raised once
        `reconnects` attempts in a row have failed.
        """
        following = Following(self._credential, silence=silence, reconnects=reconnects, first_wait=first_wait)
        connect = aiohttp.ClientTimeout(sock_connect=self._timeout)
        return AsyncStream(self._session, self._address, self._tls, following, connect)

    async def aclose(self) -> None:
        """Close the session this client opened, if it opened one."""
        if self._owned is not None:
            await self._owned.close()
            self._owned = None

    async def __aenter__(self) -> Self:
        """Return the client, to be closed when the block ends."""
        return self

    async def __aexit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Close the client."""
        await self.aclose()


class AsyncStream:
    """The live stream, followed asynchronously. `async for` it for each `Arrival`; `aclose` it to let go."""

    def __init__(
        self,
        session: Callable[[], aiohttp.ClientSession],
        address: Address,
        tls: TlsSetting,
        following: Following,
        connect: aiohttp.ClientTimeout,
    ) -> None:
        """Hold what opening and reading the stream needs; nothing is sent until it is iterated."""
        self._session = session
        self._address = address
        self._tls = tls
        self._following = following
        self._connect = connect
        self._arrivals = self._follow()

    def __aiter__(self) -> AsyncIterator[Arrival]:
        """Return the stream itself."""
        return self

    async def __anext__(self) -> Arrival:
        """Return the next arrival, waiting for it."""
        return await anext(self._arrivals)

    def held(self) -> dict[str, Live | Stale]:
        """Return the last value of each kind the stream carried, and whether it is still current."""
        return self._following.held()

    async def _follow(self) -> AsyncGenerator[Arrival]:
        while True:
            async for arrival in self._opening():
                yield arrival
            await asyncio.sleep(self._following.retry())

    async def _opening(self) -> AsyncGenerator[Arrival]:
        call = self._following.call()
        for route in self._address.routes:
            opened = await self._open(route, call)
            if opened is not None:
                break
        else:
            return
        async with opened as response:
            self._following.opened()
            why = Break.ENDED
            while chunk := await self._chunk(response):
                if isinstance(chunk, Break):
                    why = chunk
                    break
                for arrival in self._following.heard(chunk):
                    yield arrival
        for arrival in self._following.broke(why):
            yield arrival

    async def _open(self, route: Route, call: Call) -> aiohttp.ClientResponse | None:
        """Open the stream over one route: the response once it is open, or nothing where it did not open.

        A refusal the stack answered with, or a certificate it does not hold to,
        is raised; anything else leaves the next route, or the next attempt, to try.
        """
        try:
            response = await self._session().request(
                call.method,
                route.url(call.path),
                headers={**call.headers, **route.headers()},
                ssl=self._tls,
                server_hostname=route.named,
                middlewares=STRAIGHT,
                allow_redirects=False,
                raise_for_status=False,
                timeout=self._connect,
            )
            if response.status == OPENED:
                return response
            answer = received(response.status, response.headers, await response.read())
        except aiohttp.ServerFingerprintMismatch, aiohttp.ClientSSLError:
            failure = CertificateRefusedError(CERTIFICATE_REFUSED)
        except aiohttp.ClientError, TimeoutError:
            return None
        else:
            refusal = opening_refusal(answer)
            if refusal is not None:
                raise refusal
            return None
        raise failure

    async def _chunk(self, response: aiohttp.ClientResponse) -> bytes | Break:
        try:
            async with asyncio.timeout(self._following.silence):
                return await response.content.readany()
        except TimeoutError:
            return Break.SILENT
        except aiohttp.ClientError, OSError:
            return Break.DROPPED

    async def aclose(self) -> None:
        """Stop following and let the connection go."""
        await self._arrivals.aclose()

    async def __aenter__(self) -> Self:
        """Return the stream, to be closed when the block ends."""
        return self

    async def __aexit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Close the stream."""
        await self.aclose()


async def admit_async(
    address: Address,
    password: str,
    *,
    name: str | None = None,
    session: aiohttp.ClientSession | None = None,
) -> Session:
    """Offer a password, once, and come away with a session or with why there is none.

    A household member gives their `name`; the operator gives none. The session's
    credential is what an `AsyncClient` is then built with. The offer waits as
    long as a client's call does by default; `asyncio.timeout` around it waits less.
    """
    offered = operation.admission(password, name)
    tls = tls_for(address)
    limit = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    if session is not None:
        return offered.read(await exchange(checked(session), address, tls, offered.call, limit))
    async with aiohttp.ClientSession() as opened:
        return offered.read(await exchange(opened, address, tls, offered.call, limit))
