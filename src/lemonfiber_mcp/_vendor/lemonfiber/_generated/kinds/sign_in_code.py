# Copyright (c) 2026 NightWorksIO
"""The `sign-in-code` envelope, and the shapes only `sign-in-code` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.instant import Instant


class SignInCode(typing.TypedDict):
    """A code to sign in by, or the sign-in by a code still waiting."""

    approve_at: typing.NotRequired[str | None]
    """Where the member approves the code, where one was just asked for."""
    code: typing.NotRequired[str | None]
    """The code the member enters where they approve it, where one was just asked for."""
    lapses_at: Instant
    """When the code lapses."""
    waiting: str
    """The handle that finishes signing in by the code."""


class SignInCodeEnvelope(typing.TypedDict):
    """The envelope carrying `sign-in-code`."""

    api_version: int
    data: SignInCode
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["sign-in-code"]


__all__ = [
    "SignInCode",
    "SignInCodeEnvelope",
]
