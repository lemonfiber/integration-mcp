# Copyright (c) 2026 NightWorksIO
"""The `alert` envelope, and the shapes only `alert` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.alert__dashboard import Alert


class AlertEnvelope(typing.TypedDict):
    """The envelope carrying `alert`."""

    api_version: int
    data: Alert
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["alert"]


__all__ = [
    "AlertEnvelope",
]
