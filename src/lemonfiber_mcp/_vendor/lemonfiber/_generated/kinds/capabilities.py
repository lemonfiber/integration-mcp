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


class CapabilitiesEnvelope(typing.TypedDict):
    """The envelope carrying `capabilities`."""

    api_version: int
    data: Capabilities
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["capabilities"]


type CapabilityState = typing.Literal["available", "unconfigured", "unpermitted"]
"""What one capability comes to for the credential that asked."""


__all__ = [
    "Capabilities",
    "CapabilitiesEnvelope",
    "CapabilityState",
]
