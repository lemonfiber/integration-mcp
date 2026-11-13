# Copyright (c) 2026 NightWorksIO
"""The `notify` envelope, and the shapes only `notify` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.alerts__notify import NotificationKind


class NotifyBackend(typing.TypedDict):
    """One back-end, as the read lists it."""

    chosen_by: NotifyChosenBy
    """Who chose it."""
    failures: list[NotifyDelivery]
    """Every failed delivery since its last confirmed one, newest first."""
    hosted: typing.NotRequired[NotifyHosted | None]
    """Where it is hosted, absent where it is the household's own."""
    id: str
    """The stack's name for it, the same on every read."""
    kind: NotifyBackendKind
    """What it speaks."""
    last: typing.NotRequired[NotifyDelivery | None]
    """Its newest delivery, absent where it has never delivered."""
    proof: NotifyProof
    """How far it is proven."""
    retry: typing.NotRequired[NotifyRetry | None]
    """The delivery still to be tried again, absent where none is."""
    where: str
    """The host and topic or path it reaches, with no credential."""


type NotifyBackendKind = typing.Literal["ntfy", "gotify", "webhook", "apprise", "unifiedpush"]
"""What a back-end speaks."""


type NotifyChosenBy = typing.Literal["operator"] | NotifyChosenByVariant2
"""Who chose a back-end."""


class NotifyChosenByVariant2(typing.TypedDict):
    """A household member, by their account's id."""

    member: str


class NotifyDelivery(typing.TypedDict):
    """One delivery to one back-end."""

    at: int
    """When it was sent, in seconds since the Unix epoch."""
    kind: NotificationKind
    """Which kind of alert it carried."""
    outcome: NotifyOutcome
    """What became of it."""


class NotifyEnvelope(typing.TypedDict):
    """The envelope carrying `notify`."""

    api_version: int
    data: NotifyReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["notify"]


class NotifyHosted(typing.TypedDict):
    """A back-end on a host that is not the household's own."""

    host: str
    """The host it reaches."""
    leaves: list[str]
    """What leaves for it, in the operator's words."""


type NotifyOutcome = typing.Literal["confirmed", "sent"] | NotifyOutcomeVariant3
"""What became of one delivery."""


class NotifyOutcomeVariant3(typing.TypedDict):
    """The back-end refused it or did not answer, in its own words."""

    failed: str


type NotifyProof = typing.Literal["unproven"] | NotifyProofVariant2 | NotifyProofVariant3
"""How far a back-end is proven."""


class NotifyProofVariant2(typing.TypedDict):
    """A test was seen arriving, at this instant in seconds since the Unix epoch."""

    proven: int


class NotifyProofVariant3(typing.TypedDict):
    """Nothing is delivered to it until it is proven again, and why."""

    held: str


class NotifyReport(typing.TypedDict):
    """Where a message goes: every back-end the stack delivers to."""

    backends: list[NotifyBackend]
    """Each back-end, in the order it was added."""
    rehearsed: bool
    """Whether this was a rehearsal of a change, with nothing kept."""
    state: NotifyState
    """Where delivery as a whole stands."""
    unread: list[NotifyUnread]
    """Each back-end whose record could not be read, with why."""


class NotifyRetry(typing.TypedDict):
    """A delivery still to be tried again."""

    attempt: int
    """Which attempt that will be, from one."""
    next: int
    """When it is tried next, in seconds since the Unix epoch."""
    of: int
    """How many attempts it is given."""


type NotifyState = typing.Literal["unconfigured", "ready", "degraded", "unreachable"]
"""Where delivery as a whole stands."""


class NotifyUnread(typing.TypedDict):
    """A back-end whose record could not be read."""

    backend: str
    """The back-end, by its id."""
    because: str
    """Why."""


__all__ = [
    "NotifyBackend",
    "NotifyBackendKind",
    "NotifyChosenBy",
    "NotifyChosenByVariant2",
    "NotifyDelivery",
    "NotifyEnvelope",
    "NotifyHosted",
    "NotifyOutcome",
    "NotifyOutcomeVariant3",
    "NotifyProof",
    "NotifyProofVariant2",
    "NotifyProofVariant3",
    "NotifyReport",
    "NotifyRetry",
    "NotifyState",
    "NotifyUnread",
]
