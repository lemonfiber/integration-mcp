# Copyright (c) 2026 NightWorksIO
"""The shapes `held`, `part-way` and `title` all carry.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Pinned(typing.TypedDict):
    """The certificate a guarded door presents, as a client pins it."""

    fingerprint: str
    """SHA-256 over the certificate's DER encoding, lower-case hex."""


__all__ = [
    "Pinned",
]
