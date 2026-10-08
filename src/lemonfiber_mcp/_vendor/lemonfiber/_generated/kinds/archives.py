# Copyright (c) 2026 NightWorksIO
"""The `archives` envelope, and the shapes only `archives` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class ArchivesEnvelope(typing.TypedDict):
    """The envelope carrying `archives`."""

    api_version: int
    data: Listing
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["archives"]


class Listing(typing.TypedDict):
    """The archives this machine has kept."""

    archives: list[str]
    """Each one by the name it was written under, newest first.

    The name is the whole of what another surface needs: it is what a restore
    asks for, and it carries the moment the archive was taken and what it
    covers, because that is how a capture names one.
    """


__all__ = [
    "ArchivesEnvelope",
    "Listing",
]
