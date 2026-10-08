# Copyright (c) 2026 NightWorksIO
"""The `preview` envelope, and the shapes only `preview` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.lifecycle__preview import Plan


class PreviewEnvelope(typing.TypedDict):
    """The envelope carrying `preview`."""

    api_version: int
    data: Plan
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["preview"]


__all__ = [
    "PreviewEnvelope",
]
