# Copyright (c) 2026 NightWorksIO
"""The `guide` envelope, and the shapes only `guide` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.instant import Instant


class Airing(typing.TypedDict):
    """A programme in a channel's guide."""

    certificate: typing.NotRequired[str | None]
    """Its certificate, as the server holds it, where it has one."""
    ends: Instant
    """When it ends."""
    starts: Instant
    """When it starts."""
    title: str
    """What it is called."""


class GuideEnvelope(typing.TypedDict):
    """The envelope carrying `guide`."""

    api_version: int
    data: GuideReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["guide"]


class GuideReport(typing.TypedDict):
    """The live TV guide one member may watch: each channel with its programmes from now
    across the guide window.
    """

    channels: list[Guided]
    """Each channel their own account may watch whose programme now is within their
    limits. Empty where their account may not watch live TV.
    """
    id: str
    """The identifier the media server files them under."""
    member: str
    """The member this was asked for, by the name they are known by."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""


class Guided(typing.TypedDict):
    """One channel in a member's guide."""

    guide_until: typing.NotRequired[Instant | None]
    """When the last programme the media server's guide holds on it inside the window
    ends; none where it holds none.
    """
    id: str
    """The identifier the server tells it apart by."""
    name: str
    """What it is called."""
    number: typing.NotRequired[str | None]
    """Its number, where it has one."""
    programmes: list[Airing]
    """Each programme on it from now across the guide window, in the order they air, the
    one on now first; one outside the member's limits is left out, a gap.
    """


__all__ = [
    "Airing",
    "GuideEnvelope",
    "GuideReport",
    "Guided",
]
