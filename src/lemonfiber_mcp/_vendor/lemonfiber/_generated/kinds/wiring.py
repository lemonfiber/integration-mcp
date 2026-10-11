# Copyright (c) 2026 NightWorksIO
"""The `wiring` envelope, and the shapes only `wiring` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.plugins__wiring import Wired
from ..shared.substitution__wiring import Unfilled


class WiringEnvelope(typing.TypedDict):
    """The envelope carrying `wiring`."""

    api_version: int
    data: WiringReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["wiring"]


class WiringReport(typing.TypedDict):
    """What this stack wires to what."""

    unfilled: list[Unfilled]
    """Every capability something asks for and nothing fills, naming what asked.

    Repeated out of the links above rather than left to be found among them: a
    stack with one unfilled ask among twenty working ones is a stack whose one
    problem is a line in a list, and a consumer that had to notice it would be
    the reason nobody did.
    """
    wired: list[Wired]
    """Every link, in the order the stack declares them."""


__all__ = [
    "WiringEnvelope",
    "WiringReport",
]
