# Copyright (c) 2026 NightWorksIO
"""The `word` envelope, and the shapes only `word` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.glossary__word import Term


class WordEnvelope(typing.TypedDict):
    """The envelope carrying `word`."""

    api_version: int
    data: Term
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["word"]


__all__ = [
    "WordEnvelope",
]
