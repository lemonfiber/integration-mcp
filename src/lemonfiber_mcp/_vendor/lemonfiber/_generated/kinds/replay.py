# Copyright (c) 2026 NightWorksIO
"""The `replay` envelope, and the shapes only `replay` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Replay(typing.TypedDict):
    """What a stream opened again from an id says of what it is handed before going on."""

    alerts: ReplayAlerts
    """Whether it holds every alert raised since the id."""


type ReplayAlerts = typing.Literal["whole", "partial"]
"""Whether a replay holds every alert raised since the id it was asked from."""


class ReplayEnvelope(typing.TypedDict):
    """The envelope carrying `replay`."""

    api_version: int
    data: Replay
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["replay"]


__all__ = [
    "Replay",
    "ReplayAlerts",
    "ReplayEnvelope",
]
