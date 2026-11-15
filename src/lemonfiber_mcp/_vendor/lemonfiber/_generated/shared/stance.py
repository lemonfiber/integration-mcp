# Copyright (c) 2026 NightWorksIO
"""The shapes `adoption`, `beside`, `config`, `import` and `replacement` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Stance = typing.Literal["unchanged", "pending", "blocked", "applied"]
"""Where a proposed change stands once it has been read against what is in force."""


__all__ = [
    "Stance",
]
