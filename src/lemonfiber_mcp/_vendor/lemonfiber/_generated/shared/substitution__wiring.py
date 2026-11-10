# Copyright (c) 2026 NightWorksIO
"""The shapes `substitution` and `wiring` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .plugins__substitution__wiring import Apis


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
    files: typing.NotRequired[str | None]
    """The medium it asked a filler of, where nothing filling it files that medium."""
    media_types: typing.NotRequired[list[str]]
    """The media it asked a filler of, where nothing filling it files one of them."""
    native: typing.NotRequired[Apis | None]
    """The upstream's own API it asked in, or every API it asked in any of, where no
    upstream filling it declares one of them.
    """


__all__ = [
    "Unfilled",
]
