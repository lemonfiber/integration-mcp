# Copyright (c) 2026 NightWorksIO
"""The shapes `stuck` and `trace` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Stage = typing.Literal[
    "not-monitored",
    "monitored",
    "searching",
    "found",
    "grabbed",
    "downloading",
    "downloaded",
    "importing",
    "imported",
    "available",
]
"""A stage in an item's journey, ordered from \"nobody asked for it\" to \"playable\". The
declaration order is the pipeline order, so one stage compares less than a later one.
"""


__all__ = [
    "Stage",
]
