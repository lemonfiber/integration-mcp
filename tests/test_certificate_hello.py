# Copyright (c) 2026 NightWorksIO
"""A ClientHello read before the handshake: the name it is for and the protocols it offers, or nothing."""

import ssl

import pytest

from lemonfiber_mcp.certificates import hello

ADDRESS = "127.0.0.1"
"""What a client connects to without naming a host, which sends no server name."""


def client_hello(name: str, protocols: list[str]) -> bytes:
    """Return the first record a TLS client sends, asking for a name and offering protocols."""
    context = ssl.create_default_context()
    if protocols:
        context.set_alpn_protocols(protocols)
    incoming, outgoing = ssl.MemoryBIO(), ssl.MemoryBIO()
    client = context.wrap_bio(incoming, outgoing, server_hostname=name)
    with pytest.raises(ssl.SSLWantReadError):
        client.do_handshake()
    return outgoing.read()


def test_the_name_and_the_protocols_are_read_in_the_clients_order() -> None:
    asked = hello.read(client_hello("mcp.home.example", ["acme-tls/1", "http/1.1"]))
    assert asked == hello.Hello("mcp.home.example", ("acme-tls/1", "http/1.1"))


def test_a_hello_without_a_name_or_protocols_asks_for_neither() -> None:
    assert hello.read(client_hello(ADDRESS, [])) == hello.NOTHING_ASKED


def test_a_name_is_read_in_lower_case() -> None:
    asked = hello.read(client_hello("MCP.Home.Example", []))
    assert isinstance(asked, hello.Hello)
    assert asked.server_name == "mcp.home.example"


@pytest.mark.parametrize("cut", [0, 1, 4, 5, 60])
def test_a_hello_not_yet_whole_is_waited_for(cut: int) -> None:
    whole = client_hello("mcp.home.example", ["acme-tls/1"])
    assert hello.read(whole[:cut]) is hello.INCOMPLETE


@pytest.mark.parametrize("data", [b"GET /", b"GET / HTTP/1.1\r\n\r\n"])
def test_what_is_not_a_handshake_asks_for_nothing(data: bytes) -> None:
    assert hello.read(data) == hello.NOTHING_ASKED


def test_a_read_past_the_end_is_refused() -> None:
    reader = hello.Reader(b"ab")
    with pytest.raises(ValueError, match=r"^past the end$"):
        reader.take(3)


def test_a_handshake_that_is_not_a_client_hello_asks_for_nothing() -> None:
    assert hello.read(bytes([22, 3, 3, 0, 4, 2, 0, 0, 0])) == hello.NOTHING_ASKED


def test_a_client_hello_that_cannot_be_read_asks_for_nothing() -> None:
    assert hello.read(bytes([22, 3, 3, 0, 4, 1, 0, 0, 9])) == hello.NOTHING_ASKED


def test_a_client_hello_with_no_extensions_asks_for_nothing() -> None:
    body = bytes([3, 3]) + bytes(32) + bytes([0]) + bytes([0, 2, 0, 0x2F]) + bytes([1, 0])
    message = bytes([1]) + len(body).to_bytes(3) + body
    record = bytes([22, 3, 1]) + len(message).to_bytes(2) + message
    assert hello.read(record) == hello.NOTHING_ASKED


def test_a_server_name_of_another_kind_is_not_a_host_name() -> None:
    names = bytes([1, 0, 1, 0x61])
    extension = hello.Reader(len(names).to_bytes(2) + names)
    assert hello.server_name(extension) is None
