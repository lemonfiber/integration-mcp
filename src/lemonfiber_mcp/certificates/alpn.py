# Copyright (c) 2026 NightWorksIO
"""TLS-ALPN-01 (RFC 8737), answered on the serving port while it serves.

Each connection's ClientHello is read before the handshake begins. One asking
for `acme-tls/1` and nothing else, for a name with a challenge pending, is
answered from that challenge's own context; every other is handed on to the
server's context untouched, so serving never pauses for a renewal.
"""

import datetime
import hashlib
import secrets
import ssl
import threading
from typing import TYPE_CHECKING, Final, cast, override

from cryptography import x509

from lemonfiber_mcp.certificates import hello, making, state
from lemonfiber_mcp.certificates.settings import KeyType

if TYPE_CHECKING:
    import pathlib

ACME_TLS: Final = "acme-tls/1"
HTTP_1_1: Final = "http/1.1"
ACME_IDENTIFIER: Final = x509.ObjectIdentifier("1.3.6.1.5.5.7.1.31")
"""The `id-pe-acmeIdentifier` extension a challenge certificate carries the key authorization's digest in."""
OCTET_STRING: Final = 0x04
CHALLENGE_LIFETIME: Final = datetime.timedelta(days=1)


def challenge_certificate(name: str, key_authorization: str) -> tuple[x509.Certificate, making.PrivateKey]:
    """Return the certificate answering a TLS-ALPN-01 challenge for a name, and its key."""
    key = making.generated(KeyType.EC_P256)
    digest = hashlib.sha256(key_authorization.encode()).digest()
    now = datetime.datetime.now(datetime.UTC)
    subject = making.named(f"lemonfiber MCP challenge for {name}")
    certificate = (
        making.builder(subject, key, CHALLENGE_LIFETIME, now)
        .issuer_name(subject)
        .add_extension(x509.SubjectAlternativeName([x509.DNSName(name)]), critical=False)
        .add_extension(
            x509.UnrecognizedExtension(ACME_IDENTIFIER, bytes([OCTET_STRING, len(digest)]) + digest),
            critical=True,
        )
        .sign(key, making.hashes.SHA256())
    )
    return certificate, key


def answering_context(
    certificate: x509.Certificate,
    key: making.PrivateKey,
    held: pathlib.Path,
) -> ssl.SSLContext:
    """Return a server context presenting a challenge certificate, speaking `acme-tls/1` alone.

    The certificate and its key pass through `held`, the state directory a
    read-only container still writes to, only while they are loaded.
    """
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_alpn_protocols([ACME_TLS])
    named = secrets.token_hex(8)
    chain, private_key = held / f"{named}-chain.pem", held / f"{named}-key.pem"
    try:
        state.write(chain, making.certificate_pem(certificate))
        state.write(private_key, making.key_pem(key))
        context.load_cert_chain(chain, private_key)
    finally:
        chain.unlink(missing_ok=True)
        private_key.unlink(missing_ok=True)
    return context


class Challenges:
    """The TLS-ALPN-01 answers pending, by name, shared by the thread ordering and the server answering."""

    def __init__(self, held: pathlib.Path) -> None:
        """Hold no answer yet, and where an answer's certificate passes through while it is loaded."""
        self._held = held
        self._lock = threading.Lock()
        self._contexts: dict[str, ssl.SSLContext] = {}

    def present(self, name: str, key_authorization: str) -> None:
        """Answer a name's challenge with the certificate its key authorization makes."""
        context = answering_context(*challenge_certificate(name, key_authorization), self._held)
        with self._lock:
            self._contexts[name] = context

    def withdraw(self, name: str) -> None:
        """Stop answering a name's challenge."""
        with self._lock:
            self._contexts.pop(name, None)

    def context_for(self, asked: hello.Hello) -> ssl.SSLContext | None:
        """Return the context answering a ClientHello, where it asks for `acme-tls/1` alone for a pending name."""
        if asked.protocols != (ACME_TLS,) or asked.server_name is None:
            return None
        with self._lock:
            return self._contexts.get(asked.server_name)


class Peeking(ssl.SSLObject):
    """A server-side TLS object that reads the ClientHello before its handshake, to choose the context answering it."""

    answers: Challenges | None = None
    """The pending TLS-ALPN-01 answers, until the ClientHello has been read."""
    arriving: ssl.MemoryBIO | None = None
    """Where the ClientHello arrives, until it has been read."""

    @override
    def do_handshake(self) -> None:
        """Choose the context from the ClientHello once it has all arrived, then shake hands."""
        if self.arriving is not None and self.answers is not None:
            arrived = self.arriving.read()
            self.arriving.write(arrived)
            asked = hello.read(arrived)
            if isinstance(asked, hello.Incomplete):
                raise ssl.SSLWantReadError
            self.arriving = None
            answering = self.answers.context_for(asked)
            if answering is not None:
                self.context = answering
        super().do_handshake()


class Answering(ssl.SSLContext):
    """The serving context, whose connections answer a pending TLS-ALPN-01 challenge where one asks for it."""

    sslobject_class = Peeking
    pending: Challenges | None = None

    @override
    def wrap_bio(
        self,
        incoming: ssl.MemoryBIO,
        outgoing: ssl.MemoryBIO,
        server_side: bool = False,
        server_hostname: str | bytes | None = None,
        session: ssl.SSLSession | None = None,
    ) -> ssl.SSLObject:
        """Wrap a connection, holding where its ClientHello arrives so it can be read before the handshake."""
        wrapped = cast("Peeking", super().wrap_bio(incoming, outgoing, server_side, server_hostname, session))
        wrapped.answers = self.pending
        wrapped.arriving = incoming
        return wrapped
