# Copyright (c) 2026 NightWorksIO
"""The `glossary` envelope, and the shapes only `glossary` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.glossary__word import Term


class GlossaryEnvelope(typing.TypedDict):
    """The envelope carrying `glossary`."""

    api_version: int
    data: Vocabulary
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["glossary"]


class Vocabulary(typing.TypedDict):
    """Every word this product explains, for somebody who asked what there is to ask
    about.
    """

    words: list[Term]
    """The words, in the order somebody meets them."""


__all__ = [
    "GlossaryEnvelope",
    "Vocabulary",
]
