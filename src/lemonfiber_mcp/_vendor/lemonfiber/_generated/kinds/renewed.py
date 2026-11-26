# Copyright (c) 2026 NightWorksIO
"""The `renewed` envelope, and the shapes only `renewed` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Renewed(typing.TypedDict):
    """The grant to play of a member whose client spoke, and until when it holds."""

    lasts_until: str
    """The last day the grant holds unless their client speaks again, as `YYYY-MM-DD`."""
    member: str
    """The member, by the id their session or key names."""
    rehearsed: bool
    """Whether this was a rehearsal, which renews nothing."""


class RenewedEnvelope(typing.TypedDict):
    """The envelope carrying `renewed`."""

    api_version: int
    data: Renewed
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["renewed"]


__all__ = [
    "Renewed",
    "RenewedEnvelope",
]
