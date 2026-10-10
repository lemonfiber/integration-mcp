# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `LIFE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

LIFE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "LIFE-10": ListedRefusal(
        "RESTART_MOVED",
        400,
        "Raised where a restart names an offer that is not the one a fresh look at the stack builds.",
    ),
}
"""What the contract says of each `LIFE` code."""
