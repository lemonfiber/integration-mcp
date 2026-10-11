# Copyright (c) 2026 NightWorksIO
"""The `asked` envelope, and the shapes only `asked` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.askable__asked import TitleKind


class AskedEnvelope(typing.TypedDict):
    """The envelope carrying `asked`."""

    api_version: int
    data: AskedReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["asked"]


class AskedReport(typing.TypedDict):
    """What asking for one title came to, or would come to under a rehearsal."""

    kind: TitleKind
    """Whether it is a series or a film."""
    leaves: LeftAfter
    """What is left of the member's allowance once it is counted."""
    member: str
    """The member it was asked for, by the name they are known by."""
    outcome: Became
    """What it came to."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""
    released: bool
    """Whether the title has come out yet. One that has not is asked for, and arrives
    once it is out.
    """
    said: str
    """All of it, in one household sentence."""
    seasons: list[int]
    """The seasons asked for, none for a film."""
    title: str
    """The id of the title asked for."""


type Became = typing.Literal["asked", "waiting", "on-its-way"]
"""What asking for a title came to."""


class LeftAfter(typing.TypedDict):
    """What is left of a member's allowance once an ask is counted, for each kind a limit
    holds them to.
    """

    films: typing.NotRequired[int | None]
    """Films still to ask for, absent where nothing limits them."""
    television: typing.NotRequired[int | None]
    """Seasons of television still to ask for, absent where nothing limits them."""


__all__ = [
    "AskedEnvelope",
    "AskedReport",
    "Became",
    "LeftAfter",
]
