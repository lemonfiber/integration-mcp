# Copyright (c) 2026 NightWorksIO
"""The `held` envelope, and the shapes only `held` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.held__part_way__playing__title import Medium
from ..shared.held__part_way__title import Pinned


class Held(typing.TypedDict):
    """One thing the household holds, as a member is shown it.

    What a person recognises and nothing else. There is no file path, no container,
    no bitrate and no library id: a member deciding what to watch is not choosing a
    transcode, and a surface handed those would have to decide not to draw them.
    """

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


class HeldEnvelope(typing.TypedDict):
    """The envelope carrying `held`."""

    api_version: int
    data: HeldReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["held"]


class HeldReport(typing.TypedDict):
    """What one member can watch, and who they are."""

    available: bool
    """Whether the shelf could be read at all.

    An empty shelf and an unread one are different answers, and collapsing them
    would tell a household they own nothing on the day the media server rebooted.
    Anything that could not be read is said in `findings` and this goes false.
    """
    findings: list[str]
    """What is worth saying about this shelf, in the words its reader would use.

    Always written, empty or not. A field the schema requires and the document
    sometimes omits is one a reader has to guess about, and an empty list already
    says the thing it would say: there is nothing to report about this shelf.
    """
    holdings: list[Held]
    """What they hold, newest first."""
    id: str
    """The identifier the media server files them under."""
    member: str
    """The member this was asked for, by the name they are known by."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


__all__ = [
    "Held",
    "HeldEnvelope",
    "HeldReport",
]
