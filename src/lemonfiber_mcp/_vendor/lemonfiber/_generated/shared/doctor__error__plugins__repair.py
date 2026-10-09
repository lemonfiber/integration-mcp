# Copyright (c) 2026 NightWorksIO
"""The shapes `doctor`, `error`, `plugins` and `repair` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Remedy(typing.TypedDict):
    """One thing the operator can do about a problem."""

    action: str
    """The action, phrased as something to do rather than something to know."""
    detail: typing.NotRequired[str | None]
    """Where to look, when that helps."""


__all__ = [
    "Remedy",
]
