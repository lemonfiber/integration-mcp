# Copyright (c) 2026 NightWorksIO
"""The `hosting` envelope, and the shapes only `hosting` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Changed(typing.TypedDict):
    """What one run of this command did to the machine."""

    installed: bool
    """Whether it installed it, rather than took it back."""
    name: str
    """The command it acted on."""
    rehearsed: bool
    """Whether this was a rehearsal, in which case nothing above happened."""
    started: bool
    """Whether it started the command, which only installing does."""
    touched: list[str]
    """Everything it wrote or removed, so nothing goes unnamed in either direction."""


class HostedCommand(typing.TypedDict):
    """One long-running command, and what stands between it and this machine."""

    command: str
    """How it is typed in a terminal, which is what hosting installs."""
    definition: typing.NotRequired[str | None]
    """The service definition installed for it, where there is one."""
    guarantees: str
    """What it does for as long as it runs, in one sentence."""
    missing: typing.NotRequired[str | None]
    """The program the definition names, where nothing is there any more."""
    name: str
    """lemonfiber's own name for it."""
    output: typing.NotRequired[str | None]
    """Where a hosted run writes the words it would have said on a terminal."""
    runs: typing.NotRequired[str | None]
    """The whole command line that definition runs."""
    standing: Hosting
    """What stands between it and the machine."""


type Hosting = typing.Literal[
    "not-hosted", "hosted", "installed-unverified", "stopped", "orphaned", "unsupported"
]
"""What stands between one long-running command and the machine.

Written with hyphens because these are the words the operator reads and the
requirement names, and a reading that spelled them differently would be a
second vocabulary for one set of facts.
"""


class HostingEnvelope(typing.TypedDict):
    """The envelope carrying `hosting`."""

    api_version: int
    data: HostingReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["hosting"]


class HostingReport(typing.TypedDict):
    """What this machine keeps running on lemonfiber's behalf.

    Defaultable so a test can read one out of a `Result` without a branch it can
    never take: a closure standing in for the impossible arm is a region no
    passing run enters, and the coverage gate counts those.
    """

    caveat: typing.NotRequired[str | None]
    """What is true of this manager and worth knowing before it is relied on."""
    changed: typing.NotRequired[Changed | None]
    """What this run changed, where it was asked to change something."""
    commands: list[HostedCommand]
    """Every long-running command there is, hosted or not."""
    instruction: typing.NotRequired[str | None]
    """What to do instead, where lemonfiber cannot configure this platform."""
    manager: Manager
    """The service manager this platform has, or the absence of one."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


type Manager = typing.Literal["launchd", "systemd", "unsupported"]
"""The service manager a machine has, or the absence of one lemonfiber configures.

The absence is the default, because a machine nobody has told is a machine
nothing is known about, and guessing at a manager is how a report comes to
claim a platform it never asked.
"""


__all__ = [
    "Changed",
    "HostedCommand",
    "Hosting",
    "HostingEnvelope",
    "HostingReport",
    "Manager",
]
