# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `CRED` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

CRED: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "CRED-4": ListedRefusal(
        "REPLACEMENT_MOVED",
        400,
        "Raised where a replacement of the media server's internal certificate answers an offer that is not the one a fresh reading builds.",
    ),
}
"""What the contract says of each `CRED` code."""
