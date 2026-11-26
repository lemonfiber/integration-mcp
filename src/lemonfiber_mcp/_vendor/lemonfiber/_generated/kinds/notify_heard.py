# Copyright (c) 2026 NightWorksIO
"""The `notify-heard` envelope, and the shapes only `notify-heard` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Heard(typing.TypedDict):
    """Which service told of an event."""

    service: str
    """The service whose key it presented."""


class NotifyHeardEnvelope(typing.TypedDict):
    """The envelope carrying `notify-heard`."""

    api_version: int
    data: Heard
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["notify-heard"]


__all__ = [
    "Heard",
    "NotifyHeardEnvelope",
]
