# Copyright (c) 2026 NightWorksIO
"""The `watch` envelope, and the shapes only `watch` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class SupervisionReport(typing.TypedDict):
    """What a watch saw, once the data root it was guarding was lost."""

    forms: list[str]
    """The forms that were being watched, and are now stopped."""
    reason: str
    """Why the watch ended: the data root vanished, or a different volume took
    its place — or, on a run that only said what a watch would do, that nothing
    was watched at all.
    """
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    stopped: bool
    """Whether stopping the services succeeded."""
    would: typing.NotRequired[Vigil | None]
    """The watch this run would have kept, where it only said what it would do.

    A guard is the one command with no ending of its own, so a rehearsal of it
    cannot be the command with its last step left out — it would hold until the
    drive was pulled. What it answers with is this instead, and the fields above
    then describe a watch that never began: nothing ended, and nothing was
    stopped. Absent on every watch that actually ran.
    """


class Vigil(typing.TypedDict):
    """The watch a run would keep, and what it would do at the end of it."""

    command: list[str]
    """The invocation it would run the moment that location went, word for word.

    Built by the same path a real watch stops the services through, rather than
    described beside it: an argv reported from a second reckoning is one nobody
    runs, and the one nobody runs is the one that stops being right.
    """
    every: int
    """How often it would look, in seconds."""
    root: str
    """The data location it would hold."""


class WatchEnvelope(typing.TypedDict):
    """The envelope carrying `watch`."""

    api_version: int
    data: SupervisionReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["watch"]


__all__ = [
    "SupervisionReport",
    "Vigil",
    "WatchEnvelope",
]
