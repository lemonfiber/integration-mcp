# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `UPDATE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

UPDATE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "UPDATE-5": ListedRefusal(
        "UPDATE_MOVED",
        400,
        "Raised where an update names an offer that is not the one a fresh look at the releases builds.",
    ),
}
"""What the contract says of each `UPDATE` code."""
