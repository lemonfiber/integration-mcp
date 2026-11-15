# Copyright (c) 2026 NightWorksIO
"""The `plugin-recording` envelope, and the shapes only `plugin-recording` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.violation import Violation


class Failed(typing.TypedDict):
    """A service none of whose recordings was written, and why."""

    log: list[str]
    """The last lines its container wrote, scrubbed and with nothing a terminal obeys."""
    service: str
    """The service."""
    step: str
    """The step it failed at."""
    why: str
    """Why."""


class PluginRecordingEnvelope(typing.TypedDict):
    """The envelope carrying `plugin-recording`."""

    api_version: int
    data: Recorded
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugin-recording"]


class Recorded(typing.TypedDict):
    """Every recording a plugin's manifest names, taken again."""

    failed: list[Failed]
    """Each service whose recordings were not taken."""
    holds: bool
    """Whether every recording was written or reproduced, each with a note, and each no
    case asked removed.
    """
    id: str
    """The plugin's id."""
    recordings: list[RecordingTaken]
    """Each recording, in the order the manifest names them."""
    refusals: list[Violation]
    """Everything this build refuses about the manifest; nothing is taken where any is."""


class RecordingTaken(typing.TypedDict):
    """One recording a manifest names, and what taking it came to."""

    fixture: typing.NotRequired[str | None]
    """The recording it names."""
    named: str
    """What names it: a proof, a claim's probe or a contributed check."""
    took: Took
    """What taking it came to."""


type Took = (
    TookWritten
    | TookUnnoted
    | TookReproduced
    | TookUnreproduced
    | TookOverran
    | TookUnrecorded
    | TookRemoved
    | TookUnasked
    | TookLeft
)
"""What taking one recording came to."""


class TookLeft(typing.TypedDict):
    """The recording is of a case reaching a host outside the stack, which a run holding
    recordings to what it takes again leaves as recorded rather than reaching.
    """

    host: str
    """The host the case reaches."""
    outcome: typing.Literal["left"]


class TookOverran(typing.TypedDict):
    """The run was still going at its limit, so there is nothing to record."""

    outcome: typing.Literal["overran"]
    seconds: int
    """The limit, in seconds."""


class TookRemoved(typing.TypedDict):
    """The recording answers no case that was asked, so it was removed."""

    outcome: typing.Literal["removed"]


class TookReproduced(typing.TypedDict):
    """The recording already held what was taken, byte for byte."""

    outcome: typing.Literal["reproduced"]


class TookUnasked(typing.TypedDict):
    """The recording answers no case that was asked, and is left as it was because the
    run writes nothing.
    """

    outcome: typing.Literal["unasked"]


class TookUnnoted(typing.TypedDict):
    """The recording was written with an empty note, which its author has to write."""

    outcome: typing.Literal["unnoted"]


class TookUnrecorded(typing.TypedDict):
    """Nothing was taken, or there is nowhere to write what was."""

    outcome: typing.Literal["unrecorded"]
    why: str
    """Why."""


class TookUnreproduced(typing.TypedDict):
    """The recording holds another result for the same image and arguments, so it is
    refused and left as it was.
    """

    outcome: typing.Literal["unreproduced"]
    why: str
    """What differs."""


class TookWritten(typing.TypedDict):
    """The recording was written."""

    outcome: typing.Literal["written"]


__all__ = [
    "Failed",
    "PluginRecordingEnvelope",
    "Recorded",
    "RecordingTaken",
    "Took",
    "TookLeft",
    "TookOverran",
    "TookRemoved",
    "TookReproduced",
    "TookUnasked",
    "TookUnnoted",
    "TookUnrecorded",
    "TookUnreproduced",
    "TookWritten",
]
