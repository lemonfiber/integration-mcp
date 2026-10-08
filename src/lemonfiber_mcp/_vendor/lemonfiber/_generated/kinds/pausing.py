# Copyright (c) 2026 NightWorksIO
"""The `pausing` envelope, and the shapes only `pausing` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.bandwidth__pausing import Pulling


class PausedClient(typing.TypedDict):
    """What one download client said about being paused or resumed."""

    client: str
    """The client, by the name the stack knows it under."""
    now: typing.NotRequired[Pulling | None]
    """What it read back after it was asked. Absent on a rehearsal, which asks nothing,
    and where the client could not be reached.
    """
    unreached: typing.NotRequired[str | None]
    """Why it could not be reached, in its own words where it gave any."""
    was: typing.NotRequired[Pulling | None]
    """Whether it was fetching before it was asked, where it said."""


type Pausing = typing.Literal["pause", "resume"]
"""Which of the two was asked for."""


class PausingEnvelope(typing.TypedDict):
    """The envelope carrying `pausing`."""

    api_version: int
    data: PausingReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["pausing"]


class PausingReport(typing.TypedDict):
    """What pausing or resuming every download client came to."""

    asked: Pausing
    """Which of the two was asked for."""
    caution: typing.NotRequired[str | None]
    """What a resume runs into where a spent cap had stopped the clients: they are let
    go as asked, and the cap stops them again the next time the line is checked.
    """
    clients: list[PausedClient]
    """Every download client the stack runs, in the order the stack declares them."""
    rehearsed: bool
    """Whether this was a rehearsal: what each client is doing now, with nothing asked
    of any of them.
    """


__all__ = [
    "PausedClient",
    "Pausing",
    "PausingEnvelope",
    "PausingReport",
]
