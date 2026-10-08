# Copyright (c) 2026 NightWorksIO
"""The `seed` envelope, and the shapes only `seed` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.import___migration__seed__status__stuck import UnsupportedReport


type Assessment = typing.Literal["assessed", "unassessable"]
"""Whether a pass could assess drift — whether it had the record of what lemonfiber
last wrote to compare against.
"""


class SeedEnvelope(typing.TypedDict):
    """The envelope carrying `seed`."""

    api_version: int
    data: SeedReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["seed"]


class SeedReport(typing.TypedDict):
    """What a seed pass amounted to."""

    assessment: Assessment
    """Whether drift could be assessed, or the expected-state record was lost."""
    rehearsed: bool
    """Whether this pass only said what it would do.

    A flag rather than a second shape, because every connection above means the
    same thing either way: what the service holds is what it holds, and what
    lemonfiber would write is what it would write. What changes is that two of the
    states are reachable only here, and that the last line of the report is an
    instruction to run it for real rather than to run it again.
    """
    unsupported: typing.NotRequired[list[UnsupportedReport]]
    """Services this pass could not wire because it cannot speak to them, each with
    why.

    Not wirings, because nothing was attempted and a wiring says how an attempt
    turned out. Not absences either, which is the point: a pass that skipped a
    service declaring an API shape this build does not speak and said nothing would
    leave the operator who wrote that declaration no way to tell it from a service
    lemonfiber had simply forgotten.
    """
    wirings: list[Wiring]
    """Every connection attempted, and how each turned out."""


type SeedSeverity = SeedSeverityInformational | SeedSeverityWarning
"""How serious a reported connection is.

Drift is normal and usually the operator's own harmless edit, so it is reported
as information rather than a failure. It escalates to a warning only when the
drift breaks the stack — a root folder pointing where nothing exists, a download
client that no longer answers — and a warning that cannot be acted on is noise,
so a warning always names both what broke and what to do about it.
"""


class SeedSeverityInformational(typing.TypedDict):
    """Nothing is broken: the connection is settled, or its drift is the operator's
    own edit that still works.
    """

    severity: typing.Literal["informational"]


class SeedSeverityWarning(typing.TypedDict):
    """The connection breaks the stack. Both the breakage and a remediation are
    named, because a warning the operator cannot act on is noise.
    """

    breakage: str
    """What is broken, in the operator's terms."""
    remediation: str
    """What to do about it."""
    severity: typing.Literal["warning"]


type SeedState = (
    SeedStateWired
    | SeedStateAlreadyWired
    | SeedStateDrifted
    | SeedStateStale
    | SeedStateConflicted
    | SeedStateAdopted
    | SeedStateUnmanaged
    | SeedStateWouldWire
    | SeedStateWouldAdopt
    | SeedStateObserved
    | SeedStateUnmatched
    | SeedStateSkipped
    | SeedStateFailed
    | SeedStateRefused
)
"""How one connection turned out after a seed pass."""


class SeedStateAdopted(typing.TypedDict):
    """An operator's edit adopted as the accepted state, kept across seeds and
    restores. Settled: lemonfiber leaves it as it is.
    """

    state: typing.Literal["adopted"]


class SeedStateAlreadyWired(typing.TypedDict):
    """Present and correct; nothing was done."""

    state: typing.Literal["already-wired"]


class SeedStateConflicted(typing.TypedDict):
    """Both the service's value and lemonfiber's intent moved away from the
    baseline. The conflict is presented — the value the operator set beside the
    one lemonfiber would write — and the value left as it is; lemonfiber does not
    resolve it on its own.

    Both values are shown in the report and serialized with it, so a
    secret-bearing field must not report a conflict through this variant: a
    conflict in a secret is to be reported without either value on show, and
    wants a masked shape of its own rather than this one.
    """

    ours: str
    """The value lemonfiber would write in its place."""
    state: typing.Literal["conflicted"]
    yours: typing.NotRequired[str | None]
    """The value the service now holds, as the operator set it; `None` where
    they cleared it.
    """


class SeedStateDrifted(typing.TypedDict):
    """Present but operator-changed; preserved."""

    state: typing.Literal["drifted"]


class SeedStateFailed(typing.TypedDict):
    """Attempted and rejected, carrying the service's own words."""

    detail: str
    """What the service said."""
    state: typing.Literal["failed"]


class SeedStateObserved(typing.TypedDict):
    """An area the operator declared unmanaged. Nothing was read from the service and
    nothing was written to it, and the reason they gave is carried so a report says
    whose decision it was.

    Apart from [`Self::Unmanaged`], which lemonfiber *infers* from a value it has
    no record of having written, and which it adopts as the baseline so that later
    runs recognise it. This one is a decision somebody wrote down, and it holds
    whether or not lemonfiber would have had anything to say — nothing is adopted,
    because adopting would be the first half of managing it again.
    """

    reason: str
    """Why the operator said to leave it alone, in their own words."""
    state: typing.Literal["observed"]


class SeedStateRefused(typing.TypedDict):
    """Refused by lemonfiber's own policy, carrying the reason a re-run will not
    resolve — such as two \\*arrs pointed at one root folder, or a service that
    does not serve the API version this build speaks. Either way nothing it
    names was written, whether it was refused before the write or the write
    itself found nothing to land in.
    """

    reason: str
    """Why it was refused, in lemonfiber's own words."""
    state: typing.Literal["refused"]


class SeedStateSkipped(typing.TypedDict):
    """Prerequisite unavailable; a later run will complete it."""

    reason: str
    """Why it could not be attempted."""
    state: typing.Literal["skipped"]


class SeedStateStale(typing.TypedDict):
    """Present and still lemonfiber's own value, but behind lemonfiber's intent —
    it should be brought up to date. Reported until an update path applies it,
    and never overwritten in the meantime.
    """

    state: typing.Literal["stale"]


class SeedStateUnmanaged(typing.TypedDict):
    """A value the service already held that lemonfiber never wrote — the operator's
    own, pre-existing. Adopted as the baseline this run rather than reported as
    drift, so an existing setup is taken on instead of flagged wholesale. Its
    value is not shown, so a secret among the adopted is never put on display.
    """

    state: typing.Literal["unmanaged"]


class SeedStateUnmatched(typing.TypedDict):
    """Something on this machine fills what a service asks for, and nothing lemonfiber
    does connects the two — the filler names no adapter, or none lemonfiber pairs with
    what the asker speaks.

    Settled, because no run changes it: the stack, or what is installed, has to. Said
    rather than left out, because a filler nothing reaches and a filler lemonfiber
    forgot would otherwise read the same, and the operator who installed one to stand
    in for another is the one who needs to know which.
    """

    reason: str
    """What fills it, what asked, and why nothing connects them."""
    state: typing.Literal["unmatched"]


class SeedStateWired(typing.TypedDict):
    """Written and read back."""

    state: typing.Literal["wired"]


class SeedStateWouldAdopt(typing.TypedDict):
    """An operator's own value a real run would take on as the accepted state, and
    this one did not.

    Apart from [`Self::WouldWire`] because it is the other direction: nothing would
    be written to the service at all, and what would move is lemonfiber's record of
    what it expects. Its value is not shown, exactly as [`Self::Unmanaged`] does not
    show one, so a secret among the adopted is never put on display by a question.
    """

    state: typing.Literal["would-adopt"]


class SeedStateWouldWire(typing.TypedDict):
    """Not there, or not at what lemonfiber would have it be, and this run only said
    so.

    The one outcome a pass that writes nothing can reach where a pass that writes
    would have written. What a real run would leave the service holding sits beside
    what it holds now, because a report saying a connection would be made without
    saying what it would be made *to* is a count rather than an account — and a
    count is what an operator asking for a rehearsal already has.

    Both values are serialized, so a secret-bearing field must not report through
    this variant carrying one. It does not have to: `ours` is absent exactly where
    a real run would generate the value rather than read it, which is the only
    place a credential arises — the torrent client's web UI password and the media
    server's admin account. A value minted to describe a rehearsal is a secret that
    exists because somebody asked a question, and it would then have to be kept or
    thrown away.

    `yours` is absent where the service holds nothing, and where this run could not
    ask without writing — reading the household's telling means signing in as the
    owner, and a session is state on somebody else's service.
    """

    ours: typing.NotRequired[str | None]
    """What a real run would leave it holding, or `None` where that value would be
    generated rather than read.
    """
    state: typing.Literal["would-wire"]
    yours: typing.NotRequired[str | None]
    """What the service holds now, or `None` where it holds nothing or could not
    be asked.
    """


class Wiring(typing.TypedDict):
    """One connection, and how it turned out."""

    connection: str
    """What was being connected, such as `SABnzbd into Sonarr`."""
    severity: SeedSeverity
    """How serious the outcome is — information by default, a warning where the
    connection breaks the stack.
    """
    state: SeedState
    """How it turned out."""


__all__ = [
    "Assessment",
    "SeedEnvelope",
    "SeedReport",
    "SeedSeverity",
    "SeedSeverityInformational",
    "SeedSeverityWarning",
    "SeedState",
    "SeedStateAdopted",
    "SeedStateAlreadyWired",
    "SeedStateConflicted",
    "SeedStateDrifted",
    "SeedStateFailed",
    "SeedStateObserved",
    "SeedStateRefused",
    "SeedStateSkipped",
    "SeedStateStale",
    "SeedStateUnmanaged",
    "SeedStateUnmatched",
    "SeedStateWired",
    "SeedStateWouldAdopt",
    "SeedStateWouldWire",
    "Wiring",
]
