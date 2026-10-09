# Copyright (c) 2026 NightWorksIO
"""The shapes `doctor` and `plugins` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .alert__dashboard__doctor__error__plugins import ProblemSeverity
from .config__credentials__doctor__outbound__plugins__wiring__wizard import ValueOrigin
from .doctor__error__plugins import Code, Problem, ProblemState, ProblemStep
from .doctor__error__plugins__repair import Remedy


type DoctorCategory = typing.Literal[
    "environment", "storage", "network", "vpn", "credentials", "services", "providers", "queue", "config"
]
"""The family a check belongs to, so a run can be narrowed to one of them.

These are the diagnostic categories the product recognises; the checks that
fill each one arrive over time, so a category may name more than lemonfiber
can yet establish.
"""


type DoctorVerdict = (
    DoctorVerdictPass | DoctorVerdictWarn | DoctorVerdictFail | DoctorVerdictUnverified | DoctorVerdictSkipped
)
"""How a single check turned out.

\"Could not check\" (`Unverified`) is its own variant rather than a level of
severity, so a check that could not run can never be mistaken for one that
passed — the dishonesty this whole subsystem exists to prevent.
"""


class DoctorVerdictFail(typing.TypedDict):
    """Not working."""

    cause: typing.NotRequired[Problem | None]
    """The problem that produced this one, where several share a root."""
    code: Code
    """The stable identifier for this kind of problem."""
    detail: typing.NotRequired[str | None]
    """The underlying technical detail, available but never leading."""
    meaning: str
    """What it means for the operator."""
    outcome: typing.Literal["fail"]
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


class DoctorVerdictPass(typing.TypedDict):
    """Verified working, with the evidence worth showing."""

    note: typing.NotRequired[str | None]
    """What was observed, where stating it helps — an address, a port."""
    outcome: typing.Literal["pass"]


class DoctorVerdictSkipped(typing.TypedDict):
    """A prerequisite was absent, so the check did not apply."""

    outcome: typing.Literal["skipped"]
    reason: str
    """Why the check did not apply."""


class DoctorVerdictUnverified(typing.TypedDict):
    """Could not be established. Never a pass."""

    outcome: typing.Literal["unverified"]
    reason: str
    """Why it could not be determined."""
    remedy: Remedy
    """What the operator can do to get an answer."""


class DoctorVerdictWarn(typing.TypedDict):
    """Working, but degraded or risky."""

    cause: typing.NotRequired[Problem | None]
    """The problem that produced this one, where several share a root."""
    code: Code
    """The stable identifier for this kind of problem."""
    detail: typing.NotRequired[str | None]
    """The underlying technical detail, available but never leading."""
    meaning: str
    """What it means for the operator."""
    outcome: typing.Literal["warn"]
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


class Finding(typing.TypedDict):
    """One thing a check established, and how it turned out."""

    category: DoctorCategory
    """The family this belongs to."""
    caused_by: typing.NotRequired[str | None]
    """The check whose finding explains this one, where another does.

    Set after the run rather than by the check itself: a check is independent
    by construction and cannot see what any other found, which is a property
    worth keeping.
    """
    check: str
    """A stable identifier for the thing checked, such as `vpn.egress-match`."""
    onset: typing.NotRequired[str | None]
    """When the stack first saw this check wrong since it last saw it right, in whole
    seconds since the epoch.

    Set after the run from the store of conditions, like [`Self::said`], so it is
    the moment the health summary names for the same check and a restart does not
    move it. Absent where the finding says nothing is wrong, and where the checks
    ran for something other than a diagnosis.
    """
    origin: ValueOrigin
    """Whose check this is: one this build ships, or one a named plugin contributed.

    Carried rather than read off the identifier. A contributed check's id is
    namespaced with the plugin's, and a reader could decode that from the colon —
    but an origin a reader has to decode is one a reader gets wrong, and the day a
    bundled id grew a colon every such reader would misattribute it in silence.
    """
    said: typing.NotRequired[str | None]
    """What the service said for itself, lately.

    Carried on the finding rather than left for the operator to go and fetch,
    because the explanation is almost always in it: a check can say a service is
    not answering, and only the service can say why. Absent where the finding is
    not about a service, where the service is fine, or where the engine would not
    say — an empty section would be a promise of evidence that is not there.

    Set after the run, like [`Self::caused_by`], since reading a service's output
    is not the check's own business and a check that did it would be doing two
    things.
    """
    service: typing.NotRequired[str | None]
    """The service this is about, where it is about one.

    Absent for the checks that are about the machine rather than about
    something running on it — the environment, the filesystem, the operator's
    own choices. Carried so that one service's trouble can be attributed to
    the service underneath it rather than counted as one more independent
    thing wrong.
    """
    service_name: typing.NotRequired[str | None]
    """What the stack calls that service in front of an operator.

    Carried beside the id rather than left for a surface to derive, because the id is
    a key and not a name: capitalising `qbittorrent` does not arrive at qBittorrent,
    and the stack has already written the name down. Absent where the finding is about
    no service, and where the stack declares no service by that id — an id standing in
    for a name would put the key back in front of the operator.

    Set after the run, like [`Self::caused_by`], from the same manifest that says
    which service depends on which.
    """
    title: str
    """The one-line summary of what was checked."""
    verdict: DoctorVerdict
    """How it turned out."""


__all__ = [
    "DoctorCategory",
    "DoctorVerdict",
    "DoctorVerdictFail",
    "DoctorVerdictPass",
    "DoctorVerdictSkipped",
    "DoctorVerdictUnverified",
    "DoctorVerdictWarn",
    "Finding",
]
