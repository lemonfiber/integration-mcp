# Copyright (c) 2026 NightWorksIO
"""The `tuned` envelope, and the shapes only `tuned` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.obstacle import Obstacle


class TunedEnvelope(typing.TypedDict):
    """The envelope carrying `tuned`."""

    api_version: int
    data: TunedReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["tuned"]


class TunedReport(typing.TypedDict):
    """A channel's live stream opened for a member, where its bytes are served at the
    guarded front door, each on a pass for that live stream and that member.
    """

    channel: str
    """The channel, by the identifier the channels list gives it."""
    direct: typing.NotRequired[str | None]
    """Where the tuner's own stream is served, carrying its pass."""
    fingerprint: typing.NotRequired[str | None]
    """SHA-256 over the certificate the door presents, lower-case hex, which a client
    pins.
    """
    lapses: typing.NotRequired[int | None]
    """When the passes lapse, in whole seconds since the Unix epoch. A client asks for
    new ones before then.
    """
    member: str
    """The member it is opened for, by the name they are known by."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""
    stream: typing.NotRequired[str | None]
    """The live stream a renewal or a stop names."""
    transcoded: typing.NotRequired[str | None]
    """Where a transcoded playlist of it is served, carrying its pass."""
    unlocated: typing.NotRequired[Obstacle | None]
    """Why nothing is located, where nothing is."""


__all__ = [
    "TunedEnvelope",
    "TunedReport",
]
