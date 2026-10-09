# Copyright (c) 2026 NightWorksIO
"""The `history` envelope, and the shapes only `history` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class ChangeReport(typing.TypedDict):
    """One change lemonfiber made, and whether it could be put back."""

    alongside: int
    """How many changes that one operation made, this one among them.

    An operation is the unit an operator agreed to, and undoing half of one leaves a
    machine in a state nobody chose — so what a single line would take with it is on
    the line rather than left to be counted off the list.
    """
    at: str
    """When it was made, as whole seconds since the Unix epoch, written in decimal.

    A string of digits rather than a number, because it is the stamp the record keeps
    and a stamp is compared and stored as text; what it counts is stated here so a
    reader can turn it into a time without guessing at a format.

    **`0` means the clock was unreadable when the change was written**, not that it
    was made at the epoch: it is how a machine whose clock would not answer stamps a
    change. It is not an instant, so two changes both stamped `0` were not made at
    the same moment, and a reader showing it as a date in 1970 would be inventing
    one.
    """
    because: typing.NotRequired[str | None]
    """Why it could not go further, where it could not."""
    did: str
    """What it did, in the operator's terms."""
    instead: typing.NotRequired[str | None]
    """What to do instead, where there is something."""
    operation: str
    """The operation that made it — a seed, a reconfigure, an applied fix — so a
    history reads as what happened rather than as bare diffs.
    """
    reversal: ChangeReversal
    """How far it could be put back."""
    target: str
    """What it was made to."""


type ChangeReversal = typing.Literal["whole", "partial", "none"]
"""How far a change can be put back.

Published as the closed set it is, rather than as a word a reader has to trust will
be one of three: a surface that lays out a history branches on it, and a set the
contract names is one a generated reader can match exhaustively.
"""


class HistoryEnvelope(typing.TypedDict):
    """The envelope carrying `history`."""

    api_version: int
    data: HistoryReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["history"]


class HistoryReport(typing.TypedDict):
    """Everything lemonfiber changed, most recent first."""

    changes: list[ChangeReport]
    """The changes, newest first."""
    horizon: str
    """How far back the record goes, in the operator's terms.

    Stated rather than left to be inferred from the oldest entry: a record that has
    been trimmed and one that has always been short look identical from the entries
    alone, and only one of them means something is missing.
    """


__all__ = [
    "ChangeReport",
    "ChangeReversal",
    "HistoryEnvelope",
    "HistoryReport",
]
