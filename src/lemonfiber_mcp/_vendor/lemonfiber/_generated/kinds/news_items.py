# Copyright (c) 2026 NightWorksIO
"""The `news-items` envelope, and the shapes only `news-items` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.instant import Instant
from ..shared.news_kind import NewsKind
from ..shared.title_kind import TitleKind, TitleUnit


class News(typing.TypedDict):
    """What a surface can mark as new, newest first within each kind."""

    problems: list[NewsProblem]
    """The checks found wrong, the most recent onset first."""
    requests: list[NewsRequest]
    """What the household has asked for, the most recently asked first."""
    unread: list[NewsKind]
    """The kinds that could not be read.

    A kind named here has an empty list because nothing could be read, not because
    nothing is there. A surface that took the empty list as everything there is
    would mark all of it as new once it could be read again.
    """
    updates: list[NewsUpdate]
    """The releases in the record this build carries, newest first."""


class NewsItemsEnvelope(typing.TypedDict):
    """The envelope carrying `news-items`."""

    api_version: int
    data: News
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["news-items"]


class NewsProblem(typing.TypedDict):
    """One check found wrong, by the check and when it went wrong."""

    check: str
    """The check that raised it."""
    onset: Instant
    """When the stack first saw it wrong since it last saw it right, in whole seconds
    since the epoch: the same moment the health summary names for it.
    """
    summary: str
    """What is wrong, in one line."""


class NewsRequest(typing.TypedDict):
    """One request, by its reference."""

    asked: typing.NotRequired[Instant | None]
    """When it was asked for, where that is known."""
    by: str
    """Who asked for it, by the name the media server holds them under."""
    kind: typing.NotRequired[TitleKind | None]
    """The kind of title it asks for, as the household list names it."""
    request: str
    """The reference the household list names it with: the request service's number
    (`42`), or `tv-<n>`, `movies-<n>`, `music-<n>` or `books-<n>` for an ask the core
    keeps.
    """
    title: typing.NotRequired[str | None]
    """What it is called, where a service has been told about it."""
    unit: typing.NotRequired[TitleUnit | None]
    """What an ask for music or books asks for, as the household list names it."""


class NewsUpdate(typing.TypedDict):
    """One release, by its version."""

    delivers: typing.NotRequired[str | None]
    """What it set out to deliver, where the record says."""
    version: str
    """The version, without the tag's leading letter."""


__all__ = [
    "News",
    "NewsItemsEnvelope",
    "NewsProblem",
    "NewsRequest",
    "NewsUpdate",
]
