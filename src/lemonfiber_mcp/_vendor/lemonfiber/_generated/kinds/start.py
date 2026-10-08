# Copyright (c) 2026 NightWorksIO
"""The `start` envelope, and the shapes only `start` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class StartEnvelope(typing.TypedDict):
    """The envelope carrying `start`."""

    api_version: int
    data: str
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["start"]


__all__ = [
    "StartEnvelope",
]
