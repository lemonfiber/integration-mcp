# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `STACK` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

STACK: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "STACK-1": ListedRefusal(
        "STACK_UNREADABLE", 500, "Raised when a stack directory holds no readable manifest."
    ),
    "STACK-10": ListedRefusal(
        "STACK_UNASSEMBLED", 500, "Raised when a manifest's files are not laid out as the contract says."
    ),
    "STACK-11": ListedRefusal(
        "PROJECT_EDITED",
        409,
        "Raised when a change would write over a generated project the operator has edited.",
    ),
    "STACK-13": ListedRefusal(
        "RESET_MOVED", 400, "Raised where the offer a reset answers is not the one a reading of it makes now."
    ),
    "STACK-15": ListedRefusal(
        "SERVICE_UNFENCED", 409, "Raised where a start names a fenced service no fence can be written for."
    ),
    "STACK-2": ListedRefusal(
        "STACK_UNUSABLE", 500, "Raised when a manifest is readable and this build cannot use it."
    ),
    "STACK-4": ListedRefusal(
        "STACK_NOT_SET_UP", 500, "Raised when lemonfiber has nowhere to write the stack."
    ),
    "STACK-5": ListedRefusal("STACK_NOT_WRITTEN", 500, "Raised when the stack could not be written to disk."),
    "STACK-6": ListedRefusal("STACK_INVALID", 500, "Raised when a manifest parses and breaks the contract."),
    "STACK-7": ListedRefusal("STACK_MALFORMED", 500, "Raised when a manifest is not TOML at all."),
    "STACK-8": ListedRefusal(
        "STACK_UNRECOGNISED", 500, "Raised when a manifest declares names this build does not know."
    ),
    "STACK-9": ListedRefusal(
        "STACK_NEEDS_NEWER", 500, "Raised when a stack names a newer lemonfiber than the one running."
    ),
}
"""What the contract says of each `STACK` code."""
