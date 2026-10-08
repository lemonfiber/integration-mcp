# Copyright (c) 2026 NightWorksIO
"""The shapes `plugins` and `undo` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Action = (
    ActionRemove
    | ActionRestore
    | ActionDelete
    | ActionWithdraw
    | ActionRewind
    | ActionRepin
    | ActionReconfigure
    | ActionRevoke
    | ActionReinstate
)
"""What an undo does.

Tagged by what it does rather than by the field it sits in, so a reader parsing
one branches on a word rather than on which keys are present.
"""


class ActionDelete(typing.TypedDict):
    """Remove a path that was created."""

    does: typing.Literal["delete"]
    path: str
    """The path to remove."""


class ActionReconfigure(typing.TypedDict):
    """Put one field of a service's own resource back to what it held.

    The only reversal that needs the service itself: the value lives inside it,
    and nothing on the host can write it. A reversal that cannot reach the
    service says so rather than reporting the field restored.
    """

    does: typing.Literal["reconfigure"]
    field: str
    """The field to put back."""
    id: str
    """The identifier to change."""
    resource: str
    """The kind of resource."""
    value: typing.NotRequired[str | None]
    """What to put back, or `None` where it held nothing."""


class ActionReinstate(typing.TypedDict):
    """Make a revoked key good again.

    Worked out so the record of a revoke has a reversal to name, and never carried
    out: a key is revoked because something should stop holding it, and reinstating
    it would hand back what the revoke took away. Whatever still needs a key is
    minted a new one.
    """

    does: typing.Literal["reinstate"]
    name: str
    """The key's name."""


class ActionRemove(typing.TypedDict):
    """Remove the resource that was created."""

    does: typing.Literal["remove"]
    id: str
    """The identifier to remove."""
    resource: str
    """The kind of resource."""


class ActionRepin(typing.TypedDict):
    """Pin a service back to the version it was standing on.

    The one reversal nothing in this product carries out. Which version runs is
    decided by the materialised stack and by what Compose was told to start, and
    a reversal of settings and files reaches neither — so this is worked out,
    reported, and left for the operator rather than attempted.
    """

    current: str
    """The version this run moved it to, which has to still be the one running
    for putting the old one back to be putting anything back.
    """
    does: typing.Literal["repin"]
    previous: str
    """The version to put back."""


class ActionRestore(typing.TypedDict):
    """Restore a value, or remove it where there was none before (`None`)."""

    does: typing.Literal["restore"]
    key: str
    """The setting to restore."""
    value: typing.NotRequired[str | None]
    """What to restore it to, or `None` to remove it."""
    wrote: str
    """What lemonfiber put there, which has to still be there for putting the
    old value back to be putting anything back.

    Carried so that a reversal can ask whether it is undoing its own work.
    Without it a reversal knows only what it would like the setting to say,
    and a setting the operator has since chosen for themselves reads exactly
    like one nobody has touched.
    """


class ActionRevoke(typing.TypedDict):
    """Revoke the key a mint made."""

    does: typing.Literal["revoke"]
    name: str
    """The key's name."""


class ActionRewind(typing.TypedDict):
    """Write a file back to what it held before lemonfiber wrote over it.

    Only where it still holds what was written. One written since is somebody
    else's work now, and is left exactly as it is.
    """

    does: typing.Literal["rewind"]
    path: str
    """The file to write back."""
    previous: str
    """What to write back into it."""
    written: int
    """The checksum of what lemonfiber wrote, which has to still be what is there
    for writing the old text back to be undoing lemonfiber's own work.
    """


class ActionWithdraw(typing.TypedDict):
    """Take a region lemonfiber wrote back out of the file it was written into.

    Only where the region is still what was written. One that was edited since, or
    whose markers were, is somebody else's work now, and is left exactly as it is.
    """

    does: typing.Literal["withdraw"]
    key: str
    """The same file beneath the stack directory, as the record of what lemonfiber
    materialised names it.
    """
    owner: str
    """Whose region it is, as its markers name it."""
    path: str
    """The file the region is in."""
    written: int
    """The checksum of what was written between the markers, which has to still be
    what is there for taking it out to be taking out lemonfiber's own work.
    """


class Undo(typing.TypedDict):
    """A single reversal, for the surface to carry out."""

    action: Action
    """What reversing it does."""
    target: str
    """The service or file to reverse it against."""


class UndoLeft(typing.TypedDict):
    """One change a reversal did not put back, and why it did not."""

    because: str
    """Why it is still standing, in the operator's terms."""
    target: str
    """What the change was against — a service, or lemonfiber's own environment file."""


class UndoNoted(typing.TypedDict):
    """What putting one change back means beyond the change itself."""

    because: str
    """What goes back, what does not go with it, and what to do instead."""
    target: str
    """What the change was against."""


class UndoReversal(typing.TypedDict):
    """What putting a run back came to.

    A report rather than a bare list, because it is what an envelope carries and an
    envelope carries a document. Two lists, and the second is the one that matters when
    it is not empty: what went back, and what did not with the reason it did not.
    """

    left: list[UndoLeft]
    """What was not put back, each with the reason it was not.

    A reversal an operator asked for by name has to say what it did *not* do. Five
    changes asked back and three carried out is a machine in a state nobody has been
    told about, and \"some of it worked\" is the sentence that makes somebody go
    looking by hand. Empty where everything went back, which is the common case.

    On a run that only said what it would do, this is what it cannot promise: a
    change that goes back through the service that made it goes back only where that
    service is answering, and a rehearsal has not asked one.
    """
    noted: typing.NotRequired[list[UndoNoted]]
    """What putting these changes back means beyond the changes themselves.

    Empty on almost every run. What lands here is a change the judgement can put
    back in full and that still leaves something behind — the one in force today
    being a setting that re-points where data lives, which goes back while the
    library stays exactly where it was moved to.

    Neither list above can carry it. It did not fail to go back, so it is not what
    was left; and reporting only that it went back would send an operator looking
    for their files at an address that no longer names them.
    """
    rehearsed: bool
    """Whether this run only said what it would put back.

    A flag rather than a second shape, because the two lists mean the same thing
    either way and a caller reading them should read one document. What changes is
    the tense a surface says them in.
    """
    reversed: list[Undo]
    """What was put back, in the order it was — or, on a run that only said what it
    would do, what would go back.
    """


__all__ = [
    "Action",
    "ActionDelete",
    "ActionReconfigure",
    "ActionReinstate",
    "ActionRemove",
    "ActionRepin",
    "ActionRestore",
    "ActionRevoke",
    "ActionRewind",
    "ActionWithdraw",
    "Undo",
    "UndoLeft",
    "UndoNoted",
    "UndoReversal",
]
