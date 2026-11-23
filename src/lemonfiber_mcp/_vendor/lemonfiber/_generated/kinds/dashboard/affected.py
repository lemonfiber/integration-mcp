# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `dashboard` carries; `kinds.dashboard` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ...shared.address import FrontDoorReport
from ...shared.dashboard_protocol import DashboardProtocol
from ...shared.estimate import HouseholdReport
from ...shared.instant import Instant
from ...shared.problem_severity import ProblemSeverity
from ...shared.service import Service


class Affected(typing.TypedDict):
    """One thing that is wrong, as the expanded summary lists it."""

    acknowledged: typing.NotRequired[bool]
    """Whether the operator has acknowledged it by declining its fix. It still stands
    and is still counted.
    """
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
    onset: Instant
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


class Downloader(typing.TypedDict):
    """One download client, and whether it is paused."""

    client: str
    """The client, by the name the stack knows it under."""
    state: DownloaderState
    """Whether it is paused, as the client reads it back."""


type DownloaderState = typing.Literal["paused", "fetching", "unknown"]
"""Whether a download client is fetching, as it reads it back."""


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


type PanelArray_of_Downloader = (
    PanelArray_of_DownloaderReady | PanelArray_of_DownloaderUnavailable | PanelArray_of_DownloaderPending
)
"""A panel's content, the reason its source could not fill it, or that its source
is still being read.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live. A pending panel is neither: its source
has not answered within the first wave of a gather, and the second fills it in.
"""


class PanelArray_of_DownloaderPending(typing.TypedDict):
    """The source has not answered yet; a snapshot that follows fills the panel."""

    panel: typing.Literal["pending"]


class PanelArray_of_DownloaderReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: list[Downloader]
    panel: typing.Literal["ready"]


class PanelArray_of_DownloaderUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelArray_of_DownloaderUnavailableData
    panel: typing.Literal["unavailable"]


class PanelArray_of_DownloaderUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


type PanelArray_of_Queue = (
    PanelArray_of_QueueReady | PanelArray_of_QueueUnavailable | PanelArray_of_QueuePending
)
"""A panel's content, the reason its source could not fill it, or that its source
is still being read.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live. A pending panel is neither: its source
has not answered within the first wave of a gather, and the second fills it in.
"""


class PanelArray_of_QueuePending(typing.TypedDict):
    """The source has not answered yet; a snapshot that follows fills the panel."""

    panel: typing.Literal["pending"]


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


type PanelArray_of_Service = (
    PanelArray_of_ServiceReady | PanelArray_of_ServiceUnavailable | PanelArray_of_ServicePending
)
"""A panel's content, the reason its source could not fill it, or that its source
is still being read.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live. A pending panel is neither: its source
has not answered within the first wave of a gather, and the second fills it in.
"""


class PanelArray_of_ServicePending(typing.TypedDict):
    """The source has not answered yet; a snapshot that follows fills the panel."""

    panel: typing.Literal["pending"]


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


type PanelArray_of_Transfer = (
    PanelArray_of_TransferReady | PanelArray_of_TransferUnavailable | PanelArray_of_TransferPending
)
"""A panel's content, the reason its source could not fill it, or that its source
is still being read.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live. A pending panel is neither: its source
has not answered within the first wave of a gather, and the second fills it in.
"""


class PanelArray_of_TransferPending(typing.TypedDict):
    """The source has not answered yet; a snapshot that follows fills the panel."""

    panel: typing.Literal["pending"]


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


type PanelFrontDoorReport = (
    PanelFrontDoorReportReady | PanelFrontDoorReportUnavailable | PanelFrontDoorReportPending
)
"""A panel's content, the reason its source could not fill it, or that its source
is still being read.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live. A pending panel is neither: its source
has not answered within the first wave of a gather, and the second fills it in.
"""


class PanelFrontDoorReportPending(typing.TypedDict):
    """The source has not answered yet; a snapshot that follows fills the panel."""

    panel: typing.Literal["pending"]


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


type PanelHouseholdReport = (
    PanelHouseholdReportReady | PanelHouseholdReportUnavailable | PanelHouseholdReportPending
)
"""A panel's content, the reason its source could not fill it, or that its source
is still being read.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live. A pending panel is neither: its source
has not answered within the first wave of a gather, and the second fills it in.
"""


class PanelHouseholdReportPending(typing.TypedDict):
    """The source has not answered yet; a snapshot that follows fills the panel."""

    panel: typing.Literal["pending"]


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


type PanelStorage = PanelStorageReady | PanelStorageUnavailable | PanelStoragePending
"""A panel's content, the reason its source could not fill it, or that its source
is still being read.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live. A pending panel is neither: its source
has not answered within the first wave of a gather, and the second fills it in.
"""


class PanelStoragePending(typing.TypedDict):
    """The source has not answered yet; a snapshot that follows fills the panel."""

    panel: typing.Literal["pending"]


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


class PanelVpnPending(typing.TypedDict):
    """The source has not answered yet; a snapshot that follows fills the panel."""

    panel: typing.Literal["pending"]


class PanelVpnReady(typing.TypedDict):
    """The source answered; here is the panel."""

    data: Vpn
    panel: typing.Literal["ready"]


class PanelVpnUnavailableData(typing.TypedDict):
    reason: str
    """Why the panel could not be filled, in the operator's terms."""


class Queue(typing.TypedDict):
    """One curator's queue, and how much of it is stuck."""

    depth: int
    """How many items are queued."""
    service: str
    """The service whose queue this is."""
    stuck: int
    """How many of them are stuck rather than progressing."""


class Storage(typing.TypedDict):
    """The storage picture: what is free, when it runs out, and whether imports link."""

    config_free: DashboardReading
    """Bytes free on the volume the services keep their configuration and databases
    on, which fills apart from the data volume where the two are different disks
    and stops every service when it does. A [`Reading`] for the same reason.
    """
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
    "DashboardReading",
    "DashboardReadingKnown",
    "DashboardReadingStale",
    "DashboardReadingUnknown",
    "Downloader",
    "DownloaderState",
    "Duration",
    "Hardlink",
    "HealthStanding",
    "HealthSummary",
    "PanelArray_of_Downloader",
    "PanelArray_of_DownloaderPending",
    "PanelArray_of_DownloaderReady",
    "PanelArray_of_DownloaderUnavailable",
    "PanelArray_of_DownloaderUnavailableData",
    "PanelArray_of_Queue",
    "PanelArray_of_QueuePending",
    "PanelArray_of_QueueReady",
    "PanelArray_of_QueueUnavailable",
    "PanelArray_of_QueueUnavailableData",
    "PanelArray_of_Service",
    "PanelArray_of_ServicePending",
    "PanelArray_of_ServiceReady",
    "PanelArray_of_ServiceUnavailable",
    "PanelArray_of_ServiceUnavailableData",
    "PanelArray_of_Transfer",
    "PanelArray_of_TransferPending",
    "PanelArray_of_TransferReady",
    "PanelArray_of_TransferUnavailable",
    "PanelArray_of_TransferUnavailableData",
    "PanelFrontDoorReport",
    "PanelFrontDoorReportPending",
    "PanelFrontDoorReportReady",
    "PanelFrontDoorReportUnavailable",
    "PanelFrontDoorReportUnavailableData",
    "PanelHouseholdReport",
    "PanelHouseholdReportPending",
    "PanelHouseholdReportReady",
    "PanelHouseholdReportUnavailable",
    "PanelHouseholdReportUnavailableData",
    "PanelStorage",
    "PanelStoragePending",
    "PanelStorageReady",
    "PanelStorageUnavailable",
    "PanelStorageUnavailableData",
    "PanelVpnPending",
    "PanelVpnReady",
    "PanelVpnUnavailableData",
    "Queue",
    "Storage",
    "Transfer",
    "Vpn",
]
