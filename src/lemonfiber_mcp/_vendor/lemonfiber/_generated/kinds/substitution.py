# Copyright (c) 2026 NightWorksIO
"""The `substitution` envelope, and the shapes only `substitution` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.substitution__wiring import Unfilled


class Substitution(typing.TypedDict):
    """One service standing in for another, worked out before anything is written."""

    asked_by: list[str]
    """Every service that asks for it, so the reach of the change is visible."""
    capability: str
    """The capability whose filler changes."""
    leaves_unfilled: list[Unfilled]
    """What this would leave with nothing filling it, each naming what asked.

    The one thing an operator cannot find out afterwards. A service filling two
    capabilities is replaced for one of them, and the other stops being filled —
    which is a working stack becoming a broken one, on a change that reads as
    swapping like for like.
    """
    now: str
    """What would fill it."""
    setting: str
    """The setting the change writes."""
    was: typing.NotRequired[str | None]
    """What fills it now, where anything does."""
    why: typing.NotRequired[str | None]
    """What the operator said about the choice, where they said anything.

    Read back as the choice's own `why` wherever the choice is read, and absent
    where nothing was said: nothing supplies a reason on the operator's behalf.
    """


class SubstitutionEnvelope(typing.TypedDict):
    """The envelope carrying `substitution`."""

    api_version: int
    data: SubstitutionReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["substitution"]


class SubstitutionReport(typing.TypedDict):
    """What substituting one service for another would come to."""

    agreement: str
    """What this reading names itself, so a choice answering it can say which reading
    it answered.

    Named part by part — the choice itself, what fills the capability now, what asks
    for it, and what the change would leave unfilled — so a choice refused because the
    wiring moved is told which of those moved.
    """
    applied: bool
    """Whether it was written, or only worked out.

    A run that only says what it would do writes nothing and reports the same
    answer, so the two are told apart here rather than by the caller remembering
    which flags it passed.
    """
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    substitution: Substitution
    """The change itself, and what it would leave with nothing filling it."""


__all__ = [
    "Substitution",
    "SubstitutionEnvelope",
    "SubstitutionReport",
]
