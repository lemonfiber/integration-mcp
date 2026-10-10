# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `RESTORE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

RESTORE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "RESTORE-11": ListedRefusal(
        "MOVED_ON", 400, "Raised when consent was given for a listing that no longer stands."
    ),
}
"""What the contract says of each `RESTORE` code."""
