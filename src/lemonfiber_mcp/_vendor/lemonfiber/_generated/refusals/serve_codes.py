# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `SERVE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

SERVE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "SERVE-6": ListedRefusal("UNRENDERABLE", 500, "Raised when an answer could not be rendered."),
    "SERVE-7": ListedRefusal(
        "NO_JOB_NAME", 500, "Raised when this machine will not supply the randomness a job is named with."
    ),
    "SERVE-8": ListedRefusal(
        "UNANSWERED", 500, "Raised when an action's work ended before it had an answer to give."
    ),
}
"""What the contract says of each `SERVE` code."""
