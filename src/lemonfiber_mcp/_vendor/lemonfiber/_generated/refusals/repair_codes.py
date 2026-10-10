# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `REPAIR` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

REPAIR: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "REPAIR-1": ListedRefusal(
        "STALE", 400, "Raised when consent was given for an offer that no longer stands."
    ),
}
"""What the contract says of each `REPAIR` code."""
