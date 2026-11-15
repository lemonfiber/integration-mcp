# Copyright (c) 2026 NightWorksIO
"""The shapes `settled` and `setup` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Protocols(typing.TypedDict):
    """Which download protocols the operator actually has accounts for.

    A form names both, because a form describes what it *does* rather than what
    this operator has paid for. Narrowing happens afterwards, so a tunnel is
    never started with credentials that were never supplied.
    """

    torrent: bool
    """A VPN and torrent client are configured."""
    usenet: bool
    """A Usenet provider is configured."""


__all__ = [
    "Protocols",
]
