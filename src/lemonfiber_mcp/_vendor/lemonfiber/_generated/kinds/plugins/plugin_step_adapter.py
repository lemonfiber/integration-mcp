# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `plugins` carries; `kinds.plugins` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .api_kind import (
    ApiKind,
    Contribution,
    PluginAdapterOwner,
    PluginChange,
    PluginChangedCheck,
    PluginDeclaration,
    PluginEvidence,
    PluginFailingAsDeclared,
    PluginOverriding,
    PluginPair,
    PluginPlaced,
)
from ...shared.doctor__error__plugins import StepCame
from ...shared.plugins__undo import UndoReversal


class PluginInstall(typing.TypedDict):
    """What an install came to, and what it took to get there.

    **The three lists below are stated whether the run wrote anything or not, and that
    is the whole of what makes a rehearsal worth running.** A rehearsal that reported
    less than the real run would be a preview of a different operation; one that
    reported it from code of its own would be a second derivation free to disagree
    with the one that acts. So they are filled in one place, from the manifest and from
    the very list of writes the install is carried out from, and the surface says them
    in whichever tense `recorded` calls for.
    """

    against: typing.NotRequired[PluginEvidence | None]
    """What those verdicts were reached against, or nothing where none were reached.

    Carried rather than assumed, because the two kinds of evidence are not the
    same claim: an author's read asks the recordings a plugin ships, and an
    install asks the service running on this machine. The weaker must not be
    readable as the stronger, and a reader handed a verdict has nothing else in
    the document to tell them apart.
    """
    changes: list[PluginChange]
    """Every change it makes to the machine, in the order it makes them."""
    contests: list[WiringContest]
    """Every ask of the stack's the install leaves contested that is not contested
    now, as it would then stand.

    A plugin's service that claims what the stack asks for is a candidate like any
    other, so installing it leaves the ask refused until somebody chooses — which is
    a change to what the stack does, and stated with the rest before it happens.
    """
    overrides: list[PluginOverriding]
    """Every bundled thing the plugin declares it will change.

    The full extent rather than a sample of it: a manifest may change a bundled
    setting only through a recipe, and a recipe reaching one no `[[override]]`
    names is refused before anything is written.
    """
    proofs: list[PluginProving]
    """Every proof that has to hold before the plugin is installed, and on a run
    that asked them, what each came to.
    """
    recipes_ran: list[PluginRecipeRan]
    """Every install recipe the act ran, in order, with what each step came to; an
    empty list where none ran, which is every rehearsal and every plugin declaring no
    install recipe.

    A recipe that did not hold ends the act with a problem carrying the same account,
    so this is the account of recipes that held.
    """
    recorded: bool
    """Whether it was written down. A rehearsal leaves this false."""
    reversed: typing.NotRequired[UndoReversal | None]
    """What putting the install back came to, where something failed and it was.

    The rollback layer's own report rather than a shape of this verb's: what went
    back, and what did not with the reason each is still standing. Absent on a run
    that had nothing to put back, which is both a rehearsal and an install that
    held.
    """
    verified: typing.NotRequired[PluginVerification | None]
    """What the stack's own checks made of the install, or nothing on a run that
    asked them nothing.

    The other half of what an install has to establish, and the half a plugin
    cannot establish for itself: its proofs say the plugin works, and this says the
    stack still does. Absent on a rehearsal, which writes nothing and so has
    nothing to hold a reading against.
    """
    would: PluginInstalled
    """What the install settled, said whether or not it was written down."""


class PluginProving(typing.TypedDict):
    """One proof that has to hold before a plugin is reported installed."""

    asks: str
    """What it asks, as the method and the path it is asked at."""
    came_to: typing.NotRequired[PluginVerdict | None]
    """What asking it came to, or nothing where it was not asked.

    Absent on a rehearsal, which asks nothing. That is a different fact from a
    proof that was asked and established nothing, and the two must not read alike:
    one is an account of what would happen, the other is a service that did not
    answer.
    """
    establishes: str
    """What it establishes, in one line."""
    of: typing.NotRequired[str | None]
    """Which of the plugin's services it asks, where the manifest settles that.

    Nothing where it does not, which is a manifest the reader has already refused
    — carried as an absence rather than as a guess, so that a report built from a
    manifest nobody held to the reader says *this was not settled* instead of
    naming whichever service came first.
    """
    proof: str
    """The proof's id, which its verdict is reported against."""
    why: str
    """Why it is worth asserting."""


class PluginRecipe(typing.TypedDict):
    """One recipe, as an operator agrees to what it does."""

    id: str
    """The recipe's id within the plugin."""
    pairs: list[PluginPair]
    """Every value it could carry, and where to."""
    steps: list[PluginStep]
    """Every call, in the order the recipe makes them."""
    title: str
    """What it accomplishes, in one line."""
    why: str
    """Why it is worth running."""


class PluginRecipeRan(typing.TypedDict):
    """What one recipe came to."""

    held: bool
    """Whether every step it made came to what it should."""
    recipe: str
    """The recipe's id."""
    steps: list[PluginStepRan]
    """Every step it declares, in order, with what each came to."""
    why: typing.NotRequired[str | None]
    """Why it did not, where it did not."""


class PluginRemoval(typing.TypedDict):
    """What taking a plugin off the machine came to, or would come to."""

    interrupts: list[str]
    """Every service that stops when it goes, named before any of them does.

    By service rather than by plugin, because a service is what an operator notices
    stopping: a plugin that brought two containers takes two things away, and the
    plugin's name alone would not say which of the addresses they use goes quiet.
    None of them comes back — a removal is not a restart — which is why this is
    stated before the run rather than discovered after it.
    """
    leaves: list[PluginUnfilled]
    """Every capability that would have nothing filling it afterwards.

    Stated before it happens rather than reported after, which is the requirement
    and also the only useful order: an operator told afterwards that their requests
    no longer reach anything has been informed rather than asked.
    """
    plugin: str
    """The plugin this is about."""
    removed: bool
    """Whether the record of what is installed was written without it.

    False on a rehearsal and on a run that got as far as putting the files back and
    no further, which are two different machines and are told apart by what the
    reversal says rather than by a second flag here.
    """
    went_back: UndoReversal
    """What putting its changes back came to, or would come to.

    The rollback layer's own report rather than a shape of this verb's: a removal is
    a reversal with a name on it, and an account of its own would be a second
    description of the same work.
    """


class PluginRestored(typing.TypedDict):
    """Where an update did not hold: what putting the version it replaced back came to."""

    placed: bool
    """Whether everything its record says it placed is on the machine again."""
    running: bool
    """Whether its containers are running again.

    Apart from `placed`, because the two fail differently: a document that would not
    land is a disk, and a container that would not start is the engine — and an
    operator fixes them in different places.
    """
    version: str
    """The version put back, which is the one the record still names."""


class PluginServiceAdapter(typing.TypedDict):
    """One adapter of lemonfiber's that one of the plugin's own services names."""

    kind: ApiKind
    """Which of lemonfiber's adapters it is."""
    owner: PluginAdapterOwner
    """Whose it is, which is lemonfiber's."""
    service: str
    """The service that names it."""


type PluginSourceStanding = (
    PluginSourceStandingReachable | PluginSourceStandingUnreachable | PluginSourceStandingUnasked
)
"""What asking a plugin's source came to.

**Unreachable is not untrusted.** A plugin whose source has gone keeps running as it
was installed; what it loses is the way to a newer version, and that is said now
rather than found out at the next update.
"""


class PluginSourceStandingReachable(typing.TypedDict):
    """It answered, so the plugin can be updated from it."""

    standing: typing.Literal["reachable"]


class PluginSourceStandingUnasked(typing.TypedDict):
    """Nothing was asked, so nothing is known either way."""

    standing: typing.Literal["unasked"]
    why: str
    """Why nothing was asked."""


class PluginSourceStandingUnreachable(typing.TypedDict):
    """It did not answer, or is no longer there, so the plugin cannot be updated from it."""

    standing: typing.Literal["unreachable"]
    why: str
    """What asking it said."""


class PluginStep(typing.TypedDict):
    """One call a recipe makes, in the order it makes them."""

    adapter: typing.NotRequired[PluginStepAdapter | None]
    """The adapter the destination is reached through, or nothing where it is a name
    outside the stack, which no adapter of lemonfiber's speaks to.
    """
    id: str
    """The step's id within its recipe."""
    method: str
    """The HTTP method it calls with."""
    path: str
    """The path it calls."""
    to: str
    """Where it calls: a service of this stack's or the plugin's own, or a name outside
    both, as the manifest wrote it. Never a resolved address.
    """


class PluginStepAdapter(typing.TypedDict):
    """The adapter a call reaches its destination through."""

    kind: ApiKind
    """Which of lemonfiber's adapters it is."""
    owner: PluginAdapterOwner
    """Whose it is, which is lemonfiber's."""


class PluginStepRan(typing.TypedDict):
    """What one step came to."""

    came: StepCame
    """What it came to."""
    landed: bool
    """Whether it reached somewhere other than this plugin's own services, which an
    install going back cannot undo.
    """
    status: typing.NotRequired[int | None]
    """The status its last answer carried, where anything answered."""
    step: str
    """The step's id."""
    to: str
    """Where it calls, by the name the manifest gives it."""
    tries: int
    """How many times it was made."""
    why: typing.NotRequired[str | None]
    """Why it came to what it did, where that wants saying."""


class PluginSubstituted(typing.TypedDict):
    """A capability the operator chose one of a plugin's services to fill.

    The only way anything a plugin brought comes to fill what the stack asks for in
    place of the stack's own: a plugin cannot choose, and wiring by name is not
    something a plugin can introduce. So what a plugin substituted is what the operator
    substituted with it, and it is read off the recorded choices rather than off the
    plugin.
    """

    capability: str
    """The capability it fills."""
    plugin: str
    """The plugin whose service it is."""
    service: str
    """The service chosen."""


class PluginUnfilled(typing.TypedDict):
    """A capability that would have nothing filling it."""

    capability: str
    """The core name nothing would fill."""
    filled_by: str
    """The plugin that is filling it now, which is the one going.

    Named rather than left to the reader, because the sentence an operator has to
    act on is *this is the only thing filling it* and a capability on its own does
    not say that.
    """


type PluginVerdict = (
    PluginVerdictPassed | PluginVerdictFailed | PluginVerdictUnproven | PluginVerdictFailingAsDeclared
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


class PluginVerdictPassed(typing.TypedDict):
    """The recording answers what the binding declares."""

    outcome: typing.Literal["passed"]


class PluginVerdictUnproven(typing.TypedDict):
    """It could not be run, and so established nothing either way."""

    outcome: typing.Literal["unproven"]
    why: str
    """What stopped it being run."""


class PluginVerification(typing.TypedDict):
    """What the stack's own checks made of an install."""

    broke: list[PluginChangedCheck]
    """Every check this install made worse.

    Empty is the answer an install needs, and it is the common one. What is here
    is what takes the install back.
    """
    unsettled: list[PluginChangedCheck]
    """Every check nothing could be concluded about across the two readings.

    Reported and never acted on. *I could not tell* is not *it is still broken*,
    and an install reversed because a check could not reach a provider it also
    could not reach an hour ago would be punishing a plugin for the weather. It is
    said out loud rather than dropped, because the assurance an operator thought
    they had is the thing that went.
    """


class WiringContest(typing.TypedDict):
    """An ask several services claim and nothing has chosen between, so it reaches
    nothing.
    """

    by: str
    """The service that asked."""
    capability: str
    """What it asked for."""
    claimants: list[str]
    """Every claimant, named — a plugin's with the plugin beside it."""


PluginInstalled = typing.TypedDict(
    "PluginInstalled",
    {
        "adapters": typing.NotRequired[list[PluginServiceAdapter]],
        "contributions": typing.NotRequired[list[Contribution]],
        "declared": typing.NotRequired[PluginDeclaration],
        "description": typing.NotRequired[str | None],
        "from": typing.NotRequired[str],
        "installed_at": typing.NotRequired[str],
        "name": typing.NotRequired[str | None],
        "plugin": str,
        "provides": typing.NotRequired[list[str]],
        "recipes": typing.NotRequired[list[PluginRecipe]],
        "revision": typing.NotRequired[str],
        "services": list[PluginPlaced],
        "signed": typing.NotRequired[str],
        "version": str,
    },
)
"""One plugin's install, as it was decided."""


PluginSource = typing.TypedDict(
    "PluginSource",
    {
        "from": str,
        "plugin": str,
        "standing": PluginSourceStanding,
    },
)
"""Whether one installed plugin's source can still be fetched."""


PluginUpdate = typing.TypedDict(
    "PluginUpdate",
    {
        "from": str,
        "install": PluginInstall,
        "interrupts": list[str],
        "plugin": str,
        "restored": typing.NotRequired[PluginRestored | None],
        "stopped": typing.NotRequired[str | None],
        "to": str,
        "went_back": UndoReversal,
    },
)
"""What updating a plugin came to, or would come to, as one account.

**One account, because it is one operation.** An update is the version installed
going back and another coming on, and a report that gave those as a removal and an
install side by side would invite reading them as two things that might each have
happened. What an operator has to be able to read off this is which version the
machine is on, and there are exactly two answers: the new one, where
`install.recorded` is true, or the one it replaced, which `restored` says the state
of.
"""


__all__ = [
    "PluginInstall",
    "PluginInstalled",
    "PluginProving",
    "PluginRecipe",
    "PluginRecipeRan",
    "PluginRemoval",
    "PluginRestored",
    "PluginServiceAdapter",
    "PluginSource",
    "PluginSourceStanding",
    "PluginSourceStandingReachable",
    "PluginSourceStandingUnasked",
    "PluginSourceStandingUnreachable",
    "PluginStep",
    "PluginStepAdapter",
    "PluginStepRan",
    "PluginSubstituted",
    "PluginUnfilled",
    "PluginUpdate",
    "PluginVerdict",
    "PluginVerdictFailed",
    "PluginVerdictFailingAsDeclared",
    "PluginVerdictPassed",
    "PluginVerdictUnproven",
    "PluginVerification",
    "WiringContest",
]
