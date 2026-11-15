# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `NOTIFY` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

NOTIFY: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "NOTIFY-1": ListedRefusal(
        "NOT_A_BACKEND_NAME", 400, "Raised when a back-end is added under a word that cannot name one."
    ),
    "NOTIFY-10": ListedRefusal(
        "EVENTS_REFUSED", 401, "Raised when an event arrives without the key the core gave its sender."
    ),
    "NOTIFY-2": ListedRefusal(
        "BACKEND_NAME_TAKEN", 409, "Raised when a back-end is added under a name another holds."
    ),
    "NOTIFY-3": ListedRefusal("NO_SUCH_BACKEND", 404, "Raised when no back-end holds the name asked about."),
    "NOTIFY-4": ListedRefusal(
        "HOSTED_UNACKNOWLEDGED",
        400,
        "Raised when a back-end on a host that is not the household's own is added without saying so.",
    ),
    "NOTIFY-5": ListedRefusal(
        "NOT_A_BACKEND_ADDRESS", 400, "Raised when a back-end's address is not one it can be reached at."
    ),
    "NOTIFY-6": ListedRefusal(
        "BACKEND_INCOMPLETE", 400, "Raised when a back-end is added without what its kind needs."
    ),
    "NOTIFY-7": ListedRefusal(
        "NOT_A_RETRY_SCHEDULE", 400, "Raised when a back-end's attempts and delays do not agree."
    ),
    "NOTIFY-8": ListedRefusal(
        "NOT_OFFERED", 400, "Raised when a member chooses a back-end that is not offered to members."
    ),
    "NOTIFY-9": ListedRefusal("NO_SUCH_WAKE", 404, "Raised when a phone confirms a wake nobody sent it."),
}
"""What the contract says of each `NOTIFY` code."""
