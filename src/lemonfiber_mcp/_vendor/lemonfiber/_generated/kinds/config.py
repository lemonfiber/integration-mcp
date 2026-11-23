# Copyright (c) 2026 NightWorksIO
"""The `config` envelope, and the shapes only `config` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.setting_report import SettingReport, Validation
from ..shared.stance import Stance


class Active(typing.TypedDict):
    """One download still coming down when a reduction was asked for."""

    name: str
    """What it is, as the client names it."""
    progress: int
    """How far along, from zero to a hundred."""
    protocol: str
    """Which client has it."""


class ConfigEnvelope(typing.TypedDict):
    """The envelope carrying `config`."""

    api_version: int
    data: ConfigReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["config"]


class ConfigReport(typing.TypedDict):
    """The answer to a configuration command."""

    changed: bool
    """Whether this command changed, or would change, a setting."""
    consequence: typing.NotRequired[str | None]
    """What this change costs, where making it decides something with a
    consequence — moving the library, turning port forwarding off, or naming a
    front door. Stated for a change that is only staged as well as one that
    landed, since the moment before it happens is the moment it is worth reading.
    Absent for a read, and for a change to a setting nobody catalogued a cost for.
    """
    decisions: list[DecisionReport]
    """Every answer setup writes, in the catalogue's order, whether or not anything holds
    it. Never a value: a value is read where it is held, withheld there as it is.
    """
    rehearsed: bool
    """Whether this was a rehearsal, so a change that `changed` reports was one
    that *would* be made rather than one that was.
    """
    review: typing.NotRequired[Review | None]
    """The difference between the configuration in force and the one proposed, and
    where that proposal stands: applied, staged for a confirmation, turned away,
    or nothing to do. Absent for a read, which proposes nothing.
    """
    settings: list[SettingReport]
    """The settings asked about — one for a lookup, all of them for a listing."""
    unmanaged: list[UnmanagedReport]
    """Each area the operator declared unmanaged, in the order written, with what it
    covers now. Empty where nothing is declared. An area and a reason are the
    operator's own text, to be shown as plain text.
    """
    unmanaged_more: int
    """How many declared areas `unmanaged` leaves out for being too many."""


type Cost = typing.Literal["cheap", "consequential"]
"""What changing a decision costs."""


type CoveredKind = typing.Literal["service", "path", "setting"]
"""What a thing a declaration covers is, read off where it was found.

Never off its name, since a stack may name a service `config`: one area can cover a
service, a file and a setting at once, each listed as what it is.
"""


class CoveredReport(typing.TypedDict):
    """One thing a declaration covers."""

    kind: CoveredKind
    """What it is."""
    name: str
    """Its name: a service's id, a file's place in the stack or the project, or a
    setting's key.
    """


type DecisionKey = typing.Literal[
    "DATA_ROOT",
    "MEDIA_SERVER_MODE",
    "LEMONFIBER_USENET",
    "LEMONFIBER_TORRENT",
    "LEMONFIBER_VPN",
    "PUID",
    "PGID",
    "VPN_PROVIDER",
    "INDEXER_URL",
    "INDEXER_APIKEY",
    "USENET_HOST",
    "USENET_PORT",
    "USENET_USER",
    "USENET_PASS",
    "USENET_TLS",
    "LEMONFIBER_FRONT_DOOR",
    "TZ",
    "LEMONFIBER_LOCALE",
]
"""The setting an answer setup writes is held in."""


class DecisionReport(typing.TypedDict):
    """One answer setup writes, as it can be changed afterwards."""

    affects: str
    """What changing it affects, in the core's words."""
    cost: Cost
    """What changing it costs."""
    credential: bool
    """Whether its value is withheld as a credential."""
    held: bool
    """Whether the answer is held, in the configuration or the settings store."""
    key: DecisionKey
    """The setting the answer is kept in."""
    setting: typing.NotRequired[str | None]
    """The name `settings set` takes, where the settings store keeps the answer. Absent
    where `config set` takes it.
    """


class Edited(typing.TypedDict):
    """A setting changed outside lemonfiber since it last wrote one.

    Both sides, so the operator chooses between them rather than being told one of
    them lost. Values a listing withholds are withheld here too — a report a script
    can log must not be the one place a password is printed.
    """

    found: str
    """What the file holds now."""
    secret: bool
    """Whether either value was withheld rather than shown."""
    wrote: str
    """What lemonfiber last wrote there."""


class Findings(typing.TypedDict):
    """What a proposed change comes to on this machine.

    Empty on every change that comes to nothing beyond its value, which is most of
    them: a report full of empty lists about a timezone would teach the operator to
    skip the one that matters.
    """

    active: list[Active]
    """What is still coming down, where a reduction would interrupt it."""
    edited: typing.NotRequired[Edited | None]
    """The hand-edit found in the configuration file, where one was found."""
    keeps: list[str]
    """What this change leaves exactly as it is, said in full — because an operator
    dropping a way of downloading is weighing whether they lose what they built
    with it.
    """
    library: list[LibraryPath]
    """The library paths the services hold, and what moving the data location does
    to each. Empty for every change that does not move it.
    """
    opens: list[Opening]
    """What this change newly asks the operator for, in the order they meet it."""
    stops: list[str]
    """What this change stops running, by service name."""


class LibraryPath(typing.TypedDict):
    """One library path a service files into, and what moving the data location does
    to it.
    """

    because: str
    """Why it does or does not, in the operator's terms."""
    carried: bool
    """Whether the library at this path survives the move."""
    host: typing.NotRequired[str | None]
    """The host directory it would resolve to after the move, where the move can
    resolve it at all.
    """
    path: str
    """The path as that service holds it, which is a path inside its container."""
    service: str
    """The service holding it."""


class Opening(typing.TypedDict):
    """One thing a way of downloading newly asks the operator for.

    What is opened and nothing beside it: an operator adding Usenet is shown the
    Usenet provider and the settings its login is kept in, and never the tunnel,
    which they neither need nor asked about.
    """

    because: str
    """Why this protocol needs it."""
    setting: typing.NotRequired[str | None]
    """The setting its answer is kept in, where it is kept in one. Absent for an
    account the operator has to go and obtain, which no setting holds.
    """
    what: str
    """What it is, in the operator's terms."""


class Review(typing.TypedDict):
    """A proposed change, read against what is in force, and where it stands."""

    change: ConfigChange
    """The difference, as it would be applied."""
    findings: typing.NotRequired[Findings]
    """What the change comes to on this machine, beyond the value it changes.

    Filled by whoever went and asked — the services where they file, the clients
    what they are fetching — and empty on every change that comes to nothing
    beyond its value. Carried on a staged proposal as well as an applied one: a
    review that withheld this until after the yes would be asking for a yes to
    something unstated.
    """
    proof: typing.NotRequired[Validation | None]
    """What proving the replacement credential came to, where one was proven.

    A replacement is proven against its live service before the credential it
    replaces is discarded, so this is present for exactly those settings and
    absent everywhere else.
    """
    refusal: typing.NotRequired[str | None]
    """Why nothing was written, where nothing was and the reason is not simply that
    somebody has yet to say yes.
    """
    stance: Stance
    """Where the proposal stands."""


class UnmanagedReport(typing.TypedDict):
    """One area the operator declared unmanaged, as it covers things now."""

    area: str
    """The area as written, a control or layout character written as its bytes in hex."""
    area_cut: bool
    """Whether `area` was cut short."""
    covers: list[CoveredReport]
    """Each thing the area covers now, in the order the stack holds them. Empty where it
    covers nothing.
    """
    covers_more: int
    """How many covered things `covers` leaves out for being too many."""
    why: str
    """The reason the operator gave, written as `area` is."""
    why_cut: bool
    """Whether `why` was cut short."""


ConfigChange = typing.TypedDict(
    "ConfigChange",
    {
        "cost": Cost,
        "from": typing.NotRequired[str | None],
        "key": str,
        "to": str,
    },
)
"""The difference between the configuration in force and the one proposed.

One setting, because one call changes one setting. What makes it a diff rather than
a value is `from`: an operator deciding whether to go ahead is deciding between two
things, and a report that showed only the new one would be asking them to remember
the old one correctly.
"""


__all__ = [
    "Active",
    "ConfigChange",
    "ConfigEnvelope",
    "ConfigReport",
    "Cost",
    "CoveredKind",
    "CoveredReport",
    "DecisionKey",
    "DecisionReport",
    "Edited",
    "Findings",
    "LibraryPath",
    "Opening",
    "Review",
    "UnmanagedReport",
]
