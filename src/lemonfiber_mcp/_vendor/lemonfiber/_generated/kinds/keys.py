# Copyright (c) 2026 NightWorksIO
"""The `keys` envelope, and the shapes only `keys` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing

from ..shared.keys__minted_key import KeyPurpose


class KeyListing(typing.TypedDict):
    """Every key this machine has minted, and what became of a revoke."""

    keys: list[ListedKey]
    """In the order they were minted."""
    purposes: str
    """What a purpose in the listing is worth, said with it."""
    rehearsed: bool
    """Whether this was a rehearsal: what revoking would come to, with nothing revoked."""
    revoked: typing.NotRequired[str | None]
    """The key this run revoked, where it revoked one."""


type KeyState = typing.Literal["active", "revoked", "orphaned", "unconfirmed"]
"""Where a key stands."""


class KeysEnvelope(typing.TypedDict):
    """The envelope carrying `keys`."""

    api_version: int
    data: KeyListing
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["keys"]


class ListedKey(typing.TypedDict):
    """One key as the listing shows it, without its secret."""

    member_minted: bool
    """Whether a household member minted it for themselves."""
    minted: str
    """When it was minted."""
    name: str
    """The name it was minted under."""
    purpose: KeyPurpose
    """What the minter said it is for. A declaration, not something the core verified."""
    revoked: typing.NotRequired[str | None]
    """When it was revoked, where it has been."""
    scope: str
    """What it admits: `read`, `act` or `member:<name>`."""
    state: KeyState
    """Where it stands."""
    used: typing.NotRequired[str | None]
    """When it was last admitted, where it has been."""


__all__ = [
    "KeyListing",
    "KeyState",
    "KeysEnvelope",
    "ListedKey",
]
