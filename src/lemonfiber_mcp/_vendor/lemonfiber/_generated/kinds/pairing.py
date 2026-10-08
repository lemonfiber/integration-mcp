# Copyright (c) 2026 NightWorksIO
"""The `pairing` envelope, and the shapes only `pairing` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class Pairing(typing.TypedDict):
    """Pairing material, and what the operator is told beside it."""

    caution: typing.NotRequired[str | None]
    """What is worth knowing about the address itself, where anything is."""
    compare: str
    """The fingerprint in the short form a person compares with what the phone shows
    after typing the line in, as [`comparable`] derives it.
    """
    material: PairingMaterial
    """The material itself."""
    replacing: str
    """What would make every paired phone refuse this machine, said now rather than
    discovered then. In words any surface can show: how the certificate is replaced
    is each surface's own to say, so this names no command.
    """
    until: str
    """When it stops being good, as a date and a time of day."""
    written: str
    """The material as the one line a code carries and a person types."""


class PairingEnvelope(typing.TypedDict):
    """The envelope carrying `pairing`."""

    api_version: int
    data: Pairing
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["pairing"]


class PairingMaterial(typing.TypedDict):
    """What a phone is handed, exactly as it reads it.

    Four fields and no more: a reader refuses one it does not know, which is what keeps a
    credential from ever riding along under a name nobody thought to forbid.
    """

    address: str
    """Where the phone reaches the stack: an `https` address on the household network."""
    expires: int
    """When the material stops being good, in seconds since the Unix epoch."""
    fingerprint: str
    """The certificate that address presents: SHA-256 over its DER encoding, in
    lower-case hex. Not the digest of its public key.
    """
    stack: str
    """The stack's own identifier: opaque, minted once from nothing and kept, and the
    same across every issue of the material, a change of address and a replacement of
    the certificate. Not the stack's name and not its version, and it carries nothing
    about the household or anybody in it.
    """


__all__ = [
    "Pairing",
    "PairingEnvelope",
    "PairingMaterial",
]
