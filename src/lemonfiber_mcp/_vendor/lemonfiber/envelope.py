# Copyright (c) 2026 NightWorksIO
"""The envelope every answer arrives in, read and refused where it cannot be spoken."""

import json
from typing import TYPE_CHECKING, Final, TypeIs, cast

from lemonfiber._generated import CONTRACT_API_VERSION, KINDS, Envelope, Kind, KindNarrowing
from lemonfiber.problems import (
    ApiVersionMismatchError,
    UnexpectedKindError,
    UnknownKindError,
    UnreadableResponseError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

SPOKEN_API_VERSION: Final = CONTRACT_API_VERSION
"""The wire version this package speaks, as the contract it was generated from states it."""


def read_envelope(document: object) -> Envelope:
    """Read a decoded document as an envelope, typed by its kind.

    The version is checked before anything else is read: an answer in a version
    this package does not speak is refused whole, naming both versions.
    """
    if not is_document(document):
        msg = "it is not an envelope"
        raise UnreadableResponseError(msg)
    version = document.get("api_version")
    if not isinstance(version, int) or isinstance(version, bool):
        msg = "it carries no api_version"
        raise UnreadableResponseError(msg)
    if version != SPOKEN_API_VERSION:
        raise ApiVersionMismatchError(SPOKEN_API_VERSION, version)
    kind = document.get("kind")
    if not isinstance(kind, str) or not kind:
        msg = "it names no kind"
        raise UnreadableResponseError(msg)
    if "data" not in document:
        msg = "it carries no data"
        raise UnreadableResponseError(msg)
    if not is_known(document):
        raise UnknownKindError(kind)
    return document


def is_document(value: object) -> TypeIs[Mapping[str, object]]:
    """Tell whether a decoded value is a JSON object."""
    return isinstance(value, dict)


def is_known(fields: Mapping[str, object]) -> TypeIs[Envelope]:
    """Tell whether an envelope's kind is one this package was generated with."""
    return fields.get("kind") in KINDS


NOT_JSON: Final = object()
"""What a body that is not JSON is read as, so the parser's error is let go before the refusal is raised."""


def parse_envelope(body: bytes | str) -> Envelope:
    """Parse an answer's body and read it as an envelope.

    A body that is not JSON is refused once the parser's error is let go: that
    error holds the whole body, which may carry a session's credential.
    """
    try:
        document: object = json.loads(body)
    except ValueError, RecursionError:
        document = NOT_JSON
    if document is NOT_JSON:
        msg = "it is not JSON"
        raise UnreadableResponseError(msg)
    return read_envelope(document)


def _expect(envelope: Envelope, kind: Kind, /) -> Envelope:
    if envelope["kind"] != kind:
        raise UnexpectedKindError(kind, envelope["kind"])
    return envelope


expect: Final = cast("KindNarrowing", _expect)
"""Narrow an envelope to the kind it is expected to be, refusing any other.

    status = expect(envelope, "status")  # a StatusEnvelope, or UnexpectedKindError
"""
