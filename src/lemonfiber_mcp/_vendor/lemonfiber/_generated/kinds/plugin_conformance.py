# Copyright (c) 2026 NightWorksIO
"""The `plugin-conformance` envelope, and the shapes only `plugin-conformance` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.violation import Violation


class Conformed(typing.TypedDict):
    """What a plugin's recordings say about the contracts its adapters speak."""

    cases: list[Judged]
    """Every case of every contract an adapter speaks, as its recording answered it."""
    conforms: bool
    """Whether nothing is refused and every case passed."""
    id: str
    """The plugin's id."""
    refusals: list[Violation]
    """Everything the manifest is refused for, which no recording can make up for."""


class Judged(typing.TypedDict):
    """One case, as its recording answered it."""

    case: str
    """The case."""
    contract: str
    """The contract it is a case of, as `capability@major`."""
    recording: str
    """Where its recording is, beneath the plugin's source."""
    verdict: Verdict
    """What it came to."""


class PluginConformanceEnvelope(typing.TypedDict):
    """The envelope carrying `plugin-conformance`."""

    api_version: int
    data: Conformed
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["plugin-conformance"]


type Verdict = VerdictPassed | VerdictFailed | VerdictUnrecorded | VerdictUnproven
"""What one case's recording came to."""


class VerdictFailed(typing.TypedDict):
    """It is not, in every way it is not."""

    faults: list[str]
    """Every way the recorded answer is outside the case."""
    outcome: typing.Literal["failed"]


class VerdictPassed(typing.TypedDict):
    """The recorded answer is one the contract declares for the case."""

    outcome: typing.Literal["passed"]


class VerdictUnproven(typing.TypedDict):
    """A recording is there and could not be judged, so it established nothing."""

    outcome: typing.Literal["unproven"]
    why: str
    """What stopped it being judged."""


class VerdictUnrecorded(typing.TypedDict):
    """No recording of the case is there."""

    outcome: typing.Literal["unrecorded"]


__all__ = [
    "Conformed",
    "Judged",
    "PluginConformanceEnvelope",
    "Verdict",
    "VerdictFailed",
    "VerdictPassed",
    "VerdictUnproven",
    "VerdictUnrecorded",
]
