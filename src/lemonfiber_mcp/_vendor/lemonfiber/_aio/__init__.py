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
from typing import TYPE_CHECKING, Self

import aiohttp

from lemonfiber._aio.transport import STRAIGHT, TlsSetting, asked, checked, exchange, tls_for
from lemonfiber._protocol import operation
from lemonfiber._protocol.calls import DEFAULT_TIMEOUT, Call, received, with_credential
from lemonfiber._protocol.following import DEFAULT_EVERY, job_name, next_wait
from lemonfiber._protocol.refusals import CERTIFICATE_REFUSED, LAPSED, opening_refusal
from lemonfiber._protocol.retry import Attempts
from lemonfiber.jobs import Ended, Finished, Running
from lemonfiber.problems import (
    CertificateRefusedError,
    ClaimLapsedError,
)
from lemonfiber.reads import ASKABLE_ID_POSTER, HELD_ID_BACKDROP, HELD_ID_POSTER
from lemonfiber.stream import FIRST_WAIT, OPENED, RECONNECTS_ALLOWED, SILENCE_ALLOWED, Break, Following

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator, AsyncIterator, Callable, Mapping, Sequence
    from types import TracebackType

    from lemonfiber._generated import (
        DeviceChallengeEnvelope,
        DeviceKeyEnvelope,
        DeviceKeysEnvelope,
        Envelope,
        JobEnvelope,
        KeyClaimEnvelope,
        KeysEnvelope,
        LogEnvelope,
        MintedKey,
        MintedKeyEnvelope,
    )
    from lemonfiber._protocol.calls import Json, Query
    from lemonfiber.address import Address, Route
    from lemonfiber.capabilities import CapabilitySet
    from lemonfiber.credential import Credential, Session
    from lemonfiber.device_keys import Registering
    from lemonfiber.files import BundleFile, Picture
    from lemonfiber.jobs import JobStanding
    from lemonfiber.keys import KeyLink, Minting
    from lemonfiber.reads import Read
    from lemonfiber.stream import Arrival, Live, Stale


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

    async def askable_poster(self, title: str, query: Query | None = None) -> Picture:
        """Fetch the poster of a title a member may ask for, by the id their search lists it under.

        `query` takes `member` and `kind`. A title the member may not ask for is `WISH-3`,
        and one with no poster is `WISH-13`.
        """
        return await self._run(operation.picture(ASKABLE_ID_POSTER, title, query))

    async def act(self, action: str, arguments: Mapping[str, Json] | None = None) -> Envelope:
        """Tell lemonfiber to do something the command line could also do. Sent once, never retried."""
        return await self._run(operation.action(action, arguments))

    async def keys(self) -> KeysEnvelope:
        """Ask for the integration keys this credential may see, without their secrets."""
        return await self._run(operation.keys())

    async def mint(self, minting: Minting) -> MintedKeyEnvelope:
        """Mint one integration key, its secret in this answer and in no other. Sent once, never retried."""
        return await self._run(operation.mint(minting))

    async def mint_claim(self, minting: Minting) -> KeyClaimEnvelope:
        """Mint one integration key as a claim, answered with the key link that collects it and no secret."""
        return await self._run(operation.mint_claim(minting))

    async def revoke(self, name: str) -> KeysEnvelope:
        """Revoke one integration key by its name, answered with the keys as they now stand."""
        return await self._run(operation.revoke(name))

    async def register_device_key(self, registering: Registering) -> DeviceKeyEnvelope:
        """Register a phone's key pair as a device key. Sent once, never retried."""
        return await self._run(operation.register_device_key(registering))

    async def device_keys(self) -> DeviceKeysEnvelope:
        """Ask for the operator's device keys, revoked ones included."""
        return await self._run(operation.device_keys())

    async def device_key_challenge(self, name: str) -> DeviceChallengeEnvelope:
        """Ask a challenge for one device key, good for one mint within a minute. Sent once."""
        return await self._run(operation.device_key_challenge(name))

    async def revoke_device_key(self, name: str) -> DeviceKeysEnvelope:
        """Revoke one device key by its name; the keys it proved stay. Sent once, never retried."""
        return await self._run(operation.revoke_device_key(name))

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


async def collect_async(link: KeyLink, *, session: aiohttp.ClientSession | None = None) -> MintedKey:
    """Collect the key a key link's claim was minted for, once, over the TLS the link's fingerprint verifies.

    As `collect` does, on a session of the caller's where one is given.
    """
    if link.lapsed():
        raise ClaimLapsedError(LAPSED)
    collecting = operation.collection(link.claim)
    tls = tls_for(link.address)
    limit = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
    if session is not None:
        return collecting.read(await exchange(checked(session), link.address, tls, collecting.call, limit))
    async with aiohttp.ClientSession() as opened:
        return collecting.read(await exchange(opened, link.address, tls, collecting.call, limit))
