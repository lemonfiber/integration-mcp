# Copyright (c) 2026 NightWorksIO
"""What the server is told at start: where the stack is, the pin it is held to, and the key it asks with.

Read from the environment, never from the command line, which any process
listing shows. A key is taken only as an integration key, shaped as the core
mints one; nothing here takes a password.
"""

import pathlib
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from lemonfiber import Address, AddressRefusedError, CertificatePin, Credential

if TYPE_CHECKING:
    from collections.abc import Mapping

ADDRESS: Final = "LEMONFIBER_ADDRESS"
PIN: Final = "LEMONFIBER_PIN"
KEY: Final = "LEMONFIBER_KEY"
KEY_FILE: Final = "LEMONFIBER_KEY_FILE"
KEY_SHAPE: Final = re.compile(r"lfk_[0-9a-f]+")
"""An integration key as the core mints one: its prefix and lower-case hexadecimal."""


class SettingsError(Exception):
    """The server cannot start with what it was given; the message names the setting and never its value."""


@dataclass(frozen=True, slots=True)
class Stack:
    """Where the stack is, and the pin it is held to where it is not on this machine."""

    address: Address
    pin: CertificatePin | None


def stack_from(environment: Mapping[str, str]) -> Stack:
    """Read the stack's address and pin, refusing an address off this machine given without a pin."""
    url = environment.get(ADDRESS, "").strip()
    if not url:
        msg = f"{ADDRESS} is not set: give the address lemonfiber printed when the key was minted."
        raise SettingsError(msg)
    written = environment.get(PIN, "").strip() or None
    try:
        pin = None if written is None else CertificatePin(written)
        address = Address(url, pin=pin)
    except AddressRefusedError as refused:
        msg = f"{ADDRESS} or {PIN} was refused: {refused}"
        raise SettingsError(msg) from None
    return Stack(address, pin)


def key_from(written: str, where: str) -> Credential:
    """Return a key as the credential it travels as, refusing anything not shaped as an integration key."""
    secret = written.strip()
    if not KEY_SHAPE.fullmatch(secret):
        msg = (
            f"{where} does not hold an integration key. Mint one for this server, with the purpose "
            "`mcp`, and give it here; nothing else is accepted, the operator's password least of all."
        )
        raise SettingsError(msg)
    return Credential(secret)


def key_of(environment: Mapping[str, str]) -> tuple[Credential, str]:
    """Return the key the server asks with, and its text for withholding, from the setting or the file it names."""
    given = environment.get(KEY, "")
    named = environment.get(KEY_FILE, "").strip()
    if given and named:
        msg = f"{KEY} and {KEY_FILE} are both set; give the key one way."
        raise SettingsError(msg)
    if named:
        try:
            given = pathlib.Path(named).read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            msg = f"{KEY_FILE} names a file that could not be read."
            raise SettingsError(msg) from None
        return key_from(given, KEY_FILE), given.strip()
    if not given:
        msg = f"Neither {KEY} nor {KEY_FILE} is set: give the integration key minted for this server."
        raise SettingsError(msg)
    return key_from(given, KEY), given.strip()
