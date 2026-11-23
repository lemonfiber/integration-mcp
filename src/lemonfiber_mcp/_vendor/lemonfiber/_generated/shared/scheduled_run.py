# Copyright (c) 2026 NightWorksIO
"""The shapes `dashboard`, `ran` and `status` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .instant import Instant


class ScheduledRun(typing.TypedDict):
    """One run of a run-and-exit service, as it ended."""

    ended: Instant
    """When it ended."""
    exit: typing.NotRequired[int | None]
    """How it exited, absent where it never started or a signal ended it."""
    log: list[str]
    """The last lines it wrote, oldest first, each with any credential in it withheld;
    none to a key, a member or the shared stream, none of which is handed them.
    """
    started: Instant
    """When it started."""


__all__ = [
    "ScheduledRun",
]
