# Copyright (c) 2026 NightWorksIO
"""The `error` envelope, and the shapes only `error` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.doctor__error__plugins import Problem


class ErrorEnvelope(typing.TypedDict):
    """The envelope carrying `error`."""

    api_version: int
    data: Problem
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["error"]


__all__ = [
    "ErrorEnvelope",
]
