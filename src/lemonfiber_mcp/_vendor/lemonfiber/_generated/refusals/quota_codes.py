# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `QUOTA` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

QUOTA: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "QUOTA-2": ListedRefusal(
        "NO_LIMIT", 400, "Raised where a policy that lives inside a limit was chosen without one."
    ),
    "QUOTA-4": ListedRefusal(
        "NOT_WAITING", 404, "Raised where the request named is not one that is waiting on anybody."
    ),
    "QUOTA-5": ListedRefusal(
        "NO_REASON", 400, "Raised where a request was turned down and the reason said nothing."
    ),
    "QUOTA-6": ListedRefusal(
        "NOBODY", 404, "Raised where nobody in the household goes by the name that was given."
    ),
    "QUOTA-7": ListedRefusal(
        "NEVER_HERE", 404, "Raised where the request service holds no account for somebody who has one here."
    ),
}
"""What the contract says of each `QUOTA` code."""
