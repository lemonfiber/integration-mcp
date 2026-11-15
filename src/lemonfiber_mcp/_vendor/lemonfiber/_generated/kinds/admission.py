# Copyright (c) 2026 NightWorksIO
"""The `admission` envelope, and the shapes only `admission` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.instant import Instant


class AdmissionEnvelope(typing.TypedDict):
    """The envelope carrying `admission`."""

    api_version: int
    data: Admitted
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["admission"]


class Admitted(typing.TypedDict):
    """A session opened, and the moment it stops being one.

    The ending is carried rather than left for a client to work out, because a client
    that guessed would be a second opinion about who is admitted — and the two would
    disagree on the day somebody's clock is wrong.
    """

    member: typing.NotRequired[str | None]
    """The household member this session is for, where it is a member's.

    **Absent is the operator**, which is the whole of the discriminator. A second
    field naming which kind of person this is could disagree with this one, and
    the day they disagreed a client would have to choose which to believe.
    """
    name: typing.NotRequired[str | None]
    """The member's display name as the media server holds it, where it is a member's."""
    token: str
    """The secret this session is carried by, sent in the header the per-run token is."""
    until: Instant
    """When it stops being one."""


__all__ = [
    "AdmissionEnvelope",
    "Admitted",
]
