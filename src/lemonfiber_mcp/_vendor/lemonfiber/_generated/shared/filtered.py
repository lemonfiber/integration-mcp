# Copyright (c) 2026 NightWorksIO
"""The shapes `lifecycle`, `preview` and `status` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Filtered(typing.TypedDict):
    """A service a closure asked for that the configuration leaves out, and why."""

    forms: list[str]
    """The forms that asked for it, in the order the stack declares them."""
    id: str
    """The service's identifier."""
    name: str
    """What it is called in front of an operator."""
    needs: StackProtocol
    """The provider it cannot run without."""
    profile: str
    """The profile it belongs to, which is what the configuration leaves out."""


type StackProtocol = typing.Literal["usenet", "torrent"]
"""A download provider a profile can depend on.

Serialisable as well as readable, for the same reason [`Criticality`] is: it
reaches an operator. A profile left out of a closure is only half reported
without the provider it wanted.
"""


__all__ = [
    "Filtered",
    "StackProtocol",
]
