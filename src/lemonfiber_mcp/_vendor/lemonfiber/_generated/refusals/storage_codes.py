# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `STORAGE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

STORAGE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "STORAGE-9": ListedRefusal(
        "ROOT_REFUSED",
        409,
        "Raised where `DATA_ROOT` names an NFS export lemonfiber cannot write into the mount options, so no project is written from it.",
    ),
}
"""What the contract says of each `STORAGE` code."""
