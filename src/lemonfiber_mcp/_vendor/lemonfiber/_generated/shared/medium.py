# Copyright (c) 2026 NightWorksIO
"""The shapes `held`, `part-way`, `playing` and `title` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Medium = typing.Literal["film", "series", "episode", "other"]
"""The kinds of thing a household holds.

Named rather than passed through as the server's own word, because a surface
drawing \"Series\" against one server and \"tvshow\" against another would be
rendering a detail of which server this household runs.

`Medium` rather than `Kind`, `Holding` or `Sort`: this product already calls the two
request services a [`crate::media::Kind`], a request's suspension a
[`crate::service::asking::Holding`], and what one line of a manifest is a
`uninstall::Sort` — and one word meaning two things in one vocabulary is how a
reader comes to trust the wrong one. The contract flattens every type name into one
namespace, so a clash there is a clash for anything reading it by name.
"""


__all__ = [
    "Medium",
]
