# Copyright (c) 2026 NightWorksIO
"""The shapes `config` and `wizard` both carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from .config__credentials__doctor__outbound__plugins__wiring__wizard import ValueOrigin


class SettingReport(typing.TypedDict):
    """One setting, as it is safe to show."""

    key: str
    """The setting's name."""
    origin: ValueOrigin
    """Where the value came from, beside the value rather than behind a second
    request — reading a setting and reading what put it there are one act.
    """
    secret: bool
    """Whether the value was withheld."""
    value: str
    """Its value, or a note that it is set and withheld."""


type Validation = ValidationValid | ValidationRejected | ValidationUnreachable | ValidationDegraded
"""What proving a credential against its live service established — never the
input, only the outcome.

Read back as well as built. A surface that is not in this process asks setup to
prove a credential and is told what came of it, so the four outcomes are tagged
by name rather than distinguished by which field is present — the same reason an
answer carries the step it belongs to.
"""


class ValidationDegraded(typing.TypedDict):
    """It authenticated, but cannot do the job it is for — exhausted, limited, or
    otherwise unable.
    """

    detail: str
    """What it can no longer do, and why where the service says."""
    outcome: typing.Literal["degraded"]


class ValidationRejected(typing.TypedDict):
    """The service answered and refused: the credential is wrong for it."""

    detail: str
    """What the service said, in terms the operator can act on."""
    outcome: typing.Literal["rejected"]


class ValidationUnreachable(typing.TypedDict):
    """Nothing usable answered, so nothing can be concluded about the credential."""

    detail: str
    """Why nothing usable came back."""
    outcome: typing.Literal["unreachable"]


class ValidationValid(typing.TypedDict):
    """Proven working, carrying the capability observed while proving it."""

    observed: str
    """The observed fact — what the service did, not that it merely answered."""
    outcome: typing.Literal["valid"]


__all__ = [
    "SettingReport",
    "Validation",
    "ValidationDegraded",
    "ValidationRejected",
    "ValidationUnreachable",
    "ValidationValid",
]
