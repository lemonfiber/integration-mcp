# Copyright (c) 2026 NightWorksIO
"""The shapes `backup` and `restore` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Scope = ScopeWholeStack | ScopeService | ScopeExisting
"""How much of the stack a backup covers.

Whole-stack is the common case, but restoring one service is often what is
actually wanted — one \\*arr's configuration mangled while the rest is fine —
so the scope is recorded in the archive and honoured on the way back.
"""


class ScopeExisting(typing.TypedDict):
    """An existing setup's own configuration, at the host paths it keeps it in.

    The one scope whose sources are not lemonfiber's layout. A capture taken
    before a takeover has to cover the tree that is already there — lemonfiber's
    own holds nothing worth protecting until the takeover has happened — so the
    host path each tree was read from is recorded here, in the manifest, rather
    than inferred from a layout that does not describe it.

    Recording those paths is also what makes putting one back an ordinary
    extraction the operator performs deliberately, rather than something
    lemonfiber does on their behalf into a tree it does not manage.
    """

    project: str
    """The Compose project the capture was taken from."""
    scope: typing.Literal["existing"]
    trees: list[Tree]
    """The host trees captured, in the order the survey reported them."""


class ScopeService(typing.TypedDict):
    """One named service's configuration alone."""

    name: str
    """The service whose configuration this covers."""
    scope: typing.Literal["service"]


class ScopeWholeStack(typing.TypedDict):
    """Every service's configuration, plus lemonfiber's own and the stack."""

    scope: typing.Literal["whole_stack"]


class Tree(typing.TypedDict):
    """One host tree captured from a setup lemonfiber does not manage.

    Both halves are needed to find it again: the archive path says where it sits
    inside the archive, and the host path says where it was read from. Nothing
    derives the second from the first, because a tree outside lemonfiber's layout
    has no layout to derive it from.
    """

    archive_path: str
    """Where it sits inside the archive."""
    host_path: str
    """Where it was read from, on the machine whose setup was taken over."""


__all__ = [
    "Scope",
    "ScopeExisting",
    "ScopeService",
    "ScopeWholeStack",
    "Tree",
]
