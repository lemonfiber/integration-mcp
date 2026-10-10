# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `RATE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

RATE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "RATE-6": ListedRefusal(
        "PAUSING_MOVED",
        400,
        "Raised where pausing or resuming the download clients names an offer that is not the one a fresh look at them builds.",
    ),
}
"""What the contract says of each `RATE` code."""
