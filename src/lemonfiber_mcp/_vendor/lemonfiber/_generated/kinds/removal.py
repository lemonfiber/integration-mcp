# Copyright (c) 2026 NightWorksIO
"""The `removal` envelope, and the shapes only `removal` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class RemovalEnvelope(typing.TypedDict):
    """The envelope carrying `removal`."""

    api_version: int
    data: HouseholdRemoval
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["removal"]


type Revoked = typing.Literal["everywhere", "media-server-only", "nothing"]
"""How far a removal got, across the two services a household member exists on.

The media server is removed first and the request service second, because the
request service authenticates *through* the media server — so once the first is gone
they can do nothing either way, and a failure at the second leaves an account that
cannot sign in rather than somebody who can still watch.
"""


HouseholdRemoval = typing.TypedDict(
    "HouseholdRemoval",
    {
        "asks-through-the-request-service": bool,
        "confirmed": bool,
        "findings": list[str],
        "name": str,
        "rehearsed": bool,
        "requests": int,
        "revoked": Revoked,
    },
)
"""What removing somebody costs, and what it did.

Read before anything is written: the whole point of the unconfirmed run is that every
figure here is knowable without removing anybody.
"""


__all__ = [
    "HouseholdRemoval",
    "RemovalEnvelope",
    "Revoked",
]
