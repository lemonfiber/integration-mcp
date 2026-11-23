# Copyright (c) 2026 NightWorksIO
"""The `walkthrough-offer` envelope, and the shapes only `walkthrough-offer` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.reason import Reason, Shape


class WalkthroughOfferEnvelope(typing.TypedDict):
    """The envelope carrying `walkthrough-offer`."""

    api_version: int
    data: Why
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["walkthrough-offer"]


type Why = WhyVariant1 | WhyVariant2
"""Whether a walkthrough is worth offering to this stack, and which one."""


class WhyVariant1(typing.TypedDict):
    """Offer this shape of walk."""

    offer: Shape


WhyVariant2 = typing.TypedDict(
    "WhyVariant2",
    {
        "not": Reason,
    },
)
"""Do not offer. What is missing first, said as the reason it would have stopped at."""


__all__ = [
    "WalkthroughOfferEnvelope",
    "Why",
    "WhyVariant1",
    "WhyVariant2",
]
