# Copyright (c) 2026 NightWorksIO
"""The `in-flight` envelope, and the shapes only `in-flight` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.dashboard_protocol import DashboardProtocol


class InFlightEnvelope(typing.TypedDict):
    """The envelope carrying `in-flight`."""

    api_version: int
    data: InFlightReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["in-flight"]


class InFlightReport(typing.TypedDict):
    """What is still coming down inside what a stop would stop."""

    downloads: list[Unfinished]
    """Each download still coming down, with how far it has got."""


class Unfinished(typing.TypedDict):
    """One download a teardown would interrupt.

    Carries the protocol as well as the name, because \"still downloading\" is only
    half of what an operator needs — the other half is which client to go and look in,
    and a stack running both has two places it could be.
    """

    name: str
    """What it is, as the client names it."""
    progress: int
    """How far along, from zero to a hundred."""
    protocol: DashboardProtocol
    """Which client has it."""


__all__ = [
    "InFlightEnvelope",
    "InFlightReport",
    "Unfinished",
]
