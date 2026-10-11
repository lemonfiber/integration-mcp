# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `WORD` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

WORD: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "WORD-1": ListedRefusal(
        "UNRECOGNISED",
        404,
        "A word this product does not explain, as a refusal that says what it does. Through the error model rather than a bare line, so it carries a code and a way forward like every other refusal \u2014 and the way forward is the list itself, which is short enough to be the answer rather than a pointer at one. It lies in the naming: the word is the whole of what was asked for, and there is no entry for it. A surface that reported this as its own failure would be telling a caller to try again at something that will never work.",
    ),
}
"""What the contract says of each `WORD` code."""
