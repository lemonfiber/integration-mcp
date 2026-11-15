# Copyright (c) 2026 NightWorksIO
"""The `plugin-claims` envelope, and the shapes only `plugin-claims` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.plugin_constraint import PluginEvidence, PluginVerdict
from ..shared.violation import Violation


class Asserted(typing.TypedDict):
    """One assertion that is not a probe, and what its recording came to."""

    id: str
    """What a verdict is reported against."""
    kind: Assertion
    """Which of the two it is."""
    says: str
    """What it establishes, in one line."""
    service: str
    """The service it asks."""
    verdict: PluginVerdict
    """What the recording said about it."""


type Assertion = typing.Literal["proof", "check"]
"""Which kind of assertion a verdict is about.

A probe is reported against the capability it demonstrates and is not here. These
two are, because neither belongs to a capability: one gates the install of this
plugin and the other is a row in a register that runs every day afterwards.
"""


class Claimed(typing.TypedDict):
    """Everything a plugin's source says, and what this build makes of it."""

    against: PluginEvidence
    """What every verdict in this report was reached against."""
    capabilities: list[Claiming]
    """What its services declare they can do."""
    checks: list[Asserted]
    """The checks it contributes, against the recordings they name.

    Reported and never counted against the install. A contributed check reports on a
    running stack rather than gating one, so a check that its own recording refuses
    is a check doing its job on a machine in the state it was recorded in — which is
    a different fact from a claim its recordings refute.
    """
    contributions: list[Contributed]
    """What it adds to lemonfiber's own registers."""
    extension_points_version: int
    """The extension points generation it was held to."""
    id: str
    """The plugin's id."""
    installable: bool
    """Whether this plugin would be installed as it stands.

    Carried rather than left for a reader to work out. It is one rule over two of
    the fields above, and a consumer deciding it for itself would be a second copy
    of that rule — free to disagree with the exit status this same answer produces.
    """
    name: str
    """Its human-facing name."""
    proofs: list[Asserted]
    """What must hold before it is installed, against the recordings it ships."""
    refusals: list[Violation]
    """Everything the two published vocabularies refuse, in one pass."""
    version: str
    """The author's own version of it."""
    vocabulary_version: int
    """The capability vocabulary generation it was held to.

    Carried for the reason every other read under this word carries one: an author
    comparing what they were refused for with what they read needs to know whether
    the difference is their manifest or this build.
    """


class Claiming(typing.TypedDict):
    """One capability a plugin's service declares, and what this build makes of it."""

    filling: typing.NotRequired[Filling | None]
    """What asking for it would come to, or nothing where nothing can ask.

    A namespaced capability has no answer here rather than an empty one: nothing
    consumes it, which is what *inert* means, and reporting it as unfilled would be
    describing a gap where there is a design.
    """
    name: str
    """The capability's name."""
    own: bool
    """Whether it is this plugin's own rather than one from the core vocabulary."""
    probes: list[ProbeRan]
    """Every probe the claim binds, in the order the vocabulary declares them."""
    service: str
    """The service declaring it."""
    shown: Shown
    """How far the claim has been shown."""


type Filling = FillingBy | FillingContested | FillingUnfilled
"""What asking for a capability comes to.

Carried as one word and its subject rather than as three shapes, so a reader of the
machine-readable form branches on `answer` and finds the rest where the word says.
"""


class FillingBy(typing.TypedDict):
    """Exactly one candidate claims it, and it is what a wiring reaches."""

    answer: typing.Literal["by"]
    service: str
    """The service that fills it."""


class FillingContested(typing.TypedDict):
    """More than one does. Refused until the operator chooses, and every one of them
    is named — resolving it by install order, precedence or recency is the thing
    this answer exists instead of.
    """

    answer: typing.Literal["contested"]
    claimants: list[str]
    """Every candidate, named."""


class FillingUnfilled(typing.TypedDict):
    """Nothing installed claims it, or everything that does has been refuted or is
    unproven.
    """

    answer: typing.Literal["unfilled"]


class PluginClaimsEnvelope(typing.TypedDict):
    """The envelope carrying `plugin-claims`."""

    api_version: int
    data: Claimed
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugin-claims"]


class ProbeRan(typing.TypedDict):
    """One probe a claim binds, and what running it against its recording came to."""

    probe: str
    """The probe the vocabulary declares, by name."""
    verdict: PluginVerdict
    """What the recording said about it."""


type Shown = typing.Literal["claimed", "demonstrated", "unproven", "refuted"]
"""How far a claim has been shown.

The four the vocabulary's own states name. `Claimed` is not a weaker
`Demonstrated`: it is what a declaration is before anything has asked the service,
which is a fact about this moment rather than about the service.
"""


Contributed = typing.TypedDict(
    "Contributed",
    {
        "at": str,
        "for": typing.NotRequired[str | None],
        "id": str,
        "says": str,
    },
)
"""One row a plugin adds to a register lemonfiber already runs."""


__all__ = [
    "Asserted",
    "Assertion",
    "Claimed",
    "Claiming",
    "Contributed",
    "Filling",
    "FillingBy",
    "FillingContested",
    "FillingUnfilled",
    "PluginClaimsEnvelope",
    "ProbeRan",
    "Shown",
]
