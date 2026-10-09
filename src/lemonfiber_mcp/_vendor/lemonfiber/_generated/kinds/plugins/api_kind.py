# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `plugins` carries; `kinds.plugins` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ...shared.doctor__plugins import DoctorVerdict, Finding


class Api(typing.TypedDict):
    """How lemonfiber talks to a service when seeding.

    The same shape on a plugin's service as on the stack's own, which is what lets a
    plugin name one of these adapters rather than supply one of its own.
    """

    key_source: KeySource
    """Where the credential comes from."""
    kind: ApiKind
    """Selects the client implementation."""
    path: typing.NotRequired[str | None]
    """The file holding the credential, where one applies."""
    version: typing.NotRequired[int | None]
    """The major version of the service's HTTP API — the `/api/vN` path segment.

    Required for the `servarr` shape and read there, because that one shape
    spans two versions (Sonarr and Radarr at v3, Lidarr and Prowlarr at v1),
    so the version is data rather than a guess from a service's name. Absent
    for the other kinds, whose one fixed version their client already knows.
    """


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
    is not evidence — except for a refusal, which is the one answer no port proxy can
    produce.

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


type KeySource = typing.Literal[
    "config-xml", "config-ini", "config-json", "config-yaml", "api-settings", "generated", "none"
]
"""Where a service's credential comes from."""


type PluginAdapterOwner = typing.Literal["lemonfiber"]
"""Whose an adapter is.

One answer, and the field exists so that the answer is on the wire: an adapter a
plugin could bring would be code a stranger wrote running with lemonfiber's
authority, which nothing here can load.
"""


class PluginChange(typing.TypedDict):
    """One change installing a plugin makes to the machine.

    A path and what goes at it, which is the whole of what an install touches. Two of
    them can be edits to a file the stack already has — the proxy's and the
    dashboard's — and those say so, as a region, so an operator reading the account
    knows which of their files the install writes into.
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


class PluginPlaced(typing.TypedDict):
    """One service of an installed plugin, as it was placed."""

    api: typing.NotRequired[Api | None]
    """The adapter lemonfiber reaches it through, where the plugin named one.

    Defaulted for a record written before this was kept, which reads as naming
    none: a service operated generically, as it was when installed.
    """
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
    image: str
    """The registry path, carrying no pin of its own."""
    listens: typing.NotRequired[int | None]
    """The port it answers on inside the stack's network, where it declared one."""
    media_types: typing.NotRequired[list[str]]
    """The media it files, in the stack manifest's vocabulary, which decides what it
    comes to in each service that asks for what it provides.

    Defaulted for a record written before this was kept, which reads as filing
    nothing named.
    """
    name: typing.NotRequired[str]
    """What it is called, for a reader, which is what its dashboard entry is listed as.

    Defaulted for a record written before this was kept, which lists it by its id
    rather than leaving it off the panel.
    """
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
    service: str
    """The service's id, which is the name its container is written under."""
    tag: str
    """The readable name that digest went by when it was installed."""
    takes_data: bool
    """Whether the library is mounted for it."""


type PluginPuts = typing.Literal["directory", "document", "region"]
"""What an install puts at one path."""


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


class PluginSecret(typing.TypedDict):
    """One credential a plugin says it will hold, without a value and with no place for one."""

    id: str
    """What the value is, within the plugin."""
    of: str
    """Whose credential it is."""
    why: str
    """What holding it is for."""


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


__all__ = [
    "Api",
    "ApiKind",
    "Contribution",
    "Expect",
    "Expected",
    "ExpectedKind",
    "KeySource",
    "PluginAdapterOwner",
    "PluginChange",
    "PluginChangedCheck",
    "PluginConstraint",
    "PluginDeclaration",
    "PluginDeclaredVerdict",
    "PluginEvidence",
    "PluginExpectedFailure",
    "PluginFailingAsDeclared",
    "PluginOverriding",
    "PluginPair",
    "PluginPlaced",
    "PluginPuts",
    "PluginReached",
    "PluginReachedHousehold",
    "PluginReachedLoopback",
    "PluginRequest",
    "PluginSecret",
]
