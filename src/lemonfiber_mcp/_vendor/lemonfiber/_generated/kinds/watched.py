# Copyright (c) 2026 NightWorksIO
"""The `watched` envelope, and the shapes only `watched` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class WatchedEnvelope(typing.TypedDict):
    """The envelope carrying `watched`."""

    api_version: int
    data: WatchedReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["watched"]


class WatchedReport(typing.TypedDict):
    """A player's report of how far a member got, as the media server now holds it."""

    ended: bool
    """Whether it was recorded as finished."""
    id: str
    """The title or episode, by the identifier the shelf lists it under."""
    position: int
    """How far in, in whole seconds, as recorded."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""


__all__ = [
    "WatchedEnvelope",
    "WatchedReport",
]
