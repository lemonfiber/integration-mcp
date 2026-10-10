# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `READ` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

READ: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "READ-1": ListedRefusal(
        "UNWANTED", 400, "Raised where a read was given a parameter its answer has nowhere to put."
    ),
    "READ-10": ListedRefusal(
        "TOO_MANY_AT_ONCE", 400, "Raised where more holdings were asked for than one read answers with."
    ),
    "READ-11": ListedRefusal(
        "NO_SUCH_GROUP", 400, "Raised where a diagnosis was narrowed to a group or check that is not one."
    ),
    "READ-12": ListedRefusal(
        "NO_SUCH_REMOVAL", 400, "Raised where a removal was named that is none of the four there are."
    ),
    "READ-13": ListedRefusal(
        "NO_UPDATE_OBJECT",
        400,
        "Raised where moving forward was asked about and neither stack nor self named.",
    ),
    "READ-14": ListedRefusal(
        "NOT_A_LINE_COUNT",
        400,
        "Raised where how many log lines to begin with is not a number within the ceiling.",
    ),
    "READ-15": ListedRefusal(
        "NOT_A_CHOICE", 400, "Raised where a parameter that takes a yes or a no is neither true nor false."
    ),
    "READ-16": ListedRefusal(
        "MEMBER_AND_DEFAULTS",
        400,
        "Raised where a household read named a member and asked for the household's defaults as well.",
    ),
    "READ-2": ListedRefusal(
        "REPEATED", 400, "Raised where a parameter carrying one value was given more than once."
    ),
    "READ-3": ListedRefusal("NO_SUCH_READ", 404, "Raised where no read goes by the name that was asked for."),
    "READ-4": ListedRefusal(
        "NO_TERM", 400, "Raised where a trace was asked for and named nothing to follow."
    ),
    "READ-5": ListedRefusal(
        "NOT_A_SEASON", 400, "Raised where the season to narrow a trace to is not a number."
    ),
    "READ-6": ListedRefusal("NO_SETTING", 400, "Raised where a setting was asked for by an empty name."),
    "READ-7": ListedRefusal(
        "NO_MEMBER", 400, "Raised where a household member was asked for by an empty name."
    ),
    "READ-8": ListedRefusal(
        "NO_SHELF_WITHOUT_A_MEMBER",
        400,
        "Raised where a shelf was asked for and nobody was named whose it is.",
    ),
    "READ-9": ListedRefusal(
        "NOT_A_COUNT", 400, "Raised where how many holdings to answer with is not a whole number."
    ),
}
"""What the contract says of each `READ` code."""
