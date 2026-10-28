# Copyright (c) 2026 NightWorksIO
"""What the contract says of each refusal code of the `LIFE` family.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .listed import ListedRefusal, RefusalCode

LIFE: typing.Final[typing.Mapping[RefusalCode, ListedRefusal]] = {
    "LIFE-10": ListedRefusal(
        "RESTART_MOVED",
        400,
        "Raised where a restart names an offer that is not the one a fresh look at the stack builds.",
    ),
    "LIFE-11": ListedRefusal(
        "MOUNT_LINKED", 409, "Raised when a start finds a service's mount source reached through a link."
    ),
    "LIFE-3": ListedRefusal("ALREADY_WORKING", 409, "Another run is already working on this stack."),
    "LIFE-4": ListedRefusal(
        "REGISTRY_REFUSED", 400, "Fetching images is switched off, so there was nothing to fetch with."
    ),
}
"""What the contract says of each `LIFE` code."""
