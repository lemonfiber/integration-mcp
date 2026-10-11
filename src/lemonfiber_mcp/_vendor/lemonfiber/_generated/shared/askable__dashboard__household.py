# Copyright (c) 2026 NightWorksIO
"""The shapes `askable`, `dashboard` and `household` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type AskingStanding = typing.Literal["unlimited", "within-quota", "near-quota", "quota-exhausted"]
"""Where one member stands against what a period allows them.

Four, and the one worth having is the middle: somebody told only when they have run
out has been told too late to do anything but wait, which is the answer this whole
feature exists to avoid handing anybody.
"""


class Counted(typing.TypedDict):
    """One of the two counts the request service keeps, and what it has left."""

    limit: typing.NotRequired[int | None]
    """How many the period allows. Absent where nothing limits them, which is a
    different answer from a limit of nought.
    """
    period: typing.NotRequired[str | None]
    """How long the period is, in the words a household says it in — absent where
    the count runs from the beginning rather than over a window.
    """
    remaining: typing.NotRequired[int | None]
    """How many more they may ask for. Absent where nothing limits them."""
    used: int
    """How many the period has already counted against them."""


class MemberAsking(typing.TypedDict):
    """What one member may ask for, where the request service could be asked.

    Both counts, because the service keeps them apart and folding them would report a
    household as within its limit while the half that matters is spent: television is
    counted a season at a time, so one ask for a six-season series spends six.
    """

    films: Counted
    """Films, counted one to a request."""
    frees_up: typing.NotRequired[str | None]
    """When the count next lets go of something, so one more becomes possible.

    Absent where nothing limits them, and where the request service's own dates
    could not be read — an invented one would be a promise about a day on which
    nothing happens. The period is a window that rolls rather than a month that
    ends, so this is the moment their earliest counted request ages out.
    """
    policy: Policy
    """What happens to what they ask for."""
    standing: AskingStanding
    """Where they stand against what their period allows, taken over both counts."""
    television: Counted
    """Television, counted one to a season."""


type Policy = typing.Literal["trusted", "within-a-limit", "everything-waits"]
"""What happens to what a household member asks for.

Three, and they are the three the request service can actually be put into. A
household is in one of them because of two settings taken together — whether requests
arrive unseen, and whether a period limits how many — so the words here are a reading
of that pair rather than a fourth setting kept beside it.

Choosing per person is not a fourth policy. It is one of these three chosen for one
member rather than for the house, which is why what a surface offers is a policy and,
separately, who it is for.
"""


__all__ = [
    "AskingStanding",
    "Counted",
    "MemberAsking",
    "Policy",
]
