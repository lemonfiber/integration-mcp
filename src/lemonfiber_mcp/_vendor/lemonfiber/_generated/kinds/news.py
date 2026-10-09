# Copyright (c) 2026 NightWorksIO
"""The `news` envelope, and the shapes only `news` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.news__news_items import NewsKind


class Newest(typing.TypedDict):
    """The newest of each kind, by what names them and nothing else.

    What the event stream says. A surface marks a tab from it without reading the
    items, and reads [`News`] on the screen that lists them.
    """

    problems: list[NewsCheck]
    """The checks most recently found wrong, each with its onset."""
    requests: list[int]
    """The numbers of the household's newest requests."""
    unread: list[NewsKind]
    """The kinds that could not be read, as [`News::unread`] names them."""
    updates: list[str]
    """The versions of the newest releases in the record this build carries."""


class NewsCheck(typing.TypedDict):
    """A check found wrong, by the check and when it went wrong."""

    check: str
    """The check that raised it."""
    onset: str
    """When the stack first saw it wrong since it last saw it right, in whole seconds
    since the epoch.
    """


class NewsEnvelope(typing.TypedDict):
    """The envelope carrying `news`."""

    api_version: int
    data: Newest
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["news"]


__all__ = [
    "Newest",
    "NewsCheck",
    "NewsEnvelope",
]
