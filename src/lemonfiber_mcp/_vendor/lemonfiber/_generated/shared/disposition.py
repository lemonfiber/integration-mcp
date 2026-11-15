# Copyright (c) 2026 NightWorksIO
"""The shapes `music` and `quality` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Disposition = typing.Literal["shown", "recorded", "rehearsed", "held", "reapplied", "would-reapply"]
"""What a quality command did to the stored choice."""


class MusicChoice(typing.TypedDict):
    """One audio-format choice in force, for media that has no resolution — the same
    question as a [`PresetChoice`], answered in format terms rather than resolution.
    """

    format: str
    """The format's plain-language name."""
    means: str
    """What it means, in the operator's terms."""
    note: str
    """The practical caveat worth knowing — playing it, or finding it."""
    scope: str
    """What this applies to — `music`."""
    size_per_hour: str
    """Roughly how much disk an hour of it takes."""
    targets: str
    """The audio format it targets, in plain terms."""


__all__ = [
    "Disposition",
    "MusicChoice",
]
