# Copyright (c) 2026 NightWorksIO
"""The shapes `dashboard`, `doctor`, `error`, `held`, `household`, `part-way`, `play`, `playing`, `plugins`, `title` and `tuned` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

type Code = str
"""A stable identifier for a kind of problem.

Stability is the whole point: an operator who searches for a code should find
the same answer a year later. Every code is declared in the error crate's `codes`
module, and a code is never recycled.
"""


__all__ = [
    "Code",
]
