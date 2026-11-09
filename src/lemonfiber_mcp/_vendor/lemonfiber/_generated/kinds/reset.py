# Copyright (c) 2026 NightWorksIO
"""The `reset` envelope, and the shapes only `reset` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.lifecycle__plugins__reset__settings__substitution__update import StackMoveTaken
from ..shared.lifecycle__quality__reset__update import StackEdit


class ResetEnvelope(typing.TypedDict):
    """The envelope carrying `reset`."""

    api_version: int
    data: ResetReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["reset"]


class ResetReport(typing.TypedDict):
    """What a full reset did, or — until it is confirmed — would do: the operator edits it
    reverts back to lemonfiber's own state, and whether it was carried out or only shown.
    """

    confirmed: bool
    """Whether the reset was carried out, or only previewed pending confirmation."""
    guards: typing.NotRequired[list[StackMoveTaken]]
    """Each of lemonfiber's own guards this act moved onto its plugin after its own
    change, or on a reading would move, for good and with no yes of its own; one it
    could not move stays on offer and says why.
    """
    offer: str
    """The name of this reading, which the reset takes as its yes."""
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    reverted: list[StackEdit]
    """The operator's edits that were reverted — or, unconfirmed, that a reset would
    revert — each with the diff of what is lost against what lemonfiber restores.
    """
    reverted_connections: list[str]
    """The service connections whose drifted value was reverted to lemonfiber's — or,
    unconfirmed, would be — each named as it reads in a seed report.
    """


__all__ = [
    "ResetEnvelope",
    "ResetReport",
]
