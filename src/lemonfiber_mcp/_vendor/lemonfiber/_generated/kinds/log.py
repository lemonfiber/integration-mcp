# Copyright (c) 2026 NightWorksIO
"""The `log` envelope, and the shapes only `log` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class LogEnvelope(typing.TypedDict):
    """The envelope carrying `log`."""

    api_version: int
    data: LogLine
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["log"]


type LogLevel = typing.Literal["trace", "debug", "info", "warn", "error", "fatal"]
"""How bad a line says it is.

Ordered, so a filter can ask for \"warnings and worse\" without a table of which
level outranks which. Deliberately coarse: these six are what services agree
on, and a seventh that only one of them writes would be a level nobody could filter
by across the stack.
"""


class LogLine(typing.TypedDict):
    """One line of output from one service, and how bad it says it is.

    What a machine-readable surface hands on, rather than the engine's line alone, so
    a consumer can mark the lines that say they failed, or find the first of them,
    without reading the text for itself — a second reading of severity would be a
    second answer, and the two would disagree about some service's spelling.
    """

    at: typing.NotRequired[str | None]
    """When the container itself says it wrote the line, where it said so.

    Kept verbatim and unparsed. Containers disagree with the host clock and
    with each other, and the only defensible ordering is each container's own
    account of itself — which a reader can only apply if it is carried
    rather than replaced by an arrival time.
    """
    level: typing.NotRequired[LogLevel | None]
    """How bad the line says it is, in one lowercase word.

    Absent where the line says nothing about itself. It is never guessed from
    the stream the line arrived on or from the words in it: most of this stack
    writes ordinary progress to standard error, and a line saying it could not
    find something is often a routine miss.
    """
    line: str
    """The line, without its trailing newline."""
    service: str
    """The Compose service it came from."""
    stream: Stream
    """Which stream it arrived on."""


type Stream = typing.Literal["stdout", "stderr"]
"""Which stream a log line arrived on."""


__all__ = [
    "LogEnvelope",
    "LogLevel",
    "LogLine",
    "Stream",
]
