# Copyright (c) 2026 NightWorksIO
"""The `push-endpoint` envelope, and the shapes only `push-endpoint` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class PushEndpointEnvelope(typing.TypedDict):
    """The envelope carrying `push-endpoint`."""

    api_version: int
    data: RegisteredPushEndpoint
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["push-endpoint"]


class RegisteredPushEndpoint(typing.TypedDict):
    """A push endpoint registered."""

    endpoint: str
    """The `https` address its distributor gave."""
    name: str
    """The name it was registered under."""
    registered: str
    """When it was registered."""
    rehearsed: bool
    """Whether this was a rehearsal: what registering would come to, with nothing kept."""


__all__ = [
    "PushEndpointEnvelope",
    "RegisteredPushEndpoint",
]
