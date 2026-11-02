# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `plugins` carries; `kinds.plugins` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ...shared.doctor__error__plugins import StepCame
from ...shared.doctor__plugins import DoctorVerdict, Finding


type ApiKind = typing.Literal[
    "servarr",
    "sabnzbd",
    "qbittorrent",
    "seerr",
    "bindery",
    "jellyfin",
    "bazarr",
    "audiobookshelf",
    "nzbhydra2",
]
"""The API shapes lemonfiber knows how to speak.

Four services share the `servarr` shape, which is what makes one client
enough for them. Bindery is its own kind deliberately: it is not a Servarr
application and Prowlarr's app sync does not reach it. Bazarr is its own for
the neighbouring reason: it is told about the \\*arrs rather than being one of
them, in a form body a client of the shared shape could not send.
"""


class Expect(typing.TypedDict):
    """What the answer has to be.

    A status is a claim about the network path rather than about the service: Docker
    publishes a port by putting a proxy in front of it, and that proxy accepts a
    connection before knowing whether anything inside is listening. So a status alone
    is not evidence — except for a refusal or a redirect to HTTPS, answers no port proxy
    produces.

    **A key of the four key-wise constraints is a place rather than a name.** A plain
    name is a top-level member, and one beginning with `/` is a JSON Pointer, extended
    with a step that picks an entry of a list by a field it holds. A flat name was enough while every service answered a flat object, and the
    only thing it could say about a service that nests its payload was that the envelope
    was there — which is a probe that passes by observing that something replied.
    """

    body_starts_with: typing.NotRequired[str | None]
    """What the body must begin with, where it is not JSON."""
    content_type: typing.NotRequired[str | None]
    """A substring of the content type the answer was served as."""
    exit: typing.NotRequired[int | None]
    """The exit status a run must end with. Not sufficient alone."""
    json: typing.NotRequired[dict[str, Expected] | None]
    """Places the answer must carry, each with the exact value it must hold."""
    json_array_min: typing.NotRequired[int | None]
    """The answer read as an array, with at least this many entries.

    A catalogue is very often a list rather than an object, and none of the
    object-shaped constraints can say anything about one.
    """
    json_at_least: typing.NotRequired[dict[str, int] | None]
    """Places the answer must carry, each with a number it must not be below."""
    json_has_keys: typing.NotRequired[list[str] | None]
    """Places the answer must carry, whatever they hold."""
    json_is_absent: typing.NotRequired[bool | None]
    """The answer did not parse as JSON at all.

    Which is what a service that serves its application shell for every path it does
    not implement answers — and the reason a status alone proves nothing against
    one: the shell comes back `200` whether the API behind it exists or not, so what
    has to be said is that the body was *not* a document.
    """
    json_types: typing.NotRequired[dict[str, ExpectedKind] | None]
    """Places the answer must carry, each with the kind of value it must be."""
    status: typing.NotRequired[int | None]
    """The status the answer must carry."""
    stdout_starts_with: typing.NotRequired[str | None]
    """What a run's standard output must begin with."""


type Expected = bool | int | str
"""Exactly what a place must hold.

Three kinds and no nesting: a flag that must be set, a number that must match, or a
word. A value deeper than this is asking about a document rather than about a claim
— and where the thing worth asserting is deeper *in* the answer, the key reaches it
rather than the value growing to match.
"""


type ExpectedKind = typing.Literal["bool", "int", "str", "list", "dict"]
"""The kind of value a key must hold.

Five, and closed. A name outside them is one no runner could evaluate, and an
assertion nothing evaluates is a proof that silently checks less than it says —
which is worse than one that fails.

Named for what it is the kind *of*, rather than `Kind`, because this is published
and whoever generates from it flattens every definition into one scope. `Kind` is
the one name there a generator is certain to want for itself: every envelope this
contract describes is keyed by its `kind`, so the union of them is a `Kind` too, and
two of them in one module is a definition nothing can be compiled against.
"""


type PluginAdapterOwner = typing.Literal["lemonfiber"]
"""Whose an adapter is.

One answer, and the field exists so that the answer is on the wire: an adapter a
plugin could bring would be code a stranger wrote running with lemonfiber's
authority, which nothing here can load.
"""


class PluginAsking(typing.TypedDict):
    """One capability a placed service asks for."""

    capability: str
    """The core capability asked for."""
    each: typing.NotRequired[bool]
    """Whether every service that fills it is reached rather than one."""
    native: typing.NotRequired[str | None]
    """The upstream's own API it talks in, which it reaches in place of the adapter."""


class PluginChange(typing.TypedDict):
    """One change installing a plugin makes to the machine.

    A path and what goes at it, which is the whole of what an install touches. None is an
    edit to a file the stack already has: a plugin's route is the proxy's routing table
    and its dashboard entry the panel list's, each applied over its contract.
    """

    path: str
    """Where it lands, in full.

    In full rather than relative to the stack, because *what is this about to do
    to my machine* is answered by a path somebody can go and look at — and a
    relative one is right about a directory the reader has to work out for
    themselves.
    """
    puts: PluginPuts
    """What lands there."""


class PluginChangedCheck(typing.TypedDict):
    """One check that stands differently after an install than it did before."""

    before: typing.NotRequired[DoctorVerdict | None]
    """How the same check read before the install, or nothing where it was not
    raised at all.

    Absent means the check produced no finding beforehand, which is read as it
    holding: a finding no longer raised is a fault no longer there, and the same
    rule read backwards is that one not yet raised was not yet a fault.
    """
    now: Finding
    """The check as it reads now, with everything the diagnosis says about it.

    The finding itself rather than a summary of it, because what an operator does
    next is read the remedy, the service's own output and what else is causing it
    — and a second, thinner shape of the same fact is where those stop arriving.
    """


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


class PluginDeclaration(typing.TypedDict):
    """What a plugin declared about itself, as its install read it."""

    claims: typing.NotRequired[list[str]]
    """Every capability it claims, core and its own, in the order it declares them.

    Apart from what its services fill: a claim is what it says it can do and has to
    demonstrate, and a capability of its own is claimed without anything asking for
    it.
    """
    license: typing.NotRequired[str]
    """The licence it is distributed under."""
    overrides: typing.NotRequired[list[PluginOverriding]]
    """Every bundled setting it declares it may change."""
    reaches: typing.NotRequired[list[str]]
    """Every destination a recipe of its could reach that is not one of its own
    services: a service of this stack's, or a name outside it.

    Recorded as declared rather than sorted into the two here, because which names
    are this stack's is a question about the stack, and the stack a record is read
    against is the one on the machine when it is read.
    """
    reviewed: typing.NotRequired[bool]
    """Whether anybody reviewed it before it was installed.

    True for a plugin installed by name through a catalogue index whose signature
    verified, and false for every install from a source an operator named. Carried
    rather than left implicit, because an unreviewed plugin is to be said to be one
    for as long as it is installed.
    """
    secrets: typing.NotRequired[list[PluginSecret]]
    """Every credential it says it will hold."""
    upstream: typing.NotRequired[str]
    """Where its source is published, as the plugin names it."""


type PluginDeclaredVerdict = typing.Literal["fails"]
"""The one verdict a declaration may name."""


class PluginDemand(typing.TypedDict):
    """What asking for one of an installed plugin's demand recipes came to."""

    plugin: str
    """The plugin whose recipe it is."""
    ran: typing.NotRequired[PluginRecipeRan | None]
    """What running it came to, or nothing where it was only read."""
    recipe: PluginRecipe
    """The recipe as the operator agrees to it: its calls, what it asks for, and every
    value it would carry where.
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


class PluginExpectedFailure(typing.TypedDict):
    """A recording an assertion fails on, the one constraint of its expectation that fails
    there, and why.

    For an assertion whose passing state nobody can record, such as a check that a server
    has an owner where claiming one needs an account the plugin's CI does not hold: the
    state it exists to find can be recorded, and the declaration says which constraint
    tells the two states apart. It changes the verdict on that recording and on nothing
    else — the live service and every other recording are held to the expectation as it
    is written.

    It names a constraint rather than only a recording, because a recording that began
    failing for another reason — a truncated file, an error recorded by mistake — would
    otherwise read as failing as declared, excusing a failure nobody had looked at.
    """

    constraint: PluginConstraint
    """The key of the expectation that fails on the recording, and one it carries."""
    fixture: str
    """The recording the assertion fails on. It may be the assertion's own `fixture`."""
    place: typing.NotRequired[str | None]
    """Where within that constraint it fails, written exactly as the expectation writes
    it. Present for a key-wise constraint and absent for one about the whole answer.
    """
    reason: str
    """Why this recording is one the assertion fails on. Reported with the verdict every
    time.
    """
    verdict: PluginDeclaredVerdict
    """`fails`, and nothing else: passing is what the expectation already says, and
    could-not-run is never excused.
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


class PluginOverriding(typing.TypedDict):
    """One bundled thing a plugin declares it will change."""

    setting: str
    """Which bundled setting it changes."""
    why: str
    """What changing it is for."""


type PluginPuts = typing.Literal["directory", "document", "key", "secrets", "starting", "upstream"]
"""What an install puts at one path."""


class PluginRecipe(typing.TypedDict):
    """One recipe, as an operator agrees to what it does."""

    id: str
    """The recipe's id within the plugin."""
    inputs: typing.NotRequired[list[PluginRecipeInput]]
    """Every value it asks the operator for when it runs, in the order it declares them."""
    on: typing.NotRequired[PluginRecipeOn]
    """When it runs: as part of an install and an update, or only when asked for by name."""
    pairs: list[PluginPair]
    """Every value it could carry, and where to."""
    steps: list[PluginStep]
    """Every call, in the order the recipe makes them."""
    title: str
    """What it accomplishes, in one line."""
    why: str
    """Why it is worth running."""


class PluginRecipeInput(typing.TypedDict):
    """One value a recipe asks the operator for when it runs.

    Never the value: a reading says what will be asked, and what is given for it is
    handed to the recipe and said back by nothing.
    """

    ask: str
    """What the operator is asked for it."""
    name: str
    """What the input is called, which is what a value is given for it under."""
    secret: bool
    """Whether the value may be a secret, so a surface takes it without showing it."""


type PluginRecipeOn = typing.Literal["install", "demand"]
"""When a recipe runs."""


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


class PluginRequest(typing.TypedDict):
    """What is asked, and where.

    Three fields and no more, and the third is the one worth explaining. A service that
    answers XML unless a caller asks for JSON cannot satisfy a capability whose probe
    requires a JSON assertion, and until this field there was nowhere to ask: Plex
    answers `text/xml` at every path, including the one its health probe uses, unless
    the request carries `Accept: application/json`.

    **It is one media type and not a header map, and the difference is the point.** A
    probe declares who it is asked as, and `none` on every `guarded` probe has meant what
    it says partly because nothing could be presented. A map of headers would make that a
    convention a reviewer has to hold — any service may name its credential header
    whatever it likes, so no list of refused names could ever be closed — where one named
    field keeps it a property of the format. A probe still cannot present anything,
    because there is nowhere to write it.
    """

    accept: typing.NotRequired[str | None]
    """The one representation the answer is asked for, as a media type.

    Absent where the service needs no asking, which is most of them.
    """
    method: str
    """The HTTP method."""
    path: str
    """The path on the service being asked."""
    varies: typing.NotRequired[dict[str, str]]
    """Each place in the answer whose value the service makes afresh on every run, a JSON
    Pointer into its JSON, to the RE2 shape the whole value there is held to wherever a
    recording is taken again. Never sent.
    """


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


type ServiceConstant = str | int | bool
"""A value written exactly as declared."""


Contribution = typing.TypedDict(
    "Contribution",
    {
        "action": typing.NotRequired[str | None],
        "at": str,
        "category": typing.NotRequired[str | None],
        "detail": typing.NotRequired[str | None],
        "expect": typing.NotRequired[Expect | None],
        "expected": typing.NotRequired[list[PluginExpectedFailure]],
        "fixture": typing.NotRequired[str | None],
        "for": typing.NotRequired[str | None],
        "id": str,
        "request": typing.NotRequired[PluginRequest | None],
        "service": typing.NotRequired[str | None],
        "timeout_s": typing.NotRequired[int | None],
        "title": typing.NotRequired[str | None],
        "why": typing.NotRequired[str | None],
    },
)
"""A row in a register lemonfiber already runs.

The fields beyond `at` and `id` are the row its point declares, and the point is
published — so the required set, the optional set, the closed sets and the bounds
are read from `extension-points.json` rather than restated here. What this type
fixes is that a contribution is declared in this block and nowhere else, and that
it carries nothing outside the union of the rows the published points take.
"""


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


PluginSecret = typing.TypedDict(
    "PluginSecret",
    {
        "for": typing.NotRequired[str | None],
        "id": str,
        "lapses_s": typing.NotRequired[int | None],
        "minted": typing.NotRequired[bool],
        "needed_to_start": typing.NotRequired[bool],
        "needs": typing.NotRequired[dict[str, list[ServiceConstant]]],
        "of": str,
        "was": typing.NotRequired[str | None],
        "why": str,
    },
)
"""One credential a plugin says it will hold, without a value and with no place for one."""


__all__ = [
    "ApiKind",
    "Contribution",
    "Expect",
    "Expected",
    "ExpectedKind",
    "PluginAdapterOwner",
    "PluginAsking",
    "PluginChange",
    "PluginChangedCheck",
    "PluginConstraint",
    "PluginDeclaration",
    "PluginDeclaredVerdict",
    "PluginDemand",
    "PluginEvidence",
    "PluginExpectedFailure",
    "PluginFailingAsDeclared",
    "PluginOverriding",
    "PluginPair",
    "PluginPuts",
    "PluginRecipe",
    "PluginRecipeInput",
    "PluginRecipeOn",
    "PluginRecipeRan",
    "PluginRequest",
    "PluginSecret",
    "PluginStep",
    "PluginStepAdapter",
    "PluginStepRan",
    "ServiceConstant",
]
