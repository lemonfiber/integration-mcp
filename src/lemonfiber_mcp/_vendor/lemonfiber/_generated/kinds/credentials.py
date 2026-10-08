# Copyright (c) 2026 NightWorksIO
"""The `credentials` envelope, and the shapes only `credentials` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.config__credentials__doctor__outbound__plugins__wiring__wizard import ValueOrigin


type CredentialReach = CredentialReachUpdated | CredentialReachPending | CredentialReachFailed
"""How far a rotation reached one consumer."""


class CredentialReachFailed(typing.TypedDict):
    """It could not be updated. Named rather than dropped, because a consumer left
    holding the old value is the failure this list exists to surface.
    """

    detail: str
    """Why it could not be."""
    reach: typing.Literal["failed"]


class CredentialReachPending(typing.TypedDict):
    """It will hold the replacement once one more thing happens, and that thing is
    named. A consumer reading the value out of a container's environment has it
    fixed at the moment the container was created, so recording a new one is
    only half of reaching it.
    """

    detail: str
    """What still has to happen, written as the command that does it."""
    reach: typing.Literal["pending"]


class CredentialReachUpdated(typing.TypedDict):
    """It now holds the replacement."""

    reach: typing.Literal["updated"]


type CredentialState = typing.Literal["absent", "active", "stale", "invalid", "rotating", "superseded"]
"""Where a credential stands, as far as lemonfiber can tell without spending it.

Six states rather than a boolean because the operator's next move differs for
each: an absent credential is one to supply, a stale one is one to prove, an
invalid one is one to replace, and the two rotation states exist so a run
interrupted half-way through a replacement is legible rather than mysterious.
"""


class CredentialsEnvelope(typing.TypedDict):
    """The envelope carrying `credentials`."""

    api_version: int
    data: Inventory
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["credentials"]


class Inventory(typing.TypedDict):
    """The whole answer to a question about credentials.

    Every ask answers with the inventory as it now stands, and adds what became of
    whatever else was asked for. An operator who has just rotated something wants to
    see the inventory that rotation produced, not a receipt they have to go and check
    against one.
    """

    held: list[CredentialHeld]
    """Every credential, whether or not it is present."""
    protection: Protection
    """What keeping them in files does and does not protect against."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    revealed: typing.NotRequired[Revealed | None]
    """One value, where one was asked for."""
    rotated: typing.NotRequired[Rotation | None]
    """What became of a rotation, where one was asked for."""


type Origin = typing.Literal["operator", "service", "lemonfiber"]
"""Who produced a credential, which decides what can be done about it."""


class Propagation(typing.TypedDict):
    """One consumer, and how far the rotation reached it."""

    consumer: str
    """What authenticates with the credential."""
    reach: CredentialReach
    """How far the rotation reached it."""


class Protection(typing.TypedDict):
    """The honest account of what the credential store protects against.

    Two lists and a sentence, carried as data rather than printed here, so the API
    serves the same words the terminal prints and neither can drift into a claim the
    other does not make.
    """

    against: list[str]
    """What it protects against."""
    not_against: list[str]
    """What it does not protect against."""
    summary: str
    """What the storage is, before any claim about it."""


class Revealed(typing.TypedDict):
    """One stored value, handed back because the operator asked for it and said so.

    Separate from [`Held`] rather than a field on it, so that the inventory cannot
    carry a value by accident: a surface that renders the inventory has nothing to
    render, whatever it does.
    """

    name: str
    """Which credential this is."""
    value: typing.NotRequired[str | None]
    """The value, present only where the ask was confirmed."""
    warning: str
    """What the operator is told before it appears, whether or not it appears."""


class Rotation(typing.TypedDict):
    """What one rotation came to."""

    consumers: list[Propagation]
    """Every consumer, and how far the rotation reached it."""
    credential: str
    """Which credential was to be replaced."""
    settled: Settled
    """What became of the replacement."""


type Settled = (
    SettledReplaced
    | SettledRefused
    | SettledUnproven
    | SettledReplacedUnproven
    | SettledRehearsed
    | SettledUnknown
    | SettledElsewhere
)
"""What became of a rotation."""


class SettledElsewhere(typing.TypedDict):
    """A replacement for this one does not come from here.

    Either the operator's provider issued it, in which case inventing one would
    produce a credential no service has ever heard of; or the service that holds
    it offers no way to change it in place. Either way what is owed is a
    sentence saying where a replacement does come from, not an attempt.
    """

    detail: str
    """Where a replacement comes from, and what to do once it exists."""
    settled: typing.Literal["elsewhere"]


class SettledRefused(typing.TypedDict):
    """The service answered and refused the replacement. Nothing was changed."""

    detail: str
    """What the service said, with any credential in it withheld."""
    settled: typing.Literal["refused"]


class SettledRehearsed(typing.TypedDict):
    """Nothing was attempted, because this run only said what a rotation would do.

    Its own outcome rather than one of the refusals above, because it is not a
    refusal: nothing went wrong, and what an operator is being told is what would
    happen if they ran it again meaning it. Carrying its own three fields rather
    than one sentence, because \"it would rotate the qBittorrent password\" is not a
    report — where the value lives is what would be written over, and what is owed
    afterwards is the half nobody finds out about until a consumer stops working.

    No value appears here and none is generated to put here. A replacement minted
    to describe a rotation is a secret that exists because somebody asked a
    question, and it would then have to be kept or thrown away — and one thrown
    away may be one the service has already taken.
    """

    afterwards: list[str]
    """What would still need doing before every consumer held the replacement."""
    detail: str
    """What a real run would do, step by step, in lemonfiber's own words."""
    location: str
    """Where the value that would be replaced is kept."""
    settled: typing.Literal["rehearsed"]


class SettledReplaced(typing.TypedDict):
    """The replacement was proven and is now the value in force."""

    observed: str
    """What the service did while proving it — an observation, never the value."""
    settled: typing.Literal["replaced"]


class SettledReplacedUnproven(typing.TypedDict):
    """The service replaced the credential itself, and the replacement did not answer.

    The one way of not landing that keeps nothing: a service asked to replace its
    own key drops the old one the moment it makes the new one, so there is no order
    that proves first. What is owed is the command that hands the new one out once
    the service answers.
    """

    detail: str
    """What did not answer, and what to run once it does."""
    settled: typing.Literal["replaced-unproven"]


class SettledUnknown(typing.TypedDict):
    """Nothing in this stack holds a credential by that name."""

    known: list[str]
    """The names that would have been accepted."""
    settled: typing.Literal["unknown"]


class SettledUnproven(typing.TypedDict):
    """Nothing usable answered, so the replacement could not be proven. Nothing
    was changed, because an unproven replacement is not a better one.
    """

    detail: str
    """Why nothing could be concluded."""
    settled: typing.Literal["unproven"]


CredentialHeld = typing.TypedDict(
    "CredentialHeld",
    {
        "advisory": typing.NotRequired[str | None],
        "consumers": list[str],
        "fingerprint": typing.NotRequired[str | None],
        "from": ValueOrigin,
        "location": str,
        "name": str,
        "origin": Origin,
        "setting": str,
        "state": CredentialState,
    },
)
"""One credential, described without being disclosed.

There is deliberately no value here, and no field a value could be put in later
without the change being visible in review.
"""


__all__ = [
    "CredentialHeld",
    "CredentialReach",
    "CredentialReachFailed",
    "CredentialReachPending",
    "CredentialReachUpdated",
    "CredentialState",
    "CredentialsEnvelope",
    "Inventory",
    "Origin",
    "Propagation",
    "Protection",
    "Revealed",
    "Rotation",
    "Settled",
    "SettledElsewhere",
    "SettledRefused",
    "SettledRehearsed",
    "SettledReplaced",
    "SettledReplacedUnproven",
    "SettledUnknown",
    "SettledUnproven",
]
