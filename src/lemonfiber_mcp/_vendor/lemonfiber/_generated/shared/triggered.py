# Copyright (c) 2026 NightWorksIO
"""The shapes `music` and `upgrade` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Triggered = TriggeredStarted | TriggeredNotStarted | TriggeredFailed
"""What became of asking one service to re-search its existing content."""


class TriggeredFailed(typing.TypedDict):
    """The service refused the command or could not be reached."""

    detail: str
    """The service's own account of why."""
    state: typing.Literal["failed"]


class TriggeredNotStarted(typing.TypedDict):
    """The service had not finished starting — no key yet — so nothing was asked of
    it; running the upgrade again once it is up will reach it.
    """

    state: typing.Literal["not-started"]


class TriggeredStarted(typing.TypedDict):
    """The re-search was accepted and now runs in the service's background."""

    state: typing.Literal["started"]


__all__ = [
    "Triggered",
    "TriggeredFailed",
    "TriggeredNotStarted",
    "TriggeredStarted",
]
