# Copyright (c) 2026 NightWorksIO
"""What a phone's key pair is registered as a device key with: its public half, the platform's attestation, the password."""

from dataclasses import dataclass, field

from lemonfiber._protocol.calls import Json, base64url


@dataclass(frozen=True, slots=True)
class AndroidAttestation:
    """An Android key attestation: each certificate's DER, the key's own first."""

    chain: tuple[bytes, ...]

    def fields(self) -> dict[str, Json]:
        """Return the attestation as a registration's body carries it."""
        return {"platform": "android", "chain": [base64url(certificate) for certificate in self.chain]}


@dataclass(frozen=True, slots=True)
class IosAttestation:
    """An App Attest attestation object's CBOR, made with the SHA-256 of the public half's DER as its client data hash."""

    attestation: bytes

    def fields(self) -> dict[str, Json]:
        """Return the attestation as a registration's body carries it."""
        return {"platform": "ios", "object": base64url(self.attestation)}


@dataclass(frozen=True, slots=True)
class Registering:
    """What one device key is registered with.

    The password is the operator's, given again for this one request. It is sent
    in the body, kept by nothing here, and left out of the representation.
    """

    name: str
    """What to call it: lower-case letters, digits, dots, dashes and underscores."""
    public_key: bytes = field(repr=False)
    """The public half's `SubjectPublicKeyInfo` DER."""
    attestation: AndroidAttestation | IosAttestation = field(repr=False)
    password: str = field(repr=False)
