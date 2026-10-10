# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `MIGRATE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

MIGRATE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "MIGRATE-1": ListedRefusal(
        "OFFER_MOVED",
        400,
        "Raised when a replacement was agreed to for an offer that is not the one standing now.",
    ),
}
"""What the contract says of each `MIGRATE` code."""
