# Copyright (c) 2026 NightWorksIO
"""The shapes `update` and `version` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type ChangelogState = typing.Literal["current", "pending", "stale"]
"""Whether the record describes what this build could have shipped.

The three the specification names, and the distinction between the last two is
the one worth keeping: being behind the tags is a lag, and contradicting them is
a fault.
"""


class Entry(typing.TypedDict):
    """One change, as a reader meets it."""

    reference: typing.NotRequired[str | None]
    """Where it was reviewed, where it was reviewed anywhere."""
    requirements: list[str]
    """The requirements it served, which are the link rather than the headline."""
    summary: str
    """What changed, in the words it was written in."""


class Group(typing.TypedDict):
    """The entries of one kind, under the name an operator reads them by."""

    entries: list[Entry]
    """The changes, in the order they were made."""
    title: str
    """What this group of changes is: new, fixed, faster, or maintenance."""


class Notes(typing.TypedDict):
    """What a surface shows about the record, given the version asking."""

    releases: list[ReleaseSummary]
    """Every release the record holds, newest first."""
    requirements: dict[str, Requirement]
    """What each requirement the running release cites is, and where it is defined."""
    running: typing.NotRequired[Release | None]
    """What the running version changed, where the record holds its release."""
    state: ChangelogState
    """Whether the record describes what this build could have shipped."""


class Release(typing.TypedDict):
    """One release, and everything the record holds about it."""

    carried: typing.NotRequired[str | None]
    """The version whose goals this tag carried, where that is not its own."""
    delivers: typing.NotRequired[str | None]
    """What it set out to deliver, in the words the version was staged under."""
    groups: list[Group]
    """The changes, gathered by what kind of change each is."""
    patches: typing.NotRequired[str | None]
    """The version this one patched, where it is a patch."""
    released_on: typing.NotRequired[str | None]
    """The day it was published, where the record of it says."""
    tag: str
    """The tag it was cut from."""
    user_facing: bool
    """Whether anything in it is a change an operator would notice."""
    version: str
    """The version, without the tag's leading letter."""
    withdrawn: typing.NotRequired[str | None]
    """Why it was withdrawn, where it was."""


class ReleaseSummary(typing.TypedDict):
    """One release as a listing shows it: everything but what it changed.

    Kept apart from [`Release`] rather than being it with the entries left out,
    because the two are read for different things. A listing answers which releases
    there have been and which of them was taken back; only the one being read needs
    to carry every line of what it changed.
    """

    delivers: typing.NotRequired[str | None]
    """What it set out to deliver."""
    patches: typing.NotRequired[str | None]
    """The version this one patched, where it is a patch."""
    released_on: typing.NotRequired[str | None]
    """The day it was published, where the record of it says."""
    user_facing: bool
    """Whether anything in it is a change an operator would notice."""
    version: str
    """The version."""
    withdrawn: typing.NotRequired[str | None]
    """Why it was withdrawn, where it was."""


class Requirement(typing.TypedDict):
    """One requirement, and every release that shipped something citing it."""

    feature: str
    """The feature it belongs to, in words."""
    shipped_in: list[str]
    """Every version that shipped something citing it, newest first."""
    url: typing.NotRequired[str | None]
    """Where it is defined, unless it has since been withdrawn."""
    withdrawn: typing.NotRequired[bool]
    """Whether it was withdrawn after it shipped."""


__all__ = [
    "ChangelogState",
    "Entry",
    "Group",
    "Notes",
    "Release",
    "ReleaseSummary",
    "Requirement",
]
