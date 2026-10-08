# Copyright (c) 2026 NightWorksIO
"""The `undo` envelope, and the shapes only `undo` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.plugins__undo import UndoReversal


class UndoEnvelope(typing.TypedDict):
    """The envelope carrying `undo`."""

    api_version: int
    data: UndoReversal
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["undo"]


__all__ = [
    "UndoEnvelope",
]
