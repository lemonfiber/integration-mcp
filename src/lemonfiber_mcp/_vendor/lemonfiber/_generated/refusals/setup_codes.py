# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `SETUP` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

SETUP: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "SETUP-1": ListedRefusal(
        "NOT_REVIEWED", 400, "Raised when apply is asked for before the answers have been reviewed."
    ),
    "SETUP-16": ListedRefusal(
        "GUARD_UNANSWERED",
        400,
        "Raised when a VPN answer leaves the egress guard without what it needs to start.",
    ),
    "SETUP-5": ListedRefusal(
        "DOES_NOT_APPLY", 400, "Raised when an answer is not meaningful on the platform setup is running on."
    ),
    "SETUP-7": ListedRefusal(
        "ALREADY_SET_UP", 400, "Raised when setup is answered on a machine that is already set up."
    ),
    "SETUP-8": ListedRefusal(
        "NOTHING_TO_RECOVER", 400, "Raised when a recovery is asked for and no apply stopped part-way."
    ),
}
"""What the contract says of each `SETUP` code."""
