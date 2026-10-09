# Copyright (c) 2026 NightWorksIO
"""The `pull` envelope, and the shapes only `pull` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class PullEnvelope(typing.TypedDict):
    """The envelope carrying `pull`."""

    api_version: int
    data: str
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["pull"]


__all__ = [
    "PullEnvelope",
]
