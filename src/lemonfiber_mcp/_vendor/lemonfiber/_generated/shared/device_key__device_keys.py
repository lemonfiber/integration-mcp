# Copyright (c) 2026 NightWorksIO
"""The shapes `device-key` and `device-keys` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type DeviceKeyBacking = typing.Literal["strongbox", "enclave", "tee"]
"""Where a device key lives, as its attestation says."""


__all__ = [
    "DeviceKeyBacking",
]
