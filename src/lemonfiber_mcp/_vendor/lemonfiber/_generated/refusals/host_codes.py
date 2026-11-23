# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `HOST` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

HOST: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "HOST-7": ListedRefusal(
        "NOT_SCHEDULED",
        404,
        "Raised when the service named to run on its schedule is no run-and-exit service.",
    ),
}
"""What the contract says of each `HOST` code."""
