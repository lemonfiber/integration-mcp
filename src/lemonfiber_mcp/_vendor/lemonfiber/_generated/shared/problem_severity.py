# Copyright (c) 2026 NightWorksIO
"""The shapes `alert`, `dashboard`, `doctor`, `error` and `plugins` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type ProblemSeverity = typing.Literal["advisory", "warning", "error", "critical"]
"""How much a problem matters.

Four levels, deliberately. More would not be applied consistently, and
inconsistent severity is worse than coarse severity.
"""


__all__ = [
    "ProblemSeverity",
]
