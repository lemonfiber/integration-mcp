# Copyright (c) 2026 NightWorksIO
"""The `job` envelope, and the shapes only `job` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class JobEnvelope(typing.TypedDict):
    """The envelope carrying `job`."""

    api_version: int
    data: Started
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["job"]


class Started(typing.TypedDict):
    """Work that outlives the request that started it: its name, and what it was.

    The action is carried beside the name because a client holding several has to
    tell them apart, and asking it to remember which name it gave which request is
    asking it to keep a second copy of what this already knows.
    """

    action: str
    """The action that was asked for, as it was named."""
    job: str
    """The name to ask what became of this work by."""


__all__ = [
    "JobEnvelope",
    "Started",
]
