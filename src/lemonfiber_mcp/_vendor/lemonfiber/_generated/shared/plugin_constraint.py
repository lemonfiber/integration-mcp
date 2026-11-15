# Copyright (c) 2026 NightWorksIO
"""The shapes `plugin-claims` and `plugins` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type PluginConstraint = typing.Literal[
    "status",
    "json",
    "json_has_keys",
    "json_types",
    "json_at_least",
    "json_array_min",
    "json_is_absent",
    "content_type",
    "body_starts_with",
    "exit",
    "stdout_starts_with",
]
"""A kind of constraint an expectation can put on a body.

The same vocabulary a proof's expectation and a contributed check's use, so that
\"a status alone is not evidence\" is one rule rather than three. Read as well as
written: a declaration that an assertion fails on a recording names the one of these
that fails there.
"""


type PluginEvidence = typing.Literal["recordings", "service"]
"""What the verdicts in a report were reached against.

One value, because one is all this build can produce: nothing here asks a service
anything. It is a field rather than a sentence for the reason a verdict is one — a
reader handed `demonstrated` has nothing else in the document to tell a recording
that answered from a service that did, and the weaker of those two claims must not
be readable as the stronger. The prose says it on the page; this says it to
whatever consumes the report: an author's own CI, a catalogue, anything counting
passes. Naming the axis now is what made the second kind of evidence a change the
compiler walked somebody through rather than one they had to remember.
"""


class PluginFailingAsDeclared(typing.TypedDict):
    """One recording an assertion fails on as its manifest declares."""

    constraint: PluginConstraint
    """The constraint of the expectation that fails there."""
    fixture: str
    """The recording."""
    held: str
    """What the recording held there."""
    place: typing.NotRequired[str | None]
    """Where within that constraint, for one that looks at places."""
    reason: str
    """Why the manifest says this recording is one the assertion fails on."""


type PluginVerdict = (
    PluginVerdictPassed
    | PluginVerdictFailed
    | PluginVerdictUnproven
    | PluginVerdictFailingAsDeclared
    | PluginVerdictOpen
)
"""What one assertion came to, whatever answered it."""


class PluginVerdictFailed(typing.TypedDict):
    """It does not, in every way it does not."""

    faults: list[str]
    """Every way the recorded answer is not the declared one."""
    outcome: typing.Literal["failed"]


class PluginVerdictFailingAsDeclared(typing.TypedDict):
    """It fails on the recordings its manifest declares it fails on, on the constraint
    each declaration names and on nothing else, and holds on every other recording it
    was run against.

    Apart from passed and from failed, and counted as neither. The assertion does not
    hold there, so a pass would say the opposite of what the recording shows; and the
    failure is the one its author described and gave a reason for, so it does not
    fail the run. Only ever reached against recordings: the live service is held to
    the expectation as it is written.
    """

    declared: list[PluginFailingAsDeclared]
    """Each declared recording, what it held, and why it is one the assertion fails on."""
    outcome: typing.Literal["failing-as-declared"]


class PluginVerdictOpen(typing.TypedDict):
    """The part an adapter claims is left open, because nobody entered the code its claim
    takes: whoever reaches it first can claim it.

    Apart from passed and from failed, and counted as neither: the adapter holds to its
    contract, and the part is not yet the household's. Only ever reached against the
    live service, by an install's or a re-proof's claim.
    """

    outcome: typing.Literal["open"]
    why: str
    """The part, and the code its claim takes."""


class PluginVerdictPassed(typing.TypedDict):
    """The recording answers what the binding declares."""

    outcome: typing.Literal["passed"]


class PluginVerdictUnproven(typing.TypedDict):
    """It could not be run, and so established nothing either way."""

    outcome: typing.Literal["unproven"]
    why: str
    """What stopped it being run."""


__all__ = [
    "PluginConstraint",
    "PluginEvidence",
    "PluginFailingAsDeclared",
    "PluginVerdict",
    "PluginVerdictFailed",
    "PluginVerdictFailingAsDeclared",
    "PluginVerdictOpen",
    "PluginVerdictPassed",
    "PluginVerdictUnproven",
]
