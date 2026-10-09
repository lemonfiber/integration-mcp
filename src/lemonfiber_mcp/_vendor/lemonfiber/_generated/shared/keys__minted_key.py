# Copyright (c) 2026 NightWorksIO
"""The shapes `keys` and `minted-key` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type KeyPurpose = typing.Literal["home-assistant", "mcp", "other"]
"""What the minter said a key is for.

A label and nothing more. The core cannot tell what a program does with a key, so the
listing shows this as the minter's own declaration rather than as anything verified.
"""


__all__ = [
    "KeyPurpose",
]
