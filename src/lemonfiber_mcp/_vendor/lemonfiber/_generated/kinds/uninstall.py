# Copyright (c) 2026 NightWorksIO
"""The `uninstall` envelope, and the shapes only `uninstall` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Coming(typing.TypedDict):
    """One download still coming down when the removal was asked for."""

    name: str
    """What it is, as the client names it."""
    progress: int
    """How far along, from zero to a hundred."""


class Foreign(typing.TypedDict):
    """Something beneath the data location that the stack did not put there."""

    at: str
    """The directory it is in, relative to the data location — or the file itself,
    where it sits directly in the data location.
    """
    bytes: int
    """What they occupy."""
    files: int
    """How many files were found under it."""


class Item(typing.TypedDict):
    """One thing a removal reaches, said to be going or said to be kept."""

    bytes: typing.NotRequired[int | None]
    """What it occupies, where that is knowable. Absent for a container or a network,
    whose room is the image's rather than their own.
    """
    kept: typing.NotRequired[str | None]
    """Why it is being kept rather than removed, where it is being kept.

    `None` is the ordinary case: this line is going. A reason here is the whole of
    how an image shared with another project, or a path this run could not
    confirm, stays on the list without being taken.
    """
    name: str
    """What it is called — a container name, an image reference, or a full path."""
    secret: bool
    """Whether it holds a credential, so a report can say what destroying it destroys."""
    sort: Sort
    """Which of the four sorts of thing it is."""
    what: str
    """What it is, in the operator's words."""


class Outside(typing.TypedDict):
    """Something an uninstall leaves behind, and how to remove it by hand."""

    by_hand: str
    """How to remove it on this platform, as the operator would type or do it."""
    found: bool
    """Whether this machine was found to have it.

    A survey that could not look says nothing was found rather than that nothing
    is there, which is why the entry is listed either way and this field carries
    the difference.
    """
    what: str
    """What it is."""
    why: str
    """Why it is not lemonfiber's to take away."""


type Sort = typing.Literal["container", "network", "image", "path"]
"""What sort of thing one line of a manifest is."""


type Tier = typing.Literal["stop", "services", "configuration", "media"]
"""Which of the four removals was asked for."""


class Uninstall(typing.TypedDict):
    """A removal, before or after it happened."""

    manifest: UninstallManifest
    """What removing would come to, or what it came to."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    removal: UninstallRemoval
    """Whether anything was removed on this run."""


class UninstallConfidence(typing.TypedDict):
    """How much of a manifest was read and how much stood in for what could not be."""

    complete: bool
    """Whether every source this tier needed answered."""
    unread: list[str]
    """What could not be read, each in the words of whatever refused.

    The point of the field: a manifest that is short says so and says why, rather
    than reading as a machine with less on it than it has.
    """


class UninstallEnvelope(typing.TypedDict):
    """The envelope carrying `uninstall`."""

    api_version: int
    data: Uninstall
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["uninstall"]


class UninstallLeft(typing.TypedDict):
    """Something a removal could not take."""

    by_hand: str
    """How to finish it by hand."""
    name: str
    """What is still there."""
    why: str
    """What the machine said about it, verbatim."""


class UninstallManifest(typing.TypedDict):
    """What removing would come to, shown before anything is removed."""

    agreement: str
    """What this reading names itself, so an answer says which reading it answered."""
    backup: typing.NotRequired[str | None]
    """Whether a backup was offered before configuration is destroyed, and how."""
    bytes: int
    """What the lines that are going occupy, where that is knowable."""
    coming: list[Coming]
    """What is still coming down, which stopping would interrupt."""
    confidence: UninstallConfidence
    """How much of this was read, and what could not be."""
    foreign: list[Foreign]
    """What is beneath the data location that the stack did not put there.

    Not a warning. While this is non-empty the data location is never removed as
    one tree, and only the stack's own directories beneath it are offered.
    """
    items: list[Item]
    """Every line it reaches, each said to be going or said to be kept."""
    keeps: str
    """What it leaves alone, in the operator's words."""
    outside: list[Outside]
    """What lemonfiber cannot remove, each with how to remove it by hand."""
    removes: str
    """What it takes, in the operator's words."""
    tier: Tier
    """Which removal this is."""
    volume: typing.NotRequired[str | None]
    """Whether the data location is on a network share or a drive that unplugs.

    Said where it is, so removing across a mount an operator forgot was a mount is
    something they read before agreeing rather than after.
    """


type UninstallRemoval = (
    UninstallRemovalSurveyed | UninstallRemovalConfirmed | UninstallRemovalComplete | UninstallRemovalPartial
)
"""Whether anything was removed on this run, and what became of it.

Four states rather than the five a removal passes through. `removing` is the
interval between the last two and is said through the narrator as it happens — a
value returned at the end cannot be the state a run is in while it runs, and a
variant nothing could ever answer with would be a state that is documentation
pretending to be a value.
"""


class UninstallRemovalComplete(typing.TypedDict):
    """Everything the manifest named as going is gone."""

    credentials: list[str]
    """The credentials this destroyed, said rather than left to be inferred."""
    gone: list[str]
    """What went, by the name the manifest gave it."""
    state: typing.Literal["complete"]


class UninstallRemovalConfirmed(typing.TypedDict):
    """The tier and the manifest were agreed to, and this run changes nothing — the
    state a rehearsal ends in.
    """

    state: typing.Literal["confirmed"]


class UninstallRemovalPartial(typing.TypedDict):
    """Some of it could not be removed, and each of those is named with how to
    finish it by hand.
    """

    credentials: list[str]
    """The credentials this destroyed."""
    gone: list[str]
    """What went, by the name the manifest gave it."""
    left: list[UninstallLeft]
    """What is still there, and how to remove it."""
    state: typing.Literal["partial"]


class UninstallRemovalSurveyed(typing.TypedDict):
    """Everything is enumerated with its size, and nothing has been removed."""

    state: typing.Literal["surveyed"]


__all__ = [
    "Coming",
    "Foreign",
    "Item",
    "Outside",
    "Sort",
    "Tier",
    "Uninstall",
    "UninstallConfidence",
    "UninstallEnvelope",
    "UninstallLeft",
    "UninstallManifest",
    "UninstallRemoval",
    "UninstallRemovalComplete",
    "UninstallRemovalConfirmed",
    "UninstallRemovalPartial",
    "UninstallRemovalSurveyed",
]
