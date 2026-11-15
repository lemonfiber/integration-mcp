# Copyright (c) 2026 NightWorksIO
"""The shapes `dashboard`, `held`, `household`, `part-way`, `play`, `playing`, `title` and `tuned` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .code import Code


class Obstacle(typing.TypedDict):
    """Something in the way of one part of an answer, said by its code.

    What a read carries beside the part it could not give, rather than a sentence of its
    own: a sentence carries no code, so nothing could word it again for whoever reads it.
    """

    code: Code
    """The code that names what is in the way."""
    remedy: str
    """What to do about it."""
    said: str
    """What is in the way, in one sentence."""


__all__ = [
    "Obstacle",
]
