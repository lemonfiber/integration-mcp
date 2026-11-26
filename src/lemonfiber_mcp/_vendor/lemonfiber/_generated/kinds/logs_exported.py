# Copyright (c) 2026 NightWorksIO
"""The `logs-exported` envelope, and the shapes only `logs-exported` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class LogsExported(typing.TypedDict):
    """Where an export went, or would have gone."""

    path: str
    """The file, named relative to the directory the viewer was run in."""
    rehearsed: bool
    """Whether it only said where it would have written."""


class LogsExportedEnvelope(typing.TypedDict):
    """The envelope carrying `logs-exported`."""

    api_version: int
    data: LogsExported
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["logs-exported"]


__all__ = [
    "LogsExported",
    "LogsExportedEnvelope",
]
