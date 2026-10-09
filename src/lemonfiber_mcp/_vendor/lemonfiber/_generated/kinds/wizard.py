# Copyright (c) 2026 NightWorksIO
"""The `wizard` envelope, and the shapes only `wizard` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.config__wizard import SettingReport, Validation


type Phase = typing.Literal["in-progress", "reviewing", "applying", "applied"]
"""Where an in-flight or finished setup stands in its lifecycle.

The persisted marker a later run reads to tell answers still being gathered
from a half-written apply. Only these four are ever written: the two states a
run infers instead of storing — no setup at all, and an apply that stopped
mid-write — are read off the world rather than trusted from a file (see
[`Status`]).
"""


type Ran = bool
"""Whether a walk through setup was carried out or rehearsed, written as the bare
`true` or `false` every other report writes its `rehearsed` as.

Two words rather than a fourth switch on a report that already holds three, which
is a report somebody reads by remembering which `true` means what. On the wire it
is the same boolean every report carries, so a client reads one shape.
"""


class WizardEnvelope(typing.TypedDict):
    """The envelope carrying `wizard`."""

    api_version: int
    data: WizardReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["wizard"]


class WizardReport(typing.TypedDict):
    """Where a setup run stands, and what it is still asking for.

    The answer to every step of setup driven from outside this process: a surface
    asks where the walk is, submits one answer, and is told where the walk is now.
    Nothing here is a copy of the wizard's own state — it is read off the wizard
    each time, so a surface cannot hold a stale one and act on it.

    **The answers themselves are never in it.** Setup gathers an indexer key and a
    provider password, and this report is one a script can log, so it says what was
    *decided* and never what was *entered* — the same line [`SetupReport`] holds.
    What will be written is in `plan`, with every credential withheld exactly as
    `config show` withholds one.
    """

    asks: bool
    """Whether that step asks a question, as opposed to only informing."""
    at: WizardStep
    """The step the operator is on."""
    offered: bool
    """Whether this machine has setup left to do. False once configuration
    exists and nothing is part-way through, which is when a surface directs
    the operator to reconfiguration instead of asking the first question again.
    """
    phase: Phase
    """Where this run stands in its lifecycle. `applying` read back here means an
    apply stopped part-way, because an apply that is still running is one this
    answer is waiting on.
    """
    plan: list[SettingReport]
    """What applying will write, in the order it will be written, with any value
    nobody has argued for showing withheld.
    """
    proof: typing.NotRequired[Validation | None]
    """What proving the credential just given came to, where one was given.

    Setup tests an indexer key and a Usenet login against their live services as
    they are entered, and this is what the service answered — never what was
    entered. Absent for every other answer, and for a step that gave none.
    """
    ready_for_review: bool
    """Whether every applicable question is answered, so the plan can be applied."""
    rehearsed: Ran
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    unanswered: list[WizardStep]
    """Every question that applies on this machine and has no answer yet, in the
    order they are put.
    """
    written: list[str]
    """What an apply that stopped part-way had already written, each said plainly.

    The partial state a recovery is chosen about, so whoever chooses has seen it.
    Empty for every other phase, and empty too for an apply that stopped before
    it wrote anything.
    """


type WizardStep = typing.Literal[
    "welcome",
    "preflight",
    "prerequisites",
    "protocols",
    "vpn",
    "data-location",
    "credentials",
    "provider",
    "service-user",
    "library",
    "household",
    "notifications",
    "autostart",
    "review",
]
"""A step of setup, in the order the operator meets it.

Some steps only inform (they detect and state, and the operator acknowledges);
others ask a question whose answer the wizard records. The apply-and-onward
steps — writing config, pulling images, wiring services — are not modelled
here yet: they arrive with the features they drive, and this machine covers
the read-only phase that precedes them.
"""


__all__ = [
    "Phase",
    "Ran",
    "WizardEnvelope",
    "WizardReport",
    "WizardStep",
]
