# Copyright (c) 2026 NightWorksIO
"""The shapes `doctor`, `error` and `plugins` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .alert__dashboard__doctor__error__plugins import ProblemSeverity
from .doctor__error__plugins__repair import Remedy


type Code = str
"""A stable identifier for a kind of problem.

Stability is the whole point: an operator who searches for a code should find
the same answer a year later. Every code is declared in the error crate's `codes`
module, and a code is never recycled.
"""


class Problem(typing.TypedDict):
    """Something that went wrong, in the form an operator can act on."""

    cause: typing.NotRequired[Problem | None]
    """The problem that produced this one, where several share a root."""
    code: Code
    """The stable identifier for this kind of problem."""
    detail: typing.NotRequired[str | None]
    """The underlying technical detail, available but never leading."""
    meaning: str
    """What it means for the operator."""
    remedies: list[Remedy]
    """What to do, most likely first."""
    severity: ProblemSeverity
    """How much it matters."""
    state: ProblemState
    """Where it stands with respect to being fixed."""
    steps: typing.NotRequired[list[ProblemStep]]
    """Every step a run declares, with what each came to, where the problem ended a run
    of steps part-way; absent from every other problem.

    Data beside the detail rather than in it, so a client reads what changed
    somewhere going back cannot reach without parsing a sentence written for a person.
    """
    summary: str
    """What happened, in one plain sentence."""


type ProblemState = typing.Literal["actionable", "guided", "remediable", "unknown", "suppressed"]
"""Where a problem stands with respect to being fixed."""


class ProblemStep(typing.TypedDict):
    """What one step of a run that stopped part-way came to."""

    came: StepCame
    """What it came to."""
    landed: bool
    """Whether it reached somewhere other than the plugin's own services, which going
    back cannot undo.
    """
    recipe: str
    """The recipe the step belongs to."""
    step: str
    """The step's id within it."""


type StepCame = typing.Literal[
    "answered",
    "skipped",
    "not-reached",
    "unreachable",
    "refused",
    "withheld",
    "unexpected",
    "uncaptured",
    "oversized",
]
"""What one step of a recipe came to."""


__all__ = [
    "Code",
    "Problem",
    "ProblemState",
    "ProblemStep",
    "StepCame",
]
