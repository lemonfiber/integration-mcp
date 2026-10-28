# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `SETTING` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

SETTING: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "SETTING-1": ListedRefusal(
        "NO_SUCH_SETTING", 404, "Raised where nothing in this stack reads a setting by the name given."
    ),
    "SETTING-2": ListedRefusal(
        "A_SECRET", 400, "Raised where the name given is a secret's, which this command never writes."
    ),
    "SETTING-3": ListedRefusal(
        "TAKEN_ELSEWHERE",
        400,
        "Raised where the name given belongs to the other of the two commands that write settings.",
    ),
    "SETTING-4": ListedRefusal(
        "UNWRITABLE_VALUE", 400, "Raised where a value cannot be written as the setting asked for."
    ),
    "SETTING-5": ListedRefusal(
        "SETTINGS_MOVED",
        400,
        "Raised when a change answers an offer read against settings that have since moved.",
    ),
    "SETTING-6": ListedRefusal(
        "ALREADY_HOLDS", 400, "Raised where the setting already holds what the change asks for."
    ),
    "SETTING-7": ListedRefusal(
        "OUTSIDE_ITS_CHOICES",
        400,
        "Raised where a change would leave a setting holding a value outside its choices.",
    ),
}
"""What the contract says of each `SETTING` code."""
