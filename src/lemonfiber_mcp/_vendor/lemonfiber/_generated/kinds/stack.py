# Copyright (c) 2026 NightWorksIO
"""The `stack` envelope, and the shapes only `stack` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class NonInteractive(typing.TypedDict):
    """How any action is run without a question being put."""

    form: str
    """The words an action is run with, as the command line takes them."""


class StackEnvelope(typing.TypedDict):
    """The envelope carrying `stack`."""

    api_version: int
    data: StackReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["stack"]


class StackException(typing.TypedDict):
    """A part of the stack that the plain Compose words alone do not bring up as lemonfiber
    does, and why.
    """

    because: str
    """Why, in the operator's words."""
    part: str
    """The part, by its id."""


class StackReport(typing.TypedDict):
    """How this stack runs without lemonfiber."""

    env: str
    """The `.env` file beside it."""
    exceptions: list[StackException]
    """Every part the words alone do not bring up as lemonfiber does. Empty where there
    is none.
    """
    non_interactive: NonInteractive
    """How any action is run without a question being put."""
    plain_up: list[str]
    """The `docker compose` words that bring the stack up with no lemonfiber running, as
    lemonfiber's own start would run them.
    """
    project: str
    """The directory the Compose project is written to."""
    source: StackSource
    """Whether this machine runs the stack this build ships or the operator's own."""


type StackSource = typing.Literal["bundled"] | StackSourceVariant2
"""Which stack this machine runs."""


class StackSourceVariant2(typing.TypedDict):
    """The operator's own stack directory, by its path."""

    own: str


__all__ = [
    "NonInteractive",
    "StackEnvelope",
    "StackException",
    "StackReport",
    "StackSource",
    "StackSourceVariant2",
]
