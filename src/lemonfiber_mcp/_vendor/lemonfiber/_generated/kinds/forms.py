# Copyright (c) 2026 NightWorksIO
"""The `forms` envelope, and the shapes only `forms` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class FormReport(typing.TypedDict):
    """One form the stack declares, as a listing shows it.

    The manifest's own words rather than lemonfiber's: forms come from the stack, so a
    stack of somebody's own names and describes them however it likes, and a listing that
    paraphrased would be describing a different stack from the one being run.
    """

    composable: bool
    """Whether it can be started alongside another form.

    Worth saying in the listing rather than only when a combination is refused: an
    operator choosing between two forms is exactly who needs to know they are a choice.
    """
    description: str
    """What it is for, in one line."""
    id: str
    """What to type to start it."""
    name: str
    """What it is called."""


class FormsEnvelope(typing.TypedDict):
    """The envelope carrying `forms`."""

    api_version: int
    data: FormsReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["forms"]


class FormsReport(typing.TypedDict):
    """Every form this stack declares."""

    forms: list[FormReport]
    """The forms, in the order the stack declares them."""


__all__ = [
    "FormReport",
    "FormsEnvelope",
    "FormsReport",
]
