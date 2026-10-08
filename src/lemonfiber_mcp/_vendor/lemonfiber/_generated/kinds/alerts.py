# Copyright (c) 2026 NightWorksIO
"""The `alerts` envelope, and the shapes only `alerts` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class AlertReport(typing.TypedDict):
    """What the operator will be told about, and what changing it came to."""

    changed: bool
    """Whether this call changed the answer."""
    exceptions: list[ExceptionReport]
    """Events set apart from the preset, quietest name first."""
    means: str
    """What that preset means, in the operator's terms."""
    preset: str
    """The preset in force for events with no exception of their own."""
    rehearsed: bool
    """Whether it only reported what it would have written."""


class AlertsEnvelope(typing.TypedDict):
    """The envelope carrying `alerts`."""

    api_version: int
    data: AlertReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["alerts"]


class ExceptionReport(typing.TypedDict):
    """One event kind the operator set apart from the preset."""

    kind: str
    """The kind of event, by the name a finding gives it."""
    wanted: bool
    """Whether it is heard about, whatever the preset would say."""


__all__ = [
    "AlertReport",
    "AlertsEnvelope",
    "ExceptionReport",
]
