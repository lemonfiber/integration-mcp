# Copyright (c) 2026 NightWorksIO
"""The `device-challenge` envelope, and the shapes only `device-challenge` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class DeviceChallenge(typing.TypedDict):
    """A challenge, as the phone is handed it to sign."""

    challenge: str
    """The challenge, in base64url, signed as it is written here."""
    expires: str
    """When it stops standing, one minute after it was issued."""


class DeviceChallengeEnvelope(typing.TypedDict):
    """The envelope carrying `device-challenge`."""

    api_version: int
    data: DeviceChallenge
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["device-challenge"]


__all__ = [
    "DeviceChallenge",
    "DeviceChallengeEnvelope",
]
