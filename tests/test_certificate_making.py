# Copyright (c) 2026 NightWorksIO
"""Keys and certificates: a root that signs only for its names, what it issues, a pinned one, and the state they live in."""

import contextlib
import datetime
import hashlib
import ipaddress
import os
import ssl
import stat
from typing import TYPE_CHECKING, Final

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509 import verification

from lemonfiber_mcp.certificates import making, state
from lemonfiber_mcp.certificates.settings import KeyType, Name

if TYPE_CHECKING:
    import pathlib

NOW: Final = datetime.datetime(2026, 10, 9, tzinfo=datetime.UTC)
NAMES: Final = ("mcp.home.example", ipaddress.ip_address("192.168.1.42"))
HOST_ONLY: Final[tuple[Name, ...]] = ("mcp.home.example",)
ADDRESS_ONLY: Final[tuple[Name, ...]] = (ipaddress.ip_address("192.168.1.42"),)
IPV6_ONLY: Final[tuple[Name, ...]] = (ipaddress.ip_address("fd00::42"),)
UNCONFIGURED: Final[tuple[Name, ...]] = (
    "elsewhere.example",
    ipaddress.ip_address("10.0.0.1"),
    ipaddress.ip_address("fd00::66"),
)
EVERY_KIND: Final = [HOST_ONLY, ADDRESS_ONLY, IPV6_ONLY, NAMES]


def identity(name: Name) -> x509.DNSName | x509.IPAddress:
    """Return a name as the verifier asks for it."""
    return x509.DNSName(name) if isinstance(name, str) else x509.IPAddress(name)


def verified(root: x509.Certificate, leaf: x509.Certificate, name: Name, now: datetime.datetime) -> bool:
    """Tell whether cryptography's verifier accepts a leaf for a name under a root."""
    verifier = (
        verification.PolicyBuilder()
        .store(verification.Store([root]))
        .time(now)
        .build_server_verifier(identity(name))
    )
    try:
        verifier.verify(leaf, [])
    except verification.VerificationError:
        return False
    return True


def handshaken(
    root: x509.Certificate,
    leaf: x509.Certificate,
    key: making.PrivateKey,
    name: Name,
    held: pathlib.Path,
) -> bool:
    """Tell whether OpenSSL, through this Python's ssl, completes a handshake checking a leaf for a name under a root."""
    chain, private_key = held / "chain.pem", held / "key.pem"
    chain.write_bytes(making.certificate_pem(leaf))
    private_key.write_bytes(making.key_pem(key))
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(chain, private_key)
    client_context = ssl.create_default_context(cadata=making.certificate_pem(root).decode())
    to_server, to_client = ssl.MemoryBIO(), ssl.MemoryBIO()
    client = client_context.wrap_bio(to_client, to_server, server_hostname=str(name))
    server = server_context.wrap_bio(to_server, to_client, server_side=True)
    with contextlib.suppress(ssl.SSLWantReadError):
        client.do_handshake()
    with contextlib.suppress(ssl.SSLWantReadError):
        server.do_handshake()
    try:
        client.do_handshake()
    except ssl.SSLCertVerificationError:
        return False
    return True


def accepted(names: tuple[Name, ...], leaf_names: tuple[Name, ...], held: pathlib.Path) -> tuple[bool, bool]:
    """Return whether each validator accepts a leaf for `leaf_names` signed by a root made for `names`."""
    now = datetime.datetime.now(datetime.UTC)
    signer = making.generated(KeyType.EC_P384)
    root = making.root(names, signer, now)
    key = making.generated(KeyType.EC_P256)
    leaf = making.issued(leaf_names, key, root, signer, now)
    return verified(root, leaf, leaf_names[0], now), handshaken(root, leaf, key, leaf_names[0], held)


@pytest.mark.parametrize("kind", list(KeyType))
def test_every_kind_of_key_is_made_here(kind: KeyType) -> None:
    key = making.generated(kind)
    assert isinstance(key, ec.EllipticCurvePrivateKey if kind.value.startswith("ec") else rsa.RSAPrivateKey)
    assert (
        serialization.load_pem_private_key(making.key_pem(key), password=None).public_key()
        == key.public_key()
    )


def test_a_root_signs_certificates_only_and_only_for_its_names() -> None:
    signer = making.generated(KeyType.EC_P384)
    root = making.root(NAMES, signer, NOW)
    basic = root.extensions.get_extension_for_class(x509.BasicConstraints)
    assert basic.critical
    assert (basic.value.ca, basic.value.path_length) == (True, 0)
    usage = root.extensions.get_extension_for_class(x509.KeyUsage).value
    assert usage.key_cert_sign
    assert not usage.digital_signature
    constraints = root.extensions.get_extension_for_class(x509.NameConstraints)
    assert constraints.critical
    assert making.permitted(root) == set(NAMES)
    assert root.not_valid_after_utc - root.not_valid_before_utc == making.ROOT_LIFETIME + making.BACKDATED


@pytest.mark.parametrize("names", EVERY_KIND)
def test_both_validators_accept_what_a_root_issues_for_its_own_names(
    names: tuple[Name, ...],
    tmp_path: pathlib.Path,
) -> None:
    for name in names:
        assert accepted(names, (name,), tmp_path) == (True, True)


@pytest.mark.parametrize("names", EVERY_KIND)
@pytest.mark.parametrize("elsewhere", UNCONFIGURED)
def test_both_validators_refuse_what_a_root_signs_for_any_other_name_or_address(
    names: tuple[Name, ...],
    elsewhere: Name,
    tmp_path: pathlib.Path,
) -> None:
    assert accepted(names, (elsewhere,), tmp_path) == (False, False)


@pytest.mark.parametrize(
    ("names", "kept"),
    [
        (HOST_ONLY, list(making.EVERY_ADDRESS)),
        (ADDRESS_ONLY, [making.EVERY_HOST_NAME]),
        (IPV6_ONLY, [making.EVERY_HOST_NAME]),
        (NAMES, []),
    ],
)
def test_a_root_excludes_every_kind_of_name_it_is_given_none_of(
    names: tuple[Name, ...],
    kept: list[x509.GeneralName],
) -> None:
    root = making.root(names, making.generated(KeyType.EC_P384), NOW)
    constraints = root.extensions.get_extension_for_class(x509.NameConstraints).value
    assert list(constraints.excluded_subtrees or []) == kept


def test_every_address_and_every_host_name_are_excluded_whole() -> None:
    assert [subtree.value for subtree in making.EVERY_ADDRESS] == [
        ipaddress.ip_network("0.0.0.0/0"),
        ipaddress.ip_network("::/0"),
    ]
    assert making.EVERY_HOST_NAME.value == ""


def test_a_root_vouches_for_tls_servers_and_no_client() -> None:
    now = datetime.datetime.now(datetime.UTC)
    signer = making.generated(KeyType.EC_P384)
    root = making.root(HOST_ONLY, signer, now)
    assert list(root.extensions.get_extension_for_class(x509.ExtendedKeyUsage).value) == [
        x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
    ]
    key = making.generated(KeyType.EC_P256)
    client = (
        making.builder(making.named("client"), key, making.ISSUED_LIFETIME, now)
        .issuer_name(root.subject)
        .add_extension(
            x509.AuthorityKeyIdentifier.from_issuer_public_key(signer.public_key()),
            critical=False,
        )
        .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False)
        .sign(signer, making.hashes.SHA256())
    )
    verifier = (
        verification.PolicyBuilder().store(verification.Store([root])).time(now).build_client_verifier()
    )
    with pytest.raises(verification.VerificationError):
        verifier.verify(client, [])


def usage(*, signs: bool) -> x509.KeyUsage:
    """Return the key usage of a root where it signs certificates, and of a server's certificate where not."""
    return x509.KeyUsage(
        digital_signature=not signs,
        content_commitment=False,
        key_encipherment=False,
        data_encipherment=False,
        key_agreement=False,
        key_cert_sign=signs,
        crl_sign=signs,
        encipher_only=False,
        decipher_only=False,
    )


def common_name(certificate: x509.Certificate) -> object:
    """Return a certificate's common name."""
    return certificate.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value


def test_a_root_and_what_it_issues_say_their_use_exactly_and_as_critical() -> None:
    signer = making.generated(KeyType.EC_P384)
    root = making.root(NAMES, signer, NOW)
    leaf = making.issued(NAMES, making.generated(KeyType.EC_P256), root, signer, NOW)
    for certificate, signs in ((root, True), (leaf, False)):
        used = certificate.extensions.get_extension_for_class(x509.KeyUsage)
        assert (used.value, used.critical) == (usage(signs=signs), True)
        assert certificate.extensions.get_extension_for_class(x509.BasicConstraints).critical
    assert common_name(root) == "lemonfiber MCP root for mcp.home.example"
    assert common_name(leaf) == "lemonfiber MCP server for mcp.home.example"


def test_a_certificate_made_here_names_itself_by_a_label_no_validator_reads_as_a_host_name() -> None:
    leaf = making.pinned(ADDRESS_ONLY, making.generated(KeyType.EC_P256), NOW)
    common_name = leaf.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
    assert common_name == "lemonfiber MCP server for 192.168.1.42"
    assert leaf.issuer == leaf.subject


def test_what_a_root_issues_verifies_against_it_and_serves_tls_for_its_names() -> None:
    signer = making.generated(KeyType.EC_P384)
    root = making.root(NAMES, signer, NOW)
    key = making.generated(KeyType.EC_P256)
    leaf = making.issued(NAMES, key, root, signer, NOW)
    leaf.verify_directly_issued_by(root)
    assert making.covered(leaf) == set(NAMES)
    assert not leaf.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
    assert leaf.not_valid_after_utc == NOW + making.ISSUED_LIFETIME
    assert making.matches(leaf, key)
    assert not making.matches(leaf, signer)


def test_a_pinned_certificate_is_its_own_issuer_for_ten_years() -> None:
    key = making.generated(KeyType.EC_P256)
    leaf = making.pinned(NAMES, key, NOW)
    leaf.verify_directly_issued_by(leaf)
    assert leaf.not_valid_after_utc == NOW + making.PINNED_LIFETIME


def test_a_fingerprint_is_sha256_over_der_in_lower_case_hex() -> None:
    leaf = making.pinned(NAMES, making.generated(KeyType.EC_P256), NOW)
    assert (
        making.fingerprint(leaf) == hashlib.sha256(leaf.public_bytes(serialization.Encoding.DER)).hexdigest()
    )


def test_a_chain_is_written_leaf_first() -> None:
    signer = making.generated(KeyType.EC_P384)
    root = making.root(NAMES, signer, NOW)
    leaf = making.issued(NAMES, making.generated(KeyType.EC_P256), root, signer, NOW)
    assert x509.load_pem_x509_certificates(making.certificate_pem(leaf, root)) == [leaf, root]
    assert making.certificate_pem(leaf, root) == making.certificate_pem(leaf) + making.certificate_pem(root)


def test_a_certificate_without_alternative_names_covers_none() -> None:
    key = making.generated(KeyType.EC_P256)
    bare = (
        making.builder(making.named("bare"), key, making.ISSUED_LIFETIME, NOW)
        .issuer_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, "bare")]))
        .sign(key, making.hashes.SHA256())
    )
    assert making.covered(bare) == set()


def test_the_state_directory_is_made_for_this_user_alone(tmp_path: pathlib.Path) -> None:
    kept = state.kept(tmp_path / "state" / "nested")
    assert stat.S_IMODE(kept.stat().st_mode) == state.DIRECTORY_MODE


def test_a_state_directory_others_can_read_is_refused(tmp_path: pathlib.Path) -> None:
    open_to_all = tmp_path / "open"
    open_to_all.mkdir()
    open_to_all.chmod(0o755)
    with pytest.raises(state.StateError, match="0700"):
        state.kept(open_to_all)


def test_a_state_directory_another_user_owns_is_refused(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    someone_else = os.getuid() + 1
    monkeypatch.setattr(state.os, "getuid", lambda: someone_else)
    with pytest.raises(state.StateError, match="another user"):
        state.kept(tmp_path)


def test_a_state_path_that_is_a_file_is_refused(tmp_path: pathlib.Path) -> None:
    taken = tmp_path / "taken"
    taken.write_text("", encoding="utf-8")
    with pytest.raises(state.StateError, match="could not be made"):
        state.kept(taken)


def test_a_state_path_under_a_file_is_refused(tmp_path: pathlib.Path) -> None:
    taken = tmp_path / "taken"
    taken.write_text("", encoding="utf-8")
    taken.chmod(0o600)
    with pytest.raises(state.StateError):
        state.kept(taken / "below")


def test_a_kept_file_is_written_whole_and_readable_by_this_user_alone(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "keys" / "key.pem"
    state.write(path, b"first")
    state.write(path, b"second")
    assert path.read_bytes() == b"second"
    assert stat.S_IMODE(path.stat().st_mode) == state.FILE_MODE
    assert sorted(item.name for item in path.parent.iterdir()) == ["key.pem"]
    assert stat.S_IMODE(path.parent.stat().st_mode) == state.DIRECTORY_MODE
