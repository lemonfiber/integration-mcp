# Copyright (c) 2026 NightWorksIO
"""The `trace` envelope, and the shapes only `trace` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.stuck__trace import Stage


class Coverage(typing.TypedDict):
    """How much of a traced series is here, season by season — the aggregate that turns a
    single furthest stage into an answer about the whole. The counts are of parts someone
    asked for; what nobody asked for is reported beside them, never folded in.
    """

    have: int
    """How many wanted parts are here, across every season."""
    seasons: list[SeasonCoverage]
    """Each season, in order."""
    unmonitored: int
    """How many parts nobody asked for, across every season."""
    wanted: int
    """How many parts were asked for, across every season."""


class Part(typing.TypedDict):
    """One part of a traced item — an episode of a series. A film has no parts: the item is
    the whole, and a trace of it says all there is to say. A series does not, which is the
    gap this closes: \"the show is imported\" is true the moment one episode lands, and reads
    as done while nine are still missing.
    """

    number: int
    """Its number within that season."""
    season: int
    """Which season it belongs to."""
    stage: Stage
    """How far this one part got, on the same scale as the item as a whole."""
    title: str
    """Its title, as a person would name it."""


class SeasonCoverage(typing.TypedDict):
    """How much of one season is actually here, and what is outstanding — the season-level
    answer, which for a series is the one an operator can act on.
    """

    have: int
    """How many of the wanted parts are here."""
    outstanding: list[Part]
    """The wanted parts that are not here yet, each carrying the stage it rests at, so
    one that stalled is told apart from one still downloading.
    """
    season: int
    """The season number. Season zero is where a service files specials."""
    unmonitored: int
    """How many parts nobody asked for — unmonitored and not on disk."""
    wanted: int
    """How many parts were asked for, or are already here — the denominator. Parts
    nobody asked for are counted separately rather than inflating this, so a season
    with every wanted episode present reads as complete even where specials are not.
    """


type TraceConfidence = typing.Literal["certain", "uncertain"]
"""How sure the correlation behind a trace is — a release renamed between services can
only be matched fuzzily, and a guess presented as fact is worse than a marked one.
"""


class TraceEnvelope(typing.TypedDict):
    """The envelope carrying `trace`."""

    api_version: int
    data: TraceReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["trace"]


class TraceMoment(typing.TypedDict):
    """One moment in a traced item's history: what happened and when. Where [`TraceStage`]
    is the linear progress, this is the log an \\*arr kept — the grabs, the failed
    downloads, the import and any later removal — so a repeated attempt is seen as the
    pattern it is rather than flattened to a single furthest stage.
    """

    at: str
    """When the service reported it."""
    outcome: TraceOutcome
    """What happened."""


type TraceOutcome = typing.Literal["grabbed", "download-failed", "imported", "removed"]
"""A notable thing that happened to an item, as an \\*arr's history records it. Where the
furthest stage answers \"how far did it get?\", the sequence of outcomes answers \"what
has been tried?\" — a release grabbed more than once, a download that failed and was
tried again, a file imported and later removed. Repeated failed grabs are a pattern
worth seeing, not something a single furthest-stage reading can show.
"""


class TraceReport(typing.TypedDict):
    """Where one item is in the pipeline: how far it got, why it stopped if it did, and the
    stages it passed through — the answer to \"where is my show?\".
    """

    confidence: TraceConfidence
    """How sure the trace is of the item it followed."""
    coverage: typing.NotRequired[Coverage | None]
    """How much of the item is actually here, season by season — present for an item
    made of parts, absent for a film, which is the whole item and has none.

    The furthest stage alone cannot answer this: a series is \"imported\" the moment one
    episode lands, which reads as done while the rest are missing.
    """
    findings: list[str]
    """Disagreements between the services about this item, each in plain language — a
    media server holding what no service is monitoring, and the like. Orthogonal to
    the linear pipeline: not where the item got to, but where two services' views of
    it contradict, surfaced rather than silently reconciled.
    """
    furthest: Stage
    """The furthest stage the item reached."""
    history: list[TraceMoment]
    """The notable events in its history, oldest first — the grabs, failed downloads,
    imports and removals. Repeated attempts show here as the pattern they are, which
    the single furthest stage cannot.
    """
    item: str
    """The term the item was searched for by."""
    matched: bool
    """Whether a monitored item matched the term at all — a false here is itself the
    answer: nobody asked for it.
    """
    stages: list[TraceStage]
    """The stages it passed through, in order."""
    stall: typing.NotRequired[str | None]
    """Why it stopped, where it plainly has — or absent where it is progressing or done."""


class TraceStage(typing.TypedDict):
    """One stage a traced item reached, named as the operator would read it: the stage,
    the service that recorded it, and when.
    """

    at: typing.NotRequired[str | None]
    """When it happened, as the service reported it — absent for a stage inferred
    rather than timed, such as being monitored.
    """
    service: str
    """The service that recorded it."""
    stage: Stage
    """The stage reached."""


__all__ = [
    "Coverage",
    "Part",
    "SeasonCoverage",
    "TraceConfidence",
    "TraceEnvelope",
    "TraceMoment",
    "TraceOutcome",
    "TraceReport",
    "TraceStage",
]
