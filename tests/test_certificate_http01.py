# Copyright (c) 2026 NightWorksIO
"""HTTP-01 on port 80: the pending token's answer, `404` for anything else, and closed once the order is settled."""

import http.client
import socket
from typing import TYPE_CHECKING, Final

import pytest

from lemonfiber_mcp.certificates import http01

if TYPE_CHECKING:
    from collections.abc import Iterator

CHALLENGE_PATH: Final = "/.well-known/acme-challenge/abc"
KEY_AUTHORIZATION: Final = "abc.thumbprint"


def free_port() -> int:
    """Return a port nothing listens on."""
    with socket.socket(socket.AF_INET6) as probe:
        probe.bind(("::1", 0))
        return int(probe.getsockname()[1])


@pytest.fixture
def port(monkeypatch: pytest.MonkeyPatch) -> Iterator[int]:
    """Open the responder on a free port standing in for 80, and close it after."""
    chosen = free_port()
    monkeypatch.setattr(http01, "PORT", chosen)
    responder = http01.Responder({CHALLENGE_PATH: KEY_AUTHORIZATION})
    responder.open()
    yield chosen
    responder.close()
    responder.close()


def asked(port: int, method: str, path: str, host: str = "127.0.0.1") -> tuple[int, bytes]:
    """Return the status and body a request on the responder is answered with."""
    connection = http.client.HTTPConnection(host, port, timeout=5)
    try:
        connection.request(method, path)
        answer = connection.getresponse()
        return answer.status, answer.read()
    finally:
        connection.close()


def test_the_pending_token_is_answered_with_its_key_authorization(port: int) -> None:
    assert asked(port, "GET", CHALLENGE_PATH) == (200, KEY_AUTHORIZATION.encode())
    assert asked(port, "GET", CHALLENGE_PATH, host="::1") == (200, KEY_AUTHORIZATION.encode())


@pytest.mark.parametrize(
    ("method", "path"),
    [("GET", "/"), ("GET", "/.well-known/acme-challenge/other"), ("POST", CHALLENGE_PATH)],
)
def test_anything_else_is_not_found_and_never_redirected(port: int, method: str, path: str) -> None:
    assert asked(port, method, path) == (404, b"")


def test_a_request_line_that_is_not_one_is_not_found() -> None:
    assert http01.answer_of({CHALLENGE_PATH: KEY_AUTHORIZATION}, b"nonsense\r\n") == (http01.NOT_FOUND, b"")


def test_port_80_is_closed_once_the_order_is_settled(monkeypatch: pytest.MonkeyPatch) -> None:
    chosen = free_port()
    monkeypatch.setattr(http01, "PORT", chosen)
    responder = http01.Responder({CHALLENGE_PATH: KEY_AUTHORIZATION})
    responder.open()
    responder.close()
    with pytest.raises(ConnectionRefusedError):
        asked(chosen, "GET", CHALLENGE_PATH)


def test_a_request_with_more_headers_than_are_read_is_still_answered(port: int) -> None:
    with socket.create_connection(("127.0.0.1", port), timeout=5) as connection:
        headers = "".join(f"X-{number}: {number}\r\n" for number in range(http01.MOST_HEADERS + 5))
        connection.sendall(f"GET {CHALLENGE_PATH} HTTP/1.1\r\n{headers}\r\n".encode())
        assert connection.recv(1024).startswith(b"HTTP/1.1 200 OK")
