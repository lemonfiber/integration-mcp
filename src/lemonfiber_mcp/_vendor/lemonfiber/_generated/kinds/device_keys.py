# Copyright (c) 2026 NightWorksIO
"""The `device-keys` envelope, and the shapes only `device-keys` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.device_key__device_keys import DeviceKeyBacking


class DeviceKeyListing(typing.TypedDict):
    """Every device key this machine has registered, and what became of a revoke."""

    keys: list[ListedDeviceKey]
    """In the order they were registered."""
    rehearsed: bool
    """Whether this was a rehearsal: what revoking would come to, with nothing revoked."""
    revoked: typing.NotRequired[str | None]
    """The device key this request revoked, where it revoked one."""


class DeviceKeysEnvelope(typing.TypedDict):
    """The envelope carrying `device-keys`."""

    api_version: int
    data: DeviceKeyListing
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["device-keys"]


class ListedDeviceKey(typing.TypedDict):
    """One device key as the listing shows it."""

    app: str
    """The app that made it."""
    backing: DeviceKeyBacking
    """Where it lives, as its attestation said."""
    fingerprint: str
    """The SHA-256 of its public half's `SubjectPublicKeyInfo`, in lower-case hex."""
    name: str
    """The name it was registered under."""
    registered: str
    """When it was registered."""
    revoked: typing.NotRequired[str | None]
    """When it was revoked, where it has been."""
    used: typing.NotRequired[str | None]
    """When it last proved a mint, where it has."""


__all__ = [
    "DeviceKeyListing",
    "DeviceKeysEnvelope",
    "ListedDeviceKey",
]
