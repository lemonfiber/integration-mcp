# Copyright (c) 2026 NightWorksIO
"""The `notify-mine` envelope, and the shapes only `notify-mine` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class NotifyMineEnvelope(typing.TypedDict):
    """The envelope carrying `notify-mine`."""

    api_version: int
    data: NotifyMineReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["notify-mine"]


class NotifyMineReport(typing.TypedDict):
    """The ways a member may be told that something they asked for is ready, and nothing
    technical.
    """

    offered: list[NotifyOffered]
    """Each way the operator offered the household, in the order it was offered."""
    phone: bool
    """Whether this member's own phone is registered to be woken."""
    rehearsed: bool
    """Whether this was a rehearsal of a choice, with nothing kept."""


class NotifyOffered(typing.TypedDict):
    """One way to be told that the operator offered the household, as a member reads it."""

    id: str
    """What it is chosen by."""
    name: str
    """The name the household reads it by."""
    receiving: bool
    """Whether this member is told on it."""


__all__ = [
    "NotifyMineEnvelope",
    "NotifyMineReport",
    "NotifyOffered",
]
