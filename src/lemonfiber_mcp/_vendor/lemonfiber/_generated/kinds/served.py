# Copyright (c) 2026 NightWorksIO
"""The `served` envelope, and the shapes only `served` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.instant import Instant


class Described(typing.TypedDict):
    """What a certificate says about itself."""

    fingerprint: str
    """What a phone pins: SHA-256 over the certificate's DER encoding, lower-case hex."""
    issuer: str
    """Who signed it, as an RFC 4514 string, cut where it is too long to show."""
    issuer_cut: bool
    """Whether the issuer was cut, being too long to show whole."""
    names: list[str]
    """The names it is made out to, its subject alternative names, each whole; those too
    many or too long to show, or not written as text, are left out.
    """
    names_more: int
    """How many of the names it is made out to are left out, being too many or too long to
    show, or not written as text.
    """
    self_signed: bool
    """Whether it was signed by its own key under its own name."""
    subject: str
    """Who it is made out to, as an RFC 4514 string, cut where it is too long to show."""
    subject_cut: bool
    """Whether the subject was cut, being too long to show whole."""
    valid_from: Instant
    """When it begins to hold."""
    valid_until: Instant
    """When it stops holding."""


class ServedEnvelope(typing.TypedDict):
    """The envelope carrying `served`."""

    api_version: int
    data: ServedReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["served"]


class ServedReport(typing.TypedDict):
    """What a run serving the surface presents, answers to and wrote down."""

    certificate: typing.NotRequired[Described | None]
    """The certificate it presents, as it describes itself, where the run is encrypted."""
    encrypted: bool
    """Whether it presents a certificate, rather than plain text."""
    named: typing.NotRequired[str | None]
    """The name a request has to carry beyond this machine, where the run is encrypted on
    a network.
    """
    network: bool
    """Whether it is offered to the network, rather than to this machine alone."""
    port: int
    """The port it listens on."""
    unrecorded: typing.NotRequired[str | None]
    """Why where it is served could not be written down, where it could not."""


__all__ = [
    "Described",
    "ServedEnvelope",
    "ServedReport",
]
