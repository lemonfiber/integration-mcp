# Copyright (c) 2026 NightWorksIO
"""The synchronous client, on urllib3.

A pinned address is reached through a connection pool holding the pin as
`assert_fingerprint`: urllib3 compares the certificate's SHA-256 digest with it
once the handshake completes and before a byte of the request is written, and
refuses the connection where they differ. The pool is built here from the
address alone, so no argument reaches the transport's options.
"""

import time
from typing import TYPE_CHECKING, Final, Self

import urllib3
import urllib3.exceptions

from lemonfiber._protocol import operation
from lemonfiber._protocol.calls import DEFAULT_TIMEOUT, Answer, Call, received, with_credential
from lemonfiber._protocol.following import DEFAULT_EVERY, job_name, next_wait
from lemonfiber._protocol.refusals import CERTIFICATE_REFUSED, NOT_ANSWERING, opening_refusal
from lemonfiber._protocol.retry import Attempts
from lemonfiber.jobs import Ended, Finished, Running
from lemonfiber.problems import CertificateRefusedError, LemonfiberError, UnreachableError
from lemonfiber.stream import FIRST_WAIT, OPENED, RECONNECTS_ALLOWED, SILENCE_ALLOWED, Break, Following

if TYPE_CHECKING:
    from collections.abc import Generator, Iterator, Mapping, Sequence
    from types import TracebackType

    from lemonfiber._generated import Envelope, JobEnvelope, LogEnvelope
    from lemonfiber._protocol.calls import Json, Query
    from lemonfiber.address import Address, Route
    from lemonfiber.capabilities import CapabilitySet
    from lemonfiber.credential import Credential, Session
    from lemonfiber.files import BundleFile
    from lemonfiber.jobs import JobStanding
    from lemonfiber.reads import Read
    from lemonfiber.stream import Arrival, Live, Stale

CHUNK: Final = 65536
"""The most bytes one read of the stream asks for, so a chunk the server declares larger is not held whole."""


VERIFYING: Final = "CERT_REQUIRED"
"""A certificate a trust store vouches for, as an unpinned https address is held to."""

NOT_VERIFYING: Final = "CERT_NONE"
"""No trust store asked, as a pinned address is held to its pin alone, whatever the store would say."""


type Way = tuple[Route, urllib3.HTTPConnectionPool]
"""One route to a stack, and the pool its connections are kept in."""


def pool_for(address: Address, route: Route) -> urllib3.HTTPConnectionPool:
    """Return the pool a route is reached through, holding the address's pin where it has one.

    A route that reaches a named stack by an address it resolved to checks the
    certificate against that name, and names it in the TLS handshake. How long
    a request waits is given with each request, so the pool holds no timeout.
    """
    if address.scheme == "http":
        return urllib3.HTTPConnectionPool(route.host, address.port)
    if address.pin is None:
        return urllib3.HTTPSConnectionPool(
            route.host,
            address.port,
            cert_reqs=VERIFYING,
            assert_hostname=route.named,
            server_hostname=route.named,
        )
    return urllib3.HTTPSConnectionPool(
        route.host,
        address.port,
        cert_reqs=NOT_VERIFYING,
        assert_fingerprint=address.pin.hex,
    )


def ways_to(address: Address) -> list[Way]:
    """Return every route to a stack, each with its pool, in the order they are tried."""
    return [(route, pool_for(address, route)) for route in address.routes]


def attempt(way: Way, prefix: str, call: Call, limit: float) -> Answer | None:
    """Send one call over one route, waiting at most `limit` seconds, or return nothing where no connection could be made there.

    A failure is raised once urllib3's error is let go, so nothing of the
    request, its credential included, rides along as the failure's cause.
    """
    route, pool = way
    try:
        response = pool.urlopen(
            call.method,
            prefix + call.path,
            body=call.body,
            headers={**call.headers, **route.headers()},
            retries=False,
            timeout=urllib3.Timeout(total=limit),
        )
    except urllib3.exceptions.SSLError:
        failure: LemonfiberError = CertificateRefusedError(CERTIFICATE_REFUSED)
    except urllib3.exceptions.NewConnectionError:
        return None
    except urllib3.exceptions.HTTPError:
        failure = UnreachableError(NOT_ANSWERING)
    else:
        return received(response.status, response.headers, response.data)
    raise failure


def exchange(ways: Sequence[Way], prefix: str, call: Call, limit: float) -> Answer:
    """Send one call over the first route a connection can be made on, following no redirect.

    A route is passed over only where no connection could be made, so nothing
    was sent; once a connection is made, its outcome is the call's.
    """
    for way in ways:
        answer = attempt(way, prefix, call, limit)
        if answer is not None:
            return answer
    raise UnreachableError(NOT_ANSWERING)


def asked(ways: Sequence[Way], prefix: str, call: Call, attempts: Attempts) -> Answer:
    """Send a call, and send a read again after a passing failure, as `attempts` allows.

    The last attempt's outcome is the call's: its answer, or the failure that
    nothing answered.
    """
    while True:
        outcome: Answer | UnreachableError
        try:
            outcome = exchange(ways, prefix, call, attempts.left(time.monotonic()))
        except UnreachableError as unanswered:
            outcome = unanswered
        pause = attempts.pause(outcome if isinstance(outcome, Answer) else None, time.monotonic())
        if pause is None:
            break
        time.sleep(pause)
    if isinstance(outcome, UnreachableError):
        raise outcome
    return outcome


def close_all(ways: Sequence[Way]) -> None:
    """Close every pool a client holds."""
    for _, pool in ways:
        pool.close()


class SyncClient:
    """Talks to one stack, synchronously, with one credential.

    Every answer is read through the envelope, so a version this package does
    not speak is refused rather than half understood; every refusal is a typed
    `LemonfiberError`.
    """

    def __init__(
        self,
        address: Address,
        credential: Credential,
        *,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Hold an address and a credential; nothing is sent until a call is made."""
        self._address = address
        self._credential = credential
        self._timeout = timeout
        self._ways = ways_to(address)

    @property
    def address(self) -> Address:
        """Return where this client sends, and the pin it holds that address to."""
        return self._address

    def _run[T](self, operated: operation.Operation[T]) -> T:
        call = with_credential(operated.call, self._credential)
        attempts = Attempts(operated.again, self._timeout, time.monotonic())
        return operated.read(asked(self._ways, self._address.prefix, call, attempts))

    def read(self, read: Read, query: Query | None = None) -> Envelope:
        """Ask for what a command prints under `--json`."""
        return self._run(operation.reading(read, query))

    def capabilities(self) -> CapabilitySet:
        """Ask what the stack can do, for the credential this client holds, as it stands now."""
        return self._run(operation.capabilities())

    def logs(
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
        return self._run(operation.logs(services, forms, tail))

    def bundle(self, name: str) -> BundleFile:
        """Fetch one support bundle this run wrote, by name, as the bytes it is."""
        return self._run(operation.bundle(name))

    def act(self, action: str, arguments: Mapping[str, Json] | None = None) -> Envelope:
        """Tell lemonfiber to do something the command line could also do. Sent once, never retried."""
        return self._run(operation.action(action, arguments))

    def job(self, job: str) -> JobStanding:
        """Ask where the work a name stands for got to."""
        return self._run(operation.job(job))

    def release(self, job: str) -> JobStanding:
        """Let a name go, ending the work it stands for, and say where it now stands."""
        return self._run(operation.release(job))

    def follow(
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
        started = time.monotonic()
        standing = self.job(name)
        while isinstance(standing, Running):
            time.sleep(next_wait(name, started, time.monotonic(), every, within))
            standing = self.job(name)
        return standing

    def events(
        self,
        *,
        silence: float = SILENCE_ALLOWED,
        reconnects: int = RECONNECTS_ALLOWED,
        first_wait: float = FIRST_WAIT,
    ) -> SyncStream:
        """Follow the live stream: what arrives, what has gone stale across a gap, and each gap itself.

        Silence longer than `silence` seconds is a broken stream. A broken stream
        is reopened from the last event it carried, waiting `first_wait` seconds
        and twice as long after each failure, and `StreamLostError` is raised once
        `reconnects` attempts in a row have failed.
        """
        following = Following(self._credential, silence=silence, reconnects=reconnects, first_wait=first_wait)
        return SyncStream(self._ways, self._address.prefix, following, self._timeout)

    def close(self) -> None:
        """Close every connection this client holds."""
        close_all(self._ways)

    def __enter__(self) -> Self:
        """Return the client, to be closed when the block ends."""
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Close the client."""
        self.close()


class SyncStream:
    """The live stream, followed synchronously. Iterate it for each `Arrival`; close it to let go."""

    def __init__(
        self,
        ways: Sequence[Way],
        prefix: str,
        following: Following,
        connect: float = DEFAULT_TIMEOUT,
    ) -> None:
        """Hold what opening and reading the stream needs; nothing is sent until it is iterated."""
        self._ways = ways
        self._prefix = prefix
        self._following = following
        self._connect = connect
        self._arrivals = self._follow()

    def __iter__(self) -> Iterator[Arrival]:
        """Return the stream itself."""
        return self

    def __next__(self) -> Arrival:
        """Return the next arrival, waiting for it."""
        return next(self._arrivals)

    def held(self) -> dict[str, Live | Stale]:
        """Return the last value of each kind the stream carried, and whether it is still current."""
        return self._following.held()

    def _follow(self) -> Generator[Arrival]:
        while True:
            response = self._open()
            if response is not None:
                self._following.opened()
                try:
                    why = yield from self._read(response)
                except BaseException:
                    response.close()
                    raise
                response.drain_conn()
                response.release_conn()
                yield from self._following.broke(why)
            time.sleep(self._following.retry())

    def _open(self) -> urllib3.BaseHTTPResponse | None:
        call = self._following.call()
        for way in self._ways:
            response = self._attempt(way, call)
            if response is not None:
                return self._judged(response)
        return None

    def _attempt(self, way: Way, call: Call) -> urllib3.BaseHTTPResponse | None:
        """Ask for the stream over one route: the response, or nothing where none came back.

        A certificate the stack does not hold to is raised; anything else leaves
        the next route, or the next attempt, to try.
        """
        route, pool = way
        try:
            response = pool.urlopen(
                call.method,
                self._prefix + call.path,
                headers={**call.headers, **route.headers()},
                retries=False,
                preload_content=False,
                timeout=urllib3.Timeout(connect=self._connect, read=self._following.silence),
            )
        except urllib3.exceptions.SSLError:
            failure = CertificateRefusedError(CERTIFICATE_REFUSED)
        except urllib3.exceptions.HTTPError:
            return None
        else:
            return response
        raise failure

    @staticmethod
    def _judged(response: urllib3.BaseHTTPResponse) -> urllib3.BaseHTTPResponse | None:
        """Return a response that opened the stream, raising the refusal where the stack answered with one."""
        if response.status == OPENED:
            return response
        answer = received(response.status, response.headers, response.read())
        response.release_conn()
        refusal = opening_refusal(answer)
        if refusal is not None:
            raise refusal
        return None

    def _read(self, response: urllib3.BaseHTTPResponse) -> Generator[Arrival, None, Break]:
        while True:
            try:
                chunk = response.read1(CHUNK)
            except urllib3.exceptions.ReadTimeoutError:
                return Break.SILENT
            except urllib3.exceptions.HTTPError, OSError:
                return Break.DROPPED
            if not chunk:
                return Break.ENDED
            yield from self._following.heard(chunk)

    def close(self) -> None:
        """Stop following and let the connection go."""
        self._arrivals.close()

    def __enter__(self) -> Self:
        """Return the stream, to be closed when the block ends."""
        return self

    def __exit__(
        self,
        kind: type[BaseException] | None,
        error: BaseException | None,
        trace: TracebackType | None,
    ) -> None:
        """Close the stream."""
        self.close()


def admit(
    address: Address,
    password: str,
    *,
    name: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> Session:
    """Offer a password, once, and come away with a session or with why there is none.

    A household member gives their `name`; the operator gives none. The session's
    credential is what a `SyncClient` is then built with.
    """
    offered = operation.admission(password, name)
    ways = ways_to(address)
    try:
        return offered.read(exchange(ways, address.prefix, offered.call, timeout))
    finally:
        close_all(ways)
