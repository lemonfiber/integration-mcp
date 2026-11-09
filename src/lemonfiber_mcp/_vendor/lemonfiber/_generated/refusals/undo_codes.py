# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `UNDO` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

UNDO: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "UNDO-5": ListedRefusal(
        "MOVED_FOR_GOOD",
        409,
        "Raised when a run moved one of lemonfiber's own guards onto its plugin, which no undo or removal puts back.",
    ),
}
"""What the contract says of each `UNDO` code."""
