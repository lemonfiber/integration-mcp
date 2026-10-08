# Copyright (c) 2026 NightWorksIO
"""The `music` envelope, and the shapes only `music` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.music__quality import Disposition, MusicChoice
from ..shared.music__upgrade import Triggered


class MusicEnvelope(typing.TypedDict):
    """The envelope carrying `music`."""

    api_version: int
    data: MusicReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["music"]


class MusicReport(typing.TypedDict):
    """What choosing an audio format for music did: the choice, whether it was recorded
    or only rehearsed, and — once recorded — what became of applying it to the music
    service.

    Music has no resolution and no community profile to lean on, so unlike a resolution
    preset the choice is carried straight to the service through its API. The choice is
    still recorded first, so it is remembered even when the service cannot be reached.
    """

    choice: MusicChoice
    """The format chosen, what it means, and what it costs."""
    disposition: Disposition
    """Whether the choice was recorded, or only rehearsed."""
    outcome: typing.NotRequired[Triggered | None]
    """What became of applying it to the music service, or `None` for a rehearsal
    that applied nothing.
    """
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


__all__ = [
    "MusicEnvelope",
    "MusicReport",
]
