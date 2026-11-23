# Copyright (c) 2026 NightWorksIO
"""The `ran` envelope, and the shapes only `ran` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.scheduled_run import ScheduledRun


class RanEnvelope(typing.TypedDict):
    """The envelope carrying `ran`."""

    api_version: int
    data: RunReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["ran"]


class RunReport(typing.TypedDict):
    """What `lemonfiber run` came to for one service."""

    due: bool
    """Whether a time fell due, a run was owed or one was asked for at once, so it ran or
    would have.
    """
    held: typing.NotRequired[str | None]
    """Why nothing was looked at, where something held it back."""
    ran: typing.NotRequired[ScheduledRun | None]
    """The run, where one went."""
    rehearsed: bool
    """Whether nothing was run because this was a rehearsal."""
    service: str
    """The service."""
    skipped: int
    """How many times fell due while that run was still going, each skipped."""


__all__ = [
    "RanEnvelope",
    "RunReport",
]
