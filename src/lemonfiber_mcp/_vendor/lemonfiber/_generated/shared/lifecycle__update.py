# Copyright (c) 2026 NightWorksIO
"""The shapes `lifecycle` and `update` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class MoveOffered(typing.TypedDict):
    """A move in place the bundle offers: the plugin and the stack's own service of its id it
    would take the place of.
    """

    configured_by: typing.NotRequired[str | None]
    """The part's adapter that writes the configuration the service reads, where one does:
    it runs only once the move is taken, so until then the service starts without what
    that configuration holds, the credentials it reaches other services with included.
    """
    plugin: str
    """The plugin the bundle installs."""
    service: str
    """The stack's own service it would take the place of, under the same container name,
    configuration directory, data and names.
    """


__all__ = [
    "MoveOffered",
]
