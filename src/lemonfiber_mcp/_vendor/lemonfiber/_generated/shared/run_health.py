# Copyright (c) 2026 NightWorksIO
"""The shapes `dashboard` and `status` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .scheduled_run import ScheduledRun


type RunHealth = typing.Literal["not-run", "succeeded", "failed"]
"""How a run-and-exit service's last run exited."""


class ScheduledService(typing.TypedDict):
    """One run-and-exit service, as its runs left it."""

    fired: bool
    """Whether this machine's scheduler holds its job, so its times are fired."""
    health: RunHealth
    """Its health: how its last run exited."""
    id: str
    """Its id, which is its Compose service name."""
    last: typing.NotRequired[ScheduledRun | None]
    """Its last run, where it has run."""
    name: str
    """What it is called in front of an operator."""
    running: bool
    """Whether a run of it is going now."""
    skipped: int
    """How many of its times fell due while a run was still going, each skipped."""


__all__ = [
    "RunHealth",
    "ScheduledService",
]
