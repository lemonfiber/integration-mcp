# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `ASK` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

ASK: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "ASK-1": ListedRefusal(
        "NO_SUCH_ACTION", 404, "Raised where no action goes by the name that was asked for."
    ),
    "ASK-10": ListedRefusal(
        "WRONG_METHOD", 405, "Raised where an endpoint was asked with a method it does not answer."
    ),
    "ASK-11": ListedRefusal(
        "NOT_A_KEY_REQUEST",
        400,
        "Raised where the body of a mint is not a key's name, scope, purpose and the password.",
    ),
    "ASK-12": ListedRefusal(
        "NOT_AN_IDEMPOTENCY_KEY",
        400,
        "Raised where an action's `Idempotency-Key` is not one to 255 visible characters, or is given more than once.",
    ),
    "ASK-13": ListedRefusal(
        "IDEMPOTENCY_KEY_REUSED",
        400,
        "Raised where an `Idempotency-Key` already sent with one action and its arguments is sent with another.",
    ),
    "ASK-2": ListedRefusal(
        "MISSING_ARGUMENT", 400, "Raised where an action was not given an argument it needs."
    ),
    "ASK-3": ListedRefusal(
        "UNRECOGNISED_ARGUMENT", 400, "Raised where an argument was given a value that names nothing."
    ),
    "ASK-4": ListedRefusal(
        "UNWANTED_ARGUMENT",
        400,
        "Raised where an action was given an argument its command has nowhere to put.",
    ),
    "ASK-5": ListedRefusal(
        "ARGUMENTS_TOGETHER",
        400,
        "Raised where two arguments that each name a different request arrived together.",
    ),
    "ASK-6": ListedRefusal(
        "NOT_ARGUMENTS", 400, "Raised where the body of an action is not arguments it can read."
    ),
    "ASK-7": ListedRefusal(
        "NO_SUCH_JOB", 404, "Raised where a job was asked about that this run did not start."
    ),
    "ASK-8": ListedRefusal(
        "NOT_AN_ANSWER", 400, "Raised where the body of a setup step is not an answer it can read."
    ),
    "ASK-9": ListedRefusal(
        "NO_ENDPOINT", 404, "Raised where a path under the endpoints is one no endpoint answers."
    ),
}
"""What the contract says of each `ASK` code."""
