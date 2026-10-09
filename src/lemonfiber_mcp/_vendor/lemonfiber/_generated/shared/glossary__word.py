# Copyright (c) 2026 NightWorksIO
"""The shapes `glossary` and `word` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Term(typing.TypedDict):
    """A word this product uses, and what somebody meeting it needs to know."""

    also_called: list[str]
    """What other services in this stack call the same thing.

    Sonarr and `SABnzbd` do not agree on words, and an operator moving between
    their screens should not have to work out that two of them are one.
    """
    deep: typing.NotRequired[str | None]
    """More, for somebody who asks — never needed in order to act."""
    forms: list[str]
    """The other forms this product itself writes the word in, where a state or a
    stage is named by one — `grabbed` for `grab`, `seeding` for `seed`.

    Apart from [`Self::also_called`], which is another service's word and one this
    product must never write as its own. These are this product's own words, and a
    surface explaining a word it was sent looks for the word it was sent here, so
    that nothing on the far side has to guess which term an inflection belongs to.
    """
    short: str
    """One sentence: what it is for and what it costs or gains.

    Enough to act on. Somebody who reads only this should not be stuck.
    """
    word: str
    """The word as it appears in the interface."""


__all__ = [
    "Term",
]
