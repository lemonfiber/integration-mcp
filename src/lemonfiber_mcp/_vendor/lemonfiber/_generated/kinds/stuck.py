# Copyright (c) 2026 NightWorksIO
"""The `stuck` envelope, and the shapes only `stuck` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.stuck__trace import Stage


class StuckEntry(typing.TypedDict):
    """One stuck item queue health found, named so it links straight to its own trace."""

    service: str
    """The curator whose queue is holding it."""
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
    """The items whose downloads are stuck, across the curators — the landing point for \"N
    items stuck\" that queue health reports, each entry naming the item so the operator
    goes straight to its per-item trace rather than to a count to investigate.
    """

    incomplete: bool
    """Whether a curator's queue could not be read, so the list may be short — reported
    rather than read as \"nothing stuck\", the same honesty a trace keeps.
    """
    items: list[StuckEntry]
    """The stuck items, each linkable to its trace."""


__all__ = [
    "StuckEntry",
    "StuckEnvelope",
    "StuckReport",
]
