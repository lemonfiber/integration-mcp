# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `plugins` carries; `kinds.plugins` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .service_value import PluginInstall, PluginInstalled, PluginNonconforming, PluginProving, PluginUnfilled
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


class PluginRemoval(typing.TypedDict):
    """What taking a plugin off the machine came to, or would come to."""

    interrupts: list[str]
    """Every service that stops when it goes, named before any of them does.

    By service rather than by plugin, because a service is what an operator notices
    stopping: a plugin that brought two containers takes two things away, and the
    plugin's name alone would not say which of the addresses they use goes quiet.
    None of them comes back — a removal is not a restart — which is why this is
    stated before the run rather than discovered after it.
    """
    leaves: list[PluginUnfilled]
    """Every capability that would have nothing filling it afterwards.

    Stated before it happens rather than reported after, which is the requirement
    and also the only useful order: an operator told afterwards that their requests
    no longer reach anything has been informed rather than asked.
    """
    plugin: str
    """The plugin this is about."""
    removed: bool
    """Whether the record of what is installed was written without it.

    False on a rehearsal and on a run that got as far as putting the files back and
    no further, which are two different machines and are told apart by what the
    reversal says rather than by a second flag here.
    """
    went_back: UndoReversal
    """What putting its changes back came to, or would come to.

    The rollback layer's own report rather than a shape of this verb's: a removal is
    a reversal with a name on it, and an account of its own would be a second
    description of the same work.
    """


class PluginReproof(typing.TypedDict):
    """What asking an installed plugin's adapters again came to."""

    asked: bool
    """Whether its adapters were asked, rather than only said to be."""
    cleared: bool
    """Whether every answer kept against the plugin was cleared, which a proof that did
    not hold never does.
    """
    kept: list[PluginNonconforming]
    """Every answer kept against the plugin when it was proved, which a pass clears."""
    plugin: str
    """The plugin proved."""
    proofs: list[PluginProving]
    """Each proof asked, or that would be asked, with what it came to."""


class PluginRestored(typing.TypedDict):
    """Where an update did not hold: what putting the version it replaced back came to."""

    placed: bool
    """Whether everything its record says it placed is on the machine again."""
    running: bool
    """Whether its containers are running again.

    Apart from `placed`, because the two fail differently: a document that would not
    land is a disk, and a container that would not start is the engine — and an
    operator fixes them in different places.
    """
    version: str
    """The version put back, which is the one the record still names."""


type PluginSourceStanding = (
    PluginSourceStandingReachable | PluginSourceStandingUnreachable | PluginSourceStandingUnasked
)
"""What asking a plugin's source came to.

**Unreachable is not untrusted.** A plugin whose source has gone keeps running as it
was installed; what it loses is the way to a newer version, and that is said now
rather than found out at the next update.
"""


class PluginSourceStandingReachable(typing.TypedDict):
    """It answered, so the plugin can be updated from it."""

    standing: typing.Literal["reachable"]


class PluginSourceStandingUnasked(typing.TypedDict):
    """Nothing was asked, so nothing is known either way."""

    standing: typing.Literal["unasked"]
    why: str
    """Why nothing was asked."""


class PluginSourceStandingUnreachable(typing.TypedDict):
    """It did not answer, or is no longer there, so the plugin cannot be updated from it."""

    standing: typing.Literal["unreachable"]
    why: str
    """What asking it said."""


class PluginSubstituted(typing.TypedDict):
    """A capability the operator chose one of a plugin's services to fill.

    The only way anything a plugin brought comes to fill what the stack asks for in
    place of the stack's own: a plugin cannot choose, and wiring by name is not
    something a plugin can introduce. So what a plugin substituted is what the operator
    substituted with it, and it is read off the recorded choices rather than off the
    plugin.
    """

    capability: str
    """The capability it fills."""
    plugin: str
    """The plugin whose service it is."""
    service: str
    """The service chosen."""


class PluginsEnvelope(typing.TypedDict):
    """The envelope carrying `plugins`."""

    api_version: int
    data: PluginInstalls
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugins"]


PluginSource = typing.TypedDict(
    "PluginSource",
    {
        "from": str,
        "plugin": str,
        "standing": PluginSourceStanding,
    },
)
"""Whether one installed plugin's source can still be fetched."""


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
    "PluginRemoval",
    "PluginReproof",
    "PluginRestored",
    "PluginSource",
    "PluginSourceStanding",
    "PluginSourceStandingReachable",
    "PluginSourceStandingUnasked",
    "PluginSourceStandingUnreachable",
    "PluginSubstituted",
    "PluginUpdate",
    "PluginsEnvelope",
]
