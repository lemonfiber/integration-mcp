# Copyright (c) 2026 NightWorksIO
"""The `capabilities` envelope, and the shapes only `capabilities` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Capabilities(typing.TypedDict):
    """Every capability this stack has, by the path its request is served at."""

    capabilities: dict[str, CapabilityState]
    """What each comes to for the credential that asked. A request this stack does
    not have is absent rather than listed as anything.
    """
    scope: CredentialScope
    """Whose credential asked."""
    stack: typing.NotRequired[str | None]
    """The stack's own identifier, the one pairing material carries, to every credential
    alike: what tells two credentials apart from two stacks. Never the address or the
    certificate, which re-pairing exists to change. Absent only where this machine
    has nowhere to keep one.
    """


class CapabilitiesEnvelope(typing.TypedDict):
    """The envelope carrying `capabilities`."""

    api_version: int
    data: Capabilities
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["capabilities"]


type CapabilityState = typing.Literal["available", "unconfigured", "unpermitted"]
"""What one capability comes to for the credential that asked."""


type CredentialScope = typing.Literal["operator", "read", "act", "member"]
"""Whose credential asked, as a client is told it.

Said rather than left to be inferred from which requests are permitted: a client
guessing a member from a missing read would guess wrong the day that read moves.
"""


__all__ = [
    "Capabilities",
    "CapabilitiesEnvelope",
    "CapabilityState",
    "CredentialScope",
]
