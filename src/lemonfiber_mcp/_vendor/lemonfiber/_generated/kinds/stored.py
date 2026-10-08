# Copyright (c) 2026 NightWorksIO
"""The `stored` envelope, and the shapes only `stored` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Kept(typing.TypedDict):
    """One thing lemonfiber keeps on this machine."""

    at: str
    """Where it is, in full."""
    secret: bool
    """Whether it holds a credential, which is what decides how carefully a copy of
    it has to be treated.
    """
    what: str
    """What it is, in the operator's words."""
    why: str
    """Why it is kept."""


class Root(typing.TypedDict):
    """A directory everything lemonfiber keeps sits under."""

    at: str
    """The directory itself."""
    what: str
    """What lives under it, and what losing it would cost."""


class Stored(typing.TypedDict):
    """Everything lemonfiber keeps on this machine, and what became of it."""

    beside: list[StoredBeside]
    """What is on this machine that is not lemonfiber's to keep or remove."""
    kept: list[Kept]
    """Each thing kept, configuration first and then what can be made again."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    removal: StoredRemoval
    """Whether this run removed any of it."""
    roots: list[Root]
    """The two directories all of it lives under."""


class StoredBeside(typing.TypedDict):
    """Something on this machine that lemonfiber neither keeps nor removes."""

    what: str
    """What it is."""
    why: str
    """Whose it is, and why it is not lemonfiber's to take away."""


class StoredEnvelope(typing.TypedDict):
    """The envelope carrying `stored`."""

    api_version: int
    data: Stored
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["stored"]


class StoredLeft(typing.TypedDict):
    """Something a removal could not take away."""

    at: str
    """The path that is still there."""
    why: str
    """What the machine said about it, so it can be finished by hand."""


type StoredRemoval = StoredRemovalNotAsked | StoredRemovalUnconfirmed | StoredRemovalDone
"""Whether anything was removed on this run, and what became of it."""


class StoredRemovalDone(typing.TypedDict):
    """Carried out."""

    gone: list[str]
    """The directories that are gone."""
    left: list[StoredLeft]
    """What could not be removed, each with the reason."""
    state: typing.Literal["done"]


class StoredRemovalNotAsked(typing.TypedDict):
    """Nobody asked. This is a listing."""

    state: typing.Literal["not-asked"]


class StoredRemovalUnconfirmed(typing.TypedDict):
    """Asked for without the agreement it takes, so nothing was touched."""

    state: typing.Literal["unconfirmed"]


__all__ = [
    "Kept",
    "Root",
    "Stored",
    "StoredBeside",
    "StoredEnvelope",
    "StoredLeft",
    "StoredRemoval",
    "StoredRemovalDone",
    "StoredRemovalNotAsked",
    "StoredRemovalUnconfirmed",
]
