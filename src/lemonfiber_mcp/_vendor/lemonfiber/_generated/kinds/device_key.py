# Copyright (c) 2026 NightWorksIO
"""The `device-key` envelope, and the shapes only `device-key` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.device_key__device_keys import DeviceKeyBacking


class DeviceKeyEnvelope(typing.TypedDict):
    """The envelope carrying `device-key`."""

    api_version: int
    data: RegisteredDeviceKey
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["device-key"]


class RegisteredDeviceKey(typing.TypedDict):
    """A device key registered."""

    app: str
    """The app that made it, as `LEMONFIBER_DEVICE_KEY_APPS` spells an identity."""
    backing: DeviceKeyBacking
    """Where it lives, as its attestation says."""
    fingerprint: str
    """The SHA-256 of its public half's `SubjectPublicKeyInfo`, in lower-case hex."""
    name: str
    """The name it was registered under."""
    registered: str
    """When it was registered."""


__all__ = [
    "DeviceKeyEnvelope",
    "RegisteredDeviceKey",
]
