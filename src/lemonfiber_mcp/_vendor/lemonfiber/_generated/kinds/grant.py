# Copyright (c) 2026 NightWorksIO
"""The `grant` envelope, and the shapes only `grant` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class GrantEnvelope(typing.TypedDict):
    """The envelope carrying `grant`."""

    api_version: int
    data: GrantReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["grant"]


class GrantReport(typing.TypedDict):
    """A grant to play on a member's own account, the token the device plays with, and how
    long it lasts.
    """

    granted: bool
    """Whether a session was opened for the device. A rehearsal opens none."""
    lasts_until: str
    """The last day the grant holds unless the member's client speaks to the core
    before then, as `YYYY-MM-DD`.
    """
    member: str
    """The member the device now plays as, by the name they are known by."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""
    token: typing.NotRequired[str | None]
    """The token the device presents at the guarded front door, as
    `Authorization: Bearer <token>`. Answered once, here, and kept by nothing in the
    core; absent where nothing was granted.
    """


__all__ = [
    "GrantEnvelope",
    "GrantReport",
]
