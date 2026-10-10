# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `WIRE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

WIRE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "WIRE-1": ListedRefusal(
        "NO_SUCH_FILLER", 404, "A capability was named that no service in this stack provides."
    ),
    "WIRE-2": ListedRefusal(
        "CANNOT_FILL", 400, "The service named cannot do the thing it was asked to fill."
    ),
    "WIRE-3": ListedRefusal(
        "NOTHING_ASKS",
        400,
        "Nothing in this stack asks for the capability, so a choice would change nothing.",
    ),
    "WIRE-4": ListedRefusal(
        "CHOICE_UNWRITABLE", 500, "The setting recording the choice could not be written."
    ),
    "WIRE-5": ListedRefusal(
        "WIRING_MOVED",
        400,
        "Raised when a choice answers an offer that was read against a wiring that has since moved.",
    ),
    "WIRE-6": ListedRefusal(
        "UNREASONABLE",
        400,
        "Raised when the reason given for a choice is longer than a reason may be, or holds a line break or another control character.",
    ),
    "WIRE-7": ListedRefusal(
        "ALREADY_FILLS",
        400,
        "Raised where the service chosen already fills the capability, so there is nothing to change.",
    ),
}
"""What the contract says of each `WIRE` code."""
