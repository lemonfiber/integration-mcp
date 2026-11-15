# Copyright (c) 2026 NightWorksIO
"""The shapes `lifecycle` and `migration` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class ConflictReport(typing.TypedDict):
    """A port lemonfiber wants for a service that something else already answers on."""

    held_by: str
    """The project already holding it."""
    port: int
    """The host port both want."""
    wanted_by: str
    """The lemonfiber service that would publish it."""


__all__ = [
    "ConflictReport",
]
