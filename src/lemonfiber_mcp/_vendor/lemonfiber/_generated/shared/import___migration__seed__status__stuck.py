# Copyright (c) 2026 NightWorksIO
"""The shapes `import`, `migration`, `seed`, `status` and `stuck` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class UnsupportedReport(typing.TypedDict):
    """Something lemonfiber cannot act on, named rather than passed over.

    Written for a migration survey and read by two reports now. The second is the
    status of a stack the operator maintains themselves, where a service declaring an
    API this build cannot reach is named the same way — what, and why — rather than
    being dropped from every feature that would have used it. One shape for both,
    because \"named rather than passed over\" is the whole of what either is saying and
    two shapes would be two ways of saying it.
    """

    because: str
    """Why lemonfiber cannot act on it, in the operator's terms."""
    what: str
    """What was found, by the name the thing that found it gives it — a project and
    service for a survey, a service id for a stack lemonfiber runs.
    """


__all__ = [
    "UnsupportedReport",
]
