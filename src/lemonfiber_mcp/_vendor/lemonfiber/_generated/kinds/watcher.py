# Copyright (c) 2026 NightWorksIO
"""The `watcher` envelope, and the shapes only `watcher` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Covers = CoversVariant1 | CoversVariant2 | CoversVariant3
"""What a monitor lemonfiber provisions covers, which its tag names."""


class CoversVariant1(typing.TypedDict):
    """A service of the stack, by its id."""

    service: str


class CoversVariant3(typing.TypedDict):
    """A job the stack runs on a schedule, by its id."""

    job: str


class Heartbeat(typing.TypedDict):
    """A heartbeat's interval and grace, and its last check-in."""

    every_s: int
    """The seconds between the check-ins it expects."""
    grace_s: int
    """The seconds past its interval it waits before it alarms."""
    last_check_in: typing.NotRequired[int | None]
    """When it last checked in, in seconds since the Unix epoch, where it ever has."""


type MonitorKind = typing.Literal["http", "keyword", "port", "ping", "dns", "docker", "heartbeat"]
"""How a monitor checks what it watches."""


class Unconfigured(typing.TypedDict):
    """What a monitor was asked to watch, what it watches instead, and why."""

    wanted: str
    """What it was asked to watch."""
    watches: str
    """What it watches."""
    why: str
    """Why, in the stack's words."""


type WatchPath = typing.Literal["household", "internal"]
"""Which path an entry point's monitor watches."""


type WatchState = typing.Literal["up", "down", "pending", "paused", "expected-down", "not-reporting"]
"""What a monitor sees."""


class WatchedTarget(typing.TypedDict):
    """One monitor, and what it covers where lemonfiber made it."""

    active: bool
    """Whether it is checking, rather than only defined."""
    covers: typing.NotRequired[Covers | None]
    """What it covers, by the record of what lemonfiber provisioned; absent for a monitor
    lemonfiber did not make.
    """
    heartbeat: typing.NotRequired[Heartbeat | None]
    """A heartbeat's interval, grace and last check-in."""
    kind: MonitorKind
    """How it checks."""
    last_reading: typing.NotRequired[int | None]
    """When it last took a reading, in seconds since the Unix epoch, where it ever has."""
    name: str
    """Its own name in the watcher."""
    path: typing.NotRequired[WatchPath | None]
    """Which path an entry point's monitor watches."""
    since: int
    """Since when, in seconds since the Unix epoch."""
    state: WatchState
    """What it sees."""
    unconfigured: typing.NotRequired[Unconfigured | None]
    """What it was asked to watch and what it watches instead, where it does not watch
    what it should.
    """


class WatcherEnvelope(typing.TypedDict):
    """The envelope carrying `watcher`."""

    api_version: int
    data: WatcherReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["watcher"]


class WatcherReport(typing.TypedDict):
    """Which part watches the stack from outside it, whether it answers, and what each of its
    monitors sees beside what it covers.
    """

    monitors: typing.NotRequired[list[WatchedTarget]]
    """Every monitor it holds, the operator's and lemonfiber's."""
    reachable: bool
    """Whether the watcher answers. False is coverage nobody can see, never all clear."""
    read_at: int
    """When it was asked, in seconds since the Unix epoch."""
    uncovered: typing.NotRequired[list[Covers]]
    """Every critical service and household entry point no active monitor covers."""
    unreachable_because: typing.NotRequired[str | None]
    """Why it does not answer, where it does not."""
    watcher: typing.NotRequired[str | None]
    """The plugin filling `status.watch`, where one does."""


CoversVariant2 = typing.TypedDict(
    "CoversVariant2",
    {
        "entry-point": str,
    },
)
"""A household-facing entry point, by the id of the service it is."""


__all__ = [
    "Covers",
    "CoversVariant1",
    "CoversVariant2",
    "CoversVariant3",
    "Heartbeat",
    "MonitorKind",
    "Unconfigured",
    "WatchPath",
    "WatchState",
    "WatchedTarget",
    "WatcherEnvelope",
    "WatcherReport",
]
