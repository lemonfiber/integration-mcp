# Copyright (c) 2026 NightWorksIO
"""The shapes `settings` and `wizard` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Choosable(typing.TypedDict):
    """One value a setting accepts."""

    needs: dict[str, list[str]]
    """The values of other settings under which it is a choice: each setting with the
    values it has to hold one of, and none where it always is.
    """
    open: bool
    """Whether it is a choice now."""
    value: str
    """The value."""


__all__ = [
    "Choosable",
]
