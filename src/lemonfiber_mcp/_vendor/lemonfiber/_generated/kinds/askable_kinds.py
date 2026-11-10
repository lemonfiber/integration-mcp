# Copyright (c) 2026 NightWorksIO
"""The `askable-kinds` envelope, and the shapes only `askable-kinds` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.askable__askable_kinds__asked import TitleKind, TitleUnit


class AskableKind(typing.TypedDict):
    """One kind a member may ask for now, with the units it is asked for in."""

    kind: TitleKind
    """The kind."""
    units: list[TitleUnit]
    """The units a title of it is asked for in, none for series and films."""


class AskableKindsEnvelope(typing.TypedDict):
    """The envelope carrying `askable-kinds`."""

    api_version: int
    data: AskableKindsReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["askable-kinds"]


class AskableKindsReport(typing.TypedDict):
    """Which kinds a member may ask for now."""

    kinds: list[AskableKind]
    """Each kind they may ask for now, series first."""
    member: str
    """The member asked about, by the name they are known by."""


__all__ = [
    "AskableKind",
    "AskableKindsEnvelope",
    "AskableKindsReport",
]
