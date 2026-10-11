# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `RATE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

RATE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "RATE-1": ListedRefusal(
        "NOTHING_MEASURED", 400, "Raised when a limit is expressed as a share of a line nothing has measured."
    ),
    "RATE-2": ListedRefusal(
        "NO_ZONE",
        400,
        "Raised when a schedule is asked for and nothing says which zone the clients would read it in.",
    ),
    "RATE-3": ListedRefusal(
        "LIMIT_UNREADABLE",
        400,
        "Raised when what was asked for could not be read as a limit, a window or a cap.",
    ),
    "RATE-4": ListedRefusal("NOTHING_TO_LIMIT", 400, "Raised when there is no download client to limit."),
    "RATE-5": ListedRefusal(
        "NOTHING_TO_PAUSE", 400, "Raised when there is no download client to pause or resume."
    ),
    "RATE-6": ListedRefusal(
        "PAUSING_MOVED",
        400,
        "Raised where pausing or resuming the download clients names an offer that is not the one a fresh look at them builds.",
    ),
}
"""What the contract says of each `RATE` code."""
