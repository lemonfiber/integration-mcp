# Copyright (c) 2026 NightWorksIO
"""The `admission` envelope, and the shapes only `admission` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


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

    The id and nothing else. What that member is called, what they may watch and
    what they have left are read from the household report, which already carries
    all of it per member — so there is one fact here and no second copy of
    anything that could go stale against the read.
    """
    token: str
    """The secret this session is carried by, sent in the header the per-run token is."""
    until: str
    """When it stops being one, written as every other instant this product writes."""


__all__ = [
    "AdmissionEnvelope",
    "Admitted",
]
