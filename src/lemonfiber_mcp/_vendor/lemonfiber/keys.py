# Copyright (c) 2026 NightWorksIO
"""What an integration key is minted with, and the key link a key minted as a claim is collected with."""

import datetime
import re
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, override

from lemonfiber.address import Address, CertificatePin
from lemonfiber.credential import VISIBLE
from lemonfiber.problems import ConfigurationError, KeyLinkRefusedError

if TYPE_CHECKING:
    from lemonfiber._generated import KeyPurpose

KEY_LINK: Final = "lemonfiber://key"
"""What every key link begins with, before its parameters."""

LINKED: Final = ("address", "fingerprint", "stack", "expires", "claim")
"""The parameters a key link carries, each once, and no others."""

WHOLE_SECONDS: Final = re.compile(r"^\d+$", re.ASCII)
"""How a key link writes when its claim lapses: whole seconds since 1970, in UTC."""


MINT_FORM: Final = "lemonfiber-mint/1"
"""The first line of the text a device key signs to prove a mint."""

LINE_END: Final = "\n"
"""What ends every line of the text a device key signs."""


@dataclass(frozen=True, slots=True)
class DeviceProof:
    """A registered device key's signature over the text `signed_text` spells for a mint and a challenge.

    The challenge and the signature are left out of the representation.
    """

    device: str
    """The device key's name."""
    challenge: str = field(repr=False)
    """The challenge, as the stack handed it over."""
    signature: bytes = field(repr=False)
    """ECDSA P-256 over SHA-256, in DER, as the phone's hardware made it."""


@dataclass(frozen=True, slots=True)
class Minting:
    """What one integration key is minted with, and the operator's proof.

    The proof is the minter's password, given again for this one mint, or a
    device key's signature in its place; exactly one of the two. Neither is kept
    by anything here or shown in the representation.
    """

    name: str
    scope: str
    """What it admits: `read`, `act`, or `member:` and the account it acts as."""
    purpose: KeyPurpose
    password: str | None = field(default=None, repr=False)
    device: DeviceProof | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        """Refuse a mint proved by both the password and a device key, or by neither."""
        if (self.password is None) == (self.device is None):
            msg = "A mint is proved by the password or by a device key's signature, exactly one of the two."
            raise ConfigurationError(msg)


def signed_text(name: str, scope: str, purpose: KeyPurpose, challenge: str, *, claim: bool = False) -> bytes:
    """Return the text a device key signs to prove a mint over `challenge`, as UTF-8.

    The form, the challenge, the name, the scope, the purpose and `claim` or
    `key`, each ended by a line feed. A part holding a line feed is refused: it
    would sign another mint.
    """
    lines = (MINT_FORM, challenge, name, scope, purpose, "claim" if claim else "key")
    if any(LINE_END in line for line in lines):
        msg = "A mint's name, scope, purpose and challenge are each one line of the signed text; one holds a line feed."
        raise ConfigurationError(msg)
    return "".join(line + LINE_END for line in lines).encode()


class KeyLink:
    """A key link, as a key minted as a claim hands one over: where the stack is, its pin, and the claim.

    The address is held to the link's fingerprint, so the key is collected over
    the TLS that fingerprint verifies and over nothing a trust store vouches
    for. The claim is left out of the representation.
    """

    __slots__ = ("_address", "_claim", "_lapses", "_pin", "_stack")

    def __init__(self, link: str) -> None:
        """Read a key link, refusing one that is not exactly what a claim's mint writes."""
        said = parameters(link.strip())
        try:
            self._pin = CertificatePin(said["fingerprint"])
            self._address = Address(said["address"], pin=self._pin)
        except ConfigurationError as unusable:
            raise KeyLinkRefusedError(str(unusable)) from None
        if not VISIBLE.match(said["claim"]) or not said["stack"]:
            msg = "A key link names its stack and carries a claim; this one is missing one of them."
            raise KeyLinkRefusedError(msg)
        self._lapses = lapsing(said["expires"])
        self._stack = said["stack"]
        self._claim = said["claim"]

    @property
    def address(self) -> Address:
        """Return where the key is collected, held to the link's fingerprint."""
        return self._address

    @property
    def pin(self) -> CertificatePin:
        """Return the certificate the stack is held to, as the link's fingerprint names it."""
        return self._pin

    @property
    def stack(self) -> str:
        """Return the identifier of the stack the key is for."""
        return self._stack

    @property
    def lapses(self) -> datetime.datetime:
        """Return when the claim stops collecting the key, in UTC."""
        return self._lapses

    @property
    def claim(self) -> str:
        """Return the claim, which collects the key once."""
        return self._claim

    def lapsed(self) -> bool:
        """Tell whether the claim has lapsed by now."""
        return time.time() >= self._lapses.timestamp()

    @override
    def __repr__(self) -> str:
        return f"KeyLink({self._address.base!r}, stack={self._stack!r}, lapses={self._lapses.isoformat()!r})"


def lapsing(written: str) -> datetime.datetime:
    """Return when a key link says its claim lapses, refusing what is not whole seconds a date can hold."""
    try:
        if WHOLE_SECONDS.match(written):
            return datetime.datetime.fromtimestamp(int(written), tz=datetime.UTC)
    except OverflowError, ValueError, OSError:
        pass
    msg = "A key link says when its claim lapses in whole seconds; this one does not."
    raise KeyLinkRefusedError(msg)


def parameters(link: str) -> dict[str, str]:
    """Return each parameter a key link carries, refusing a link that is not one or carries anything else."""
    begins, _, query = link.partition("?")
    if begins != KEY_LINK:
        msg = f"A key link begins with {KEY_LINK}; this one does not."
        raise KeyLinkRefusedError(msg)
    pairs = urllib.parse.parse_qsl(query, keep_blank_values=True)
    said = dict(pairs)
    if sorted(name for name, _ in pairs) != sorted(LINKED):
        msg = f"A key link carries {', '.join(LINKED)}, each once, and nothing else; this one does not."
        raise KeyLinkRefusedError(msg)
    return said
