# Copyright (c) 2026 NightWorksIO
"""The `stop-seeding` envelope, and the shapes only `stop-seeding` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.space__stop_seeding import Candidate


class Gone(typing.TypedDict):
    """What became of a download the client was asked to let go."""

    bytes: int
    """What it occupied, as the client reported it."""
    name: str
    """What the client is no longer holding."""
    rehearsed: bool
    """Whether this was a rehearsal, which asks the client for nothing."""


class Letting(typing.TypedDict):
    """One completed download, what letting it go would cost, and what became of it."""

    agreement: str
    """What this offer names itself, so an answer to it can say which offer it
    answered.
    """
    download: Candidate
    """The download, in the same words the account names it in: where it stands, what
    it occupies, and what removing it costs.
    """
    goes: str
    """What goes with it, carried rather than left for a surface to remember."""
    gone: typing.NotRequired[Gone | None]
    """What became of an answered offer, and nothing where the offer is all this is."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


class StopSeedingEnvelope(typing.TypedDict):
    """The envelope carrying `stop-seeding`."""

    api_version: int
    data: Letting
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["stop-seeding"]


__all__ = [
    "Gone",
    "Letting",
    "StopSeedingEnvelope",
]
