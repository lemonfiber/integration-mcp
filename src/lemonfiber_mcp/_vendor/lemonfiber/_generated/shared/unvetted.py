# Copyright (c) 2026 NightWorksIO
"""The shapes `lifecycle`, `plugins`, `settings`, `substitution` and `update` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Unvetted(typing.TypedDict):
    """The operator's own overlay, named because nothing in it was held to the model."""

    overlay: str
    """Where the overlay is."""
    services: list[str]
    """Every service it changes, by the names it gives them."""


__all__ = [
    "Unvetted",
]
