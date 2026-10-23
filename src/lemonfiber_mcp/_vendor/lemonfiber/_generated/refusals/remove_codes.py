# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `REMOVE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

REMOVE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "REMOVE-7": ListedRefusal(
        "REMOVAL_MOVED",
        400,
        "Said where the offer answered is not the one a reading of the removal makes now.",
    ),
}
"""What the contract says of each `REMOVE` code."""
