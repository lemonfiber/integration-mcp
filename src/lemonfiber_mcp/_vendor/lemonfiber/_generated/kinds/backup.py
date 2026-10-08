# Copyright (c) 2026 NightWorksIO
"""The `backup` envelope, and the shapes only `backup` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.backup__restore import Scope


class BackupEnvelope(typing.TypedDict):
    """The envelope carrying `backup`."""

    api_version: int
    data: BackupReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["backup"]


class BackupReport(typing.TypedDict):
    """What a capture produced."""

    pace: Pace
    """What the capture moved, against what a capture is meant to stay inside.

    Read off the room check that already ran, so saying it costs nothing: the trees
    were walked to decide whether the archive would fit, and this is the same number
    put to a second use.
    """
    path: str
    """Where the archive was written, or — on a run that only said what it would
    capture — where it would have gone.
    """
    pruned: list[str]
    """The older backups retention pruned, oldest first — or would prune."""
    rehearsed: bool
    """Whether this run only said what it would capture.

    A flag rather than a second shape, because every other field means the same
    thing either way: a capture is settled before it is written — the room is
    measured, the manifest described, the name and the path derived, and retention
    worked out — so what a rehearsal reports is what a real run would report, with
    the one write left out. What changes is the tense a surface says it in.
    """
    scope: Scope
    """What the backup covers."""
    sensitive: bool
    """Whether it carries credentials, and so must be handled as sensitive."""


class Pace(typing.TypedDict):
    """What a capture came to, against the time a capture is meant to take.

    Reported and never enforced. The room check already walks the trees to decide
    whether the archive fits, so the bytes are in hand before anything is written and
    cost nothing extra to say — and what they are measured against is the work, not a
    clock. A wall-clock gate on a machine whose disk throughput varies by more than the
    margin either passes for reasons unrelated to this product or fails for them, and
    neither reading is worth having.
    """

    brisk: bool
    """Whether this capture is inside it."""
    budget: int
    """The bytes a capture may move and still be expected to finish in time.

    Carried with the reading rather than left for a reader to look up, so a surface
    showing this does not need a second copy of the number to compare against.
    """
    moved: int
    """The bytes the captured trees came to, as the room check measured them."""


__all__ = [
    "BackupEnvelope",
    "BackupReport",
    "Pace",
]
