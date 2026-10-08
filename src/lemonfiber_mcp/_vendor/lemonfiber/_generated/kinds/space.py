# Copyright (c) 2026 NightWorksIO
"""The `space` envelope, and the shapes only `space` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.space__stop_seeding import Candidate


class Consumption(typing.TypedDict):
    """One line of the accounting."""

    category: SpaceCategory
    """What it is about."""
    reclaim: Reclaim
    """What getting it back would cost."""
    tally: Tally
    """What it occupies, counted both ways."""


type Freshness = FreshnessLive | FreshnessAsOf
"""How much a reading can be relied on."""


class Interrupted(typing.TypedDict):
    """An import that stopped part-way, in the words of whatever stopped it."""

    name: str
    """What the service calls it."""
    partial: int
    """What is on disk for it already, where the walk could find it."""
    said: str
    """What the service said, verbatim."""


type Level = typing.Literal["unknown", "ample", "advisory", "warning", "critical", "exhausted"]
"""Where a volume stands."""


class Outsized(typing.TypedDict):
    """One file far larger than the rest."""

    bytes: int
    """What it occupies."""
    path: str
    """Where it is."""
    times_typical: int
    """How many times the middle file of this walk it is."""


class Reckoning(typing.TypedDict):
    """Where the disk stands, what is on it, and what could be got back."""

    agreement: str
    """What this offer names itself, so an answer to it can say which offer it was
    answering. The answer is this name, and nothing else is a yes to a cleanup.
    """
    candidates: list[Candidate]
    """The completed downloads, each with where it stands and what removing it
    would cost.
    """
    consumption: list[Consumption]
    """Where the room went, one line per tree plus the services' own files, and
    one line for what is committed but has not landed yet.
    """
    halted: bool
    """Whether new acquisitions are halted to keep the services writable."""
    interrupted: list[Interrupted]
    """The imports that stopped part-way, with what is on disk for each."""
    level: Level
    """Where the stack stands, which is where its worst volume stands."""
    outsized: list[Outsized]
    """The files far enough out of line with the rest to be worth pointing at."""
    reclaimable: list[Consumption]
    """What of that room could be got back, and what each would cost.

    A second reading of bytes already counted above rather than more of them: a
    seeding torrent's file is in the tree it lives in *and* here. Summing the
    two lists together would double what is on the disk, which is the mistake
    this whole module is arranged to avoid.
    """
    reclaimed: typing.NotRequired[Reclaimed | None]
    """What became of an answered cleanup, where the offer was answered."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    volumes: list[Volume]
    """The volumes watched. Either filling stops the stack, so both are reported
    whether or not they are the same drive.
    """


type Reclaim = typing.Literal[
    "by_losing_content",
    "in_progress",
    "at_the_cost_of_ratio",
    "the_easy_win",
    "already_have_it",
    "marginally",
    "you_said_not",
]
"""What getting a line's room back costs."""


class Reclaimed(typing.TypedDict):
    """What became of an answered cleanup."""

    bytes: int
    """What they occupied."""
    gone: list[str]
    """The paths that were taken, or would have been in a rehearsal."""
    left: list[SpaceLeft]
    """What could not be taken, and what the platform said about it."""
    rehearsed: bool
    """Whether this was a rehearsal. Rehearsed, `gone` and `bytes` are what would have
    been taken and nothing was: no room was freed.
    """


type Role = typing.Literal["data", "services"]
"""Which of the two volumes a reading is about."""


type SpaceCategory = (
    SpaceCategoryTree
    | SpaceCategoryLanding
    | SpaceCategorySeeding
    | SpaceCategoryOrphaned
    | SpaceCategoryExtracted
    | SpaceCategoryServices
    | SpaceCategoryUnmanaged
)
"""What one line of the accounting is about."""


class SpaceCategoryExtracted(typing.TypedDict):
    """Archives whose extracted contents sit beside them."""

    of: typing.Literal["extracted"]


class SpaceCategoryLanding(typing.TypedDict):
    """What the download clients still have to write."""

    of: typing.Literal["landing"]


class SpaceCategoryOrphaned(typing.TypedDict):
    """Downloads on disk that no service ever took."""

    of: typing.Literal["orphaned"]


class SpaceCategorySeeding(typing.TypedDict):
    """Completed downloads the client is still seeding."""

    of: typing.Literal["seeding"]


class SpaceCategoryServices(typing.TypedDict):
    """The services' own configuration and databases."""

    of: typing.Literal["services"]


class SpaceCategoryTree(typing.TypedDict):
    """One directory beneath the data root, named as the operator named it.

    Per directory rather than one figure for the library, because several
    libraries commonly share a volume and \"the library is large\" tells nobody
    which of them is growing.
    """

    name: str
    of: typing.Literal["tree"]


class SpaceCategoryUnmanaged(typing.TypedDict):
    """What the operator said to leave alone."""

    of: typing.Literal["unmanaged"]


class SpaceEnvelope(typing.TypedDict):
    """The envelope carrying `space`."""

    api_version: int
    data: Reckoning
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["space"]


class SpaceLeft(typing.TypedDict):
    """Something a cleanup could not take."""

    at: str
    """Where it is."""
    why: str
    """What the platform said, verbatim."""


class Tally(typing.TypedDict):
    """What a set of files occupies, counted both ways."""

    files: int
    """How many names were counted."""
    logical: int
    """The bytes the names add up to — what this would take with nothing shared."""
    physical: int
    """The bytes the underlying files add up to — what the volume has actually
    lost to them.
    """
    shared: int
    """How many of those names pointed at a file already counted."""


class Volume(typing.TypedDict):
    """One volume, as one run measured it."""

    at: str
    """The path that was measured."""
    committed: int
    """The bytes already committed to landing here."""
    free: typing.NotRequired[int | None]
    """Bytes free, or nothing where the volume could not be read."""
    level: Level
    """Where it stands."""
    limit: typing.NotRequired[int | None]
    """The effective limit — the mount's own size, which on a dataset given a
    quota is the quota rather than the device beneath it.
    """
    point: str
    """Where the volume holding it is mounted, which is what the limit belongs to."""
    projected: typing.NotRequired[int | None]
    """What would be free once the committed content has landed."""
    reading: Freshness
    """What the reading is worth."""
    role: Role
    """Which of the two this is."""


FreshnessAsOf = typing.TypedDict(
    "FreshnessAsOf",
    {
        "as": typing.Literal["as_of"],
        "at": int,
    },
)
"""Read across a network share, which answers with what it was last told —
carrying the moment it was taken, in seconds since the epoch, so a figure
nobody can refresh is at least dated.
"""


FreshnessLive = typing.TypedDict(
    "FreshnessLive",
    {
        "as": typing.Literal["live"],
    },
)
"""Read off a local disk, so it is true as of now."""


__all__ = [
    "Consumption",
    "Freshness",
    "FreshnessAsOf",
    "FreshnessLive",
    "Interrupted",
    "Level",
    "Outsized",
    "Reckoning",
    "Reclaim",
    "Reclaimed",
    "Role",
    "SpaceCategory",
    "SpaceCategoryExtracted",
    "SpaceCategoryLanding",
    "SpaceCategoryOrphaned",
    "SpaceCategorySeeding",
    "SpaceCategoryServices",
    "SpaceCategoryTree",
    "SpaceCategoryUnmanaged",
    "SpaceEnvelope",
    "SpaceLeft",
    "Tally",
    "Volume",
]
