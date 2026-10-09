# Copyright (c) 2026 NightWorksIO
"""Where the served certificate comes from, in each mode the server makes or reads itself.

Each source answers `obtain`, which returns the certificate to serve now:
the same one where nothing is due, or a new one where it is. It is asked at
start and again on every check, so a renewal, a replaced root or file, or a
command run beside the server is taken without a restart.
"""

import datetime
import fnmatch
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, Protocol, cast

from cryptography import x509
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa

from lemonfiber_mcp.certificates import making, state
from lemonfiber_mcp.certificates.settings import CERTIFICATE, PRIVATE_KEY, KeyType, Mode

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Callable, Mapping

    from lemonfiber_mcp.certificates.making import PrivateKey
    from lemonfiber_mcp.certificates.settings import Name, Tls

ISSUED_RENEWED_WITH: Final = datetime.timedelta(days=10)
"""How much of an issued certificate's life is left when the private root issues the next."""
ROOT_REPLACED_WITH: Final = datetime.timedelta(days=365)
"""How much of a private root's life is left when its replacement is made."""
ROOT_SWITCHED_WITH: Final = datetime.timedelta(days=30)
"""How much of a private root's life is left when the server switches to its replacement unasked."""
CERTIFICATES: Final = "certificates"
CA: Final = "ca"
CHAIN: Final = "chain.pem"
KEY: Final = "key.pem"
ROOT: Final = "root.pem"
ROOT_KEY: Final = "root-key.pem"
NEXT_ROOT: Final = "next-root.pem"
NEXT_ROOT_KEY: Final = "next-root-key.pem"
RENEWAL: Final = "renewal.json"
ROOT_KEY_TYPE: Final = KeyType.EC_P384
"""The kind of key every private root is made with."""


class CertificateError(Exception):
    """The certificate cannot be served as it stands; the message names what is wrong and never a key."""


@dataclass(frozen=True, slots=True)
class Served:
    """The certificate served now: its chain and its key on disk, and its leaf."""

    chain: pathlib.Path
    key: pathlib.Path
    leaf: x509.Certificate

    @property
    def expires(self) -> datetime.datetime:
        """Return when the leaf stops being valid."""
        return self.leaf.not_valid_after_utc

    @property
    def fingerprint(self) -> str:
        """Return the leaf's fingerprint, which says whether two certificates are one."""
        return making.fingerprint(self.leaf)


class Source(Protocol):
    """Where the served certificate comes from."""

    mode: Mode

    def obtain(self, now: datetime.datetime) -> Served:
        """Return the certificate to serve now, making or reading a new one where one is due."""
        ...

    def announced(self) -> list[str]:
        """Return what the start-up log and every change say of this source beyond its mode."""
        ...

    def due(self, served: Served, /) -> datetime.datetime | None:
        """Return when the source makes the next certificate unasked, or None where it never does."""
        ...

    @property
    def renewal(self) -> pathlib.Path | None:
        """Return where the record of renewal is kept, or None where the source keeps no state."""
        ...


def chain_of(path: pathlib.Path) -> list[x509.Certificate]:
    """Return the certificates a PEM file holds, in order."""
    return x509.load_pem_x509_certificates(path.read_bytes())


def private_key_of(path: pathlib.Path) -> PrivateKey:
    """Return the private key a PEM file holds, refusing a kind this server does not make."""
    key = serialization.load_pem_private_key(path.read_bytes(), password=None)
    if not isinstance(key, ec.EllipticCurvePrivateKey | rsa.RSAPrivateKey):
        msg = f"{path} holds a kind of key this server does not make."
        raise CertificateError(msg)
    return key


def names_held(certificate: x509.Certificate, wanted: tuple[Name, ...]) -> bool:
    """Tell whether a certificate covers every wanted name, a wildcard covering one label."""
    held = making.covered(certificate)
    patterns = [name for name in held if isinstance(name, str) and name.startswith("*.")]
    return all(
        name in held
        or (
            isinstance(name, str)
            and any(
                fnmatch.fnmatchcase(name, pattern) and name.count(".") == pattern.count(".")
                for pattern in patterns
            )
        )
        for name in wanted
    )


def leaf_dir(tls: Tls) -> pathlib.Path:
    """Return where the served certificate's chain and key are kept."""
    return tls.state / CERTIFICATES / tls.first


class Files:
    """The operator's own certificate and key, read again whenever either changes."""

    mode = Mode.FILES

    def __init__(self, tls: Tls) -> None:
        """Hold where the operator's files are and the names they must cover."""
        self._certificate = cast("pathlib.Path", tls.certificate)
        self._key = cast("pathlib.Path", tls.private_key)
        self._names = tls.names

    def obtain(self, now: datetime.datetime) -> Served:
        """Return the operator's certificate, refusing one that cannot be served, by what is wrong with it."""
        try:
            chain = chain_of(self._certificate)
            key = serialization.load_pem_private_key(self._key.read_bytes(), password=None)
        except OSError, ValueError, TypeError:
            msg = f"{CERTIFICATE} or {PRIVATE_KEY} names a file that could not be read as PEM."
            raise CertificateError(msg) from None
        leaf = chain[0]
        if not making.matches(leaf, key):
            msg = f"{PRIVATE_KEY} does not hold the key {CERTIFICATE}'s certificate was made for."
            raise CertificateError(msg)
        if now >= leaf.not_valid_after_utc:
            msg = f"{CERTIFICATE} holds a certificate that expired on {leaf.not_valid_after_utc:%Y-%m-%d}."
            raise CertificateError(msg)
        if not names_held(leaf, self._names):
            msg = f"{CERTIFICATE} holds a certificate that does not cover every name in LEMONFIBER_NAMES."
            raise CertificateError(msg)
        return Served(self._certificate, self._key, leaf)

    def announced(self) -> list[str]:
        """Return nothing beyond the mode: the operator knows their own certificate."""
        return []

    def due(self, _: Served, /) -> datetime.datetime | None:
        """Return None: what renews the operator's files is the operator's."""
        return None

    @property
    def renewal(self) -> pathlib.Path | None:
        """Return None: the operator's files keep no state here."""
        return None


def kept_leaf(
    directory: pathlib.Path,
    names: tuple[Name, ...],
    now: datetime.datetime,
) -> tuple[x509.Certificate, PrivateKey] | None:
    """Return the certificate kept in a directory and its key, where both are there, match, and cover exactly these names."""
    try:
        leaf = chain_of(directory / CHAIN)[0]
        key = private_key_of(directory / KEY)
    except OSError, ValueError, CertificateError:
        return None
    if not making.matches(leaf, key) or now >= leaf.not_valid_after_utc or making.covered(leaf) != set(names):
        return None
    return leaf, key


def keep(directory: pathlib.Path, chain: list[x509.Certificate], key: PrivateKey) -> Served:
    """Write a chain and its key where the served certificate is kept, and return it as served."""
    state.write(directory / KEY, making.key_pem(key))
    state.write(directory / CHAIN, making.certificate_pem(*chain))
    return Served(directory / CHAIN, directory / KEY, chain[0])


class Pinned:
    """A certificate of the server's own, signed by its own key, for clients that pin its fingerprint."""

    mode = Mode.PINNED

    def __init__(self, tls: Tls) -> None:
        """Hold the names it is for, the key it is made with, and where it is kept."""
        self._names = tls.names
        self._key_type = tls.key_type
        self._directory = leaf_dir(tls)
        self._made = False
        self._served: Served | None = None

    def obtain(self, now: datetime.datetime) -> Served:
        """Return the kept certificate, or make one where none is kept for these names."""
        kept = kept_leaf(self._directory, self._names, now)
        if kept is not None:
            self._served = Served(self._directory / CHAIN, self._directory / KEY, kept[0])
            return self._served
        self._made = self._served is not None or (self._directory / CHAIN).exists()
        key = making.generated(self._key_type)
        self._served = keep(self._directory, [making.pinned(self._names, key, now)], key)
        return self._served

    def replace(self, now: datetime.datetime) -> Served:
        """Make a new certificate in place of the kept one, on the operator's command."""
        self._made = True
        key = making.generated(self._key_type)
        self._served = keep(self._directory, [making.pinned(self._names, key, now)], key)
        return self._served

    def announced(self) -> list[str]:
        """Return the fingerprint to give each client, and, where it is new, that every client needs it again."""
        if self._served is None:
            return []
        said = [f"The certificate's fingerprint, for each client to pin: {self._served.fingerprint}"]
        if self._made:
            said.append("This certificate is new: give every client this fingerprint again.")
        return said

    def due(self, _: Served, /) -> datetime.datetime | None:
        """Return None: a pinned certificate is replaced only on command, since a new one breaks every pin."""
        return None

    @property
    def renewal(self) -> pathlib.Path | None:
        """Return where the record of the certificate is kept."""
        return self._directory / RENEWAL


class PrivateCa:
    """A root of the server's own, constrained to its names, issuing the certificate it serves."""

    mode = Mode.PRIVATE_CA

    def __init__(self, tls: Tls) -> None:
        """Hold the names, the key kind, and where the root and the served certificate are kept."""
        self._names = tls.names
        self._key_type = tls.key_type
        self._ca = tls.state / CA
        self._directory = leaf_dir(tls)
        self._root: x509.Certificate | None = None
        self._next: x509.Certificate | None = None
        self._uncovered: list[Name] = []

    @property
    def root_file(self) -> pathlib.Path:
        """Return where the root's certificate is kept, for a device to install."""
        return self._ca / ROOT

    def _made_root(
        self,
        names: tuple[Name, ...],
        certificate: str,
        key: str,
        now: datetime.datetime,
    ) -> x509.Certificate:
        signer = making.generated(ROOT_KEY_TYPE)
        made = making.root(names, signer, now)
        state.write(self._ca / key, making.key_pem(signer))
        state.write(self._ca / certificate, making.certificate_pem(made))
        return made

    def _held(self, certificate: str, key: str) -> tuple[x509.Certificate, PrivateKey] | None:
        try:
            return chain_of(self._ca / certificate)[0], private_key_of(self._ca / key)
        except OSError, ValueError, CertificateError:
            return None

    def _switch(self) -> None:
        (self._ca / NEXT_ROOT_KEY).replace(self._ca / ROOT_KEY)
        (self._ca / NEXT_ROOT).replace(self._ca / ROOT)
        (self._directory / CHAIN).unlink(missing_ok=True)

    def roots(self, now: datetime.datetime) -> tuple[x509.Certificate, PrivateKey]:
        """Return the root in force, making, replacing or switching to one as its life and the names say."""
        held = self._held(ROOT, ROOT_KEY)
        if held is None:
            self._made_root(self._names, ROOT, ROOT_KEY, now)
            held = cast("tuple[x509.Certificate, PrivateKey]", self._held(ROOT, ROOT_KEY))
        waiting = self._held(NEXT_ROOT, NEXT_ROOT_KEY)
        if waiting is not None and now >= held[0].not_valid_after_utc - ROOT_SWITCHED_WITH:
            self._switch()
            held, waiting = waiting, None
        permitted = making.permitted(held[0])
        self._uncovered = [name for name in self._names if name not in permitted]
        ageing = now >= held[0].not_valid_after_utc - ROOT_REPLACED_WITH
        replacement = None if waiting is None else waiting[0]
        if replacement is None and (self._uncovered or ageing):
            replacement = self._made_root(self._names, NEXT_ROOT, NEXT_ROOT_KEY, now)
        self._root, self._next = held[0], replacement
        return held

    def obtain(self, now: datetime.datetime) -> Served:
        """Return the certificate the root issued, issuing the next once ten days are left or the root changed."""
        root, signer = self.roots(now)
        names = tuple(name for name in self._names if name not in self._uncovered) or tuple(
            making.permitted(root),
        )
        kept = kept_leaf(self._directory, names, now)
        if kept is not None and now < kept[0].not_valid_after_utc - ISSUED_RENEWED_WITH:
            try:
                kept[0].verify_directly_issued_by(root)
            except ValueError, TypeError, InvalidSignature:
                pass
            else:
                return Served(self._directory / CHAIN, self._directory / KEY, kept[0])
        key = making.generated(self._key_type)
        return keep(self._directory, [making.issued(names, key, root, signer, now)], key)

    def replace(self, now: datetime.datetime) -> x509.Certificate:
        """Make a replacement root beside the one in force, on the operator's command."""
        self.roots(now)
        if self._next is None:
            self._next = self._made_root(self._names, NEXT_ROOT, NEXT_ROOT_KEY, now)
        return self._next

    def switch(self) -> bool:
        """Put the replacement root in force, deleting the old root's key; say whether there was one."""
        if not (self._ca / NEXT_ROOT).exists():
            return False
        self._switch()
        return True

    def announced(self) -> list[str]:
        """Return the root's fingerprint to check before installing it, and a replacement waiting to be installed."""
        said: list[str] = []
        if self._root is not None:
            said.append(
                f"Install the root at {self.root_file} on each device that is to connect; it is also served at "
                f"/root.pem. Its fingerprint: {making.fingerprint(self._root)}",
            )
        if self._next is not None:
            said.append(
                f"A replacement root waits to be installed, at {self._ca / NEXT_ROOT}, fingerprint "
                f"{making.fingerprint(self._next)}. Install it on every device, then run `lemonfiber-mcp ca switch`.",
            )
        if self._uncovered:
            said.append(
                f"{', '.join(map(str, self._uncovered))} is not served until the replacement root is in force: "
                "the root in force does not cover it.",
            )
        return said

    def due(self, served: Served, /) -> datetime.datetime | None:
        """Return when the root issues the next certificate: ten days before this one expires."""
        return served.expires - ISSUED_RENEWED_WITH

    @property
    def renewal(self) -> pathlib.Path | None:
        """Return where the record of renewal is kept."""
        return self._directory / RENEWAL


NOT_YET: Final = (
    "LEMONFIBER_TLS_MODE is acme, which this version of the server does not serve yet. Choose files, "
    "private-ca or pinned."
)


SOURCES: Final[Mapping[Mode, Callable[[Tls], Source]]] = {
    Mode.FILES: Files,
    Mode.PRIVATE_CA: PrivateCa,
    Mode.PINNED: Pinned,
}
"""Where the certificate comes from, by each mode this version serves."""


def source_of(tls: Tls) -> Source:
    """Return where the certificate comes from in the mode the settings chose."""
    made = SOURCES.get(tls.mode)
    if made is None:
        raise CertificateError(NOT_YET)
    return made(tls)
