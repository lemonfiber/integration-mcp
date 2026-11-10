# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `SPACE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

SPACE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "SPACE-2": ListedRefusal("NOWHERE_TO_MEASURE", 400, "Raised when there is no data location to measure."),
    "SPACE-4": ListedRefusal(
        "NOTHING_TO_ASK",
        400,
        "Raised when there is no torrent client here to be holding a completed download.",
    ),
    "SPACE-5": ListedRefusal(
        "NOT_HELD", 400, "Raised when the client answers and is holding nothing of the name given."
    ),
    "SPACE-6": ListedRefusal(
        "ANOTHER_OFFER", 400, "Raised when an agreement names an offer that is not the one standing now."
    ),
    "SPACE-8": ListedRefusal(
        "NOT_ON_OFFER",
        400,
        "Raised when an answer narrows to a category its offer does not hold as costing nothing.",
    ),
}
"""What the contract says of each `SPACE` code."""
