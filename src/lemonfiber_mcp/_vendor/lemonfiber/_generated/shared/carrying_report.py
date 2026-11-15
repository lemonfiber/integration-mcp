# Copyright (c) 2026 NightWorksIO
"""The shapes `adoption` and `migration` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class CarryingReport(typing.TypedDict):
    """What adopting one existing service would come to."""

    backup_first: bool
    """Whether its database must be backed up before lemonfiber opens it."""
    because: str
    """What that means for this service's data, in the operator's terms."""
    existing: str
    """The version standing here now."""
    ours: str
    """The version lemonfiber pins."""
    refused: bool
    """Whether lemonfiber will not do this at all."""
    service: str
    """The service, by the name lemonfiber runs it under."""
    verdict: str
    """Which of the two is the later, in one word."""


__all__ = [
    "CarryingReport",
]
