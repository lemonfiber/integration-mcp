# Copyright (c) 2026 NightWorksIO
"""What lemonfiber hands over as a file rather than as a document."""

from dataclasses import dataclass
from typing import Final

PICTURE_TYPES: Final = ("image/jpeg", "image/png", "image/webp", "image/gif", "image/avif")
"""The types a picture arrives as: raster images, which carry nothing a browser runs."""

PICTURE_MOST: Final = 2 * 1024 * 1024
"""The most bytes a picture is."""


@dataclass(frozen=True, slots=True)
class BundleFile:
    """A support bundle lemonfiber handed over, kept as the bytes that arrived."""

    name: str
    content: bytes
    content_type: str | None


@dataclass(frozen=True, slots=True)
class Picture:
    """One of a title's pictures: a raster image of at most `PICTURE_MOST` bytes, and the type it is."""

    content: bytes
    media_type: str
