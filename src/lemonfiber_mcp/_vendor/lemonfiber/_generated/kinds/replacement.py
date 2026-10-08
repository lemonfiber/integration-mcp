# Copyright (c) 2026 NightWorksIO
"""The `replacement` envelope, and the shapes only `replacement` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.adoption__beside__config__import___replacement import Stance


class ReplaceReport(typing.TypedDict):
    """What standing in place of a setup already here came to, or would come to."""

    agreement: str
    """What this offer names itself: the project and every service it would stop.

    The answer to it is this name, and nothing else is a yes to a replacement. Empty
    where there is nothing to stand in place of, because there is nothing to agree to.
    """
    project: typing.NotRequired[str | None]
    """The project that would be stood in place of."""
    refusal: typing.NotRequired[str | None]
    """Why nothing was stopped, where nothing was."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    stance: Stance
    """Where the act stands."""
    still_running: list[str]
    """The services that would not stop and are still up."""
    stopped: list[str]
    """The services that were stopped."""
    would_stop: list[str]
    """The services that would be stopped, by name."""


class ReplacementEnvelope(typing.TypedDict):
    """The envelope carrying `replacement`."""

    api_version: int
    data: ReplaceReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["replacement"]


__all__ = [
    "ReplaceReport",
    "ReplacementEnvelope",
]
