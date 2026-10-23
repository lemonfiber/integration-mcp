# Copyright (c) 2026 NightWorksIO
"""The shapes `dashboard` and `household` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .askable__dashboard__household import MemberAsking, Policy
from .dashboard__household__invitation import Unrated


class Estimate(typing.TypedDict):
    """About how much room one request will want.

    Carried as a number and a word rather than as a rendered string, so a surface can
    put it in a column and still say what it is. The word is not decoration: a figure
    with nothing hedging it is a promise, and this cannot keep one.
    """

    bytes: int
    """About how many bytes it will take."""
    measured: bool
    """Whether this was measured. Always false — nothing here has measured anything,
    and the field is present so that a surface rendering it cannot forget to say so.
    """


class HouseholdMember(typing.TypedDict):
    """One household member: who they are, what they may watch, when they were last
    seen, and everything they have asked for.
    """

    access: MemberAccess
    """What they may watch."""
    asking: typing.NotRequired[MemberAsking | None]
    """What they may ask for, and what their period has left of it.

    Absent where the request service holds no account for them, and where it could
    not be asked — an unread answer is not an unlimited member, and reporting one as
    the other would tell an operator their quota was never applied.
    """
    claimed: bool
    """Whether somebody has set a password on the account. False is an invitation
    nobody has taken up rather than a member who is not here.
    """
    last_seen: typing.NotRequired[str | None]
    """When the media server last saw them, as it timestamps it. Absent where nobody
    has ever signed in, which is exactly the unclaimed invitations.
    """
    name: str
    """The member, by the name their account is held under."""
    requests: list[MemberRequest]
    """What they asked for, newest first."""
    standing: MemberStanding
    """Where the account stands: an invitation still out or run out, a member who can
    sign in, or one switched off.
    """
    to_hand_over: list[str]
    """What this member would be told, in the words they would read it in.

    Everything a household member is owed at the moment of asking and cannot be
    shown where they ask: what happens to what they ask for, what their period has
    left and when it makes room, what is still waiting on an answer, and what was
    refused and why. Written to them rather than about them, in the household's own
    words, so it can be handed over as it stands.

    Empty where there is nothing to tell them — a member the request service holds
    no account for has no standing to report and nothing waiting.
    """


class HouseholdReport(typing.TypedDict):
    """Who is in the household, what each may watch, and what each has asked for."""

    allows: typing.NotRequired[str | None]
    """What that policy allows in a period, in the words a household says it in.

    Absent where nothing limits the household, which is not the same as a policy
    that could not be read: that one leaves [`Self::policy`] absent too.
    """
    available: bool
    """Whether the household could be read at all. A false here is why the list is
    empty, and keeps an unread record from being mistaken for an empty house — the
    same honesty a trace keeps about a silence it did not hear.
    """
    filtering: typing.NotRequired[str | None]
    """What the limits on this household are and are not, where anybody carries one.

    Absent on a household nobody has limited, because there is no claim to be modest
    about. Present the moment there is one, because a parent who has set a limit is
    exactly the reader who might take it for a lock.
    """
    findings: list[str]
    """What could not be read, and anything else worth the operator's attention."""
    members: list[HouseholdMember]
    """Everybody the media server holds an account for, in name order — including
    those who have never asked for anything, and the invitations nobody has taken
    up yet.
    """
    policy: typing.NotRequired[Policy | None]
    """What happens to what the household asks for where nobody chose otherwise for
    one person. Absent where the request service could not be asked.
    """
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


class MemberAccess(typing.TypedDict):
    """What one member may watch, in the household's own words.

    Read off the media server's account rather than kept here: that is where access is
    decided, and a second copy is a copy able to disagree.
    """

    administrator: bool
    """Whether the account administers the media server."""
    age_limit: typing.NotRequired[int | None]
    """The highest rating they may watch, where the operator set a limit."""
    disabled: bool
    """Whether the account is switched off — held, but unable to sign in."""
    every_library: bool
    """Every library, rather than a chosen few. The ordinary case."""
    libraries: list[str]
    """The libraries they may watch where it is not every one, by the names the
    operator gave them — or by the server's identifiers where the library list
    could not be read, which a finding says.
    """
    rated: typing.NotRequired[Rated | None]
    """What that limit comes to in the certificates this media server names, in the
    operator's own country. Absent where no limit is set.
    """
    restriction: Restriction
    """What they are held to, in one word — including where what they may watch and
    what they may ask for disagree.
    """
    unrated: Unrated
    """What becomes of content the media server has no rating for.

    Said either way, because an unexplained absence is the thing this answers: a
    restricted member missing half the library is either this setting or a defect,
    and an operator cannot tell which from silence.
    """


class MemberRequest(typing.TypedDict):
    """One thing a household member asked for, and where it stands in their words."""

    arrived: typing.NotRequired[str | None]
    """When the title arrived on the media server, as the request service timestamps it.
    Absent, not null, until it is there.
    """
    estimate: typing.NotRequired[Estimate | None]
    """About how much room it will want, at the quality in force.

    A guess and labelled as one — see [`crate::asking::Estimate`]. Absent where the
    request service names a kind this build does not know, since there is nothing to
    guess the length of.
    """
    id: int
    """The number the request service files it under, which is how one is named again
    when somebody rules on it.
    """
    media: typing.NotRequired[str | None]
    """What kind of thing it is — a series, a film — in the household's own words.
    Absent where the request service names a kind this build does not know.
    """
    refused: typing.NotRequired[Refused | None]
    """Why it was turned down, where it was turned down from here.

    **The request service keeps none**, so this is lemonfiber's own record and is
    said to be — a reason presented as delivered would end the operator's job at
    exactly the point it begins. Absent on a request nobody has refused, and on one
    refused in the request service itself, where there are no words to report and
    inventing some would put them in somebody's mouth.

    Whether the words were carried to the person who asked is the record's own
    `told`, which is why the two travel together: what an operator does next turns
    on it, and a reason read without it is a reason of unknown standing.
    """
    shelf_id: typing.NotRequired[str | None]
    """The identifier the media server holds the title under, which is the one the held
    read names it by, so a request that has arrived can be found on the shelf. Absent,
    not null, until it is there.
    """
    state: typing.NotRequired[RequestState | None]
    """Where the request stands, or absent where the request service reports a status
    this build does not know rather than guessing it into the nearest word.
    """
    title: typing.NotRequired[str | None]
    """What it is called: from the library of the service filing it, where it has been
    told about it and that library could be read, and otherwise from the request
    service's own record of the title. Absent where neither names it.
    """
    waiting_days: typing.NotRequired[int | None]
    """How many whole days it has been waiting on somebody, where it is waiting at all
    and the service's own date could be read.

    Only on the ones nobody has ruled on. A request already answered has not been
    waiting since it was made, and a figure beside one would be counting the wrong
    thing.
    """
    year: typing.NotRequired[int | None]
    """The year that title came out, where the service that named it knows one. Absent,
    not null, otherwise.
    """


type MemberStanding = typing.Literal["invited", "expired", "declined", "active", "suspended"]
"""Where one member's account stands.

**Switched off is its own answer rather than a flag beside another.** An account the
media server switched off after too many wrong passwords reads, on every other field,
exactly like one that works — and the person holding it has only been told their
password is wrong. What unlocks it is a reissue, which is the operator's to do, so the
operator is the one who has to be able to see it.
"""


class Passed(typing.TypedDict):
    """Where a refusal's words were carried, and when."""

    at: typing.NotRequired[str | None]
    """When the attempt was made, absent where the clock could not be written down."""
    to: list[str]
    """The services they reached, by the names the member knows them by. Empty where
    there was nowhere this could send.
    """


class Rated(typing.TypedDict):
    """What one age limit comes to, in the certificates named for it.

    Both sides, because either alone misleads. What is allowed without what is held
    back reads as a limit that stops nothing; what is held back without what is allowed
    reads as a limit that stops everything.
    """

    allows: list[str]
    """The certificates at the highest age this limit still lets through.

    Empty where the table names nothing at or below the limit, which is a limit
    that lets nothing rated through at all.
    """
    fell_back: bool
    """Whether these came from lemonfiber's own mapping because the media server's
    table named no certificates.

    Carried rather than hidden: a certificate said to be this household's when it
    is this program's is the kind of claim a parent would act on.
    """
    holds_back: list[str]
    """The certificates at the lowest age this limit holds back.

    Empty where the table names nothing above the limit, which is a limit that
    holds nothing rated back at all.
    """


class Refused(typing.TypedDict):
    """What was said when one request was turned down."""

    at: typing.NotRequired[str | None]
    """When it was turned down, so somebody reading it later knows which answer this
    was rather than assuming it is the newest.

    Absent where the machine's clock could not be written as a date, which is a
    refusal worth keeping the words of and not worth losing them over.
    """
    expired: typing.NotRequired[bool]
    """Whether nobody ruled on it and the period the household agreed to closed it,
    rather than an operator turning it down.

    The words are then this program's own, which is why the two are told apart here
    and not left to be read off the sentence: an operator scanning for what happened
    while they were away is looking for exactly the ones nobody answered, and a
    member is owed the difference between having been refused and having run out.

    Absent from every record written before a household could arrange this, which is
    the right reading of them — they are all somebody's own refusals.
    """
    reason: str
    """Why, in the words it was turned down in."""
    told: typing.NotRequired[Passed | None]
    """Whether the words have been carried to whoever asked, and where to.

    Absent until the one attempt has been made. **This is what makes a second one
    impossible rather than unlikely**: carrying happens only where this is absent,
    and it is written whether anything was reached or not — so a member with nowhere
    to send to is asked about once, and a household is never told the same thing
    twice by a run that happened to be started twice.
    """


type RequestState = typing.Literal[
    "waiting-for-approval", "declined", "failed", "getting", "partly-here", "here", "gone"
]
"""Where one request stands, in the words the person who made it would use.

Deliberately coarser than a [`crate::trace::Stage`]: a member does not need to know
that a release was grabbed but not imported, only that it is on its way. The trace is
where that detail stays, and a request names the item so it can be asked for.
"""


type Restriction = typing.Literal["unrestricted", "rating-limited", "library-limited", "both", "inconsistent"]
"""What one member is held to, in the words a household would use.

The two restrictions are one decision and two services: the media server decides
what may be *watched* and the request service what may be *asked for*. Setting one
without the other is the hole this vocabulary exists to name — a child who cannot
watch something but can pull it into the library has parents who set a limit and got
half of one.
"""


__all__ = [
    "Estimate",
    "HouseholdMember",
    "HouseholdReport",
    "MemberAccess",
    "MemberRequest",
    "MemberStanding",
    "Passed",
    "Rated",
    "Refused",
    "RequestState",
    "Restriction",
]
