# Copyright (c) 2026 NightWorksIO
"""The `copying` envelope, and the shapes only `copying` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.instant import Instant
from ..shared.tree import Tree


type CopiedScope = CopiedScopeWholeStack | CopiedScopeService | CopiedScopeExisting
"""What a running copy copies, as its reading names it."""


class CopiedScopeExisting(typing.TypedDict):
    """An existing setup's own configuration."""

    project: typing.NotRequired[str | None]
    """The Compose project it copies, to the operator alone."""
    scope: typing.Literal["existing"]
    trees: typing.NotRequired[list[Tree] | None]
    """The host trees it copies, to the operator alone."""


class CopiedScopeService(typing.TypedDict):
    """One named service's configuration alone."""

    name: str
    """The service whose configuration it copies."""
    scope: typing.Literal["service"]


class CopiedScopeWholeStack(typing.TypedDict):
    """Every service's configuration, plus lemonfiber's own and the stack."""

    scope: typing.Literal["whole_stack"]


type CopyWhat = typing.Literal["backup", "restore"]
"""Whether a copy is a backup or a restore."""


class CopyingEnvelope(typing.TypedDict):
    """The envelope carrying `copying`."""

    api_version: int
    data: CopyingReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["copying"]


class CopyingReport(typing.TypedDict):
    """The backup or restore running on this machine now, or none."""

    running: typing.NotRequired[RunningCopy | None]
    """The copy running now, or none."""


type RunningCopy = RunningCopyWorking | RunningCopyPaced | RunningCopyStalled
"""A backup or restore running now."""


class RunningCopyPaced(typing.TypedDict):
    """Held to the operator's limit."""

    job: typing.NotRequired[str | None]
    """The name an accepting reply gave the work, where one did."""
    limit: int
    """The limit, in bytes a second."""
    part: str
    """The area being written now, named."""
    scope: CopiedScope
    """What it copies."""
    started: Instant
    """When it started."""
    state: typing.Literal["paced"]
    what: CopyWhat
    """Whether it is a backup or a restore."""
    whole: int
    """The bytes it will write."""
    written: int
    """The bytes written so far."""


class RunningCopyStalled(typing.TypedDict):
    """Nothing written for the minutes the operator's setting holds."""

    job: typing.NotRequired[str | None]
    """The name an accepting reply gave the work, where one did."""
    part: str
    """The area being written now, named."""
    scope: CopiedScope
    """What it copies."""
    started: Instant
    """When it started."""
    state: typing.Literal["stalled"]
    what: CopyWhat
    """Whether it is a backup or a restore."""
    whole: int
    """The bytes it will write."""
    written: int
    """The bytes written so far."""
    wrote: Instant
    """The instant it last wrote."""


class RunningCopyWorking(typing.TypedDict):
    """Writing as fast as it can."""

    job: typing.NotRequired[str | None]
    """The name an accepting reply gave the work, where one did."""
    part: str
    """The area being written now, named."""
    scope: CopiedScope
    """What it copies."""
    started: Instant
    """When it started."""
    state: typing.Literal["working"]
    what: CopyWhat
    """Whether it is a backup or a restore."""
    whole: int
    """The bytes it will write."""
    written: int
    """The bytes written so far."""


__all__ = [
    "CopiedScope",
    "CopiedScopeExisting",
    "CopiedScopeService",
    "CopiedScopeWholeStack",
    "CopyWhat",
    "CopyingEnvelope",
    "CopyingReport",
    "RunningCopy",
    "RunningCopyPaced",
    "RunningCopyStalled",
    "RunningCopyWorking",
]
