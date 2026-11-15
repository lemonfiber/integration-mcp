# Copyright (c) 2026 NightWorksIO
"""The shapes `alerts` and `notify` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type NotificationKind = typing.Literal[
    "problem", "completion", "update", "backup", "request", "member", "ready"
]
"""What sort of thing an alert tells the operator."""


__all__ = [
    "NotificationKind",
]
