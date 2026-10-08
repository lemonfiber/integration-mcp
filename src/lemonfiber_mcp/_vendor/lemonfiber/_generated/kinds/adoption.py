# Copyright (c) 2026 NightWorksIO
"""The `adoption` envelope, and the shapes only `adoption` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.adoption__beside__config__import___replacement import Stance
from ..shared.adoption__migration import CarryingReport


class AdoptReport(typing.TypedDict):
    """What adopting a setup already here came to, or would come to."""

    back_up: list[str]
    """The host paths those services keep their data in, so a backup can be taken of
    exactly the right thing.
    """
    backed_up: typing.NotRequired[str | None]
    """Where the capture of those paths was written, once one has been taken.

    Absent on a rehearsal, which captures nothing, and absent where the setup
    mounted nothing worth capturing. Present on an adoption that went through,
    because an operator told a backup was taken is owed the path to it.
    """
    project: typing.NotRequired[str | None]
    """The project lemonfiber would manage, where exactly one could be adopted."""
    refusal: typing.NotRequired[str | None]
    """Why nothing was done, where nothing was."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    stance: Stance
    """Where the act stands."""
    upgrades: list[CarryingReport]
    """The services whose databases a newer version would upgrade, and whose data
    therefore has to be backed up before anything opens it.
    """


class AdoptionEnvelope(typing.TypedDict):
    """The envelope carrying `adoption`."""

    api_version: int
    data: AdoptReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["adoption"]


__all__ = [
    "AdoptReport",
    "AdoptionEnvelope",
]
