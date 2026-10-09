# Copyright (c) 2026 NightWorksIO
"""The `walkthrough` envelope, and the shapes only `walkthrough` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.step__walkthrough import Line, WalkthroughStep


class Handover(typing.TypedDict):
    """Where a finished walkthrough leaves the operator."""

    next: list[Next]
    """What to do next, in order."""


type Link = typing.Literal["hardlinked", "copied"]
"""What the import did with the finished download — the difference between one copy of a
file and two.
"""


type Next = typing.Literal["more-content", "household", "client-apps"]
"""One thing to do next."""


type Reason = typing.Literal[
    "no-indexers",
    "indexers-failed",
    "nothing-matched",
    "none-met-the-preset",
    "tunnel-down",
    "not-grabbed",
    "stalled",
    "import-failed",
    "no-media-server",
    "not-visible",
]
"""Why a walkthrough could not go on."""


type Shape = typing.Literal["pipeline", "library-only"]
"""Which walkthrough this stack is offered."""


class Stopped(typing.TypedDict):
    """A walkthrough that stopped: where, why, what the services were saying, and what to do."""

    logs: list[str]
    """What the services involved were saying at the time, shown inline rather than left
    for the operator to go and find — a fault report they have to research is a fault
    report they abandon.
    """
    reason: Reason
    """Why."""
    remedy: str
    """The one thing to try."""
    step: WalkthroughStep
    """The step it stopped at."""


class WalkthroughEnvelope(typing.TypedDict):
    """The envelope carrying `walkthrough`."""

    api_version: int
    data: WalkthroughReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["walkthrough"]


class WalkthroughReport(typing.TypedDict):
    """What a first-content walkthrough did — the whole of it, narrated line by line as it
    happened and gathered here so the ending can be rendered, serialised and exited on.
    """

    already_here: bool
    """Whether what was asked for was already here, and so was not acquired again."""
    handover: typing.NotRequired[Handover | None]
    """Where it leaves the operator, where it worked."""
    in_background: bool
    """Whether the download was handed to the background rather than waited out."""
    item: typing.NotRequired[str | None]
    """What it walked, where it got as far as choosing something."""
    lines: list[Line]
    """Every line it said, in order — the same lines the operator watched arrive, kept so
    a machine-readable run is not a silent one.
    """
    link: typing.NotRequired[Link | None]
    """What the import did with the file, where it got that far."""
    proves: str
    """What it set out to prove, said so the operator knows what they watched."""
    shape: Shape
    """Which walk this was."""
    state: WalkthroughState
    """Where it ended up."""
    stopped: typing.NotRequired[Stopped | None]
    """Where and why it stopped, where it did."""
    suggestions: list[str]
    """What could have been walked instead, where nothing was chosen — the safe first
    attempts, so an operator with an empty library is not left guessing.
    """


type WalkthroughState = typing.Literal[
    "offered",
    "skipped",
    "searching",
    "grabbing",
    "downloading",
    "importing",
    "complete",
    "failed",
    "abandoned",
]
"""What has become of a walkthrough."""


__all__ = [
    "Handover",
    "Link",
    "Next",
    "Reason",
    "Shape",
    "Stopped",
    "WalkthroughEnvelope",
    "WalkthroughReport",
    "WalkthroughState",
]
