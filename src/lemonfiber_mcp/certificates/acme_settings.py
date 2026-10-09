# Copyright (c) 2026 NightWorksIO
"""The `acme` mode's settings: which authority, checked against which roots, bound how, and by which challenge.

Spelled as the certificates contract spells each. The authority is Let's
Encrypt's where none is named; the challenge is TLS-ALPN-01, answered on the
port the server serves on. A secret is read from the file its setting names.
"""

import enum
import pathlib
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

from lemonfiber_mcp.certificates.settings import TlsSettingsError

if TYPE_CHECKING:
    from collections.abc import Mapping

DIRECTORY: Final = "LEMONFIBER_ACME_DIRECTORY"
ROOTS: Final = "LEMONFIBER_ACME_ROOTS"
CONTACT: Final = "LEMONFIBER_ACME_CONTACT"
EAB_KID: Final = "LEMONFIBER_ACME_EAB_KID"
EAB_HMAC_FILE: Final = "LEMONFIBER_ACME_EAB_HMAC_FILE"
CHALLENGE: Final = "LEMONFIBER_ACME_CHALLENGE"
DNS_PROVIDER: Final = "LEMONFIBER_ACME_DNS_PROVIDER"
LETS_ENCRYPT: Final = "https://acme-v02.api.letsencrypt.org/directory"
"""The directory spoken to where `LEMONFIBER_ACME_DIRECTORY` names none."""
MAILTO: Final = "mailto:"
HTTPS: Final = "https://"


class Challenge(enum.StrEnum):
    """How the authority is shown the server holds a name."""

    TLS_ALPN_01 = "tls-alpn-01"
    HTTP_01 = "http-01"
    DNS_01 = "dns-01"


@dataclass(frozen=True, slots=True)
class Binding:
    """An External Account Binding: the key identifier, and the file holding the HMAC key."""

    kid: str
    hmac_file: pathlib.Path

    def hmac_key(self) -> str:
        """Return the HMAC key the file holds, refusing a file that cannot be read."""
        try:
            key = self.hmac_file.read_bytes().decode().strip()
        except OSError, UnicodeDecodeError:
            key = ""
        if not key:
            msg = f"{EAB_HMAC_FILE} names a file that could not be read, or holds nothing."
            raise TlsSettingsError(msg)
        return key


@dataclass(frozen=True, slots=True)
class Acme:
    """Which authority, its directory's roots, the contact, the binding and the challenge."""

    directory: str
    roots: pathlib.Path | None
    contact: str | None
    binding: Binding | None
    challenge: Challenge
    dns_provider: str | None


def acme_from(environment: Mapping[str, str]) -> Acme:
    """Read the `acme` mode's settings, refusing a combination the certificates contract does not offer."""
    directory = environment.get(DIRECTORY, "").strip() or LETS_ENCRYPT
    if not directory.startswith(HTTPS):
        msg = f"{DIRECTORY} is {directory!r}; an ACME directory is spoken to over HTTPS alone."
        raise TlsSettingsError(msg)
    roots = environment.get(ROOTS, "").strip()
    contact = environment.get(CONTACT, "").strip()
    if contact and not contact.startswith(MAILTO):
        msg = f"{CONTACT} is a `mailto:` address the authority may write to."
        raise TlsSettingsError(msg)
    kid = environment.get(EAB_KID, "").strip()
    hmac_file = environment.get(EAB_HMAC_FILE, "").strip()
    if bool(kid) != bool(hmac_file):
        msg = f"{EAB_KID} and {EAB_HMAC_FILE} are given together or not at all."
        raise TlsSettingsError(msg)
    written = environment.get(CHALLENGE, "").strip() or Challenge.TLS_ALPN_01.value
    if written not in set(Challenge):
        msg = f"{CHALLENGE} is {written!r}; it is one of {', '.join(kind.value for kind in Challenge)}."
        raise TlsSettingsError(msg)
    provider = environment.get(DNS_PROVIDER, "").strip()
    return Acme(
        directory=directory,
        roots=pathlib.Path(roots) if roots else None,
        contact=contact or None,
        binding=Binding(kid, pathlib.Path(hmac_file)) if kid else None,
        challenge=Challenge(written),
        dns_provider=provider or None,
    )
