# Copyright (c) 2026 NightWorksIO
"""The `queue` envelope, and the shapes only `queue` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Act = typing.Literal["remove", "blocklist", "search"]
"""One of the three acts a run takes on an item that struck out."""


type ActOutcome = typing.Literal["done", "would", "refused", "fell-back"]
"""What became of one act."""


class ActTaken(typing.TypedDict):
    """One act as a run took it."""

    act: Act
    """The act."""
    instead: typing.NotRequired[Act | None]
    """What was done in its place, where something weaker was."""
    outcome: ActOutcome
    """What became of it."""
    why: typing.NotRequired[str | None]
    """Why, where it was refused or fell back."""


class HealRun(typing.TypedDict):
    """One run: a pass that could act."""

    at: int
    """When, in seconds since the Unix epoch."""
    items: typing.NotRequired[list[Healed]]
    """Every item it acted on, or would have."""
    rehearsed: bool
    """Whether it was a rehearsal, which acted on nothing."""


class Healed(typing.TypedDict):
    """One item a run acted on."""

    acts: list[ActTaken]
    """Each act, in the order they were taken."""
    release: str
    """The release, by its name in the client."""
    service: str
    """The curator it was queued with, or the client holding it where none was."""
    title: typing.NotRequired[str | None]
    """The title it was for, where a curator held it."""
    why: str
    """Why it was acted on."""


type HealingSwitch = typing.Literal["on", "off"]
"""Whether healing acts."""


class QueueEnvelope(typing.TypedDict):
    """The envelope carrying `queue`."""

    api_version: int
    data: QueueHealth
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["queue"]


class QueueHealth(typing.TypedDict):
    """Whether healing acts, the strikes and grace it acts after, every unhealthy item of the
    latest pass, what could not be reached, and the newest runs.
    """

    classified_at: typing.NotRequired[int | None]
    """When the latest pass classified the queue, in seconds since the Unix epoch, where
    one ever has.
    """
    grace_s: int
    """How long a newly added download is left alone, in seconds."""
    healing: HealingSwitch
    """Whether healing acts, or only classifies."""
    incomplete: bool
    """Whether the list may be short, because something could not be read."""
    items: typing.NotRequired[list[Wedged]]
    """Every unhealthy item the latest pass found; a healthy one is left out."""
    mismatch: typing.NotRequired[str | None]
    """Where a download client files a curator's downloads outside the curator's folder,
    which nothing is acted on past.
    """
    rehearsed: bool
    """Whether this answer is a run that only said what it would do."""
    runs: typing.NotRequired[list[HealRun]]
    """The newest runs first, each a pass that could act, rehearsed or not."""
    strikes_needed: int
    """How many consecutive passes flag an item for one reason before it is acted on."""
    unreachable: typing.NotRequired[list[Unreached]]
    """Every curator or download client the latest pass could not reach or verify."""


class Unreached(typing.TypedDict):
    """A curator or download client a pass could not reach or verify."""

    service: str
    """The service, by its id."""
    why: str
    """Why, in words."""


type Wedge = typing.Literal["stalled", "slow", "failed", "stuck-on-metadata", "orphaned"]
"""Why a download is unhealthy."""


Wedged = typing.TypedDict(
    "Wedged",
    {
        "added_at": typing.NotRequired[int | None],
        "class": Wedge,
        "in_grace_until": typing.NotRequired[int | None],
        "next": typing.NotRequired[list[Act] | None],
        "release": str,
        "service": str,
        "strikes": int,
        "title": typing.NotRequired[str | None],
        "why": str,
    },
)
"""One unhealthy item, as the latest pass found it."""


__all__ = [
    "Act",
    "ActOutcome",
    "ActTaken",
    "HealRun",
    "Healed",
    "HealingSwitch",
    "QueueEnvelope",
    "QueueHealth",
    "Unreached",
    "Wedge",
    "Wedged",
]
