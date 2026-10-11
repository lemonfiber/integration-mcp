# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `REHEARSE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

REHEARSE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "REHEARSE-1": ListedRefusal(
        "CANNOT", 400, "The flag cannot be honoured by this command, and never will be."
    ),
    "REHEARSE-2": ListedRefusal("NOT_YET", 400, "The flag is not honoured by this command yet."),
}
"""What the contract says of each `REHEARSE` code."""
