# Copyright (c) 2026 NightWorksIO
"""The shapes `catalogue`, `dashboard`, `lifecycle` and `status` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Criticality = typing.Literal["critical", "core", "important", "enhancing", "optional"]
"""How much a service's absence costs.

Serialisable as well as readable, because it reaches an operator: a status
report that says a service is down without saying whether that matters
leaves them to guess, and the manifest already holds the answer.
"""


__all__ = [
    "Criticality",
]
