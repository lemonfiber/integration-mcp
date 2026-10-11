# Copyright (c) 2026 NightWorksIO
"""The shapes `askable` and `asked` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type TitleKind = typing.Literal["tv", "movies"]
"""Whether a title is a series or a film, as a member's search and ask name it.

The web surface's own name for [`Kind`], whose name an SDK already gives to the kinds
of envelope: the same two words on the wire, under a name nothing else takes.
"""


__all__ = [
    "TitleKind",
]
