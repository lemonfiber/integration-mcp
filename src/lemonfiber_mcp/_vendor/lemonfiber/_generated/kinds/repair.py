# Copyright (c) 2026 NightWorksIO
"""The `repair` envelope, and the shapes only `repair` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.doctor__error__plugins__repair import Remedy


class Beyond(typing.TypedDict):
    """A repair that has run out of chances, and where to go instead."""

    check: str
    """The check whose fault has outlasted every attempt at it."""
    remedy: Remedy
    """What to do about it now that lemonfiber has stopped offering to."""


class Mended(typing.TypedDict):
    """One repair, and what became of it."""

    outcome: RepairOutcome
    """How it turned out, once the check was asked again."""
    repair: Repair
    """What was proposed."""


class Repair(typing.TypedDict):
    """One repair lemonfiber could carry out."""

    check: str
    """The check whose finding this answers, as the finding names it."""
    does: str
    """What it would do, in the words the operator will read before confirming."""
    effects: list[str]
    """What else changes if it does.

    Stated before it is confirmed and never afterwards, because an effect an operator
    learns about after the fact is not something they agreed to. Empty where a repair
    touches nothing but the thing it names.
    """
    reversible: bool
    """Whether carrying it out is recorded well enough to be undone.

    A repair that cannot be reversed is still worth offering — restarting a container
    is not undoable and is usually right — but the operator confirming one deserves to
    know which kind they are agreeing to.
    """


class RepairEnvelope(typing.TypedDict):
    """The envelope carrying `repair`."""

    api_version: int
    data: RepairReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["repair"]


type RepairOutcome = (
    RepairOutcomeFixed
    | RepairOutcomeFixFailed
    | RepairOutcomeStopped
    | RepairOutcomeDeclined
    | RepairOutcomeWouldOverwrite
    | RepairOutcomeUnmanaged
)
"""How a repair turned out, once the check that raised the finding has been asked again.

Deliberately not a boolean. \"It ran\" and \"it worked\" are different claims, and a model
that cannot tell them apart will eventually report the first as the second.
"""


class RepairOutcomeDeclined(typing.TypedDict):
    """Not carried out, because the operator said no."""

    outcome: typing.Literal["declined"]


class RepairOutcomeFixFailed(typing.TypedDict):
    """It ran, and the check still fails."""

    outcome: typing.Literal["fix_failed"]


class RepairOutcomeFixed(typing.TypedDict):
    """It ran, and the check now passes."""

    outcome: typing.Literal["fixed"]


class RepairOutcomeStopped(typing.TypedDict):
    """It stopped partway, leaving this.

    Named precisely rather than as \"failed\": a half-applied change is a different
    state to be in from an unchanged one, and the operator has to know which they are
    looking at before they try anything else.
    """

    leaving: str
    """What the machine is now in, said plainly."""
    outcome: typing.Literal["stopped"]


class RepairOutcomeUnmanaged(typing.TypedDict):
    """Not carried out, because the operator declared the area it would write
    unmanaged.

    Apart from [`Self::WouldOverwrite`], which is lemonfiber declining to write over
    a change it can see. This is lemonfiber obeying an instruction it was given, and
    telling somebody the first when they wrote the second would send them looking
    for a change they did not make.
    """

    outcome: typing.Literal["unmanaged"]


class RepairOutcomeWouldOverwrite(typing.TypedDict):
    """Refused, because it would have written over something changed by hand."""

    outcome: typing.Literal["would_overwrite"]


class RepairReport(typing.TypedDict):
    """What a repairing run offered, and what it did."""

    acted: bool
    """Whether this run was allowed to act at all."""
    agreement: str
    """What this offer is, so consent given for it can name which offer it read.

    Carried on every report rather than only on the ones that offer something: a
    surface that has to look for it is a surface that can fail to find it, and an
    offer of nothing is still an offer somebody may agree to nothing of.
    """
    beyond: list[Beyond]
    """What has been tried too often to keep offering.

    Said rather than passed over. A repair that quietly stopped being offered leaves
    the operator watching a fault nobody mentions any more, which is worse than being
    told plainly that this is past what lemonfiber can work out.
    """
    mended: list[Mended]
    """What was carried out, in the order it was."""
    offered: list[Repair]
    """What could be put right, whether or not it was."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


__all__ = [
    "Beyond",
    "Mended",
    "Repair",
    "RepairEnvelope",
    "RepairOutcome",
    "RepairOutcomeDeclined",
    "RepairOutcomeFixFailed",
    "RepairOutcomeFixed",
    "RepairOutcomeStopped",
    "RepairOutcomeUnmanaged",
    "RepairOutcomeWouldOverwrite",
    "RepairReport",
]
