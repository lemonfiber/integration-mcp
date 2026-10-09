# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `dashboard` carries; `kinds.dashboard` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .affected import Snapshot


class DashboardEnvelope(typing.TypedDict):
    """The envelope carrying `dashboard`."""

    api_version: int
    data: Snapshot
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["dashboard"]


__all__ = [
    "DashboardEnvelope",
]
