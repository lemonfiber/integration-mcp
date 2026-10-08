# Copyright (c) 2026 NightWorksIO
"""The live stream, and the three things about it that are easy to get wrong.

A silent stream and a dead one look alike, so the server speaks at least every
`HEARTBEAT` seconds and twice that in silence is a broken stream. A broken
stream is resumed from the last event id it carried. And every value held from
before a gap is stale until the stream carries it again, whatever the
resumption replays.
"""

import time
from dataclasses import dataclass
from enum import StrEnum
from http import HTTPMethod, HTTPStatus
from typing import TYPE_CHECKING, Final

from lemonfiber._protocol.calls import Call
from lemonfiber._sse import Parser
from lemonfiber.envelope import parse_envelope
from lemonfiber.problems import StreamLostError, UnknownKindError
from lemonfiber.reads import EVENTS

if TYPE_CHECKING:
    from collections.abc import Callable

    from lemonfiber._generated import Envelope
    from lemonfiber.credential import Credential

HEARTBEAT: Final = 15.0
"""How often, in seconds, the server speaks when it has nothing to say."""

SILENCE_ALLOWED: Final = HEARTBEAT * 2
"""Seconds of silence after which the stream is broken rather than quiet: one missed beat is tolerated."""

RECONNECTS_ALLOWED: Final = 5
"""How many openings in a row may fail before following gives up."""

FIRST_WAIT: Final = 1.0
"""Seconds before the first attempt to reopen a broken stream; each failed attempt doubles it."""

LONGEST_WAIT: Final = 30.0
"""The most seconds an attempt to reopen waits."""

OPENED: Final = HTTPStatus.OK
"""The status the stream opens with."""

EVENT_STREAM: Final = "text/event-stream"
RESUME_HEADER: Final = "Last-Event-ID"


class Break(StrEnum):
    """How a stream stopped carrying anything."""

    SILENT = "silent"
    """Nothing arrived, not even a heartbeat, for longer than the silence allowed."""
    ENDED = "ended"
    """The server closed the stream."""
    DROPPED = "dropped"
    """The connection failed."""


@dataclass(frozen=True, slots=True)
class Live:
    """A value the stream carried just now."""

    envelope: Envelope


@dataclass(frozen=True, slots=True)
class Stale:
    """A value held from before a gap: the last thing the stream said, not what is true now."""

    envelope: Envelope
    quiet_for: float
    """Seconds since the stream carried it."""


@dataclass(frozen=True, slots=True)
class Gap:
    """The stream broke; every value held is stale until it is carried again."""

    why: Break
    quiet_for: float
    """Seconds since anything at all arrived."""


@dataclass(frozen=True, slots=True)
class Unrecognised:
    """The stream carried a kind this package was not generated with; its payload is not exposed untyped."""

    kind: str


type Arrival = Live | Stale | Gap | Unrecognised
"""What following the stream hands over, in the order it happened."""


@dataclass(frozen=True, slots=True)
class _Held:
    envelope: Envelope
    at: float


class Following:
    """What a follower knows between openings: what is held, how current it is, and where to resume from."""

    def __init__(
        self,
        credential: Credential,
        *,
        silence: float = SILENCE_ALLOWED,
        reconnects: int = RECONNECTS_ALLOWED,
        first_wait: float = FIRST_WAIT,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Start holding nothing, with nothing to resume from."""
        self._credential = credential
        self.silence = silence
        self._reconnects = reconnects
        self._first_wait = first_wait
        self._clock = clock
        self._held: dict[str, _Held] = {}
        self._live: set[str] = set()
        self._parser = Parser()
        self._last_id: str | None = None
        self._last_heard = clock()
        self._failures = 0

    def call(self) -> Call:
        """Return the request that opens the stream, resuming from the last event id where there is one."""
        headers = {"Accept": EVENT_STREAM, **self._credential.header()}
        if self._last_id is not None:
            headers[RESUME_HEADER] = self._last_id
        return Call(HTTPMethod.GET, EVENTS, headers)

    def opened(self) -> None:
        """Begin reading a fresh opening."""
        self._parser = Parser()
        self._last_heard = self._clock()

    def heard(self, chunk: bytes) -> list[Arrival]:
        """Read a chunk: every event it completes, each recorded as live."""
        now = self._clock()
        self._last_heard = now
        self._failures = 0
        arrivals: list[Arrival] = []
        for event in self._parser.push(chunk):
            if event.id is not None:
                self._last_id = event.id
            try:
                envelope = parse_envelope(event.data)
            except UnknownKindError as unknown:
                arrivals.append(Unrecognised(unknown.kind))
                continue
            self._held[envelope["kind"]] = _Held(envelope, now)
            self._live.add(envelope["kind"])
            arrivals.append(Live(envelope))
        return arrivals

    def broke(self, why: Break) -> list[Arrival]:
        """Mark everything held as stale, and say so: the gap, then each value as it now stands."""
        now = self._clock()
        self._live.clear()
        return [
            Gap(why, now - self._last_heard),
            *(Stale(h.envelope, now - h.at) for h in self._held.values()),
        ]

    def retry(self) -> float:
        """Count one opening that broke or failed, and return how long to wait before the next.

        Raises `StreamLostError` once more openings in a row have failed than are allowed.
        """
        self._failures += 1
        if self._failures > self._reconnects:
            raise StreamLostError(self._reconnects)
        return min(self._first_wait * 2 ** (self._failures - 1), LONGEST_WAIT)

    def held(self) -> dict[str, Live | Stale]:
        """Return the last value of each kind the stream carried, and whether it is still current."""
        now = self._clock()
        return {
            kind: Live(held.envelope) if kind in self._live else Stale(held.envelope, now - held.at)
            for kind, held in self._held.items()
        }
