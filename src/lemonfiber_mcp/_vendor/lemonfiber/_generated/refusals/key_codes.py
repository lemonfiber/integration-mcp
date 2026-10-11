# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `KEY` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

KEY: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "KEY-1": ListedRefusal(
        "BAD_NAME", 400, "Raised when a key is asked for under a word that cannot name one."
    ),
    "KEY-10": ListedRefusal("NO_SUCH_KEY", 404, "Raised when no active key holds the name a revoke gave."),
    "KEY-11": ListedRefusal(
        "MEMBERS_MAY_NOT_MINT",
        409,
        "Raised when a household member asks to mint a key and the operator has not allowed members to.",
    ),
    "KEY-12": ListedRefusal(
        "CLAIM_NOT_OPEN",
        401,
        "Raised when a key is asked to be collected with a claim that collects nothing.",
    ),
    "KEY-13": ListedRefusal(
        "UNLINKABLE",
        409,
        "Raised when a key is asked to be minted as a claim and no address another machine reaches can go in its link.",
    ),
    "KEY-2": ListedRefusal(
        "NOT_A_SCOPE", 400, "Raised when a key is asked for with a scope that is none of the three."
    ),
    "KEY-3": ListedRefusal(
        "NOT_A_PURPOSE", 400, "Raised when a key is asked for with a purpose that is none of the three."
    ),
    "KEY-5": ListedRefusal(
        "NAME_TAKEN", 400, "Raised when a key is asked for under a name another key holds."
    ),
    "KEY-6": ListedRefusal(
        "NO_SUCH_MEMBER", 404, "Raised when a member's key names an account the household does not hold."
    ),
    "KEY-8": ListedRefusal(
        "NOT_FOR_YOURSELF",
        400,
        "Raised when a household member asks for a key, or a revoke, that is not theirs alone.",
    ),
}
"""What the contract says of each `KEY` code."""
