# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `PLAY` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

PLAY: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "PLAY-1": ListedRefusal(
        "NOT_AN_ITEM", 400, "Said where the title named is not something the media server could hold."
    ),
    "PLAY-2": ListedRefusal(
        "NOT_ON_THEIR_SHELF",
        404,
        "Said where the title is not one this member may watch, or is not there at all.",
    ),
    "PLAY-3": ListedRefusal(
        "NOT_A_DEVICE", 400, "Said where what names a member's device is not a device id."
    ),
    "PLAY-4": ListedRefusal(
        "NOTHING_TO_PLAY_FROM",
        503,
        "Said where there is no media server to play from, or it was never set up.",
    ),
    "PLAY-5": ListedRefusal(
        "SERVER_SILENT", 502, "Said where the media server would not answer for a member."
    ),
    "PLAY-6": ListedRefusal(
        "NOBODY_NAMED", 400, "Said where nobody is named for something only a member can be."
    ),
    "PLAY-7": ListedRefusal(
        "NOT_IN_THE_HOUSEHOLD", 404, "Said where the member named is not somebody in the household."
    ),
    "PLAY-8": ListedRefusal(
        "SIGNS_NO_DEVICE_IN", 503, "Said where the media server will not sign a device in by code."
    ),
    "PLAY-9": ListedRefusal(
        "NO_SUCH_PICTURE",
        404,
        "Said where a title on the member's shelf has no picture of the kind asked for.",
    ),
}
"""What the contract says of each `PLAY` code."""
