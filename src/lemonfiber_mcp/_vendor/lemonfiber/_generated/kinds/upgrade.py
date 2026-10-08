# Copyright (c) 2026 NightWorksIO
"""The `upgrade` envelope, and the shapes only `upgrade` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.music__upgrade import Triggered


class UpgradeEnvelope(typing.TypedDict):
    """The envelope carrying `upgrade`."""

    api_version: int
    data: UpgradeReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["upgrade"]


class UpgradeMedia(typing.TypedDict):
    """One media type an upgrade covers: its chosen quality, that quality's cost, and —
    once confirmed — what became of asking its service to re-search.

    Reported per media type rather than as one figure, because each type carries its
    own preset and so its own cost: film at maximum and television at space-saving are
    upgraded to different bars, and a single number would misstate one of them.
    """

    media_type: str
    """The media type — `tv` or `movies`."""
    outcome: typing.NotRequired[Triggered | None]
    """What became of the re-search, or `None` where the upgrade was not confirmed
    and only the cost was stated.
    """
    preset: str
    """The preset in force for it."""
    size_per_hour: str
    """Roughly what an hour of it costs at that preset."""


class UpgradeReport(typing.TypedDict):
    """What upgrading existing content did, or — unconfirmed — would do.

    Upgrading re-acquires the existing library at the chosen quality, which is a
    large, bandwidth-expensive operation, so it is a separate explicit action whose
    cost is stated before it runs and which does nothing until confirmed. Each *arr
    re-searches against its own current cutoff, so the report speaks per media type
    rather than asserting one preset across the library.
    """

    confirmed: bool
    """Whether the operator confirmed; without it nothing was triggered, only the
    cost stated.
    """
    media: list[UpgradeMedia]
    """Per media type: its preset, that preset's cost, and — confirmed — the outcome."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


__all__ = [
    "UpgradeEnvelope",
    "UpgradeMedia",
    "UpgradeReport",
]
