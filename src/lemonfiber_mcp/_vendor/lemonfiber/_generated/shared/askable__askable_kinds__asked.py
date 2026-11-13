# Copyright (c) 2026 NightWorksIO
"""The shapes `askable`, `askable-kinds` and `asked` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type TitleKind = typing.Literal["tv", "movies", "music", "books"]
"""What kind of title a curator files, a member asks for and a media server holds: a
series, a film, music or books.
"""


type TitleUnit = typing.Literal["album", "artist", "book", "author", "series"]
"""What one title of music or books is, within its kind."""


__all__ = [
    "TitleKind",
    "TitleUnit",
]
