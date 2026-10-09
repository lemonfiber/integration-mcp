# Copyright (c) 2026 NightWorksIO
"""The `self-update` envelope, and the shapes only `self-update` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Installed = typing.Literal[
    "homebrew", "scoop", "winget", "cargo", "distribution", "installer", "elsewhere", "image", "untellable"
]
"""How this copy of lemonfiber got onto the machine.

Nothing known is the default. Every other answer is a claim about somebody's
machine, and a value that arrived by nobody filling it in has established none of
them.
"""


class SelfUpdateEnvelope(typing.TypedDict):
    """The envelope carrying `self-update`."""

    api_version: int
    data: UpdateReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["self-update"]


type SelfUpdateStanding = typing.Literal["current", "update-available", "managed-externally", "check-failed"]
"""Where a copy of lemonfiber stands, in the words the specification uses.

Nothing known is the default, and it is the right one: a report built before
anything has been read has not established that this copy is current, and a
default that said so would be a claim made by an empty value.
"""


class UpdateReport(typing.TypedDict):
    """Where this copy of lemonfiber stands, and what moving it would come to."""

    afterwards: str
    """What updating leaves alone, and what it needs afterwards."""
    asked: typing.NotRequired[str | None]
    """The version the operator asked to move to, where they asked for one."""
    at: typing.NotRequired[str | None]
    """Where the running binary is, with any link followed, or nothing where this
    machine would not say.

    The answer to which of several copies on a search path is the one that ran, so
    a version somebody quotes can be attributed to a file rather than to a name.
    """
    carries: str
    """What a release brings besides the program, and when any of it is fetched."""
    changed: typing.NotRequired[str | None]
    """What the version on offer says it changed, as its release page words it.

    The question an operator is actually weighing. Carried as the notes were
    written rather than taken apart here, because what a surface does with them
    is a surface's business — a terminal flattens them, a browser renders them,
    and a script wants them as they came.
    """
    command: typing.NotRequired[str | None]
    """Exactly what to type, where there is something exact to type."""
    configuration: typing.NotRequired[str | None]
    """Whether the version named can read the configuration on this machine.

    Only where a version was named, since it is the question a downgrade asks and
    nothing else does.
    """
    installed: Installed
    """How this copy got onto the machine."""
    instead: typing.NotRequired[str | None]
    """Why there is nothing exact to type, where there is not; or, where typing the
    command is not the whole of the move, what has to follow it.
    """
    offered: typing.NotRequired[str | None]
    """The newest version released, where the check could read one."""
    owner: typing.NotRequired[str | None]
    """The tool that owns this copy, where one does."""
    replaceable: typing.NotRequired[bool | None]
    """Whether the directory holding the running binary can be written to.

    Nothing where it was not asked, which is every copy a package manager owns —
    replacing one of those is that tool's business and not this one's. Asked by
    trying rather than by reading permission bits, and reported rather than acted
    on: a copy this operator cannot replace is a thing to say with the path, never
    a reason to go looking for a way to become somebody else.
    """
    running: str
    """The version running now."""
    standing: SelfUpdateStanding
    """Which of the states this is."""
    untold: typing.NotRequired[str | None]
    """Why availability could not be told, where it could not."""


__all__ = [
    "Installed",
    "SelfUpdateEnvelope",
    "SelfUpdateStanding",
    "UpdateReport",
]
