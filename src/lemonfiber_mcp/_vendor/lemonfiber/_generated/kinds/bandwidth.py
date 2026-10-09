# Copyright (c) 2026 NightWorksIO
"""The `bandwidth` envelope, and the shapes only `bandwidth` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.bandwidth__pausing import Pulling


type Answer = AnswerHeld | AnswerSilent
"""How one download client answered about the limits on it."""


class AnswerHeld(typing.TypedDict):
    """It answered, in both directions."""

    answered: typing.Literal["held"]
    down: BandwidthHeld
    """What became of the download limit."""
    period: typing.NotRequired[Period | None]
    """Which side of the household's day it says it is on, where it keeps the
    hours itself.
    """
    up: BandwidthHeld
    """And of the upload one."""


class AnswerSilent(typing.TypedDict):
    """It did not answer, and this is what it said.

    Its own line rather than an absence, because a client nobody could reach is
    a client whose limits are unknown, and an unknown limit rendered as no
    limit is the report reading better than the stack is.
    """

    answered: typing.Literal["silent"]
    said: str
    """What went wrong, in the words of whatever refused."""


class BandwidthEnvelope(typing.TypedDict):
    """The envelope carrying `bandwidth`."""

    api_version: int
    data: Sharing
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["bandwidth"]


class BandwidthHeld(typing.TypedDict):
    """One direction on one client: what it was asked for, took, and is doing."""

    accepted: typing.NotRequired[int | None]
    """What it reports as in force."""
    asked: typing.NotRequired[int | None]
    """What it was asked to hold to, in bytes a second, where anything was."""
    moving: typing.NotRequired[int | None]
    """What it is moving right now, where it reported a figure."""
    verdict: BandwidthVerdict
    """What that adds up to."""


class BandwidthReading(typing.TypedDict):
    """One direction's limit, as declared and as it comes to."""

    limit: Limit
    """The limit as it was expressed."""
    resolved: Resolved
    """What it comes to against the measured line."""
    says: str
    """The limit and the line it was measured against, in one sentence.

    Carried rather than left to each surface, so the rule that a share is never
    shown without the figure it is a share of is kept in one place instead of
    three.
    """


type BandwidthVerdict = typing.Literal["unasked", "nothing-to-limit", "holding", "ignored", "overrunning"]
"""What became of one limit, in one direction, on one client."""


class Cap(typing.TypedDict):
    """A monthly allowance, and what to do at the end of it."""

    exceeded: WhenExceeded
    """What happens when it is reached, chosen when the cap was declared."""
    monthly: int
    """The allowance, in bytes."""


class Capacity(typing.TypedDict):
    """What the line was measured to carry."""

    down: int
    """Bytes a second down."""
    source: Source
    """Where the figure came from."""
    taken: int
    """When it was taken, in seconds since the epoch."""
    through_tunnel: bool
    """Whether the path it was measured over goes through the VPN tunnel."""
    up: int
    """Bytes a second up.

    Measured apart from the download, because a home connection is asymmetric
    and a single figure for both would make every upload share far larger than
    the operator meant.
    """


class Holding(typing.TypedDict):
    """One download client, and what became of the limits it was given."""

    answer: Answer
    """What it said."""
    client: str
    """The client, by the name the stack knows it under."""
    pulling: typing.NotRequired[Pulling | None]
    """Whether it is fetching at all, where a declared cap made that a question.

    Absent on a stack with no cap rather than assumed to be fetching: asking
    every client whether it has stopped, on a stack where nothing would ever
    stop it, is traffic spent on a figure nothing would act on.
    """


type Limit = LimitUnlimited | LimitShare | LimitAbsolute
"""How much of the line something may take."""


class Metered(typing.TypedDict):
    """What the stack itself moved in a calendar month, and what that leaves out."""

    down: int
    """Bytes pulled down, as far as the clients count them."""
    excludes: str
    """What this count does not include, always said."""
    incomplete: list[str]
    """What is known to be missing from the count itself, where anything is."""
    month: str
    """The month, as the client that dated the figures dates them."""
    up: int
    """Bytes given back."""


type Period = typing.Literal["active", "quiet"]
"""Which side of the household's day a moment falls on."""


type Reached = typing.Literal["within", "warning", "exceeded"]
"""Where a month stands against a declared cap."""


type Resolved = ResolvedUnlimited | ResolvedAt | ResolvedUnmeasured
"""What a limit comes to once it is weighed against a measured line."""


type RespiteStanding = RespiteStandingNone | RespiteStandingInForce | RespiteStandingExpired
"""Where a respite stands against the clock."""


class RespiteStandingExpired(typing.TypedDict):
    """It ran out, this long ago. Said once, then cleared."""

    seconds: int
    standing: typing.Literal["expired"]


class RespiteStandingInForce(typing.TypedDict):
    """In force, with this long left."""

    seconds: int
    standing: typing.Literal["in-force"]


class RespiteStandingNone(typing.TypedDict):
    """None was asked for."""

    standing: typing.Literal["none"]


type Restraint = typing.Literal[
    "unlimited", "limited", "scheduled-active", "scheduled-quiet", "overridden", "cap-warning", "cap-exceeded"
]
"""Where the line stands."""


class Sharing(typing.TypedDict):
    """How the line is shared, and what that costs."""

    acting: typing.NotRequired[str | None]
    """What a spent cap is doing to the figures above, where one is spent."""
    applied: bool
    """Whether this run wrote the limits to the clients or only read them."""
    cap: typing.NotRequired[Cap | None]
    """The monthly cap, where one was declared."""
    capacity: typing.NotRequired[Capacity | None]
    """What the line was measured to carry."""
    cautions: list[str]
    """What is worth knowing about that reading before trusting it."""
    clients: list[Holding]
    """What each download client was asked and what it is doing about it."""
    down: BandwidthReading
    """The download limit."""
    means: str
    """What that means for the household."""
    metered: typing.NotRequired[Metered | None]
    """What the stack itself moved this month."""
    ratio: typing.NotRequired[str | None]
    """What throttling the upload costs, where an upload limit is in force."""
    reached: typing.NotRequired[Reached | None]
    """Where the month stands against it."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    respite: RespiteStanding
    """The override, where one is running or has just run out."""
    respite_says: typing.NotRequired[str | None]
    """What the override amounts to, in words."""
    restraint: Restraint
    """Where the line stands."""
    rhythm: typing.NotRequired[Rhythm | None]
    """The household's hours, where any were declared."""
    untouched: list[str]
    """What is outside every limit here."""
    up: BandwidthReading
    """The upload limit, which is declared apart and defaults lower."""
    zone: typing.NotRequired[str | None]
    """The zone the clients read those hours in, where the stack says."""


type Source = typing.Literal["declared", "observed"]
"""Where a figure for the line came from."""


type WhenExceeded = typing.Literal["pause", "throttle", "continue"]
"""What to do when a declared cap is reached."""


LimitAbsolute = typing.TypedDict(
    "LimitAbsolute",
    {
        "as": typing.Literal["absolute"],
        "at": int,
    },
)
"""A figure in bytes a second, as it was given."""


LimitShare = typing.TypedDict(
    "LimitShare",
    {
        "as": typing.Literal["share"],
        "at": int,
    },
)
"""A proportion of what the line was measured to carry, in whole per cent."""


LimitUnlimited = typing.TypedDict(
    "LimitUnlimited",
    {
        "as": typing.Literal["unlimited"],
    },
)
"""Nothing holds it back."""


ResolvedAt = typing.TypedDict(
    "ResolvedAt",
    {
        "bytes_per_second": int,
        "is": typing.Literal["at"],
    },
)
"""This many bytes a second."""


ResolvedUnlimited = typing.TypedDict(
    "ResolvedUnlimited",
    {
        "is": typing.Literal["unlimited"],
    },
)
"""Nothing holds it back."""


ResolvedUnmeasured = typing.TypedDict(
    "ResolvedUnmeasured",
    {
        "is": typing.Literal["unmeasured"],
    },
)
"""A proportion was asked for and nothing has measured the line.

Deliberately not folded into [`Self::Unlimited`]. \"Half of an unknown
number\" resolving to \"no limit at all\" is the shape of a setting an
operator believes is in force while the stack takes the whole line.
"""


Rhythm = typing.TypedDict(
    "Rhythm",
    {
        "from": str,
        "to": str,
    },
)
"""The hours the household is awake, declared once for every download client."""


__all__ = [
    "Answer",
    "AnswerHeld",
    "AnswerSilent",
    "BandwidthEnvelope",
    "BandwidthHeld",
    "BandwidthReading",
    "BandwidthVerdict",
    "Cap",
    "Capacity",
    "Holding",
    "Limit",
    "LimitAbsolute",
    "LimitShare",
    "LimitUnlimited",
    "Metered",
    "Period",
    "Reached",
    "Resolved",
    "ResolvedAt",
    "ResolvedUnlimited",
    "ResolvedUnmeasured",
    "RespiteStanding",
    "RespiteStandingExpired",
    "RespiteStandingInForce",
    "RespiteStandingNone",
    "Restraint",
    "Rhythm",
    "Sharing",
    "Source",
    "WhenExceeded",
]
