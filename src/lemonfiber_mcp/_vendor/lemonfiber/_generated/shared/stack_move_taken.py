# Copyright (c) 2026 NightWorksIO
"""The shapes `lifecycle`, `plugins`, `reset`, `settings`, `substitution` and `update` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class StackMoveTaken(typing.TypedDict):
    """A move in place this run took, or tried to take and could not."""

    plugin: str
    """The plugin the bundle installs."""
    service: str
    """The stack's own service it took, or would have taken, the place of."""
    taken: bool
    """Whether the plugin now runs in the service's place."""
    why: typing.NotRequired[str | None]
    """Why it was not taken, where it was not."""


__all__ = [
    "StackMoveTaken",
]
