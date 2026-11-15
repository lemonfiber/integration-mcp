# Copyright (c) 2026 NightWorksIO
"""The `ended` envelope, and the shapes only `ended` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Ended(typing.TypedDict):
    """Work that ended before it finished: its name, what it was, and why it ended."""

    action: str
    """The action that was asked for, as it was named."""
    ended: JobEnding
    """Why it ended."""
    job: str
    """The name the work was answered with."""


class EndedEnvelope(typing.TypedDict):
    """The envelope carrying `ended`."""

    api_version: int
    data: Ended
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["ended"]


type JobEnding = typing.Literal["released", "let-go", "quiet"]
"""Why work ended before it finished."""


__all__ = [
    "Ended",
    "EndedEnvelope",
    "JobEnding",
]
