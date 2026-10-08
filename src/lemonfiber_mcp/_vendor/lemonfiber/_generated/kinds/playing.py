# Copyright (c) 2026 NightWorksIO
"""The `playing` envelope, and the shapes only `playing` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.held__playing import Medium


class Playback(typing.TypedDict):
    """Somebody watching something now, as the media server lists the session.

    Who and what, and where: what a household recognises about somebody watching. No
    stream, no bitrate and no transcode reason, because a member is not choosing one and
    a surface handed those would have to decide not to draw them.
    """

    device: str
    """What the device it plays on calls itself."""
    episode: typing.NotRequired[int | None]
    """The episode's number within its season, where the server numbers one."""
    medium: Medium
    """Which of the kinds this product deals in it is. An episode is of a series."""
    member: str
    """The name the account is known by."""
    member_id: str
    """The identifier the server files the account under."""
    paused: bool
    """Whether it is paused rather than playing."""
    season: typing.NotRequired[int | None]
    """The season an episode is in, where the server numbers one."""
    series: typing.NotRequired[str | None]
    """The series an episode belongs to, where it is one."""
    title: str
    """What is playing, in the words the server holds it under: an episode's own name
    where it is an episode.
    """


class PlayingEnvelope(typing.TypedDict):
    """The envelope carrying `playing`."""

    api_version: int
    data: PlayingReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["playing"]


class PlayingReport(typing.TypedDict):
    """What is playing now, and whose sessions were asked about."""

    available: bool
    """Whether the media server could be asked at all.

    Nobody watching and a server that would not say are different answers, and
    collapsing them would report a quiet house on the day the media server was down.
    Anything that could not be read is said in `findings` and this goes false.
    """
    findings: list[str]
    """What is worth saying about this reading, in the words its reader would use.

    Always written, empty or not, so a reader never has to guess what an absent
    field means.
    """
    member: str
    """The member this was narrowed to, by the name they are known by, or empty where
    it is every session in the house.
    """
    sessions: list[Playback]
    """Every session playing something, in the order the media server lists them. How
    many are playing is how many these are, rather than a count kept beside them.
    """


__all__ = [
    "Playback",
    "PlayingEnvelope",
    "PlayingReport",
]
