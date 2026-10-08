# Copyright (c) 2026 NightWorksIO
"""The shapes `beside` and `migration` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


MovedReport = typing.TypedDict(
    "MovedReport",
    {
        "from": int,
        "service": str,
        "to": int,
    },
)
"""Where one service would listen to run beside what is already here."""


__all__ = [
    "MovedReport",
]
