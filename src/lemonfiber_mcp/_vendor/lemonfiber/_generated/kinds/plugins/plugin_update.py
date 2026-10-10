# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `plugins` carries; `kinds.plugins` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .plugin_step_adapter import (
    PluginInstall,
    PluginInstalled,
    PluginNonconforming,
    PluginRemoval,
    PluginReproof,
    PluginRestored,
    PluginSource,
    PluginSubstituted,
)
from ...shared.plugins__undo import UndoReversal


class PluginInstalls(typing.TypedDict):
    """What is installed, and what installing one came to.

    One answer for the reading and for the verb, because they are one question: an
    operator who has just installed something wants to see it among what they had, and
    a rehearsal that showed only the new entry would not say what it is joining.
    """

    agreement: typing.NotRequired[str | None]
    """What this run's reading names itself, so an answer to it can say which reading
    it answered; nothing on the reading of what is installed, which offers nothing.

    Named part by part, so an answer refused because something moved is told which
    part did.
    """
    install: typing.NotRequired[PluginInstall | None]
    """What this run's install came to, or nothing where it only read.

    Boxed for the reason the update is: it carries a whole account, and every other
    run's report would otherwise be as large as the one run that installs.
    """
    installed: list[PluginInstalled]
    """Every plugin the record holds.

    What it holds, rather than what it would hold: a rehearsal wrote nothing, so
    what it settled is in `install` and not here. A listing that counted it
    would report an install that did not happen.
    """
    nonconforming: typing.NotRequired[list[PluginNonconforming]]
    """Every answer an installed plugin's adapter gave outside its contract, kept until a
    proof it passes clears it: the plugin fills none of those capabilities meanwhile.

    Filled on the reading of what is installed, as `substituted` is.
    """
    proof: typing.NotRequired[PluginReproof | None]
    """What proving a plugin again came to, or nothing where nothing was proved."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    removal: typing.NotRequired[PluginRemoval | None]
    """What this run's removal came to, or nothing where it removed nothing.

    Beside the install rather than in place of it, and never both at once: an
    install and a removal are two verbs with two accounts, and a field that held
    whichever happened would make a reader ask which one this was before they could
    read it.
    """
    sources: typing.NotRequired[list[PluginSource]]
    """Whether each installed plugin's source can still be fetched, asked now.

    Filled on the reading of what is installed and nowhere else, for the reason
    `substituted` is: it is the one read an operator makes of what each plugin is
    doing, and the one moment this machine asks anybody where a plugin came from. A
    run that installs, updates or removes one leaves it empty.
    """
    substituted: typing.NotRequired[list[PluginSubstituted]]
    """Every capability the operator chose an installed plugin's service to fill.

    Filled on the reading of what is installed, which is the one read of what each
    plugin is doing; a run that installs, updates or removes one leaves it empty,
    because none of them changes a choice.
    """
    update: typing.NotRequired[PluginUpdate | None]
    """What this run's update came to, or nothing where it updated nothing.

    A third field rather than an install and a removal filled in together, for the
    reason those two are apart: an update is one operation with one account.

    Boxed because it carries a whole install's account beside the reversal, and
    every other run's report would otherwise be as large as the one run that updates.
    """


class PluginsEnvelope(typing.TypedDict):
    """The envelope carrying `plugins`."""

    api_version: int
    data: PluginInstalls
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugins"]


PluginUpdate = typing.TypedDict(
    "PluginUpdate",
    {
        "from": str,
        "install": PluginInstall,
        "interrupts": list[str],
        "plugin": str,
        "restored": typing.NotRequired[PluginRestored | None],
        "stopped": typing.NotRequired[str | None],
        "to": str,
        "went_back": UndoReversal,
    },
)
"""What updating a plugin came to, or would come to, as one account.

**One account, because it is one operation.** An update is the version installed
going back and another coming on, and a report that gave those as a removal and an
install side by side would invite reading them as two things that might each have
happened. What an operator has to be able to read off this is which version the
machine is on, and there are exactly two answers: the new one, where
`install.recorded` is true, or the one it replaced, which `restored` says the state
of.
"""


__all__ = [
    "PluginInstalls",
    "PluginUpdate",
    "PluginsEnvelope",
]
