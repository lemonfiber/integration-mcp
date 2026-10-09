# Copyright (c) 2026 NightWorksIO
"""The `step` envelope, and the shapes only `step` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.step__walkthrough import Line


class StepEnvelope(typing.TypedDict):
    """The envelope carrying `step`."""

    api_version: int
    data: Line
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["step"]


__all__ = [
    "StepEnvelope",
]
