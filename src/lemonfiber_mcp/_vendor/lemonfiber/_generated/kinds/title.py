# Copyright (c) 2026 NightWorksIO
"""The `title` envelope, and the shapes only `title` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.held__part_way__playing__title import Medium
from ..shared.held__part_way__title import Pinned


class Episode(typing.TypedDict):
    """One episode, with where it is served."""

    backdrop: typing.NotRequired[str | None]
    """Where its backdrop is served, where it has one."""
    door: typing.NotRequired[Pinned | None]
    """The certificate the door presents, which a client pins, beside any location."""
    id: str
    """The identifier the server tells it apart by, which is what asking to play one
    of them names.
    """
    medium: Medium
    """Which of the kinds this product deals in it is."""
    minutes: typing.NotRequired[int | None]
    """How long it runs, in whole minutes, where the server knows."""
    number: typing.NotRequired[int | None]
    """Its number in the season, where it has one."""
    overview: typing.NotRequired[str | None]
    """What happens in it, where the server holds a description."""
    poster: typing.NotRequired[str | None]
    """Where its poster is served, where it has one."""
    stream_from: typing.NotRequired[str | None]
    """Where it streams from, where it plays."""
    title: str
    """What it is called, in the words the server holds it under."""
    unlocated: typing.NotRequired[str | None]
    """Why no location is stated, where none is."""
    year: typing.NotRequired[int | None]
    """The year it came out, where the server knows one. Absent rather than guessed:
    two films share a title far more often than they share a title and a year.
    """


class Season(typing.TypedDict):
    """One season of a series, with its episodes."""

    episodes: list[Episode]
    """Its episodes, in order, each with where it is served."""
    id: str
    """What the server tells it apart by."""
    name: str
    """What it is called."""
    number: typing.NotRequired[int | None]
    """Its number in the series, where it has one. Specials often have none."""


class Title(typing.TypedDict):
    """What one title is, as a member's own account reads it.

    What a person deciding whether to watch it wants, and nothing about how it is
    stored: no file, no container, no bitrate.
    """

    backdrop: typing.NotRequired[str | None]
    """Where its backdrop is served, where it has one."""
    certificate: typing.NotRequired[str | None]
    """The certificate it carries where the operator lives, where it carries one."""
    door: typing.NotRequired[Pinned | None]
    """The certificate the door presents, which a client pins, beside any location."""
    genres: list[str]
    """The genres the server files it under."""
    id: str
    """The identifier the server tells it apart by, which is what asking to play one
    of them names.
    """
    medium: Medium
    """Which of the kinds this product deals in it is."""
    minutes: typing.NotRequired[int | None]
    """How long it runs, in whole minutes, where the server knows."""
    overview: typing.NotRequired[str | None]
    """What it is about, where the server holds a description."""
    poster: typing.NotRequired[str | None]
    """Where its poster is served, where it has one."""
    released: typing.NotRequired[str | None]
    """When it came out, as a calendar date, where the server knows."""
    seasons: list[Season]
    """A series' seasons, each with its episodes, in order. Empty for anything else."""
    stream_from: typing.NotRequired[str | None]
    """Where it streams from, where it plays."""
    title: str
    """What it is called, in the words the server holds it under."""
    unlocated: typing.NotRequired[str | None]
    """Why no location is stated, where none is."""
    year: typing.NotRequired[int | None]
    """The year it came out, where the server knows one. Absent rather than guessed:
    two films share a title far more often than they share a title and a year.
    """


class TitleEnvelope(typing.TypedDict):
    """The envelope carrying `title`."""

    api_version: int
    data: TitleReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["title"]


class TitleReport(typing.TypedDict):
    """One title, as the member it was asked for may see it."""

    id: str
    """The identifier the media server files them under."""
    member: str
    """The member this was asked for, by the name they are known by."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""
    title: typing.NotRequired[Title | None]
    """The title, with where it and each of its episodes is served."""


__all__ = [
    "Episode",
    "Season",
    "Title",
    "TitleEnvelope",
    "TitleReport",
]
