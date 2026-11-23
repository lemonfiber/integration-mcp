# Copyright (c) 2026 NightWorksIO
"""The `caller` envelope, and the shapes only `caller` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


type Caller = CallerOperator | CallerMember | CallerKey
"""Who is calling."""


class CallerEnvelope(typing.TypedDict):
    """The envelope carrying `caller`."""

    api_version: int
    data: Calling
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["caller"]


type Calling = CallingKnown | CallingNobody | CallingUnconfirmed | CallingHeld | CallingExposed
"""What the session or key a request carried came to."""


class CallingExposed(typing.TypedDict):
    """A key that crossed a network in the clear."""

    standing: typing.Literal["exposed"]


class CallingHeld(typing.TypedDict):
    """A key held back by too many wrong answers."""

    retry_after: int
    """How many whole seconds are left to wait."""
    standing: typing.Literal["held"]


class CallingKnown(typing.TypedDict):
    """Somebody this run admits."""

    caller: Caller
    """Who they are."""
    standing: typing.Literal["known"]


class CallingNobody(typing.TypedDict):
    """Nobody this run admits."""

    standing: typing.Literal["nobody"]


class CallingUnconfirmed(typing.TypedDict):
    """A member the media server could not be asked about."""

    standing: typing.Literal["unconfirmed"]


CallerKey = typing.TypedDict(
    "CallerKey",
    {
        "as": typing.Literal["key"],
        "name": str,
        "scope": str,
    },
)
"""A program, on a key the operator or a member minted for it."""


CallerMember = typing.TypedDict(
    "CallerMember",
    {
        "as": typing.Literal["member"],
        "id": str,
    },
)
"""A household member, on a session of their own."""


CallerOperator = typing.TypedDict(
    "CallerOperator",
    {
        "as": typing.Literal["operator"],
    },
)
"""The operator, on a session opened with the machine's password."""


__all__ = [
    "Caller",
    "CallerEnvelope",
    "CallerKey",
    "CallerMember",
    "CallerOperator",
    "Calling",
    "CallingExposed",
    "CallingHeld",
    "CallingKnown",
    "CallingNobody",
    "CallingUnconfirmed",
]
