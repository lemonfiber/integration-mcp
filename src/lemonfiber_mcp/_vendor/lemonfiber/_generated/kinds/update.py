# Copyright (c) 2026 NightWorksIO
"""The `update` envelope, and the shapes only `update` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.lifecycle__quality__reset__update import StackEdit
from ..shared.update__version import Notes


type Ending = typing.Literal["updated", "not-fetched", "not-started", "not-reached"]
"""How one service's update ended."""


type Jump = typing.Literal["major", "minor", "patch", "untellable"]
"""How large a step from one version to another is.

Named after the part of the version that moved rather than after a size, because
that is the fact an operator weighs: a first-number change is where a project puts
the work that breaks configurations, and the two behind it are where it puts the
work that does not.
"""


class StackUpdateReport(typing.TypedDict):
    """What updating the stack would change, or what a run of it came to."""

    applied: list[UpdateApplied]
    """What became of each service the run reached, in the order it reached them."""
    backup: typing.NotRequired[str | None]
    """Where the backup taken before anything moved was written."""
    changelog: Notes
    """What the release that brought these pins changed.

    The stack this would move to is the one this build carries, and the release
    that carried this build is what says why it moved. An operator weighing a
    stack update is weighing that, and being shown only which image numbers go up
    is being shown the arithmetic rather than the reason.
    """
    changes: list[UpdateChange]
    """What would move, and what taking each step means."""
    confirmed: bool
    """Whether the steps were agreed to, or only shown."""
    halted: typing.NotRequired[str | None]
    """Why the stack is not as the run found it, where it is not.

    Two runs end that way and an operator has the same thing to do about either:
    one that met a service which would not come back and stopped there, and one
    where every step succeeded and the stack would not start again afterwards.
    The second is not a failure of the update — `state` still says `Updated`,
    because it is — but the stack came down for the capture and something has to
    say that it is still down.
    """
    in_flight: list[str]
    """What the download clients are still working on, named so an operator can
    tell whether the thing they have been waiting for is among them.
    """
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    stack_edits: list[StackEdit]
    """Stack files the operator had edited, left as they set them rather than
    overwritten with this build's own, each with the change that was held back.
    """
    state: UpdateState
    """The one word the run comes to."""


class UpdateChange(typing.TypedDict):
    """What updating one service would change."""

    because: str
    """What the step means, in the words an operator decides on."""
    current: str
    """The version it is standing on now."""
    irreversible: bool
    """Whether taking it is a step nothing walks back."""
    jump: Jump
    """How large the step between them is."""
    refused: bool
    """Whether lemonfiber refuses to take it at all."""
    service: str
    """The service, by its manifest id, which is also its Compose service name."""
    target: str
    """The version this build pins for it."""


class UpdateEnvelope(typing.TypedDict):
    """The envelope carrying `update`."""

    api_version: int
    data: StackUpdateReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["update"]


type UpdateReversal = typing.Literal["rollback", "restore"]
"""How a service could be put back the way it was.

The distinction is the whole of why this is reported rather than left to be
worked out: pinning the previous image again is a minute's work, and restoring a
backup is an evening. Offering the first where only the second can succeed is
worse than offering nothing, because it is acted on.
"""


type UpdateState = typing.Literal["current", "updates-available", "updated", "partial", "failed"]
"""Where the stack stands against the versions this build pins.

Exactly one of these is true of a run at a time. A surface that had to say
\"updates available, and also partly applied\" would be reporting the question
rather than the answer.
"""


UpdateApplied = typing.TypedDict(
    "UpdateApplied",
    {
        "detail": typing.NotRequired[str | None],
        "ending": Ending,
        "from": str,
        "reversal": UpdateReversal,
        "service": str,
        "to": str,
    },
)
"""What one service's update came to."""


__all__ = [
    "Ending",
    "Jump",
    "StackUpdateReport",
    "UpdateApplied",
    "UpdateChange",
    "UpdateEnvelope",
    "UpdateReversal",
    "UpdateState",
]
