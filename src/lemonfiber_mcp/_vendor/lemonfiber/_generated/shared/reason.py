# Copyright (c) 2026 NightWorksIO
"""The shapes `walkthrough` and `walkthrough-offer` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Reason = typing.Literal[
    "no-indexers",
    "indexers-failed",
    "nothing-matched",
    "none-met-the-preset",
    "tunnel-down",
    "not-grabbed",
    "stalled",
    "import-failed",
    "no-media-server",
    "not-visible",
]
"""Why a walkthrough could not go on."""


type Shape = typing.Literal["pipeline", "library-only"]
"""Which walkthrough this stack is offered."""


__all__ = [
    "Reason",
    "Shape",
]
