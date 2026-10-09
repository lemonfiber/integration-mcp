# Copyright (c) 2026 NightWorksIO
"""TLS-ALPN-01 answered on the serving port: a connection asking for `acme-tls/1` alone gets the challenge, any other the server."""

import datetime
import hashlib
import ssl
from typing import TYPE_CHECKING, Final

import pytest
from cryptography import x509

from lemonfiber_mcp.certificates import alpn, hello, making
from lemonfiber_mcp.certificates.manager import server_context
from lemonfiber_mcp.certificates.settings import KeyType

if TYPE_CHECKING:
    import pathlib

NAME: Final = "mcp.home.example"
KEY_AUTHORIZATION: Final = "token.thumbprint"
ROUNDS: Final = 6


def served_context(tmp_path: pathlib.Path, pending: alpn.Challenges) -> ssl.SSLContext:
    """Return the serving context with a certificate of its own loaded."""
    key = making.generated(KeyType.EC_P256)
    leaf = making.pinned((NAME,), key, datetime.datetime.now(datetime.UTC))
    (tmp_path / "chain.pem").write_bytes(making.certificate_pem(leaf))
    (tmp_path / "key.pem").write_bytes(making.key_pem(key))
    context = server_context(pending)
    context.load_cert_chain(tmp_path / "chain.pem", tmp_path / "key.pem")
    return context


def validator(protocols: list[str]) -> ssl.SSLContext:
    """Return a client context offering protocols, reading whatever certificate it is shown, as a validator does."""
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    context.set_alpn_protocols(protocols)
    return context


def shaken(
    server: ssl.SSLContext,
    client: ssl.SSLContext,
    name: str,
    *,
    split: bool = False,
) -> ssl.SSLObject:
    """Return the client's side of a handshake carried in memory, the ClientHello split in two where asked."""
    to_server, to_client = ssl.MemoryBIO(), ssl.MemoryBIO()
    client_side = client.wrap_bio(to_client, to_server, server_hostname=name)
    server_side = server.wrap_bio(to_server, to_client, server_side=True)
    held = b""
    for round_number in range(ROUNDS):
        try:
            client_side.do_handshake()
        except ssl.SSLWantReadError:
            pass
        else:
            return client_side
        if split and round_number == 0:
            held = to_server.read()
            to_server.write(held[:20])
        try:
            server_side.do_handshake()
        except ssl.SSLWantReadError:
            if held:
                to_server.write(held[20:])
                held = b""
    msg = "the handshake did not finish"
    raise AssertionError(msg)


def presented(side: ssl.SSLObject) -> x509.Certificate:
    """Return the certificate the server presented."""
    der = side.getpeercert(binary_form=True)
    assert der is not None
    return x509.load_der_x509_certificate(der)


def test_a_challenge_certificate_carries_the_digest_of_the_key_authorization_for_its_name() -> None:
    certificate, key = alpn.challenge_certificate(NAME, KEY_AUTHORIZATION)
    assert making.covered(certificate) == {NAME}
    extension = certificate.extensions.get_extension_for_oid(alpn.ACME_IDENTIFIER)
    assert extension.critical
    digest = hashlib.sha256(KEY_AUTHORIZATION.encode()).digest()
    assert extension.value.public_bytes() == bytes([0x04, 32]) + digest
    assert making.matches(certificate, key)


def test_a_challenge_is_answered_only_for_acme_tls_alone_and_a_pending_name(tmp_path: pathlib.Path) -> None:
    pending = alpn.Challenges(tmp_path)
    assert pending.context_for(hello.Hello(NAME, (alpn.ACME_TLS,))) is None
    pending.present(NAME, KEY_AUTHORIZATION)
    assert pending.context_for(hello.Hello(NAME, (alpn.ACME_TLS,))) is not None
    assert pending.context_for(hello.Hello(NAME, (alpn.ACME_TLS, alpn.HTTP_1_1))) is None
    assert pending.context_for(hello.Hello(None, (alpn.ACME_TLS,))) is None
    assert pending.context_for(hello.Hello("other.example", (alpn.ACME_TLS,))) is None
    assert list(tmp_path.iterdir()) == []
    pending.withdraw(NAME)
    pending.withdraw(NAME)
    assert pending.context_for(hello.Hello(NAME, (alpn.ACME_TLS,))) is None


@pytest.mark.parametrize("split", [False, True])
def test_the_validator_is_shown_the_challenge_and_speaks_acme_tls(
    tmp_path: pathlib.Path,
    *,
    split: bool,
) -> None:
    pending = alpn.Challenges(tmp_path)
    pending.present(NAME, KEY_AUTHORIZATION)
    side = shaken(served_context(tmp_path, pending), validator([alpn.ACME_TLS]), NAME, split=split)
    assert side.selected_alpn_protocol() == alpn.ACME_TLS
    assert presented(side).extensions.get_extension_for_oid(alpn.ACME_IDENTIFIER).critical


def test_every_other_connection_is_shown_the_server_certificate(tmp_path: pathlib.Path) -> None:
    pending = alpn.Challenges(tmp_path)
    pending.present(NAME, KEY_AUTHORIZATION)
    served = served_context(tmp_path, pending)
    browsing = shaken(served, validator([alpn.HTTP_1_1]), NAME)
    assert browsing.selected_alpn_protocol() == alpn.HTTP_1_1
    with pytest.raises(x509.ExtensionNotFound):
        presented(browsing).extensions.get_extension_for_oid(alpn.ACME_IDENTIFIER)
    elsewhere = shaken(served, validator([alpn.ACME_TLS]), "other.example")
    with pytest.raises(x509.ExtensionNotFound):
        presented(elsewhere).extensions.get_extension_for_oid(alpn.ACME_IDENTIFIER)
