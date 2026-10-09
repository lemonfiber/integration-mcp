# Copyright (c) 2026 NightWorksIO
"""The `text/event-stream` wire format, read a chunk at a time."""

import codecs
import re
from dataclasses import dataclass, field
from typing import Final

from lemonfiber.problems import UnreadableResponseError

LARGEST: Final = 16 * 1024 * 1024
"""The most characters one event's data, or one line of it, may hold."""

ENCODING: Final = "utf-8"
"""What the stream is written in; a sequence it cannot decode is read as the replacement character."""

LINE_END: Final = re.compile(r"\r\n|\r|\n")
"""What ends a line: a carriage return and a line feed, either alone, or the two together."""

RETURN: Final = "\r"
"""A carriage return, which ends a line alone unless a line feed follows it."""


@dataclass(frozen=True, slots=True)
class Event:
    """One event as the stream carried it: its id, its name and its data."""

    id: str | None
    name: str
    data: str


@dataclass(slots=True)
class _Pending:
    id: str | None = None
    name: str = "message"
    data: list[str] = field(default_factory=list[str])
    size: int = 0
    """The characters the data holds once joined, and one more."""


class Parser:
    """Gathers chunks and hands back each event as it completes.

    A chunk may end inside a line and a line inside a UTF-8 sequence, so bytes
    are held until they decode, text until a line ends, and an event until a
    blank line ends it. A line opening with a colon names no field, which is
    how the heartbeat is written, and carries nothing. An unfinished line is
    held as the pieces it arrived in and joined once a line ends, so a long
    line is not copied again with every chunk, and a carriage return at the end
    of what arrived is held until what follows says whether a line feed is part
    of the same ending.

    Nothing held grows past `largest` characters: a line that has not ended,
    or the data of an event that has not completed, beyond that is refused as
    `UnreadableResponseError` rather than held, and each character is joined
    and split a bounded number of times, however the stream is cut into chunks.
    """

    def __init__(self, *, largest: int = LARGEST) -> None:
        """Start with nothing gathered, holding no line or event beyond `largest` characters."""
        self._largest = largest
        self._decoder = codecs.getincrementaldecoder(ENCODING)(errors="replace")
        self._unfinished = [""]
        self._unfinished_size = 0
        self._pending = _Pending()

    def push(self, chunk: bytes) -> list[Event]:
        """Return the events this chunk completes, in order."""
        decoded = self._decoder.decode(chunk)
        if self._unfinished[-1].endswith(RETURN) or LINE_END.search(decoded):
            done = self._lines("".join([*self._unfinished, decoded]))
        else:
            self._unfinished.append(decoded)
            self._unfinished_size += len(decoded)
            done = []
        if self._unfinished_size > self._largest:
            what = f"the stream carried a line longer than the {self._largest} characters an event may be"
            raise UnreadableResponseError(what)
        return done

    def _lines(self, text: str) -> list[Event]:
        """Read every line a text completes, keeping the line it has not finished."""
        held = RETURN if text.endswith(RETURN) else ""
        *complete, rest = LINE_END.split(text.removesuffix(held))
        done = [event for line in complete if (event := self._line(line)) is not None]
        self._unfinished = [rest + held]
        self._unfinished_size = len(rest) + len(held)
        return done

    def _line(self, line: str) -> Event | None:
        if not line:
            return self._complete()
        name, _, value = line.partition(":")
        value = value.removeprefix(" ")
        if name == "id":
            self._pending.id = value
        elif name == "event":
            self._pending.name = value
        elif name == "data":
            self._pending.data.append(value)
            self._pending.size += len(value) + 1
            if self._pending.size > self._largest + 1:
                what = (
                    f"the stream carried an event larger than the {self._largest} characters an event may be"
                )
                raise UnreadableResponseError(what)
        return None

    def _complete(self) -> Event | None:
        pending, self._pending = self._pending, _Pending()
        if not pending.data:
            return None
        return Event(pending.id, pending.name, "\n".join(pending.data))
