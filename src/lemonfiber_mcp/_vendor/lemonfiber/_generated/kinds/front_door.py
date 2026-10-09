# Copyright (c) 2026 NightWorksIO
"""The `front-door` envelope, and the shapes only `front-door` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.dashboard__front_door import FrontDoorReport


class FrontDoorEnvelope(typing.TypedDict):
    """The envelope carrying `front-door`."""

    api_version: int
    data: FrontDoorReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["front-door"]


__all__ = [
    "FrontDoorEnvelope",
]
