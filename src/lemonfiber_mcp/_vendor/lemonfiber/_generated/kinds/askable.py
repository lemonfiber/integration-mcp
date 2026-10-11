# Copyright (c) 2026 NightWorksIO
"""The `askable` envelope, and the shapes only `askable` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.askable__asked import TitleKind
from ..shared.askable__dashboard__household import MemberAsking


class Askable(typing.TypedDict):
    """One title a member's search found."""

    id: str
    """The id it is asked for by."""
    kind: TitleKind
    """Whether it is a series or a film."""
    stands: Stands
    """Where it stands in the house."""
    title: str
    """What it is called."""
    year: typing.NotRequired[int | None]
    """The year it came out, where that is known."""


class AskableEnvelope(typing.TypedDict):
    """The envelope carrying `askable`."""

    api_version: int
    data: AskableReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["askable"]


class AskableReport(typing.TypedDict):
    """One page of what a member's search found, under their limits."""

    approval: str
    """Whether what they ask for waits for whoever runs the house, as one sentence."""
    asking: MemberAsking
    """What the member may ask for: what their period allows and has left of each kind."""
    kinds: list[TitleKind]
    """The kinds of title the house can fetch now, which are the kinds searched."""
    member: str
    """The member the search was made for, by the name they are known by."""
    next: typing.NotRequired[str | None]
    """Where the next page begins, absent on the last."""
    term: str
    """The words searched for, trimmed."""
    titles: list[Askable]
    """The titles on this page, in the order they were found."""


type Stands = typing.Literal["here", "partly-here", "on-its-way", "askable"]
"""Where a title a member's search found stands in the house."""


__all__ = [
    "Askable",
    "AskableEnvelope",
    "AskableReport",
    "Stands",
]
