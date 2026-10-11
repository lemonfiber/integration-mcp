# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `BUNDLE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

BUNDLE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "BUNDLE-8": ListedRefusal(
        "BUNDLE_NOT_HELD", 404, "Raised when a name does not name one of the bundles this run kept."
    ),
}
"""What the contract says of each `BUNDLE` code."""
