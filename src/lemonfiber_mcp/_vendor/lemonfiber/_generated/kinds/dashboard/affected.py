# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `dashboard` carries; `kinds.dashboard` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ...shared.alert__dashboard import Alert
from ...shared.alert__dashboard__doctor__error__plugins import ProblemSeverity
from ...shared.dashboard__front_door import FrontDoorReport
from ...shared.dashboard__household import HouseholdReport
from ...shared.dashboard__lifecycle__status import Service


class Affected(typing.TypedDict):
    """One thing that is wrong, as the expanded summary lists it."""

    check: str
    """The check that raised it."""
    downstream: list[str]
    """What is also wrong because of this, counted with it rather than again."""
    exit: typing.NotRequired[int | None]
    """How the service it is about exited, where it has and the engine said.

    The technical half of what happened, kept out of the summary so the plain
    words lead, and here for whoever wants the code.
    """
    meaning: str
    """What it costs the operator. The line expands to items an operator can act
    on, and an item that states only the event leaves the judgement it was
    supposed to save them.
    """
    onset: str
    """When the stack first saw it wrong since it last saw it right, in whole
    seconds since the epoch.

    The condition's own stamp, kept between runs, so every surface that reports
    the check names the same moment and a restart does not make an old fault new.
    """
    remedies: list[str]
    """What to do about it, most likely first."""
    severity: ProblemSeverity
    """How bad it is."""
    summary: str
    """What is wrong, in one line."""


type DashboardProtocol = typing.Literal["usenet", "torrent"]
"""Which protocol a transfer is moving over, since the same download reads
differently on each — a Usenet download has no peers, a torrent has no server.
"""


type DashboardReading = DashboardReadingKnown | DashboardReadingStale | DashboardReadingUnknown
"""A figure a source reports, kept apart from the two ways it can be missing.

Zero is a value a source gave; stale is the last value a source that has since
gone quiet gave; unknown is a source that never answered at all. Collapsing any
two of them sends an operator after the wrong problem — a stalled download and
a dashboard that simply stopped polling look identical only if the code lets
them.
"""


class DashboardReadingKnown(typing.TypedDict):
    """The source answered this refresh with a value — which may legitimately be
    zero.
    """

    reading: typing.Literal["known"]
    value: int


class DashboardReadingStale(typing.TypedDict):
    """The source did not answer this refresh; this is the last value it gave."""

    reading: typing.Literal["stale"]
    value: int


class DashboardReadingUnknown(typing.TypedDict):
    """The source has never answered, so nothing can be said about it."""

    reading: typing.Literal["unknown"]


class Duration(typing.TypedDict):
    nanos: int
    secs: int


type Hardlink = typing.Literal["linking", "copying", "unknown"]
"""Whether imports are hardlinking or copying — the difference between an import
that is free and one that doubles the disk it uses.
"""


type HealthStanding = typing.Literal[
    "healthy", "stopped", "unconfigured", "advisory", "degraded", "broken", "critical", "unknown"
]
"""What the stack amounts to.

Ordered from best to worst, so the worst of several is a `max` and there is no
second place to encode the ranking.
"""


class HealthSummary(typing.TypedDict):
    """The one-line summary, and what it expands to."""

    affected: list[Affected]
    """Everything that is wrong, worst first, so the line expands to the affected
    items and their remedies rather than to a number nobody can act on.
    """
    standing: HealthStanding
    """The one word."""
    wanting_attention: int
    """How many things are wrong — root causes, counted once each, so a disk that
    filled and the nine imports that then failed is one thing and not ten.
    """
    worst: typing.NotRequired[str | None]
    """The worst thing, named, so the line says something rather than only
    grading. Absent where nothing is wrong.
    """


type PanelArray_of_Queue = PanelArray_of_QueueReady | PanelArray_of_QueueUnavailable
"""A panel's content, or the reason its source could not fill it.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live.
"""


class PanelArray_of_QueueReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: list[Queue]
    panel: typing.Literal["ready"]


class PanelArray_of_QueueUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelArray_of_QueueUnavailableData
    panel: typing.Literal["unavailable"]


class PanelArray_of_QueueUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


type PanelArray_of_Service = PanelArray_of_ServiceReady | PanelArray_of_ServiceUnavailable
"""A panel's content, or the reason its source could not fill it.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live.
"""


class PanelArray_of_ServiceReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: list[Service]
    panel: typing.Literal["ready"]


class PanelArray_of_ServiceUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelArray_of_ServiceUnavailableData
    panel: typing.Literal["unavailable"]


class PanelArray_of_ServiceUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


type PanelArray_of_Transfer = PanelArray_of_TransferReady | PanelArray_of_TransferUnavailable
"""A panel's content, or the reason its source could not fill it.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live.
"""


class PanelArray_of_TransferReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: list[Transfer]
    panel: typing.Literal["ready"]


class PanelArray_of_TransferUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelArray_of_TransferUnavailableData
    panel: typing.Literal["unavailable"]


class PanelArray_of_TransferUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


type PanelFrontDoorReport = PanelFrontDoorReportReady | PanelFrontDoorReportUnavailable
"""A panel's content, or the reason its source could not fill it.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live.
"""


class PanelFrontDoorReportReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: FrontDoorReport
    panel: typing.Literal["ready"]


class PanelFrontDoorReportUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelFrontDoorReportUnavailableData
    panel: typing.Literal["unavailable"]


class PanelFrontDoorReportUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


type PanelHouseholdReport = PanelHouseholdReportReady | PanelHouseholdReportUnavailable
"""A panel's content, or the reason its source could not fill it.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live.
"""


class PanelHouseholdReportReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: HouseholdReport
    panel: typing.Literal["ready"]


class PanelHouseholdReportUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelHouseholdReportUnavailableData
    panel: typing.Literal["unavailable"]


class PanelHouseholdReportUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


type PanelStorage = PanelStorageReady | PanelStorageUnavailable
"""A panel's content, or the reason its source could not fill it.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live.
"""


class PanelStorageReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: Storage
    panel: typing.Literal["ready"]


class PanelStorageUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelStorageUnavailableData
    panel: typing.Literal["unavailable"]


class PanelStorageUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


type PanelVpn = PanelVpnReady | PanelVpnUnavailable
"""A panel's content, or the reason its source could not fill it.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live.
"""


class PanelVpnReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: Vpn
    panel: typing.Literal["ready"]


class PanelVpnUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelVpnUnavailableData
    panel: typing.Literal["unavailable"]


class PanelVpnUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


class Queue(typing.TypedDict):
    """One `*arr`'s queue, and how much of it is stuck."""

    depth: int
    """How many items are queued."""
    service: str
    """The service whose queue this is."""
    stuck: int
    """How many of them are stuck rather than progressing."""


class Snapshot(typing.TypedDict):
    """Everything the dashboard shows at one moment.

    Each source's panel is filled or marked unavailable on its own, so one dead
    source degrades one region rather than the screen. The surface builds this from
    what it gathered; the standing is read from the same facts so it cannot
    disagree with the panels.
    """

    alerts: list[Alert]
    """What the operator has been told, newest first: what is owed them where a
    channel is refusing, then what has already been said.
    """
    door: PanelFrontDoorReport
    """The one address to hand somebody who lives here.

    On the screen rather than only behind a question, because the operator who
    needs it is not the one who thought to ask: they have just been asked \"what
    do I open?\" by somebody in the next room. Built from the same reading as the
    panels beside it, so the screen and `front-door` cannot name different doors.
    """
    health: HealthSummary
    """The one-line health summary — the same computation every other surface
    uses, so no two of them can grade the same stack differently.

    Always present, unlike the panels: a stack that could not be reached has a
    summary, and it says `unknown`. An absent summary would leave the operator
    to infer health from a blank space, which is the one reading this must never
    be open to.
    """
    household: PanelHouseholdReport
    """What the household has asked for that is not moving.

    On the screen rather than only behind a question, for the reason the door
    beside it is: a request waiting on a decision or failed after one is waiting
    on the operator, and an operator who has to think to ask is one who finds out
    when somebody comes to complain.
    """
    queue: PanelArray_of_Queue
    """The per-service queues."""
    services: PanelArray_of_Service
    """Every service and what it is doing."""
    storage: PanelStorage
    """The storage picture."""
    stuck: list[Stuck]
    """What in the pipeline has stopped, worst first — assessed across the
    download clients and the \\*arrs together, because the failure that matters
    most is invisible inside either.
    """
    telemetry: Telemetry
    """Whether the screen itself can be trusted to be current."""
    transfers: PanelArray_of_Transfer
    """The active transfers."""
    vpn: typing.NotRequired[PanelVpn | None]
    """The VPN, or `None` where no VPN is configured and the panel is omitted
    rather than shown permanently red.
    """


type Stall = typing.Literal[
    "redownload-loop",
    "repeated-import-failure",
    "completed-not-imported",
    "orphaned",
    "stalled-download",
    "waiting-indefinitely",
    "slow",
]
"""Why an item is not moving.

Ordered by how much of the operator's attention each deserves, worst first, so
a summary that leads with the worst category needs no second ranking.
"""


class Storage(typing.TypedDict):
    """The storage picture: what is free, when it runs out, and whether imports link."""

    exhaustion: typing.NotRequired[Duration | None]
    """The time until the disk fills at the current rate of the queue draining
    onto it, or `None` where it is not projected to fill.
    """
    free: DashboardReading
    """Bytes free on the data volume — a [`Reading`], since a volume that could
    not be read this refresh must not render as zero free.
    """
    hardlink: Hardlink
    """Whether imports are linking or copying."""


class Stuck(typing.TypedDict):
    """One thing that is wrong, and why."""

    blocking: typing.NotRequired[str | None]
    """What the service said was blocking it, in its own words, where it said
    anything. A permission denial from an import log is worth more than any
    interpretation of it, and it is the difference between \"stuck\" and
    something an operator can fix.
    """
    held_for: int
    """How long it has been that way, in seconds — what turns \"stuck\" into a
    sentence an operator can weigh.
    """
    items: int
    """How many items this stands for. One in the ordinary case; more where they
    share a cause and the cause is what is wrong — twenty downloads stopped by
    a full disk are one thing to fix, and twenty alerts about it are how an
    operator learns to mute the queue check.
    """
    name: str
    """Which item — or, where several share one cause, that cause."""
    stall: Stall
    """What is wrong with it."""


type Telemetry = typing.Literal["live", "degraded", "disconnected", "no-stack", "unconfigured"]
"""How the screen itself is doing, which is a different question from how the
stack is doing.

The stack's own verdict is [`crate::health::Standing`]; this is only whether the
picture can be trusted to be current. Kept apart because they disagree in both
directions: a healthy stack can be shown through half-failing telemetry, and a
perfectly refreshing screen can be reporting a stack that is on fire.
"""


class Transfer(typing.TypedDict):
    """One active download, as the dashboard shows it."""

    eta: typing.NotRequired[Duration | None]
    """The time left, or `None` where it is stalled and there is none to give."""
    name: str
    """What is being downloaded."""
    progress: int
    """How far along, as a percentage from zero to a hundred."""
    protocol: DashboardProtocol
    """How it is being downloaded."""
    speed: DashboardReading
    """The current speed in bytes per second — a [`Reading`], because a genuine
    zero (stalled) and a source that has gone quiet mean opposite things here,
    and this is the very figure that difference is about.
    """


class Vpn(typing.TypedDict):
    """What the VPN is doing, and whether the download client is actually behind it."""

    country: str
    """The country that address is in."""
    egress_matches: bool
    """Whether the download client's own egress address matches the tunnel's —
    the one thing that proves traffic is genuinely leaving through it.
    """
    exit_ip: str
    """The tunnel's exit address as the outside world sees it."""
    forwarded_port: typing.NotRequired[int | None]
    """The port the provider forwards, where forwarding is on."""


__all__ = [
    "Affected",
    "DashboardProtocol",
    "DashboardReading",
    "DashboardReadingKnown",
    "DashboardReadingStale",
    "DashboardReadingUnknown",
    "Duration",
    "Hardlink",
    "HealthStanding",
    "HealthSummary",
    "PanelArray_of_Queue",
    "PanelArray_of_QueueReady",
    "PanelArray_of_QueueUnavailable",
    "PanelArray_of_QueueUnavailableData",
    "PanelArray_of_Service",
    "PanelArray_of_ServiceReady",
    "PanelArray_of_ServiceUnavailable",
    "PanelArray_of_ServiceUnavailableData",
    "PanelArray_of_Transfer",
    "PanelArray_of_TransferReady",
    "PanelArray_of_TransferUnavailable",
    "PanelArray_of_TransferUnavailableData",
    "PanelFrontDoorReport",
    "PanelFrontDoorReportReady",
    "PanelFrontDoorReportUnavailable",
    "PanelFrontDoorReportUnavailableData",
    "PanelHouseholdReport",
    "PanelHouseholdReportReady",
    "PanelHouseholdReportUnavailable",
    "PanelHouseholdReportUnavailableData",
    "PanelStorage",
    "PanelStorageReady",
    "PanelStorageUnavailable",
    "PanelStorageUnavailableData",
    "PanelVpn",
    "PanelVpnReady",
    "PanelVpnUnavailable",
    "PanelVpnUnavailableData",
    "Queue",
    "Snapshot",
    "Stall",
    "Storage",
    "Stuck",
    "Telemetry",
    "Transfer",
    "Vpn",
]
