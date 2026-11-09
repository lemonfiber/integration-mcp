# Copyright (c) 2026 NightWorksIO
"""The `boot` envelope, and the shapes only `boot` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.boot__lifecycle import Forwarded


class BootEnvelope(typing.TypedDict):
    """The envelope carrying `boot`."""

    api_version: int
    data: BootReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["boot"]


type BootOutcome = typing.Literal["passed", "failed", "waiting-for-install"]
"""What a run at boot came to."""


class BootReport(typing.TypedDict):
    """When this machine last started, what the run after it came to, and how long the
    stack has failed to come back.
    """

    booted_at: typing.NotRequired[int | None]
    """When this machine last started, in seconds since the Unix epoch, where it says."""
    declined: typing.NotRequired[str | None]
    """Why a run after that start started nothing, where one did."""
    failed_boots: typing.NotRequired[int | None]
    """How many starts it has failed to come back after since then."""
    failing_since: typing.NotRequired[int | None]
    """Since when the stack has failed to come back, in seconds since the Unix epoch."""
    last_verified: typing.NotRequired[BootVerification | None]
    """The newest verification kept against any start."""
    verified: typing.NotRequired[BootVerification | None]
    """The verification kept against that start, where one ran after it."""


type BootTunnel = BootTunnelHeld | BootTunnelNotEstablished | BootTunnelNotChecked
"""Whether the tunnel came back with the stack."""


class BootTunnelHeld(typing.TypedDict):
    """Its checks passed."""

    state: typing.Literal["held"]


class BootTunnelNotChecked(typing.TypedDict):
    """Nothing checked it: the stack runs no tunnel, did not come up, or could not be
    read.
    """

    state: typing.Literal["not-checked"]


class BootTunnelNotEstablished(typing.TypedDict):
    """A check of it failed."""

    said: str
    """Which, in the stack's words."""
    state: typing.Literal["not-established"]


class BootVerification(typing.TypedDict):
    """What one run at boot that reached the stack came to."""

    against: typing.NotRequired[int | None]
    """When the machine started that the run came after, where it said."""
    at: int
    """When the run finished."""
    not_back: typing.NotRequired[list[str]]
    """Each service that did not come back."""
    outcome: BootOutcome
    """What it came to."""
    port: typing.NotRequired[Forwarded | None]
    """The forwarded port before the start and after it, where the stack forwards one."""
    said: typing.NotRequired[str | None]
    """The sentence the run raised, where it raised one."""
    tunnel: BootTunnel
    """Whether the tunnel came back with the stack."""


__all__ = [
    "BootEnvelope",
    "BootOutcome",
    "BootReport",
    "BootTunnel",
    "BootTunnelHeld",
    "BootTunnelNotChecked",
    "BootTunnelNotEstablished",
    "BootVerification",
]
