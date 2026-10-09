# Copyright (c) 2026 NightWorksIO
"""The shapes `substitution` and `wiring` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Unfilled(typing.TypedDict):
    """A capability something asks for and nothing fills, and what asked for it.

    The pair rather than the name: a capability nothing fills is a fact about the
    stack, and a capability *`seerr` asks for* and nothing fills is a thing somebody
    can act on. Reporting the first and leaving the second to be worked out is the
    obscure failure at the point of use this exists instead of.
    """

    by: str
    """The service that asked."""
    capability: str
    """What it asked for."""


__all__ = [
    "Unfilled",
]
