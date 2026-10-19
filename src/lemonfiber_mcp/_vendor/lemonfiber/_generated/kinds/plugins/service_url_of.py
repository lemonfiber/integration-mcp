# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `plugins` carries; `kinds.plugins` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .api_kind import (
    Api,
    ApiKind,
    Contribution,
    Expect,
    PluginAdapterOwner,
    PluginAsking,
    PluginChange,
    PluginChangedCheck,
    PluginDeclaration,
    PluginEvidence,
    PluginFailingAsDeclared,
    PluginOverriding,
    PluginReached,
    PluginShape,
    ServiceConstant,
    ServiceMount,
    ServiceNetwork,
    ServicePosture,
    ServicePublish,
    ServiceSecretOf,
    ServiceSetting,
    ServiceUserMode,
)
from ...shared.doctor__error__plugins import StepCame
from ...shared.plugins__undo import UndoReversal
from ...shared.plugins__wiring import Wired


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
    asks: list[Wired]
    """Every ask its services would make, each with what it would reach and how that
    would be settled.
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
    taking: list[PluginTaking]
    """Every service taking a privileged shape, with what it is given, each approved
    apart from the offer.
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


class PluginPlaced(typing.TypedDict):
    """One service of an installed plugin, as it was placed."""

    api: typing.NotRequired[Api | None]
    """The adapter lemonfiber reaches it through, where the plugin named one.

    Defaulted for a record written before this was kept, which reads as naming
    none: a service operated generically, as it was when installed.
    """
    asks: typing.NotRequired[list[PluginAsking]]
    """Every capability it asks for."""
    asks_for: typing.NotRequired[str | None]
    """What it asks for there, where it says."""
    config_path: str
    """Where inside the container its one configuration directory is mounted.

    Resolved rather than optional. The record answers where the directory is, and
    a run that re-derived the fallback would answer for a container it did not
    write the day that fallback moved.
    """
    description: typing.NotRequired[str]
    """What the plugin says it does for the operator, which is what its dashboard entry
    says beside it.
    """
    digest: str
    """The digest that fixes what runs."""
    fields: typing.NotRequired[ServiceFields]
    """Its container fields beyond those above."""
    fronts: typing.NotRequired[str | None]
    """The service of the same plugin it stands in front of, as an adapter."""
    image: str
    """The registry path, carrying no pin of its own."""
    listens: typing.NotRequired[int | None]
    """The port it answers on inside the stack's network, where it declared one."""
    media_types: typing.NotRequired[list[str]]
    """The media it files, in the stack manifest's vocabulary, which decides what it
    comes to in each service that asks for what it provides; none in an older record.
    """
    name: typing.NotRequired[str]
    """What it is called, for a reader, which is what its dashboard entry is listed as;
    a record written before this was kept lists it by its id.
    """
    native: typing.NotRequired[str | None]
    """The API it answers the stack's other services in, where it names one."""
    networks: typing.NotRequired[list[str]]
    """The stack's own networks it joins beside the default one, because a stack service
    it stands in for is on them.

    Settled at install from the stack it was installed beside and written down, so
    the container lemonfiber writes for it stays a function of this record alone.
    Defaulted for a record written before this was kept, which reads as joining none
    and staying on the default network.
    """
    provides: typing.NotRequired[list[str]]
    """Every core capability this one service fills, which is what makes it a candidate
    when the stack asks for one.

    Per service rather than read off the plugin's whole list, because a wiring
    reaches a service and not a plugin: of a plugin's two services, the one that
    fills a capability is the one an ask for it would reach. Defaulted for a record
    written before this was kept, which reads as filling nothing — a service nothing
    is wired to, rather than one wired to on a guess.
    """
    reached: typing.NotRequired[PluginReached | None]
    """How it is reached, or nothing where it has no listener."""
    reaches: typing.NotRequired[str | None]
    """Where it reaches outside the machine, where it says."""
    replaces: typing.NotRequired[str | None]
    """The stack's own service it moves in place of, where it names one."""
    service: str
    """The service's id, which is the name its container is written under."""
    shape: typing.NotRequired[PluginShape | None]
    """The privileged shape lemonfiber writes for it, where it took one."""
    speaks: typing.NotRequired[list[str]]
    """Each capability contract it answers as an adapter, as `capability@major`."""
    starting: typing.NotRequired[str | None]
    """The digest of the starting files kept for its run proofs, where it has any."""
    tag: str
    """The readable name that digest went by when it was installed."""
    takes_data: bool
    """Whether the library is mounted for it."""


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


class PluginRun(typing.TypedDict):
    """A run of the image's own program, as a proof declares it."""

    args: list[str]
    """Each argument handed to the image's entrypoint, one string each: one to 64, each at
    most 4096 bytes and none holding a NUL.
    """
    timeout_s: typing.NotRequired[int | None]
    """How long the run may take, from 1 to 120 seconds. Default 30."""


class PluginRunProof(typing.TypedDict):
    """One proof that runs the image's own program, kept so the doctor and a later proof can
    run it again without the plugin's source.
    """

    expect: Expect
    """What the run must come to."""
    proof: str
    """The proof's id."""
    run: PluginRun
    """What the image's own program is handed."""
    service: str
    """The service whose image it runs."""
    title: str
    """What it establishes, in one line."""
    why: str
    """Why it is worth asserting."""


class PluginServiceAdapter(typing.TypedDict):
    """One adapter of lemonfiber's that one of the plugin's own services names."""

    kind: ApiKind
    """Which of lemonfiber's adapters it is."""
    owner: PluginAdapterOwner
    """Whose it is, which is lemonfiber's."""
    service: str
    """The service that names it."""


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


class PluginTaking(typing.TypedDict):
    """One service taking a privileged shape, as the reading states it."""

    approval: str
    """What approving it is written as, apart from the offer."""
    devices: list[str]
    """The devices it is given."""
    grants: list[str]
    """The kernel capabilities it is given."""
    service: str
    """The service taking it."""
    shape: PluginShape
    """The shape it takes."""


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


class ServiceFields(typing.TypedDict):
    """The container fields an install record keeps for a service, beyond those every
    record already holds.
    """

    config_ro: typing.NotRequired[bool]
    """Whether its configuration directory is read-only."""
    env: typing.NotRequired[dict[str, ServiceValue]]
    """Its environment."""
    mem_limit_mib: typing.NotRequired[int | None]
    """Its memory ceiling."""
    mount: typing.NotRequired[list[ServiceMount]]
    """Its further mounts."""
    network: typing.NotRequired[ServiceNetwork | None]
    """The network it runs inside."""
    posture: typing.NotRequired[ServicePosture]
    """How tightly it is held."""
    publish: typing.NotRequired[list[ServicePublish]]
    """Its further published ports."""
    tmpfs: typing.NotRequired[list[str]]
    """Its scratch paths in memory."""
    user_mode: typing.NotRequired[ServiceUserMode | None]
    """Who it runs as, where declared."""


class ServiceUrlOf(typing.TypedDict):
    """The address of a capability's filler."""

    files: typing.NotRequired[str | None]
    """The medium the filler asked for files."""
    native: typing.NotRequired[str | None]
    """The upstream's own API, where the ask reaches the upstream an adapter fronts."""
    url_of: str
    """The capability asked for."""


type ServiceValue = ServiceConstant | ServiceSetting | ServiceUrlOf | ServiceSecretOf
"""One environment variable's value."""


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
        "manifest": typing.NotRequired[str],
        "name": typing.NotRequired[str | None],
        "plugin": str,
        "provides": typing.NotRequired[list[str]],
        "recipes": typing.NotRequired[list[PluginRecipe]],
        "revision": typing.NotRequired[str],
        "run_proofs": typing.NotRequired[list[PluginRunProof]],
        "services": list[PluginPlaced],
        "signed": typing.NotRequired[str],
        "version": str,
    },
)
"""One plugin's install, as it was decided."""


PluginPair = typing.TypedDict(
    "PluginPair",
    {
        "approval": typing.NotRequired[str],
        "from": typing.NotRequired[str],
        "origin": str,
        "release": typing.NotRequired[str],
        "to": str,
        "value": str,
    },
)
"""One value a recipe could carry to one destination, as the operator agrees to it."""


__all__ = [
    "PluginInstall",
    "PluginInstalled",
    "PluginPair",
    "PluginPlaced",
    "PluginProving",
    "PluginRecipe",
    "PluginRecipeRan",
    "PluginRun",
    "PluginRunProof",
    "PluginServiceAdapter",
    "PluginStep",
    "PluginStepAdapter",
    "PluginStepRan",
    "PluginTaking",
    "PluginVerdict",
    "PluginVerdictFailed",
    "PluginVerdictFailingAsDeclared",
    "PluginVerdictPassed",
    "PluginVerdictUnproven",
    "PluginVerification",
    "ServiceFields",
    "ServiceUrlOf",
    "ServiceValue",
    "WiringContest",
]
