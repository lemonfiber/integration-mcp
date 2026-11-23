# Copyright (c) 2026 NightWorksIO
"""The `password` envelope, and the shapes only `password` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class PasswordEnvelope(typing.TypedDict):
    """The envelope carrying `password`."""

    api_version: int
    data: PasswordReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["password"]


class PasswordReport(typing.TypedDict):
    """What setting the password came to."""

    device_keys_revoked: bool
    """Whether every device key registered under the password before was revoked."""


__all__ = [
    "PasswordEnvelope",
    "PasswordReport",
]
