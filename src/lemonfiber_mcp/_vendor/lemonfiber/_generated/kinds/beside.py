# Copyright (c) 2026 NightWorksIO
"""The `beside` envelope, and the shapes only `beside` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.adoption__beside__config__import___replacement import Stance
from ..shared.beside__migration import MovedReport


class BesideEnvelope(typing.TypedDict):
    """The envelope carrying `beside`."""

    api_version: int
    data: BesideReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["beside"]


class BesideReport(typing.TypedDict):
    """What standing lemonfiber beside an existing setup came to, or would come to."""

    ports: list[MovedReport]
    """Where each service would listen instead, lowest original port first."""
    refusal: typing.NotRequired[str | None]
    """Why nothing was written, where nothing was."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    stance: Stance
    """Where the act stands."""
    written: typing.NotRequired[str | None]
    """Where the Compose file that says so was written."""


__all__ = [
    "BesideEnvelope",
    "BesideReport",
]
