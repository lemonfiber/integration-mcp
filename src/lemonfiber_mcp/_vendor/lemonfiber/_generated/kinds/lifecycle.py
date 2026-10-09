# Copyright (c) 2026 NightWorksIO
"""The `lifecycle` envelope, and the shapes only `lifecycle` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.dashboard__lifecycle__status import Service
from ..shared.lifecycle__migration import ConflictReport
from ..shared.lifecycle__preview import Plan
from ..shared.lifecycle__quality__reset__update import StackEdit
from ..shared.lifecycle__status import Condition


class LifecycleEnvelope(typing.TypedDict):
    """The envelope carrying `lifecycle`."""

    api_version: int
    data: LifecycleReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["lifecycle"]


class LifecycleReport(typing.TypedDict):
    """What a lifecycle command did, or would have done."""

    action: str
    """The Compose subcommand that was run."""
    command: list[str]
    """The exact command, so what happened is never a matter of trust."""
    condition: typing.NotRequired[Condition | None]
    """What those services amount to, as one word."""
    forwarding: typing.NotRequired[str | None]
    """What starting the stack did about the VPN's forwarded port, where it did
    anything. Absent in the ordinary case — the client was already on it, or
    there is no tunnel to forward through — and a sentence where the client was
    moved, or could not be.
    """
    held: typing.NotRequired[str | None]
    """Why nothing was run, where a start declined to run anything.

    Absent for every ordinary command, which is what makes it readable: a
    lifecycle report with an empty plan and a status of nothing is a report of
    something that did not happen, and without this there is nowhere to say
    whether that was a fault or the correct answer. A start at a login declines
    for three reasons the operator would each act on differently — the stack was
    stopped on purpose, autostart was never asked for, or this machine is on its
    battery and nobody said to start anyway — and a run nobody is watching has to
    leave the reason somewhere a reader finds later.
    """
    offer: typing.NotRequired[str | None]
    """The offer a restart answers: the services it would restart, named so that a
    restart carrying it back is carried out against those services or refused.
    Absent for every other action.
    """
    plan: Plan
    """What the named forms came to: the profiles, the services they hold, and
    what the configuration left out.

    The resolved plan itself rather than a copy of its parts, because it is
    stated to the operator before the command runs and read out of the
    report afterwards — two accounts of one run, and a second shape for it
    would be a way for them to differ.
    """
    port_conflicts: typing.NotRequired[list[ConflictReport]]
    """Host ports this start wants that another Compose project on this machine
    already answers on, each named on both sides.

    Empty for every action that starts nothing, and empty on a machine running one
    stack. Reported rather than refused: a port somebody deliberately shares is
    their business, and the start goes ahead — what this changes is whether an
    operator meeting a bind failure knows who is holding the port.
    """
    rehearsed: bool
    """Whether this was a rehearsal."""
    services: list[Service]
    """What each service ended up doing, where the action waited to find out, or
    where a start did not complete, read once when it ended.

    Empty for actions that do not wait. Stopping is finished when Compose
    says it is, and surveying afterwards would only report the absence it
    was asked to produce. A start that failed is not waited on, and names every
    service it addressed and those they depend on as the engine had them then.
    """
    stack_edits: list[StackEdit]
    """Stack files the operator has edited, left as they set them rather than
    overwritten with lemonfiber's own. Empty in the ordinary case; a named entry
    warns that an upgrade would change a file they changed, and shows the diff.
    """
    status: typing.NotRequired[int | None]
    """The exit status, absent for a rehearsal or a signalled process."""
    switched: typing.NotRequired[Switched | None]
    """What narrowing moved, where the command was a switch. Absent for every
    other action, which is what tells a reader that nothing was left running
    on purpose.
    """


class Switched(typing.TypedDict):
    """What narrowing the active set moved.

    Three lists rather than a before and an after, because the operator's question
    is not \"what is running now\" — they can ask that — but \"what did that do\". The
    middle list is the one that makes the verb worth having: it is the promise that
    a download in flight was not interrupted to change the shape of the stack
    around it.
    """

    kept: list[str]
    """Left running: the new closure holds them too, so nothing here asked them to
    stop. Not a promise that nothing touched them — Compose recreates a container
    whose configuration changed — but a promise that narrowing did not.
    """
    started: list[str]
    """Started, because the new closure holds them and they were not up."""
    stop_command: typing.NotRequired[list[str] | None]
    """The exact Compose invocation that stopped what fell outside, so a switch is
    no more a matter of trust than any other action. Absent where nothing had
    to stop.
    """
    stopped: list[str]
    """Stopped, because the new closure does not hold them."""


__all__ = [
    "LifecycleEnvelope",
    "LifecycleReport",
    "Switched",
]
