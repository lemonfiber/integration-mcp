# Copyright (c) 2026 NightWorksIO
"""The `quality` envelope, and the shapes only `quality` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.lifecycle__quality__reset__update import StackEdit
from ..shared.music__quality import Disposition, MusicChoice


class PresetChoice(typing.TypedDict):
    """One preset in force, and what it means for the media it applies to — the
    operator's question answered in their own terms, with no scoring vocabulary.
    """

    means: str
    """What it means, in the operator's terms rather than the tool's."""
    needs_transcoding_here: bool
    """Whether this host would have to transcode it in software — the caution
    stated before a choice a household cannot smoothly play.
    """
    preset: str
    """The preset's plain-language name."""
    resolution: str
    """The resolution and encode it targets."""
    scope: str
    """What this applies to: `everything`, or a specific media type."""
    size_per_hour: str
    """Roughly how much disk an hour of it takes."""
    transcoding: str
    """What playback costs, in plain terms."""


class QualityEnvelope(typing.TypedDict):
    """The envelope carrying `quality`."""

    api_version: int
    data: QualityReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["quality"]


class QualityReport(typing.TypedDict):
    """The operator's quality choice, what each preset means, and what the command
    did with it.
    """

    choices: list[PresetChoice]
    """The global choice first, then each media type set apart from it."""
    customised: bool
    """Whether the Recyclarr config has been hand-edited since lemonfiber wrote it —
    the `customised` state, in which the preset is no longer authoritative until
    it is deliberately re-asserted. For a reapply, whether an edit was overwritten.
    """
    disposition: Disposition
    """What became of the choice."""
    music: typing.NotRequired[MusicChoice | None]
    """The audio-format choice for music, where one is set — media that has no
    resolution, so it is reported apart from the resolution presets rather than
    forced into their shape.
    """
    overwritten: typing.NotRequired[StackEdit | None]
    """The hand-edited config a reapply replaced — or, rehearsed, would replace — with
    the diff of what goes against what lands in its place.

    Absent everywhere else, and absent for a reapply over a config already in
    lemonfiber's own hand. Consent given against a yes-or-no is consent to
    something the operator was never shown: they know a file they edited is about
    to go, and not which of their lines is in it. The lines are masked the way
    every stack-file diff is, so a key that drifted is named without its value.
    """
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


__all__ = [
    "PresetChoice",
    "QualityEnvelope",
    "QualityReport",
]
