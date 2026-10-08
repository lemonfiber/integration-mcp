# Copyright (c) 2026 NightWorksIO
"""What lemonfiber hands over as a file rather than as a document."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BundleFile:
    """A support bundle lemonfiber handed over, kept as the bytes that arrived."""

    name: str
    content: bytes
    content_type: str | None
