# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `GONE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

GONE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "GONE-2": ListedRefusal(
        "ANOTHER_READING",
        400,
        "Raised when an agreement names a reading of this machine that is not the one standing now.",
    ),
}
"""What the contract says of each `GONE` code."""
