# Copyright (c) 2026 NightWorksIO
"""The `part-way` envelope, and the shapes only `part-way` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.held__part_way__playing__title import Medium
from ..shared.held__part_way__title import Pinned


class PartWay(typing.TypedDict):
    """Something a member was part-way through, and how far."""

    backdrop: typing.NotRequired[str | None]
    """Where its backdrop is served, where it has one."""
    door: typing.NotRequired[Pinned | None]
    """The certificate the door presents, which a client pins, beside any location."""
    id: str
    """The identifier the server tells it apart by, which is what asking to play one
    of them names.
    """
    length: typing.NotRequired[int | None]
    """How long it runs, in whole seconds, where the server knows."""
    medium: Medium
    """Which of the kinds this product deals in it is."""
    position: int
    """How far in they got, in whole seconds."""
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


class PartWayEnvelope(typing.TypedDict):
    """The envelope carrying `part-way`."""

    api_version: int
    data: PartWayReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["part-way"]


class PartWayReport(typing.TypedDict):
    """What one member was part-way through, most recent first."""

    available: bool
    """Whether it could be read at all. An empty list and an unread one are different
    answers, and what could not be read is said in `findings`.
    """
    findings: list[str]
    """What is worth saying about this read, in the words its reader would use."""
    id: str
    """The identifier the media server files them under."""
    member: str
    """The member this was asked for, by the name they are known by."""
    part_way: list[PartWay]
    """Each title or episode, how far in, and where it is served."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done."""


__all__ = [
    "PartWay",
    "PartWayEnvelope",
    "PartWayReport",
]
