# Copyright (c) 2026 NightWorksIO
"""The shapes `lifecycle`, `quality`, `reset` and `update` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class StackEdit(typing.TypedDict):
    """A stack file the operator edited, preserved rather than overwritten, with the
    change an upgrade would make shown against it.
    """

    diff: str
    """The lines that differ between the operator's file and what lemonfiber would
    write — theirs marked `-`, lemonfiber's `+`, the matching head and tail left
    out. Empty where the two differ only in ways `lines` does not see.
    """
    path: str
    """The file's path within the stack directory."""


__all__ = [
    "StackEdit",
]
