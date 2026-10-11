# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `WISH` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

WISH: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "WISH-1": ListedRefusal(
        "NOT_A_SEARCH", 400, "Said where the words searched for are too few or too many to search with."
    ),
    "WISH-10": ListedRefusal(
        "NOT_ITS_SEASON",
        400,
        "Said where a season named is not one the title has, or seasons were named for a film.",
    ),
    "WISH-11": ListedRefusal(
        "NOBODY_ASKING", 400, "Said where nobody is named for something only a member can do."
    ),
    "WISH-12": ListedRefusal(
        "NOT_A_MEMBER", 404, "Said where the member named is not somebody in the household."
    ),
    "WISH-13": ListedRefusal(
        "NO_PICTURE", 404, "Said where a title a member may ask for has no picture to show them."
    ),
    "WISH-2": ListedRefusal(
        "NOT_A_PLACE",
        400,
        "Said where the place a search was asked to go on from is not one a page answered.",
    ),
    "WISH-3": ListedRefusal(
        "NOT_ASKABLE", 404, "Said where no title this member may ask for goes by the id and kind named."
    ),
    "WISH-4": ListedRefusal(
        "CANNOT_FETCH", 409, "Said where the house cannot fetch that kind of title, or anything, right now."
    ),
    "WISH-5": ListedRefusal("ALREADY_HERE", 409, "Said where the title asked for is already in the house."),
    "WISH-6": ListedRefusal(
        "NOTHING_LEFT",
        409,
        "Said where the member has asked for all their allowance lets them, until it frees up.",
    ),
    "WISH-7": ListedRefusal(
        "NO_ROOM",
        503,
        "Said where the house has no room for new things, which is the house's and nobody's limit.",
    ),
    "WISH-8": ListedRefusal(
        "NOT_WORKING",
        503,
        "Said where what answers the household's asks did not answer, so nothing was asked.",
    ),
    "WISH-9": ListedRefusal(
        "NOT_SET_UP", 503, "Said where the house has nothing to search or ask with at all."
    ),
}
"""What the contract says of each `WISH` code."""
