# Copyright (c) 2026 NightWorksIO
"""The `version` envelope, and the shapes only `version` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.update__version import Notes


class VersionEnvelope(typing.TypedDict):
    """The envelope carrying `version`."""

    api_version: int
    data: VersionReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["version"]


class VersionReport(typing.TypedDict):
    """What versions are in play: the binary, the stack it operates, and what changed.

    The changelog is here rather than behind a request of its own because it answers
    the second half of the same question. \"Which version am I on\" is asked by
    somebody deciding whether to move, and what they need next is what the version
    they are on actually brought — so every surface that already reaches this read
    reaches both halves, and none of the three had to learn a new question.
    """

    binary: str
    """The running binary's version."""
    changelog: Notes
    """What this build's release changed, and every release there has been."""
    compose: typing.NotRequired[str | None]
    """What the container engine reports, when it could be asked."""
    stack: str
    """The version of the stack this build operates."""
    supported_schema: list[int]
    """The manifest schema generations this build reads."""


__all__ = [
    "VersionEnvelope",
    "VersionReport",
]
