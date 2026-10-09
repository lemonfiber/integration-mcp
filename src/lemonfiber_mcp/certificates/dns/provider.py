# Copyright (c) 2026 NightWorksIO
"""What a DNS provider does: write a TXT record and remove it, and how long its records take to be seen."""

import pathlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Protocol

from lemonfiber_mcp.certificates.modes import CertificateError
from lemonfiber_mcp.certificates.settings import TlsSettingsError

if TYPE_CHECKING:
    from collections.abc import Mapping

TIMEOUT_SECONDS: Final = 30
"""How long one request to a provider's API is waited on."""


class ProviderError(CertificateError):
    """A provider refused or could not be reached; the message names the provider and never a credential."""


@dataclass(frozen=True, slots=True)
class Timing:
    """How long a provider's records take to be seen, and how often to look."""

    propagation: float = 120.0
    interval: float = 2.0


class Provider(Protocol):
    """Where the challenge's TXT record is written."""

    timing: Timing

    def present(self, name: str, value: str) -> None:
        """Write a TXT record holding `value` at the fully qualified `name`."""
        ...

    def cleanup(self, name: str, value: str) -> None:
        """Remove the TXT record holding `value` at `name`."""
        ...


def needed(environment: Mapping[str, str], setting: str) -> str:
    """Return a setting's value, refusing a start without it, by name."""
    value = environment.get(setting, "").strip()
    if not value:
        msg = f"{setting} is not set, and the DNS provider needs it."
        raise TlsSettingsError(msg)
    return value


def secret(environment: Mapping[str, str], setting: str) -> str:
    """Return the secret held by the file a `_FILE` setting names, refusing one that cannot be read."""
    path = pathlib.Path(needed(environment, setting))
    msg = f"{setting} names a file that could not be read, or holds nothing."
    try:
        held = path.read_bytes().decode().strip()
    except OSError, UnicodeDecodeError:
        raise TlsSettingsError(msg) from None
    if not held:
        raise TlsSettingsError(msg)
    return held


def relative(name: str, zone: str) -> str:
    """Return a fully qualified name relative to its zone, `@` for the apex."""
    bare, apex = name.rstrip("."), zone.rstrip(".")
    return "@" if bare == apex else bare.removesuffix(f".{apex}")


def candidates(name: str) -> list[str]:
    """Return every zone a name may sit in, longest first, the top-level domain left out."""
    labels = name.rstrip(".").split(".")
    return [".".join(labels[at:]) for at in range(len(labels) - 1)]
