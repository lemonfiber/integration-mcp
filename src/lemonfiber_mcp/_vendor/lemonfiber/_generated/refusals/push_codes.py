# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `PUSH` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

PUSH: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "PUSH-1": ListedRefusal(
        "NOT_A_PUSH_NAME", 400, "Raised when a push endpoint is registered under a word that cannot name one."
    ),
    "PUSH-2": ListedRefusal(
        "PUSH_NAME_TAKEN", 409, "Raised when a push endpoint is registered under a name another holds."
    ),
    "PUSH-3": ListedRefusal(
        "PUSH_NOT_HTTPS", 400, "Raised when a push endpoint's address is not an `https` address."
    ),
    "PUSH-4": ListedRefusal(
        "PUSH_KEYS_UNREADABLE", 400, "Raised when the keys a push endpoint gave cannot be encrypted to."
    ),
    "PUSH-5": ListedRefusal(
        "PUSH_NOT_REGISTERED", 404, "Raised when no push endpoint holds the name asked about."
    ),
}
"""What the contract says of each `PUSH` code."""
