# Copyright (c) 2026 NightWorksIO
"""The shapes `bandwidth` and `pausing` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Pulling = typing.Literal["fetching", "stopped"]
"""Whether a client is fetching at all, where a cap made it a question.

Apart from the limits above rather than folded in with them, because it answers
a different question and a client held to a crawl is not a client that stopped.
A word that named both would be the vocabulary this whole path exists to avoid.
"""


__all__ = [
    "Pulling",
]
