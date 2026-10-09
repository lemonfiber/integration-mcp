# Copyright (c) 2026 NightWorksIO
"""The `stuck` envelope, and the shapes only `stuck` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.import___migration__seed__status__stuck import UnsupportedReport
from ..shared.stuck__trace import Stage


class StuckEntry(typing.TypedDict):
    """One stuck item queue health found, named so it links straight to its own trace."""

    service: str
    """The \\*arr whose queue is holding it."""
    stage: Stage
    """The stage its download is stuck at."""
    title: str
    """The item's title — the term a `trace` searches by."""


class StuckEnvelope(typing.TypedDict):
    """The envelope carrying `stuck`."""

    api_version: int
    data: StuckReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["stuck"]


class StuckReport(typing.TypedDict):
    """The items whose downloads are stuck, across the \\*arrs — the landing point for \"N
    items stuck\" that queue health reports, each entry naming the item so the operator
    goes straight to its per-item trace rather than to a count to investigate.
    """

    incomplete: bool
    """Whether an \\*arr's queue could not be read, so the list may be short — reported
    rather than read as \"nothing stuck\", the same honesty a trace keeps.
    """
    items: list[StuckEntry]
    """The stuck items, each linkable to its trace."""
    unsupported: typing.NotRequired[list[UnsupportedReport]]
    """Services whose queue lemonfiber cannot read at all, each with why.

    Apart from [`Self::incomplete`], which is a queue that was asked and would not
    answer. This is a queue that was never asked, because the service declares an
    API shape this build does not speak or a Servarr declaration it cannot reach
    through — and a reading that dropped those would be as short as an unreadable
    queue makes it, without the sentence that says so.
    """


__all__ = [
    "StuckEntry",
    "StuckEnvelope",
    "StuckReport",
]
