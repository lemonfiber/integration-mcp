# Copyright (c) 2026 NightWorksIO
"""The `standing` envelope, and the shapes only `standing` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class StackStanding(typing.TypedDict):
    """What the web API composes its routes and its answers from."""

    members_mint: bool
    """Whether household members may mint keys for themselves."""
    stack: typing.NotRequired[str | None]
    """The stack's own identifier, the one pairing material carries; absent where this
    machine has nowhere to keep one.
    """
    switched_off: list[str]
    """Each setting a command is refused without that is off on this machine."""
    told: bool
    """Whether a way to be told is configured."""
    waiting: bool
    """Whether a phone's push endpoint is waiting to be woken."""


class StandingEnvelope(typing.TypedDict):
    """The envelope carrying `standing`."""

    api_version: int
    data: StackStanding
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["standing"]


__all__ = [
    "StackStanding",
    "StandingEnvelope",
]
