# Copyright (c) 2026 NightWorksIO
"""The `import` envelope, and the shapes only `import` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.adoption__beside__config__import___replacement import Stance
from ..shared.import___migration__seed__status__stuck import UnsupportedReport


class ImportEnvelope(typing.TypedDict):
    """The envelope carrying `import`."""

    api_version: int
    data: ImportReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["import"]


class ImportReport(typing.TypedDict):
    """What copying an operator's own records across came to, or would come to."""

    carried: list[RecordReport]
    """What was carried across."""
    not_carried: list[UnsupportedReport]
    """What could not be carried, and why."""
    project: typing.NotRequired[str | None]
    """The project the records were read from."""
    refusal: typing.NotRequired[str | None]
    """Why nothing was carried, where nothing was."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    stance: Stance
    """Where the act stands."""
    would_carry: list[RecordReport]
    """What would be, where nothing has been yet."""


class RecordReport(typing.TypedDict):
    """One record carried across, or that would be."""

    kind: str
    """What kind of record it is, in the plural a person reads."""
    name: str
    """What it is called."""
    service: str
    """The service it belongs to."""


__all__ = [
    "ImportEnvelope",
    "ImportReport",
    "RecordReport",
]
