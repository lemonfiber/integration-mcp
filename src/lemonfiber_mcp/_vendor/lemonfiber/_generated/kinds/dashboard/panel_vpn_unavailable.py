# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `dashboard` carries; `kinds.dashboard` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .affected import (
    HealthSummary,
    PanelArray_of_Downloader,
    PanelArray_of_Queue,
    PanelArray_of_Service,
    PanelArray_of_Transfer,
    PanelFrontDoorReport,
    PanelHouseholdReport,
    PanelStorage,
    PanelVpnPending,
    PanelVpnReady,
    PanelVpnUnavailableData,
)
from ...shared.alert import Alert
from ...shared.run_health import ScheduledService


class DashboardEnvelope(typing.TypedDict):
    """The envelope carrying `dashboard`."""

    api_version: int
    data: Snapshot
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["dashboard"]


type PanelVpn = PanelVpnReady | PanelVpnUnavailable | PanelVpnPending
"""A panel's content, the reason its source could not fill it, or that its source
is still being read.

The difference between \"this panel is up to date\" and \"this panel's source is
unreachable\" is the whole of degrading honestly: an unavailable panel says so,
in its own words, rather than showing stale data as current or blank data as
zero — and the panels beside it stay live. A pending panel is neither: its source
has not answered within the first wave of a gather, and the second fills it in.
"""


class PanelVpnUnavailable(typing.TypedDict):
    """The source could not be reached, for this stated reason."""

    data: PanelVpnUnavailableData
    panel: typing.Literal["unavailable"]


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
    downloaders: PanelArray_of_Downloader
    """Every download client the stack runs, and whether each is paused."""
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
    scheduled: list[ScheduledService]
    """Each run-and-exit service, with how its last run ended."""
    services: PanelArray_of_Service
    """Every service and what it is doing."""
    storage: PanelStorage
    """The storage picture."""
    stuck: list[Stuck]
    """What in the pipeline has stopped, worst first — assessed across the
    download clients and the curators together, because the failure that matters
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


__all__ = [
    "DashboardEnvelope",
    "PanelVpn",
    "PanelVpnUnavailable",
    "Snapshot",
    "Stall",
    "Stuck",
    "Telemetry",
]
