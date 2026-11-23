# Copyright (c) 2026 NightWorksIO
"""The `logs` envelope, and the shapes only `logs` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class LogsEnvelope(typing.TypedDict):
    """The envelope carrying `logs`."""

    api_version: int
    data: LogsReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["logs"]


class LogsReport(typing.TypedDict):
    """What reading the logs came to."""

    lines: int
    """How many lines were read."""


__all__ = [
    "LogsEnvelope",
    "LogsReport",
]
