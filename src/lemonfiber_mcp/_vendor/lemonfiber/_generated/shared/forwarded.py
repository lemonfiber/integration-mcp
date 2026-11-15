# Copyright (c) 2026 NightWorksIO
"""The shapes `boot` and `lifecycle` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Forwarded(typing.TypedDict):
    """The VPN's forwarded port across a start."""

    now: typing.NotRequired[int | None]
    """The port the guard forwards now, where it forwards one."""
    pushed: bool
    """Whether every client inside the guard takes peers on it."""
    was: typing.NotRequired[int | None]
    """The port every client last took, where they took one."""


__all__ = [
    "Forwarded",
]
