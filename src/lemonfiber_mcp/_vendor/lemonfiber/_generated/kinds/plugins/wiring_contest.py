# Copyright (c) 2026 NightWorksIO
"""Some of the shapes only `plugins` carries; `kinds.plugins` gathers them all.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .api_kind import PluginChange, PluginDemand, PluginEvidence, PluginOverriding, PluginRecipeRan
from .plugin_granting import (
    PluginGranting,
    PluginInstalled,
    PluginProving,
    PluginSharing,
    PluginTaking,
    PluginVerification,
)
from ...shared.lifecycle__plugins__settings__substitution__update import Unvetted
from ...shared.plugins__settings__status import Waiting
from ...shared.plugins__undo import UndoReversal
from ...shared.plugins__wiring import Wired


class PluginInstall(typing.TypedDict):
    """What an install came to, and what it took to get there.

    **The three lists below are stated whether the run wrote anything or not, and that
    is the whole of what makes a rehearsal worth running.** A rehearsal that reported
    less than the real run would be a preview of a different operation; one that
    reported it from code of its own would be a second derivation free to disagree
    with the one that acts. So they are filled in one place, from the manifest and from
    the very list of writes the install is carried out from, and the surface says them
    in whichever tense `recorded` calls for.
    """

    against: typing.NotRequired[PluginEvidence | None]
    """What those verdicts were reached against, or nothing where none were reached.

    Carried rather than assumed, because the two kinds of evidence are not the
    same claim: an author's read asks the recordings a plugin ships, and an
    install asks the service running on this machine. The weaker must not be
    readable as the stronger, and a reader handed a verdict has nothing else in
    the document to tell them apart.
    """
    asks: list[Wired]
    """Every ask its services would make, each with what it would reach and how that
    would be settled.
    """
    changes: list[PluginChange]
    """Every change it makes to the machine, in the order it makes them."""
    contests: list[WiringContest]
    """Every ask of the stack's the install leaves contested that is not contested
    now, as it would then stand.

    A plugin's service that claims what the stack asks for is a candidate like any
    other, so installing it leaves the ask refused until somebody chooses — which is
    a change to what the stack does, and stated with the rest before it happens.
    """
    granting: list[PluginGranting]
    """Every credential of another service that would cross to the plugin, each approved
    apart from the offer as its `approval` names it.
    """
    overrides: list[PluginOverriding]
    """Every bundled thing the plugin declares it will change.

    The full extent rather than a sample of it: a manifest may change a bundled
    setting only through a recipe, and a recipe reaching one no `[[override]]`
    names is refused before anything is written.
    """
    proofs: list[PluginProving]
    """Every proof that has to hold before the plugin is installed, and on a run
    that asked them, what each came to.
    """
    recipes_ran: list[PluginRecipeRan]
    """Every install recipe the act ran, in order, with what each step came to; an
    empty list where none ran, which is every rehearsal and every plugin declaring no
    install recipe.

    A recipe that did not hold ends the act with a problem carrying the same account,
    so this is the account of recipes that held.
    """
    recorded: bool
    """Whether it was written down. A rehearsal leaves this false."""
    reversed: typing.NotRequired[UndoReversal | None]
    """What putting the install back came to, where something failed and it was.

    The rollback layer's own report rather than a shape of this verb's: what went
    back, and what did not with the reason each is still standing. Absent on a run
    that had nothing to put back, which is both a rehearsal and an install that
    held.
    """
    secured: typing.NotRequired[str | None]
    """What asking the egress guard among its services to hold its control server to the
    credential its adapter was handed came to, where it was more than held at once:
    the guard restarted to take it up, or why it did not. Absent where none of its
    services is a guard speaking its contract, and on every rehearsal.
    """
    sharing: list[PluginSharing]
    """Every adapter that writes the files of the service it fronts."""
    taking: list[PluginTaking]
    """Every service taking a privileged shape, with what it is given, each approved
    apart from the offer.
    """
    verified: typing.NotRequired[PluginVerification | None]
    """What the stack's own checks made of the install, or nothing on a run that
    asked them nothing.

    The other half of what an install has to establish, and the half a plugin
    cannot establish for itself: its proofs say the plugin works, and this says the
    stack still does. Absent on a rehearsal, which writes nothing and so has
    nothing to hold a reading against.
    """
    waiting: list[Waiting]
    """The services held back once the install is made, each with what it waits for."""
    would: PluginInstalled
    """What the install settled, said whether or not it was written down."""


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
    demand: typing.NotRequired[PluginDemand | None]
    """What asking for one of a plugin's demand recipes came to, or nothing where none
    was asked for.

    Boxed for the reason the install is: it carries a whole recipe, and every other
    run's report would otherwise be as large as the one run that asks for one.
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
    unvetted: typing.NotRequired[Unvetted | None]
    """The operator's overlay and every service it changes, where there is one: merged
    over the project this run would start, and held to nothing lemonfiber vets.
    """
    update: typing.NotRequired[PluginUpdate | None]
    """What this run's update came to, or nothing where it updated nothing.

    A third field rather than an install and a removal filled in together, for the
    reason those two are apart: an update is one operation with one account.

    Boxed because it carries a whole install's account beside the reversal, and
    every other run's report would otherwise be as large as the one run that updates.
    """


class PluginNonconforming(typing.TypedDict):
    """One answer a plugin's adapter gave outside a contract it speaks."""

    at: str
    """When it answered so, as RFC 3339."""
    capability: str
    """The capability it was asked as."""
    operation: str
    """The operation it was asked."""
    plugin: str
    """The plugin whose adapter answered."""
    why: str
    """What was outside the contract."""


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


class PluginUnfilled(typing.TypedDict):
    """A capability that would have nothing filling it."""

    capability: str
    """The core name nothing would fill."""
    filled_by: str
    """The plugin that is filling it now, which is the one going.

    Named rather than left to the reader, because the sentence an operator has to
    act on is *this is the only thing filling it* and a capability on its own does
    not say that.
    """


class PluginsEnvelope(typing.TypedDict):
    """The envelope carrying `plugins`."""

    api_version: int
    data: PluginInstalls
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugins"]


class WiringContest(typing.TypedDict):
    """An ask several services claim and nothing has chosen between, so it reaches
    nothing.
    """

    by: str
    """The service that asked."""
    capability: str
    """What it asked for."""
    claimants: list[str]
    """Every claimant, named — a plugin's with the plugin beside it."""


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
    "PluginInstall",
    "PluginInstalls",
    "PluginNonconforming",
    "PluginRemoval",
    "PluginReproof",
    "PluginRestored",
    "PluginSource",
    "PluginSourceStanding",
    "PluginSourceStandingReachable",
    "PluginSourceStandingUnasked",
    "PluginSourceStandingUnreachable",
    "PluginSubstituted",
    "PluginUnfilled",
    "PluginUpdate",
    "PluginsEnvelope",
    "WiringContest",
]
