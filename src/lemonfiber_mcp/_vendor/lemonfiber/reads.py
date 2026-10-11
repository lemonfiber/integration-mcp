# Copyright (c) 2026 NightWorksIO
"""Every path this client reaches, held here rather than spelled by a caller.

`Read`, `LOGS`, `BUNDLE` and the picture paths are generated from the reads the contract lists, so
a read the core serves is one this client names. The paths below are those the
contract lists no read for: the live stream, the stack's capabilities, the doors
actions and jobs are asked through, the door a session is opened at, and the
doors integration keys are kept and collected through.
"""

from typing import Final

from lemonfiber._generated import API, ASKABLE_ID_POSTER, BUNDLE, HELD_ID_BACKDROP, HELD_ID_POSTER, LOGS, Read

__all__ = [
    "ACTIONS",
    "API",
    "ASKABLE_ID_POSTER",
    "BUNDLE",
    "CAPABILITIES",
    "EVENTS",
    "HELD_ID_BACKDROP",
    "HELD_ID_POSTER",
    "JOBS",
    "KEYS",
    "KEY_CLAIMS",
    "LOGS",
    "SESSION",
    "Read",
]

EVENTS: Final = "/api/events"
"""The live stream."""

ACTIONS: Final = "/api/actions"
"""Where every action is asked for, by name."""

JOBS: Final = "/api/jobs"
"""Where work already begun is asked about and released, by name."""

SESSION: Final = "/api/session"
"""Where a password is exchanged, once, for a session."""

CAPABILITIES: Final = "/api/capabilities"
"""What the stack says it can do, for the credential that asked."""

KEYS: Final = "/api/keys"
"""Where integration keys are listed and minted, and each revoked by its name."""

KEY_CLAIMS: Final = "/api/keys/claim"
"""Where a key minted as a claim is collected, with the claim alone."""
