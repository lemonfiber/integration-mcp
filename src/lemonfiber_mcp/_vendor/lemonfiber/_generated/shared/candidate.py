# Copyright (c) 2026 NightWorksIO
"""The shapes `space` and `stop-seeding` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Candidate(typing.TypedDict):
    """One completed download, and what reclaiming it would come to."""

    bytes: int
    """What it occupies."""
    consequence: typing.NotRequired[str | None]
    """What removing it costs, where it costs anything."""
    name: str
    """What both sides call it."""
    standing: SeedingStanding
    """Where it stands."""


type SeedingStanding = SeedingStandingNeverImported | SeedingStandingSeeding | SeedingStandingLeftAlone
"""Where one completed download stands."""


class SeedingStandingLeftAlone(typing.TypedDict):
    """The operator asked for this one to be left alone."""

    standing: typing.Literal["left_alone"]


class SeedingStandingNeverImported(typing.TypedDict):
    """Nothing ever linked it into a library: it was never imported, and removing
    it loses nothing.
    """

    standing: typing.Literal["never_imported"]


class SeedingStandingSeeding(typing.TypedDict):
    """It was imported and is still seeding, so removing it has a consequence
    outside this machine.
    """

    ratio: int
    """What it has uploaded against what it downloaded, in hundredths, as the
    client reports it.

    A whole number rather than a fraction because every report this product
    makes is compared for equality somewhere, and a fraction cannot be —
    two figures a client would call the same would not be. The hundredth is
    finer than any decision made on a ratio.
    """
    standing: typing.Literal["seeding"]


__all__ = [
    "Candidate",
    "SeedingStanding",
    "SeedingStandingLeftAlone",
    "SeedingStandingNeverImported",
    "SeedingStandingSeeding",
]
