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
    PluginChangedCheck,
    PluginConstraint,
    PluginDeclaration,
    PluginRecipe,
    PluginRequest,
)
from ...shared.plugins__undo import PluginGrant


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


class PluginPlaced(typing.TypedDict):
    """One service of an installed plugin, as it was placed."""

    api: typing.NotRequired[Api | None]
    """The adapter of lemonfiber's its manifest names, which only a part the bundle
    assembles is reached through. A record read from the register holds none, whatever
    an older one carried: an installed plugin is reached over the contracts it speaks.
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
    """The line its dashboard entry shows beside it: the one its wiring names, or what
    the plugin says it does for the operator.
    """
    digest: str
    """The digest that fixes what runs."""
    fields: typing.NotRequired[ServiceFields]
    """Its container fields beyond those above."""
    fronts: typing.NotRequired[str | None]
    """The service of the same plugin it stands in front of, as an adapter."""
    health: typing.NotRequired[str | None]
    """The path it answers over HTTP to say it is up, where its health is asked that way."""
    hidden: typing.NotRequired[bool]
    """Whether its wiring hid it from the dashboard."""
    icon: typing.NotRequired[str | None]
    """The icon its dashboard entry shows, where its wiring names one."""
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
    """Networks an older record named for it. Nothing reads them: each service's place on
    the networks is derived with the project, and a record written now holds none.
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
    upstream: typing.NotRequired[dict[str, str]]
    """Each field of the `upstream.json` lemonfiber writes for it as an adapter, to the
    id of the plugin's secret that field holds.
    """


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


type PluginReached = PluginReachedLoopback | PluginReachedHousehold
"""How an installed service is reached, where it is reached at all.

The tier is the arm, so the label a tier earns lives only in the arm entitled to
one. Only a household service is proxied — the bundled policy is that an admin
surface does not get a name on the household network — and a record able to carry
a loopback service with a hostname would be a record able to describe the thing
that policy exists to prevent.

**The group is on both arms, and that is not an oversight.** Only the proxy is
the household tier's alone; the bundled dashboard carries an entry for an
operator surface too, with the address it links to rendered from the tier — nine
of the shipped stack's own entries point at this machine. A record that kept the
group for the wider tier alone would leave a loopback service off the panel its
bundled neighbours are on.

A tier and never an address, either way: lemonfiber renders one from the other
exactly as it does for a bundled service, so the two-tier policy stays a property
of the system rather than a request a plugin made.
"""


class PluginReachedHousehold(typing.TypedDict):
    """From the household, through the stack's own proxy, at this label."""

    group: typing.NotRequired[str | None]
    """The group on the bundled dashboard, where the manifest named one."""
    hostname: str
    """The single label in front of the operator's domain."""
    port: int
    """The port the service listens on."""
    tier: typing.Literal["household"]


class PluginReachedLoopback(typing.TypedDict):
    """From this machine and nowhere else. No route, and no label to route to."""

    group: typing.NotRequired[str | None]
    """The group on the bundled dashboard, where the manifest named one."""
    port: int
    """The port the service listens on."""
    tier: typing.Literal["loopback"]


class PluginRequestProof(typing.TypedDict):
    """One proof that asks one of the plugin's services a question, kept so the doctor can ask
    it again without the plugin's source.
    """

    expect: Expect
    """What the answer must be."""
    proof: str
    """The proof's id."""
    request: PluginRequest
    """What it asks."""
    service: str
    """The service it asks."""
    title: str
    """What it establishes, in one line."""
    why: str
    """Why it is worth asserting."""


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


type PluginShape = typing.Literal["egress-guard", "render"]
"""A privileged shape lemonfiber writes for a service."""


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


type ServiceConstant = str | int | bool
"""A value written exactly as declared."""


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


class ServiceNetwork(typing.TypedDict):
    """The network a service runs inside instead of its own."""

    via: str
    """The capability whose filler's network it runs inside."""


type ServicePosture = typing.Literal["standard", "confined"]
"""How tightly the container is held."""


class ServicePublish(typing.TypedDict):
    """A further port a service publishes on its tier."""

    listens: typing.NotRequired[int | None]
    """Where it answers inside the container, `port` where absent."""
    port: int
    """Where it is published on the host."""


class ServiceSecretOf(typing.TypedDict):
    """A secret the manifest declares."""

    secret: str
    """The declared secret's name."""


class ServiceSetting(typing.TypedDict):
    """An operator setting, with what is written while none is recorded."""

    default: ServiceConstant
    """What is written while the operator has recorded no value."""
    setting: str
    """The setting's name."""


class ServiceUrlOf(typing.TypedDict):
    """The address of a capability's filler."""

    files: typing.NotRequired[str | None]
    """The medium the filler asked for files."""
    native: typing.NotRequired[str | None]
    """The upstream's own API, where the ask reaches the upstream an adapter fronts."""
    url_of: str
    """The capability asked for."""


type ServiceUserMode = typing.Literal["image", "puid-env", "uid"]
"""Who the container runs as."""


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


PluginGranting = typing.TypedDict(
    "PluginGranting",
    {
        "approval": str,
        "credential": str,
        "for": str,
        "of": str,
    },
)
"""One credential that would cross to a plugin, as the reading states it."""


PluginInstalled = typing.TypedDict(
    "PluginInstalled",
    {
        "adapters": typing.NotRequired[list[PluginServiceAdapter]],
        "contributions": typing.NotRequired[list[Contribution]],
        "declared": typing.NotRequired[PluginDeclaration],
        "description": typing.NotRequired[str | None],
        "from": typing.NotRequired[str],
        "granted": typing.NotRequired[list[PluginGrant]],
        "installed_at": typing.NotRequired[str],
        "manifest": typing.NotRequired[str],
        "name": typing.NotRequired[str | None],
        "plugin": str,
        "provides": typing.NotRequired[list[str]],
        "recipes": typing.NotRequired[list[PluginRecipe]],
        "request_proofs": typing.NotRequired[list[PluginRequestProof]],
        "revision": typing.NotRequired[str],
        "run_proofs": typing.NotRequired[list[PluginRunProof]],
        "services": list[PluginPlaced],
        "signed": typing.NotRequired[str],
        "tree": typing.NotRequired[str],
        "version": str,
    },
)
"""One plugin's install, as it was decided."""


ServiceMount = typing.TypedDict(
    "ServiceMount",
    {
        "from": str,
        "ro": typing.NotRequired[bool],
        "to": str,
    },
)
"""A further path mounted from the service's own mount tree."""


__all__ = [
    "PluginEvidence",
    "PluginFailingAsDeclared",
    "PluginGranting",
    "PluginInstalled",
    "PluginPlaced",
    "PluginProving",
    "PluginReached",
    "PluginReachedHousehold",
    "PluginReachedLoopback",
    "PluginRequestProof",
    "PluginRun",
    "PluginRunProof",
    "PluginServiceAdapter",
    "PluginShape",
    "PluginTaking",
    "PluginVerdict",
    "PluginVerdictFailed",
    "PluginVerdictFailingAsDeclared",
    "PluginVerdictPassed",
    "PluginVerdictUnproven",
    "PluginVerification",
    "ServiceConstant",
    "ServiceFields",
    "ServiceMount",
    "ServiceNetwork",
    "ServicePosture",
    "ServicePublish",
    "ServiceSecretOf",
    "ServiceSetting",
    "ServiceUrlOf",
    "ServiceUserMode",
    "ServiceValue",
    "WiringContest",
]
