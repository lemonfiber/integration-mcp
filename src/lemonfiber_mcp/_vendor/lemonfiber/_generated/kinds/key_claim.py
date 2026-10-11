# Copyright (c) 2026 NightWorksIO
"""The `key-claim` envelope, and the shapes only `key-claim` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.key_claim__keys__minted_key import KeyPurpose


class KeyClaim(typing.TypedDict):
    """A key minted as a claim: the link that collects it, and no secret."""

    lapses: str
    """When the claim stops collecting the key, written as every other instant is."""
    link: str
    """The key link: `lemonfiber://key` with the address, the certificate fingerprint,
    the stack, when the claim lapses and the claim. Shown once, and drawn as a code.
    """
    name: str
    """The name it was minted under."""
    purpose: KeyPurpose
    """What the minter said it is for."""
    scope: str
    """What it admits: `read`, `act` or `member:<name>`."""


class KeyClaimEnvelope(typing.TypedDict):
    """The envelope carrying `key-claim`."""

    api_version: int
    data: KeyClaim
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["key-claim"]


__all__ = [
    "KeyClaim",
    "KeyClaimEnvelope",
]
