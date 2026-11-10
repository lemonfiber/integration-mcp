# Copyright (c) 2026 NightWorksIO
"""The `push-endpoints` envelope, and the shapes only `push-endpoints` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class ListedPushEndpoint(typing.TypedDict):
    """One push endpoint as the listing shows it."""

    endpoint: str
    """The `https` address its distributor gave."""
    name: str
    """The name it was registered under."""
    registered: str
    """When it was registered."""


class PushEndpointListing(typing.TypedDict):
    """Every push endpoint, and what became of a removal."""

    endpoints: list[ListedPushEndpoint]
    """In the order they were registered."""
    rehearsed: bool
    """Whether this was a rehearsal: what removing would come to, with nothing removed."""
    removed: typing.NotRequired[str | None]
    """The endpoint this request removed, where it removed one."""


class PushEndpointsEnvelope(typing.TypedDict):
    """The envelope carrying `push-endpoints`."""

    api_version: int
    data: PushEndpointListing
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["push-endpoints"]


__all__ = [
    "ListedPushEndpoint",
    "PushEndpointListing",
    "PushEndpointsEnvelope",
]
