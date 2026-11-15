# Copyright (c) 2026 NightWorksIO
"""The `channels` envelope, and the shapes only `channels` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.instant import Instant


class Channel(typing.TypedDict):
    """One live TV channel, as one member's account may watch it."""

    id: str
    """The identifier the server tells it apart by."""
    name: str
    """What it is called."""
    now: typing.NotRequired[Programme | None]
    """The programme on it now, where the server knows one."""
    number: typing.NotRequired[str | None]
    """Its number, where it has one."""


class ChannelsEnvelope(typing.TypedDict):
    """The envelope carrying `channels`."""

    api_version: int
    data: ChannelsReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["channels"]


class ChannelsReport(typing.TypedDict):
    """The live TV channels one member may watch, each with the programme on it now."""

    channels: list[Channel]
    """Each channel their own account may watch whose programme now is within their
    limits. Empty where their account may not watch live TV.
    """
    id: str
    """The identifier the media server files them under."""
    member: str
    """The member this was asked for, by the name they are known by."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""


class Programme(typing.TypedDict):
    """A programme on a channel."""

    certificate: typing.NotRequired[str | None]
    """Its certificate, as the server holds it, where it has one."""
    ends: typing.NotRequired[Instant | None]
    """When it ends, where the server knows."""
    title: str
    """What it is called."""


__all__ = [
    "Channel",
    "ChannelsEnvelope",
    "ChannelsReport",
    "Programme",
]
