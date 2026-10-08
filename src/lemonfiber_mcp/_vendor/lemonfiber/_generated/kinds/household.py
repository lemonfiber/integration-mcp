# Copyright (c) 2026 NightWorksIO
"""The `household` envelope, and the shapes only `household` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.dashboard__household import HouseholdReport


class HouseholdEnvelope(typing.TypedDict):
    """The envelope carrying `household`."""

    api_version: int
    data: HouseholdReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["household"]


__all__ = [
    "HouseholdEnvelope",
]
