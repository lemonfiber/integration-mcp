# Copyright (c) 2026 NightWorksIO
"""The shapes `backup`, `copying` and `restore` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Tree(typing.TypedDict):
    """One host tree captured from a setup lemonfiber does not manage.

    Both halves are needed to find it again: the archive path says where it sits
    inside the archive, and the host path says where it was read from. Nothing
    derives the second from the first, because a tree outside lemonfiber's layout
    has no layout to derive it from.
    """

    archive_path: str
    """Where it sits inside the archive."""
    host_path: str
    """Where it was read from, on the machine whose setup was taken over."""


__all__ = [
    "Tree",
]
