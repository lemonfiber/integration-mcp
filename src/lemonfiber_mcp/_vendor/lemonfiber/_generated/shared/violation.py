# Copyright (c) 2026 NightWorksIO
"""The shapes `plugin-claims`, `plugin-conformance` and `plugin-recording` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Violation(typing.TypedDict):
    """One thing a manifest got wrong, and where."""

    location: str
    """Which declaration it is about, in the manifest's own terms."""
    message: str
    """What is wrong with it."""


__all__ = [
    "Violation",
]
