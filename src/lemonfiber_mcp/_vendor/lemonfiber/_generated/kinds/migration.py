# Copyright (c) 2026 NightWorksIO
"""The `migration` envelope, and the shapes only `migration` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.adoption__migration import CarryingReport
from ..shared.beside__migration import MovedReport
from ..shared.import___migration__seed__status__stuck import UnsupportedReport
from ..shared.lifecycle__migration import ConflictReport


class LinkingReport(typing.TypedDict):
    """What an existing layout costs, where it cannot hold a hardlink."""

    because: str
    """Why they cannot, naming the filesystems it is about."""
    cost: str
    """What that costs, in room rather than in adjectives."""
    filesystems: list[str]
    """The filesystems the existing setup keeps its data on."""
    forced: bool
    """Whether lemonfiber will do it. Always false: the layout and the library in it
    are the operator's, and correctness does not outrank their data.
    """
    links: bool
    """Whether imports can be hardlinks across this layout. False whenever this is
    reported at all, since a layout that links is not reported.
    """
    remedy: str
    """What would fix it, offered."""


class MigrationEnvelope(typing.TypedDict):
    """The envelope carrying `migration`."""

    api_version: int
    data: MigrationReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["migration"]


class MigrationReport(typing.TypedDict):
    """What is already on this machine, before anything is proposed."""

    beside: list[MovedReport]
    """Where each service would listen to run beside the existing setup."""
    carrying: list[CarryingReport]
    """What adopting each recognised service would come to, by service name."""
    conflicts: list[ConflictReport]
    """Ports wanted by lemonfiber that an existing service already holds."""
    linking: typing.NotRequired[LinkingReport | None]
    """What the existing layout costs where it cannot hold a hardlink, absent where
    it can.
    """
    modes: list[ModeReport]
    """What may be done about what was found, least destructive first."""
    not_carried: list[UnsupportedReport]
    """What no migration carries across, whatever mode it runs in."""
    read: bool
    """Whether the engine answered at all.

    False means the survey found nothing because it could not look, which is a
    different answer from finding nothing, and the only one that must never be
    read as an empty machine.
    """
    standing: list[StandingReport]
    """Existing projects, by project name."""
    unsupported: list[UnsupportedReport]
    """What was found and cannot be adopted."""


class ModeReport(typing.TypedDict):
    """One thing an operator may do about a setup already here."""

    disturbs: bool
    """Whether carrying it out stops or alters what is already running."""
    mode: str
    """The word an operator types for it."""
    preselected: bool
    """Whether it is offered already chosen. Only adopting is."""
    what: str
    """What choosing it would come to, in the operator's terms."""


class OccupantReport(typing.TypedDict):
    """One container of somebody else's stack, as the engine reports it."""

    adoptable: bool
    """Whether lemonfiber knows this service and could take it over as it stands."""
    ports: list[int]
    """Every host port it publishes, lowest first."""
    running: bool
    """Whether it is running now, as against present but stopped."""
    service: str
    """The Compose service name it answers to."""


class StandingReport(typing.TypedDict):
    """One Compose project on this machine that is not lemonfiber's."""

    project: str
    """The Compose project name."""
    services: list[OccupantReport]
    """Its containers, by service name."""


__all__ = [
    "LinkingReport",
    "MigrationEnvelope",
    "MigrationReport",
    "ModeReport",
    "OccupantReport",
    "StandingReport",
]
