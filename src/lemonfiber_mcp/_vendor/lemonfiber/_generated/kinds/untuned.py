# Copyright (c) 2026 NightWorksIO
"""The `untuned` envelope, and the shapes only `untuned` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Untuned(typing.TypedDict):
    """How many live streams whose passes lapsed unrenewed were closed."""

    closed: int
    """How many were closed."""


class UntunedEnvelope(typing.TypedDict):
    """The envelope carrying `untuned`."""

    api_version: int
    data: Untuned
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["untuned"]


__all__ = [
    "Untuned",
    "UntunedEnvelope",
]
