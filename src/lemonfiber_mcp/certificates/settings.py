# Copyright (c) 2026 NightWorksIO
"""Which of the four ways the certificate comes, for which names, and where its state is kept.

Read from the environment, spelled as the certificates contract spells each
setting. Setting both of the operator's files chooses `files`; where nothing is
chosen `pinned` is served; `acme` and `private-ca` are served only where
`LEMONFIBER_TLS_MODE` names them.
"""

import enum
import ipaddress
import pathlib
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Mapping

MODE: Final = "LEMONFIBER_TLS_MODE"
NAMES: Final = "LEMONFIBER_NAMES"
CERTIFICATE: Final = "LEMONFIBER_TLS_CERTIFICATE"
PRIVATE_KEY: Final = "LEMONFIBER_TLS_PRIVATE_KEY"
KEY_TYPE: Final = "LEMONFIBER_TLS_KEY_TYPE"
STATE: Final = "LEMONFIBER_STATE"
DEFAULT_STATE: Final = pathlib.Path("/var/lib/lemonfiber-mcp")
"""Where the state is kept where `LEMONFIBER_STATE` names nowhere: the image's volume."""
HOST_NAME: Final = re.compile(
    r"(?=.{1,253}$)([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)(\.[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?)*",
)
"""A host name: dot-separated labels of letters, digits and inner hyphens, lower-cased."""


class Mode(enum.StrEnum):
    """The four ways the certificate comes."""

    FILES = "files"
    ACME = "acme"
    PRIVATE_CA = "private-ca"
    PINNED = "pinned"


class KeyType(enum.StrEnum):
    """The kinds of key a certificate may be made with."""

    EC_P256 = "ec-p256"
    EC_P384 = "ec-p384"
    RSA_2048 = "rsa-2048"
    RSA_3072 = "rsa-3072"


WHO_CAN_CHECK: Final[Mapping[Mode, str]] = {
    Mode.FILES: "Whoever trusts the authority that issued the operator's certificate can check it.",
    Mode.ACME: (
        "A public authority's certificate can be checked by every client, assistants reached through "
        "their provider included; one from the operator's own authority, by whoever trusts its root."
    ),
    Mode.PRIVATE_CA: (
        "Only a device that installed this server's root can check it. An assistant on a phone or in a "
        "browser, reached through its provider, cannot connect."
    ),
    Mode.PINNED: (
        "Only a client given its fingerprint can check it. An assistant on a phone or in a browser, "
        "reached through its provider, cannot connect."
    ),
}
"""What the start-up log says of each mode, and the documentation with it."""


class TlsSettingsError(Exception):
    """The certificate cannot be come by as configured; the message names the setting."""


type Name = str | ipaddress.IPv4Address | ipaddress.IPv6Address
"""A name a certificate is for: a host name, or an address."""


@dataclass(frozen=True, slots=True)
class Tls:
    """How the certificate comes, for which names, made with which key, and where its state is kept."""

    mode: Mode
    names: tuple[Name, ...]
    certificate: pathlib.Path | None
    private_key: pathlib.Path | None
    key_type: KeyType
    state: pathlib.Path

    @property
    def first(self) -> str:
        """Return the first name, which the state of the served certificate is kept under."""
        return str(self.names[0])


def name_of(written: str) -> Name:
    """Return one name as given, an address or a host name, refusing anything else."""
    try:
        return ipaddress.ip_address(written)
    except ValueError:
        pass
    host = written.lower().rstrip(".")
    if not HOST_NAME.fullmatch(host):
        msg = f"{NAMES} holds {written!r}, which is neither a host name nor an address."
        raise TlsSettingsError(msg)
    return host


def names_of(written: str) -> tuple[Name, ...]:
    """Return every name a comma-separated setting gives, each once, in the order given."""
    return tuple(dict.fromkeys(name_of(part.strip()) for part in written.split(",") if part.strip()))


def chosen(environment: Mapping[str, str], *, files: bool) -> Mode:
    """Return the mode the settings choose, refusing a mode that is not one."""
    written = environment.get(MODE, "").strip()
    if not written:
        return Mode.FILES if files else Mode.PINNED
    try:
        return Mode(written)
    except ValueError:
        msg = f"{MODE} is {written!r}; it is one of {', '.join(mode.value for mode in Mode)}."
        raise TlsSettingsError(msg) from None


def tls_from(environment: Mapping[str, str]) -> Tls:
    """Read how the certificate comes, refusing a combination the certificates contract does not offer."""
    certificate = environment.get(CERTIFICATE, "").strip()
    private_key = environment.get(PRIVATE_KEY, "").strip()
    if bool(certificate) != bool(private_key):
        msg = f"{CERTIFICATE} and {PRIVATE_KEY} are given together or not at all."
        raise TlsSettingsError(msg)
    files = bool(certificate)
    mode = chosen(environment, files=files)
    if files != (mode is Mode.FILES):
        msg = f"{CERTIFICATE} and {PRIVATE_KEY} are the `files` mode, and {MODE} chose {mode.value}."
        raise TlsSettingsError(msg)
    names = names_of(environment.get(NAMES, ""))
    if not names and mode is not Mode.FILES:
        msg = f"{NAMES} is not set: give the names, and for {mode.value} the addresses, clients reach this server by."
        raise TlsSettingsError(msg)
    if mode is Mode.ACME and any(not isinstance(name, str) for name in names):
        msg = f"{NAMES} holds an address, and an ACME authority issues for host names."
        raise TlsSettingsError(msg)
    key_type = environment.get(KEY_TYPE, KeyType.EC_P256.value).strip()
    if key_type not in set(KeyType):
        msg = f"{KEY_TYPE} is {key_type!r}; it is one of {', '.join(kind.value for kind in KeyType)}."
        raise TlsSettingsError(msg)
    state = environment.get(STATE, "").strip()
    return Tls(
        mode=mode,
        names=names,
        certificate=pathlib.Path(certificate) if files else None,
        private_key=pathlib.Path(private_key) if files else None,
        key_type=KeyType(key_type),
        state=pathlib.Path(state) if state else DEFAULT_STATE,
    )
