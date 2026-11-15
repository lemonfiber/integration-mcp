# Copyright (c) 2026 NightWorksIO
"""The `play` envelope, and the shapes only `play` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.obstacle import Obstacle


class PlayEnvelope(typing.TypedDict):
    """The envelope carrying `play`."""

    api_version: int
    data: PlayReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["play"]


class PlayReport(typing.TypedDict):
    """Where one title plays from in a member's browser, at the stack's front door, on a
    pass sealing a session on their own account.
    """

    id: str
    """The title or episode, by the identifier the shelf lists it under."""
    lapses: typing.NotRequired[int | None]
    """When the pass lapses, in whole seconds since the Unix epoch. A browser hands it
    back for a new one before then.
    """
    member: str
    """The member it plays as, by the name they are known by."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""
    stream_from: typing.NotRequired[str | None]
    """The playlist it plays from at the front door, carrying its pass."""
    unlocated: typing.NotRequired[Obstacle | None]
    """Why nothing is located, where nothing is."""


__all__ = [
    "PlayEnvelope",
    "PlayReport",
]
