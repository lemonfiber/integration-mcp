# Copyright (c) 2026 NightWorksIO
"""The shapes `alert` and `dashboard` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .alert__dashboard__doctor__error__plugins import ProblemSeverity


class Alert(typing.TypedDict):
    """One interruption: what happened, which way, and how much it matters."""

    affected: list[str]
    """Every check this alert speaks for, the first being [`Self::check`]. More
    than one where the same event was grouped across several services.
    """
    check: str
    """The check this came from, so an alert and its condition cannot drift apart.
    Where several were grouped, the first of them.
    """
    exit: typing.NotRequired[int | None]
    """How the service it is about exited, where it has and the engine said;
    where several were grouped, how the first of them did.

    The technical half of what happened, kept out of the summary so the plain
    words lead, and here for whoever wants the code.
    """
    id: typing.NotRequired[str | None]
    """What names this alert rather than this event: the same on an onset and on the
    resolution that ends it, and different the next time the same thing goes wrong —
    the check and which recurrence of it this is.

    So a client can close what it opened without comparing sentences. Absent on an
    alert recorded before alerts carried one.
    """
    kind: str
    """What kind of event it is, shared by every instance of it."""
    meaning: str
    """What it costs the operator, which is the half between the event and the
    fix. \"The tunnel dropped\" and \"restart the gateway\" leave whoever reads
    them to work out for themselves whether anything leaked.
    """
    moment: Moment
    """Which way it went."""
    remedies: list[str]
    """What to do about it, most likely first. An alert that says what happened
    and not what to do is a notification, which is a different and worse thing.
    """
    severity: ProblemSeverity
    """How much it matters. A resolution takes the severity of what resolved,
    because \"the critical thing is over\" is itself worth the attention the
    critical thing had.
    """
    summary: str
    """What happened, in the words the condition was raised with."""


type Moment = typing.Literal["onset", "resolved"]
"""Which way a condition went.

Both directions are worth saying and neither is worth saying twice. An operator
told a disk filled up and never told it was resolved goes on believing it — so
resolution is an alert in its own right rather than the absence of one.
"""


__all__ = [
    "Alert",
    "Moment",
]
