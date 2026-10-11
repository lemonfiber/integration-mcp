# Copyright (c) 2026 NightWorksIO
"""The shapes `plugins` and `wiring` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .config__credentials__doctor__outbound__plugins__wiring__wizard import ValueOrigin


type Reaches = ReachesAsked | ReachesByName
"""What one link reaches, and how that was settled."""


class ReachesAsked(typing.TypedDict):
    """An ask for a capability."""

    capability: str
    """The capability asked for."""
    how: typing.Literal["asked"]
    origins: dict[str, ValueOrigin]
    """Where each service that claims it came from: this build's stack, or a
    named plugin.

    Every claimant rather than only what the ask reaches, because a contest
    reaches nothing and is exactly where an operator most needs to know which of
    the names in front of them is not the stack's.
    """
    services: list[str]
    """What the ask reaches — empty where nothing fills it or a contest stands."""
    settled: WiringSettled
    """How it was settled."""


class ReachesByName(typing.TypedDict):
    """A link deliberately kept to a named service, shown as the exception it is."""

    how: typing.Literal["by-name"]
    service: str
    """The service named."""
    why: str
    """Why it is by name."""


type Whose = typing.Literal["stack", "operator"]
"""Who settled a contest between claimants."""


class Wired(typing.TypedDict):
    """One of the stack's links, answered."""

    by: str
    """The service the link runs from — what asked."""
    origin: ValueOrigin
    """Where the service that asked came from: this build's stack, or a named plugin."""
    reaches: Reaches
    """What it reaches."""


type WiringSettled = (
    WiringSettledOutright
    | WiringSettledEach
    | WiringSettledContested
    | WiringSettledChosen
    | WiringSettledUnfilled
)
"""How an ask was settled."""


class WiringSettledChosen(typing.TypedDict):
    """Several claimants, and a choice is recorded."""

    over: list[str]
    """The ones not chosen, so the choice reads as a choice."""
    settled: typing.Literal["chosen"]
    whose: Whose
    """Who chose."""
    why: typing.NotRequired[str | None]
    """Why, where the chooser said."""


class WiringSettledContested(typing.TypedDict):
    """Several claimants and the link asked for one. Refused until somebody chooses:
    install order, precedence and recency are each a way of being right most of
    the time, and the times they are wrong are somebody's stack answering to the
    wrong software.
    """

    claimants: list[str]
    """Every candidate, named, so a choice is made from a list."""
    settled: typing.Literal["contested"]


class WiringSettledEach(typing.TypedDict):
    """Every claimant, because the link asked for all of them rather than one."""

    settled: typing.Literal["each"]


class WiringSettledOutright(typing.TypedDict):
    """One claimant, and nothing to settle."""

    settled: typing.Literal["outright"]


class WiringSettledUnfilled(typing.TypedDict):
    """Nothing claims it. What asked is named beside this, which is the point."""

    settled: typing.Literal["unfilled"]


__all__ = [
    "Reaches",
    "ReachesAsked",
    "ReachesByName",
    "Whose",
    "Wired",
    "WiringSettled",
    "WiringSettledChosen",
    "WiringSettledContested",
    "WiringSettledEach",
    "WiringSettledOutright",
    "WiringSettledUnfilled",
]
