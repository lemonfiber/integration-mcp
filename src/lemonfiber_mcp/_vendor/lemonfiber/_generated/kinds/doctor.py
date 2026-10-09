# Copyright (c) 2026 NightWorksIO
"""The `doctor` envelope, and the shapes only `doctor` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.doctor__plugins import Finding


class DoctorEnvelope(typing.TypedDict):
    """The envelope carrying `doctor`."""

    api_version: int
    data: DoctorReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["doctor"]


class DoctorReport(typing.TypedDict):
    """What a diagnostic run found, and what it amounts to."""

    findings: list[Finding]
    """Each finding, in the order the checks produced them."""
    overall: Overall
    """What the findings amount to, as one word."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """


type Overall = typing.Literal["healthy", "degraded", "broken", "unknown"]
"""What a run's findings amount to."""


__all__ = [
    "DoctorEnvelope",
    "DoctorReport",
    "Overall",
]
