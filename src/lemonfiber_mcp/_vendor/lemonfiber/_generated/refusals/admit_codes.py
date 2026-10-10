# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `ADMIT` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

ADMIT: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "ADMIT-10": ListedRefusal(
        "NOT_A_PASSWORD", 400, "Raised when what was offered at the door is not a password."
    ),
    "ADMIT-11": ListedRefusal(
        "KEY_IN_THE_CLEAR",
        403,
        "Raised when a key arrived from another machine over a connection its pin does not verify.",
    ),
    "ADMIT-12": ListedRefusal(
        "NOT_FOR_A_KEY", 403, "Raised when a key asked for something its scope does not reach."
    ),
    "ADMIT-4": ListedRefusal(
        "NOT_ADMITTED", 403, "Raised when a request carried no token, session or key this run admits."
    ),
    "ADMIT-5": ListedRefusal(
        "ELSEWHERE", 403, "Raised when a request said it came from somewhere this server is not."
    ),
    "ADMIT-6": ListedRefusal(
        "NOT_YOURS", 403, "Raised when an account asked for something that is not its to ask for."
    ),
    "ADMIT-7": ListedRefusal(
        "UNCONFIRMED", 403, "Raised when the media server could not say whether an account is still one."
    ),
    "ADMIT-8": ListedRefusal(
        "NOT_THE_PASSWORD", 401, "Raised when the password offered at the door was wrong, or none is set."
    ),
    "ADMIT-9": ListedRefusal(
        "TOO_MANY_ATTEMPTS", 429, "Raised when the door has been given too many wrong passwords lately."
    ),
}
"""What the contract says of each `ADMIT` code."""
