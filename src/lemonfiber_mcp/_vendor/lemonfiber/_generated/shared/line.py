# Copyright (c) 2026 NightWorksIO
"""The shapes `step` and `walkthrough` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Line(typing.TypedDict):
    """One narrated line: a step, and what was specifically true of it."""

    detail: str
    """What was specifically true — the evidence that makes the line worth reading
    rather than a spinner. Empty where there is nothing particular to say.
    """
    said: str
    """What it is doing, in plain language."""
    step: WalkthroughStep
    """The step being narrated."""


type WalkthroughStep = typing.Literal[
    "choosing", "searching", "grabbing", "downloading", "importing", "scanning", "available"
]
"""One step of the walk, ordered from picking something to watching it play."""


__all__ = [
    "Line",
    "WalkthroughStep",
]
