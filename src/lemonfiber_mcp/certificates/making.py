# Copyright (c) 2026 NightWorksIO
"""Making keys and certificates: a private root constrained to the server's names, what it issues, and a pinned one.

Every key is generated here, in this process. A private root may sign
certificates for TLS servers and nothing else, and only for the names and
addresses it was made for: every kind of name it is given none of is excluded
whole, so a root that leaks vouches for nothing beyond them. A fingerprint
is the SHA-256 digest of a certificate's DER encoding in lower-case hex, the
form the companion's pairing material carries.
"""

import datetime
import hashlib
import ipaddress
from typing import TYPE_CHECKING, Final, cast

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID

from lemonfiber_mcp.certificates.settings import KeyType

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

    from cryptography.hazmat.primitives.asymmetric.types import PrivateKeyTypes

    from lemonfiber_mcp.certificates.settings import Name

type PrivateKey = ec.EllipticCurvePrivateKey | rsa.RSAPrivateKey

ROOT_LIFETIME: Final = datetime.timedelta(days=3650)
"""How long a private root is valid: ten years, one installation per device per decade."""
ISSUED_LIFETIME: Final = datetime.timedelta(days=30)
"""How long a certificate a private root issues is valid."""
PINNED_LIFETIME: Final = datetime.timedelta(days=3650)
"""How long a pinned certificate is valid: renewing it would break every pin."""
BACKDATED: Final = datetime.timedelta(minutes=5)
"""How far before now a certificate's validity starts, for a client whose clock runs behind."""
RSA_EXPONENT: Final = 65537
ORGANISATION: Final = "lemonfiber"
CURVES: Final[Mapping[KeyType, ec.EllipticCurve]] = {
    KeyType.EC_P256: ec.SECP256R1(),
    KeyType.EC_P384: ec.SECP384R1(),
}
RSA_SIZES: Final[Mapping[KeyType, int]] = {KeyType.RSA_2048: 2048, KeyType.RSA_3072: 3072}


def generated(kind: KeyType) -> PrivateKey:
    """Return a new private key of a kind."""
    if kind in CURVES:
        return ec.generate_private_key(CURVES[kind])
    return rsa.generate_private_key(public_exponent=RSA_EXPONENT, key_size=RSA_SIZES[kind])


def key_pem(key: PrivateKey) -> bytes:
    """Return a private key as unencrypted PKCS #8 PEM, for a file only this user reads."""
    return key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )


def certificate_pem(*certificates: x509.Certificate) -> bytes:
    """Return certificates as PEM, in the order given: a chain is its leaf first."""
    return b"".join(certificate.public_bytes(serialization.Encoding.PEM) for certificate in certificates)


def fingerprint(certificate: x509.Certificate) -> str:
    """Return a certificate's SHA-256 fingerprint over its DER encoding, in lower-case hex."""
    return hashlib.sha256(certificate.public_bytes(serialization.Encoding.DER)).hexdigest()


def general_names(names: Iterable[Name]) -> list[x509.GeneralName]:
    """Return names as a certificate carries them: host names as DNS names, addresses as IP addresses."""
    return [x509.DNSName(name) if isinstance(name, str) else x509.IPAddress(name) for name in names]


def subtrees(names: Iterable[Name]) -> list[x509.GeneralName]:
    """Return the name constraints permitting exactly these names: each host name, and each address alone."""
    return [
        x509.DNSName(name)
        if isinstance(name, str)
        else x509.IPAddress(ipaddress.ip_network(f"{name}/{name.max_prefixlen}"))
        for name in names
    ]


EVERY_ADDRESS: Final = (
    x509.IPAddress(ipaddress.ip_network("0.0.0.0/0")),
    x509.IPAddress(ipaddress.ip_network("::/0")),
)
"""What excludes every address, IPv4 and IPv6, from what a root may vouch for."""
EVERY_HOST_NAME: Final = x509.DNSName("")
"""What excludes every host name: an empty DNS name matches them all, as RFC 5280 reads it."""


def excluded(names: Iterable[Name]) -> list[x509.GeneralName]:
    """Return the constraints excluding every kind of name a root is given none of.

    A kind of name with no permitted subtree is unconstrained, so a root made
    for host names alone would otherwise vouch for any address, and one made for
    addresses alone for any host name. Directory names are left out: a
    certificate's subject is one, and excluding them all would refuse every
    certificate the root issues. Mailboxes and URIs are left out too: no form
    excludes them all in every validator, and the root's own extended key usage,
    TLS servers alone, keeps it from vouching for mail or a client instead.
    """
    given = list(names)
    kept: list[x509.GeneralName] = []
    if not any(isinstance(name, str) for name in given):
        kept.append(EVERY_HOST_NAME)
    if all(isinstance(name, str) for name in given):
        kept.extend(EVERY_ADDRESS)
    return kept


def named(common_name: str) -> x509.Name:
    """Return a certificate's subject or issuer: this organisation, and a common name."""
    return x509.Name(
        [
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, ORGANISATION),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ],
    )


def labelled(kind: str, names: tuple[Name, ...]) -> x509.Name:
    """Return the subject of a certificate this server makes: a label, never one of its names.

    A validator that finds no host name among a certificate's alternative names
    may read a common name shaped like one as a host name; an address there
    would then meet a root's exclusion of every host name. A label with spaces
    is never read so.
    """
    return named(f"lemonfiber MCP {kind} for {names[0]}")


def builder(
    subject: x509.Name,
    key: PrivateKey,
    lifetime: datetime.timedelta,
    now: datetime.datetime,
) -> x509.CertificateBuilder:
    """Return a certificate builder for a subject and public key, valid from a little before now for a lifetime."""
    return (
        x509.CertificateBuilder()
        .subject_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - BACKDATED)
        .not_valid_after(now + lifetime)
        .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
    )


def leaf_extensions(made: x509.CertificateBuilder, names: Iterable[Name]) -> x509.CertificateBuilder:
    """Return a builder made a server's certificate for these names: no authority, for TLS servers only."""
    return (
        made.add_extension(x509.SubjectAlternativeName(general_names(names)), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
    )


def root(names: tuple[Name, ...], key: PrivateKey, now: datetime.datetime) -> x509.Certificate:
    """Return a private root for these names: it signs certificates, no authority below it, and nothing outside them."""
    subject = labelled("root", names)
    made = (
        builder(subject, key, ROOT_LIFETIME, now)
        .issuer_name(subject)
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=False,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        )
        .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .add_extension(
            x509.NameConstraints(
                permitted_subtrees=subtrees(names),
                excluded_subtrees=excluded(names) or None,
            ),
            critical=True,
        )
    )
    return made.sign(key, hashes.SHA384())


def issued(
    names: tuple[Name, ...],
    key: PrivateKey,
    by: x509.Certificate,
    signer: PrivateKey,
    now: datetime.datetime,
) -> x509.Certificate:
    """Return a server's certificate for these names, issued by a private root."""
    made = leaf_extensions(
        builder(labelled("server", names), key, ISSUED_LIFETIME, now).issuer_name(by.subject),
        names,
    ).add_extension(
        x509.AuthorityKeyIdentifier.from_issuer_public_key(signer.public_key()),
        critical=False,
    )
    return made.sign(signer, hashes.SHA256())


def pinned(names: tuple[Name, ...], key: PrivateKey, now: datetime.datetime) -> x509.Certificate:
    """Return a server's certificate signed by its own key, for clients that pin it."""
    subject = labelled("server", names)
    made = leaf_extensions(builder(subject, key, PINNED_LIFETIME, now), names).issuer_name(subject)
    return made.sign(key, hashes.SHA256())


def covered(certificate: x509.Certificate) -> set[Name]:
    """Return every name a certificate's subject alternative names hold."""
    try:
        alternatives = certificate.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    except x509.ExtensionNotFound:
        return set()
    addresses = cast(
        "list[ipaddress.IPv4Address | ipaddress.IPv6Address]",
        alternatives.get_values_for_type(x509.IPAddress),
    )
    return {*alternatives.get_values_for_type(x509.DNSName), *addresses}


def permitted(root_certificate: x509.Certificate) -> set[Name]:
    """Return every name a private root's constraints permit, each host name and each address alone.

    A root made here permits only host names and single addresses, so every
    subtree is one or the other.
    """
    constraints = root_certificate.extensions.get_extension_for_class(x509.NameConstraints).value
    return {
        subtree.value
        if isinstance(subtree, x509.DNSName)
        else cast("ipaddress.IPv4Network | ipaddress.IPv6Network", subtree.value).network_address
        for subtree in constraints.permitted_subtrees or []
    }


def matches(certificate: x509.Certificate, key: PrivateKeyTypes) -> bool:
    """Tell whether a private key is the one a certificate was made for."""
    return certificate.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    ) == key.public_key().public_bytes(
        serialization.Encoding.DER,
        serialization.PublicFormat.SubjectPublicKeyInfo,
    )
