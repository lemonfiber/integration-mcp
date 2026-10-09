# Copyright (c) 2026 NightWorksIO
"""HTTP-01 (RFC 8555 §8.3): port 80, open only while an order is pending.

It answers `GET /.well-known/acme-challenge/<token>` for a pending token with
its key authorization, and `404` to everything else, with no redirect. It is
the one thing the server ever answers in plain HTTP, and it closes once the
order is settled.
"""

import socket
import socketserver
import threading
from typing import TYPE_CHECKING, Final, override

if TYPE_CHECKING:
    from collections.abc import Mapping

PORT: Final = 80
"""The port the authority asks on, which RFC 8555 fixes."""
EVERYWHERE: Final = "::"
LONGEST_LINE: Final = 8192
"""The longest request or header line read; a longer one ends the request."""
MOST_HEADERS: Final = 100
"""The most header lines read before answering."""
REQUEST_PARTS: Final = 3
"""A request line's method, target and version."""
FOUND: Final = b"200 OK"
NOT_FOUND: Final = b"404 Not Found"


def answer_of(tokens: Mapping[str, str], request_line: bytes) -> tuple[bytes, bytes]:
    """Return the status and the body a request line is answered with."""
    parts = request_line.decode("latin-1").split()
    answer = tokens.get(parts[1]) if len(parts) == REQUEST_PARTS and parts[0] == "GET" else None
    return (NOT_FOUND, b"") if answer is None else (FOUND, answer.encode())


def handler_of(tokens: Mapping[str, str]) -> type[socketserver.StreamRequestHandler]:
    """Return a handler answering each pending token's path with its key authorization, and nothing else."""

    class Answer(socketserver.StreamRequestHandler):
        """One request on port 80, answered and closed."""

        timeout = 10

        @override
        def handle(self) -> None:
            """Read the request line and the headers, then answer."""
            request_line = self.rfile.readline(LONGEST_LINE)
            for _ in range(MOST_HEADERS):
                if self.rfile.readline(LONGEST_LINE).strip() == b"":
                    break
            status, body = answer_of(tokens, request_line)
            self.wfile.write(
                b"HTTP/1.1 " + status + b"\r\nContent-Type: text/plain\r\nConnection: close\r\n"
                b"Content-Length: " + str(len(body)).encode() + b"\r\n\r\n" + body,
            )

    return Answer


class DualStack(socketserver.ThreadingTCPServer):
    """A server on every address, IPv6 and IPv4 alike."""

    address_family = socket.AF_INET6
    allow_reuse_address = True
    daemon_threads = True

    @override
    def server_bind(self) -> None:
        """Take IPv4 connections on the IPv6 socket as well."""
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()


class Responder:
    """Port 80 for as long as an order is pending."""

    def __init__(self, tokens: Mapping[str, str]) -> None:
        """Hold the pending tokens' paths and key authorizations."""
        self._tokens = dict(tokens)
        self._server: DualStack | None = None

    def open(self) -> None:
        """Open port 80 and answer in a thread of its own."""
        self._server = DualStack((EVERYWHERE, PORT), handler_of(self._tokens))
        threading.Thread(target=self._server.serve_forever, name="http-01", daemon=True).start()

    def close(self) -> None:
        """Close port 80."""
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
            self._server = None
