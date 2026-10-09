# Copyright (c) 2026 NightWorksIO
"""Stand-ins for what a DNS provider talks to: an HTTP API, and a DNS server that takes signed updates."""

import json
import socketserver
import threading
import time
import urllib.parse
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, Self, cast, override

import dns.exception
import dns.message
import dns.opcode
import dns.rcode
import dns.rdatatype
import dns.rrset
import dns.tsig
import dns.update

if TYPE_CHECKING:
    import socket
    from collections.abc import Callable, Iterable

    from dns.name import Name
    from dns.rdata import Rdata

LOOPBACK: Final = "127.0.0.1"
JSON: Final = {"Content-Type": "application/json"}
LONGEST: Final = 65535
SILENCE: Final = 1.0
"""How long a silent stand-in holds a connection without answering."""


@dataclass(frozen=True, slots=True)
class Asked:
    """One request the stand-in API was sent."""

    method: str
    path: str
    query: dict[str, list[str]]
    headers: dict[str, str]
    body: bytes

    def json(self) -> object:
        """Return the body read as JSON."""
        return json.loads(self.body)

    def form(self) -> dict[str, list[str]]:
        """Return the body read as a form."""
        return urllib.parse.parse_qs(self.body.decode())


type Answer = tuple[int, dict[str, str], bytes]
"""A status, headers and a body."""


def answered(status: int, document: object) -> Answer:
    """Return a JSON answer."""
    return status, JSON, json.dumps(document).encode()


def routed(routes: dict[tuple[str, str], Answer]) -> Callable[[Asked], Answer]:
    """Return an answer by method and path, `404` for any other."""

    def answer(asked: Asked) -> Answer:
        return routes.get((asked.method, asked.path), (404, JSON, b"{}"))

    return answer


class HttpStandIn:
    """An HTTP API on a loopback port, answering each request as a function says and keeping what it was sent."""

    def __init__(self, answer: Callable[[Asked], Answer]) -> None:
        """Hold how each request is answered."""
        self.asked: list[Asked] = []
        stand_in = self

        class Handler(socketserver.StreamRequestHandler):
            @override
            def handle(self) -> None:
                method, target, _ = self.rfile.readline().decode().split(" ", 2)
                headers: dict[str, str] = {}
                while line := self.rfile.readline().decode().strip():
                    name, _, value = line.partition(":")
                    headers[name.strip().lower()] = value.strip()
                body = self.rfile.read(int(headers.get("content-length", "0")))
                parts = urllib.parse.urlsplit(target)
                asked = Asked(method, parts.path, urllib.parse.parse_qs(parts.query), headers, body)
                stand_in.asked.append(asked)
                status, sent, content = answer(asked)
                lines = [f"HTTP/1.1 {status} Answer", f"Content-Length: {len(content)}", "Connection: close"]
                lines += [f"{name}: {value}" for name, value in sent.items()]
                self.wfile.write(("\r\n".join(lines) + "\r\n\r\n").encode() + content)

        self._server = socketserver.ThreadingTCPServer((LOOPBACK, 0), Handler)
        self._server.daemon_threads = True

    @property
    def url(self) -> str:
        """Return where the stand-in answers."""
        return f"http://{LOOPBACK}:{self._server.server_address[1]}"

    def __enter__(self) -> Self:
        """Start answering."""
        threading.Thread(target=self._server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *_: object) -> None:
        """Stop answering."""
        self._server.shutdown()
        self._server.server_close()


@dataclass
class DnsStandIn:
    """A DNS server on a loopback port: it answers from its records, and takes updates signed with its key."""

    records: dict[tuple[str, int], list[str]] = field(default_factory=dict[tuple[str, int], list[str]])
    keyring: dict[Name, dns.tsig.Key] | None = None
    updates: list[dns.message.Message] = field(default_factory=list[dns.message.Message])
    port: int = 0
    refusing: bool = False
    """Whether updates are answered `REFUSED` rather than applied."""
    silent: bool = False
    """Whether what comes over TCP is taken and never answered."""
    _servers: list[socketserver.BaseServer] = field(default_factory=list[socketserver.BaseServer])

    def add(self, name: str, kind: str, *values: str) -> None:
        """Answer a name's records of a kind with these values."""
        self.records.setdefault((name.lower(), dns.rdatatype.from_text(kind)), []).extend(values)

    def answer(self, wire: bytes) -> bytes:
        """Return the answer to one message: a query from the records or the name's CNAME, an update applied."""
        message = dns.message.from_wire(wire, keyring=self.keyring)
        response = dns.message.make_response(message)
        if message.opcode() == dns.opcode.UPDATE:
            self.updates.append(message)
            if self.refusing:
                response.set_rcode(dns.rcode.REFUSED)
                return response.to_wire()
            self._apply(cast("dns.update.UpdateMessage", message).update)
            return response.to_wire()
        question = message.question[0]
        name = str(question.name).lower()
        values = self.records.get((name, question.rdtype), [])
        if values:
            response.answer.append(dns.rrset.from_text(question.name, 60, "IN", question.rdtype, *values))
        elif aliased := self.records.get((name, dns.rdatatype.CNAME), []):
            response.answer.append(
                dns.rrset.from_text(question.name, 60, "IN", dns.rdatatype.CNAME, *aliased),
            )
        return response.to_wire()

    def _apply(self, changes: list[dns.rrset.RRset]) -> None:
        for change in changes:
            key = (str(change.name).lower(), change.rdtype)
            texts = [rdata.to_text() for rdata in cast("Iterable[Rdata]", change)]
            if change.deleting is None:
                self.records.setdefault(key, []).extend(texts)
            else:
                self.records[key] = [held for held in self.records.get(key, []) if held not in texts]

    def __enter__(self) -> Self:
        """Answer over UDP and TCP on one port."""
        stand_in = self

        class Udp(socketserver.BaseRequestHandler):
            @override
            def handle(self) -> None:
                data, sock = cast("tuple[bytes, socket.socket]", self.request)
                sock.sendto(stand_in.answer(data), self.client_address)

        class Tcp(socketserver.StreamRequestHandler):
            @override
            def handle(self) -> None:
                if stand_in.silent:
                    time.sleep(SILENCE)
                    return
                length = int.from_bytes(self.rfile.read(2))
                try:
                    answer = stand_in.answer(self.rfile.read(length))
                except dns.exception.DNSException:
                    return
                self.wfile.write(len(answer).to_bytes(2) + answer)

        self._servers, self.port = paired(Udp, Tcp)
        for server in self._servers:
            threading.Thread(target=server.serve_forever, daemon=True).start()
        return self

    def __exit__(self, *_: object) -> None:
        """Stop answering."""
        for server in self._servers:
            server.shutdown()
            server.server_close()


def paired(
    udp: type[socketserver.BaseRequestHandler],
    tcp: type[socketserver.BaseRequestHandler],
) -> tuple[list[socketserver.BaseServer], int]:
    """Return a UDP and a TCP server on one free loopback port, and the port, trying another where it is taken."""
    while True:
        over_udp = socketserver.ThreadingUDPServer((LOOPBACK, 0), udp)
        port = int(over_udp.server_address[1])
        try:
            over_tcp = socketserver.ThreadingTCPServer((LOOPBACK, port), tcp)
        except OSError:
            over_udp.server_close()
            continue
        return [over_udp, over_tcp], port


def keyring_of(name: str, key: str, algorithm: str = "hmac-sha256.") -> dict[Name, dns.tsig.Key]:
    """Return a keyring holding one TSIG key, which signs with one algorithm alone."""
    held = dns.tsig.Key(name, key, algorithm)
    return {held.name: held}
