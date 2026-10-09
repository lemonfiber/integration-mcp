# Copyright (c) 2026 NightWorksIO
"""The `minted-key` envelope, and the shapes only `minted-key` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.keys__minted_key import KeyPurpose


class MintedKey(typing.TypedDict):
    """A key minted, with everything a client on another machine needs to use it.

    The only document that ever carries the secret. Every surface that renders it does so
    once, and nothing here writes it down.
    """

    address: typing.NotRequired[str | None]
    """Where a client on another machine reaches the stack: the `https` address it was
    last served at on the network. Absent where it has never been served that way.
    """
    caution: typing.NotRequired[str | None]
    """What is worth knowing before handing the key over, where anything is: how to
    serve the stack so another machine can reach it.
    """
    name: str
    """The name it was minted under."""
    pin: typing.NotRequired[str | None]
    """The certificate that address presents: SHA-256 over its DER encoding, in
    lower-case hex. A client off this machine pins it.
    """
    purpose: KeyPurpose
    """What the minter said it is for."""
    scope: str
    """What it admits: `read`, `act` or `member:<name>`."""
    secret: Secret
    """The secret, sent in `X-Lemonfiber-Token`. It is not shown again."""


class MintedKeyEnvelope(typing.TypedDict):
    """The envelope carrying `minted-key`."""

    api_version: int
    data: MintedKey
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["minted-key"]


type Secret = str
"""A key's secret, as it is handed over once.

It has no `Debug` that prints it and no way back from its digest, and nothing here
writes it anywhere: the one reply that carries it is the only place it appears.
"""


__all__ = [
    "MintedKey",
    "MintedKeyEnvelope",
    "Secret",
]
