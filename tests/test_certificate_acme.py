# Copyright (c) 2026 NightWorksIO
"""The `acme` mode against Pebble: first issuance by each challenge, renewal, a binding, and an order that fails.

Pebble and its challenge test server are started by `scripts/pebble.sh`, which
says where they are; without them these tests are skipped. Every name resolves
to this machine, where TLS-ALPN-01 is answered on 5001 and HTTP-01 on 5002, and
each test asks for a name of its own, answered on a loopback address of its own
where Pebble reaches this machine's loopback.
"""

import asyncio
import contextlib
import datetime
import json
import logging
import os
import pathlib
import random
import re
import secrets
import socket
import socketserver
import stat
import threading
import types
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, cast, override

import anyio
import pytest
import requests
from acme import client, errors, messages
from cryptography.hazmat.primitives.asymmetric import ec
from josepy.jwk import JWKEC

from lemonfiber_mcp.certificates import acme, acme_protocol, alpn, hello, http01, making, state
from lemonfiber_mcp.certificates.acme_settings import Acme, Binding, Challenge
from lemonfiber_mcp.certificates.manager import server_context
from lemonfiber_mcp.certificates.modes import CertificateError, Served
from lemonfiber_mcp.certificates.settings import KeyType, Mode, Tls

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Generator, Iterator

NAMES: Final = ("mcp.acme.test",)
TLS_PORT: Final = 5001
HTTP_PORT: Final = 5002
"""The ports Pebble validates TLS-ALPN-01 and HTTP-01 on, the same for every name."""
EVERYWHERE: Final = "0.0.0.0"  # The tests' TLS-ALPN-01 server, reached by Pebble from wherever it runs.
LOOPBACK: Final = "127.0.0.1"
NOW: Final = datetime.datetime(2026, 10, 9, tzinfo=datetime.UTC)
PEBBLE: Final = os.environ.get("PEBBLE_DIRECTORY", "")
ROOTS: Final = os.environ.get("PEBBLE_ROOTS", "")
CHALLTESTSRV: Final = os.environ.get("PEBBLE_CHALLTESTSRV", "")
"""Where the challenge test server takes the records it answers Pebble's lookups with."""
OWN_ADDRESSES: Final = os.environ.get("PEBBLE_ADDRESSES") == "own"
"""Whether each test answers on a loopback address of its own, where Pebble reaches this machine's loopback."""
needs_pebble = pytest.mark.skipif(not PEBBLE, reason="Pebble is not running: start it with scripts/pebble.sh")


@dataclass(frozen=True, slots=True)
class Place:
    """Where one test answers the authority: a name no other test asks for, and the address it listens on."""

    name: str
    address: str

    @property
    def names(self) -> tuple[str, ...]:
        """Return the names the test's certificate is for."""
        return (self.name,)

    @property
    def reached(self) -> str:
        """Return the address the test's own listeners are reached at."""
        return LOOPBACK if self.address == EVERYWHERE else self.address

    @property
    def dual_stack(self) -> str:
        """Return the address an IPv6 listener taking IPv4 too binds to, to listen where this test does."""
        return http01.EVERYWHERE if self.address == EVERYWHERE else f"::ffff:{self.address}"


def free_loopback() -> str:
    """Return a loopback address on which both challenge ports are free."""
    while True:
        address = f"127.{secrets.randbelow(254) + 1}.{secrets.randbelow(256)}.{secrets.randbelow(254) + 1}"
        try:
            for port in (TLS_PORT, HTTP_PORT):
                with socket.create_server((address, port)):
                    pass
        except OSError:
            continue
        return address


def told(path: str, record: dict[str, str | list[str]]) -> None:
    """Tell the challenge test server a record to answer with, or to forget."""
    requests.post(f"{CHALLTESTSRV}/{path}", json=record, timeout=5).raise_for_status()


@pytest.fixture
def place() -> Iterator[Place]:
    """Return a name of this test's own, and where it answers for it.

    Parallel runs, as a mutation run's workers are, share Pebble and its ports.
    Where Pebble reaches this machine's loopback, each test listens on a loopback
    address of its own and the challenge test server resolves the test's name to
    it, so no test answers another's challenge. Elsewhere the tests share this
    machine's address and run one at a time.
    """
    name = f"t{secrets.token_hex(6)}.acme.test"
    if not OWN_ADDRESSES:
        yield Place(name, EVERYWHERE)
        return
    address = free_loopback()
    told("add-a", {"host": name, "addresses": [address]})
    yield Place(name, address)
    told("clear-a", {"host": name})


def tls_of(root: pathlib.Path, names: tuple[str, ...] = NAMES) -> Tls:
    """Return settings for the `acme` mode for some names, keeping state under `root`."""
    return Tls(Mode.ACME, names, None, None, KeyType.EC_P256, state.kept(root / "state"))


def settings_of(challenge: Challenge = Challenge.TLS_ALPN_01, *, bound: bool | None = None) -> Acme:
    """Return settings speaking to Pebble; to the one requiring a binding where `bound` is given, with it where true."""
    roots = pathlib.Path(ROOTS) if ROOTS else None
    if bound is None:
        return Acme(PEBBLE, roots, "mailto:operator@acme.test", None, challenge, None)
    binding = (
        Binding(os.environ["PEBBLE_EAB_KID"], pathlib.Path(os.environ["PEBBLE_EAB_HMAC_FILE"]))
        if bound
        else None
    )
    return Acme(os.environ["PEBBLE_EAB_DIRECTORY"], roots, None, binding, challenge, None)


def source_of(
    root: pathlib.Path,
    settings: Acme,
    pending: alpn.Challenges | None = None,
    names: tuple[str, ...] = NAMES,
) -> acme.AcmeSource:
    """Return the `acme` source for some names, its jitter fixed so a wait is the wait itself."""
    return acme.AcmeSource(tls_of(root, names), settings, pending or alpn.Challenges(root), random.Random(0))


@pytest.fixture
async def answering(tmp_path: pathlib.Path, place: Place) -> AsyncIterator[alpn.Challenges]:
    """Serve TLS on 5001 where the test answers, as the server does, answering TLS-ALPN-01 for whatever is pending."""
    pending = alpn.Challenges(tmp_path)
    key = making.generated(KeyType.EC_P256)
    state.write(tmp_path / "standing.pem", making.certificate_pem(making.pinned(place.names, key, NOW)))
    state.write(tmp_path / "standing-key.pem", making.key_pem(key))
    context = server_context(pending)
    context.load_cert_chain(tmp_path / "standing.pem", tmp_path / "standing-key.pem")

    async def closed(_: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        writer.close()

    server = await asyncio.start_server(closed, place.address, TLS_PORT, ssl=context)
    async with server:
        yield pending


async def obtained(source: acme.AcmeSource, now: datetime.datetime) -> Served:
    """Obtain in a thread, as the server does, while this loop answers the authority."""
    return await anyio.to_thread.run_sync(source.obtain, now)


def making_covered(served: Served) -> set[object]:
    """Return every name a served certificate covers."""
    return set(making.covered(served.leaf))


def acme_hello(name: str) -> hello.Hello:
    """Return what a validator's ClientHello asks for, for a name."""
    return hello.Hello(name, (alpn.ACME_TLS,))


def closed(address: str, port: int) -> bool:
    """Tell whether nothing listens on a port."""
    try:
        socket.create_connection((address, port), timeout=2).close()
    except ConnectionRefusedError:
        return True
    return False


def private(path: pathlib.Path) -> bool:
    """Tell whether a file is readable by this user alone."""
    return stat.S_IMODE(path.stat().st_mode) == state.FILE_MODE


@needs_pebble
@pytest.mark.anyio
async def test_the_first_certificate_is_issued_by_tls_alpn_01_and_kept(
    tmp_path: pathlib.Path,
    place: Place,
    answering: alpn.Challenges,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    source = source_of(tmp_path, settings_of(), answering, place.names)
    now = datetime.datetime.now(datetime.UTC)
    assert source.first(now).standing_in
    served = await obtained(source, now)
    assert not served.standing_in
    assert making_covered(served) == set(place.names)
    assert "agreeing to the authority's terms: data:text/plain" in caplog.text
    account = next((tmp_path / "state" / acme.ACCOUNT).iterdir())
    assert private(account / acme.ACCOUNT_KEY)
    assert private(account / acme.ACCOUNT_RECORD)
    assert private(served.key)
    assert source.obtain(now) == served
    assert source_of(tmp_path, settings_of(), names=place.names).first(now).fingerprint == served.fingerprint
    assert answering.context_for(acme_hello(place.name)) is None


@needs_pebble
@pytest.mark.anyio
async def test_the_first_certificate_is_issued_by_http_01_on_port_80_opened_for_it(
    tmp_path: pathlib.Path,
    place: Place,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(http01, "PORT", HTTP_PORT)
    monkeypatch.setattr(http01, "EVERYWHERE", place.dual_stack)
    source = source_of(tmp_path, settings_of(Challenge.HTTP_01), names=place.names)
    served = await obtained(source, datetime.datetime.now(datetime.UTC))
    assert making_covered(served) == set(place.names)
    assert closed(place.reached, HTTP_PORT)


@needs_pebble
@pytest.mark.anyio
async def test_the_authority_is_asked_when_to_renew(
    tmp_path: pathlib.Path,
    place: Place,
    answering: alpn.Challenges,
) -> None:
    source = source_of(tmp_path, settings_of(), answering, place.names)
    first = await obtained(source, datetime.datetime.now(datetime.UTC))
    due = cast("datetime.datetime", source.due(first))
    assert first.leaf.not_valid_before_utc < due < first.expires


@needs_pebble
@pytest.mark.anyio
async def test_a_certificate_is_renewed_when_the_authority_says(
    tmp_path: pathlib.Path,
    place: Place,
    answering: alpn.Challenges,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    said = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=2)

    def saying(_: client.ClientV2, __: bytes) -> tuple[datetime.datetime | None, datetime.datetime]:
        return said, said - datetime.timedelta(days=1)

    monkeypatch.setattr(client.ClientV2, "renewal_time", saying)
    source = source_of(tmp_path, settings_of(), answering, place.names)
    first = await obtained(source, datetime.datetime.now(datetime.UTC))
    assert source.due(first) == said
    assert await obtained(source, said - datetime.timedelta(seconds=1)) == first
    renewed = await obtained(source, said)
    assert renewed.fingerprint != first.fingerprint


@needs_pebble
@pytest.mark.anyio
async def test_a_certificate_is_renewed_with_a_third_left_where_the_authority_says_nothing(
    tmp_path: pathlib.Path,
    place: Place,
    answering: alpn.Challenges,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def silent(_: client.ClientV2, __: bytes) -> tuple[datetime.datetime | None, datetime.datetime]:
        return None, datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=6)

    monkeypatch.setattr(client.ClientV2, "renewal_time", silent)
    source = source_of(tmp_path, settings_of(), answering, place.names)
    first = await obtained(source, datetime.datetime.now(datetime.UTC))
    lifetime = first.leaf.not_valid_after_utc - first.leaf.not_valid_before_utc
    assert source.due(first) == first.leaf.not_valid_after_utc - lifetime / 3


@needs_pebble
def test_an_authority_requiring_a_binding_refuses_a_start_without_one(
    tmp_path: pathlib.Path,
    place: Place,
) -> None:
    source = source_of(tmp_path, settings_of(bound=False), names=place.names)
    with pytest.raises(CertificateError, match="LEMONFIBER_ACME_EAB_KID and LEMONFIBER_ACME_EAB_HMAC_FILE"):
        source.first(NOW)


@needs_pebble
@pytest.mark.anyio
async def test_an_authority_requiring_a_binding_issues_with_one(
    tmp_path: pathlib.Path,
    place: Place,
    answering: alpn.Challenges,
) -> None:
    source = source_of(tmp_path, settings_of(bound=True), answering, place.names)
    now = datetime.datetime.now(datetime.UTC)
    assert source.first(now).standing_in
    assert not (await obtained(source, now)).standing_in


@needs_pebble
@pytest.mark.anyio
async def test_an_order_that_fails_is_tried_again_after_a_minute_then_two(
    tmp_path: pathlib.Path,
    place: Place,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(http01, "PORT", HTTP_PORT + 1000)
    monkeypatch.setattr(http01, "EVERYWHERE", place.dual_stack)
    source = source_of(tmp_path, settings_of(Challenge.HTTP_01), names=place.names)
    now = datetime.datetime.now(datetime.UTC)
    with pytest.raises(
        CertificateError,
        match=f"could not validate {re.escape(place.name)}: urn:ietf:params:acme:error",
    ):
        await obtained(source, now)
    jitter = random.Random(0)
    first_wait = acme.FIRST_RETRY * (1 + jitter.uniform(-acme.JITTER, acme.JITTER))
    assert source.waiting_until == now + first_wait
    assert (await obtained(source, now + first_wait / 2)).standing_in
    later = now + first_wait
    with pytest.raises(CertificateError):
        await obtained(source, later)
    assert source.waiting_until == later + acme.FIRST_RETRY * 2 * (
        1 + jitter.uniform(-acme.JITTER, acme.JITTER)
    )


@needs_pebble
@pytest.mark.anyio
async def test_an_account_whose_record_is_lost_is_found_again_by_its_key(
    tmp_path: pathlib.Path,
    place: Place,
    answering: alpn.Challenges,
) -> None:
    now = datetime.datetime.now(datetime.UTC)
    await obtained(source_of(tmp_path, settings_of(), answering, place.names), now)
    record = next((tmp_path / "state" / acme.ACCOUNT).iterdir()) / acme.ACCOUNT_RECORD
    known = json.loads(record.read_text(encoding="utf-8"))
    record.unlink()
    (tmp_path / "state" / "certificates" / place.name / "chain.pem").unlink()
    await obtained(source_of(tmp_path, settings_of(), answering, place.names), now)
    assert json.loads(record.read_text(encoding="utf-8"))["url"] == known["url"]


def test_a_directory_that_cannot_be_reached_at_start_leaves_a_certificate_standing_in(
    tmp_path: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    unreachable = Acme("https://127.0.0.1:9/directory", None, None, None, Challenge.TLS_ALPN_01, None)
    source = source_of(tmp_path, unreachable)
    served = source.first(NOW)
    assert served.standing_in
    assert source.first(NOW) == served
    assert source.due(served) is None
    assert "The ACME directory could not be asked" in caplog.text
    with pytest.raises(CertificateError, match="could not be reached"):
        source.obtain(NOW)
    assert source.obtain(NOW) == served


@pytest.mark.parametrize(
    ("asked", "after"),
    [
        ("120", datetime.timedelta(seconds=120)),
        (" 7 ", datetime.timedelta(seconds=7)),
        ("Fri, 09 Oct 2026 01:00:00 GMT", datetime.timedelta(hours=1)),
    ],
)
def test_a_retry_after_is_read_as_seconds_or_a_time(asked: str, after: datetime.timedelta) -> None:
    assert acme_protocol.later_of(asked, NOW) == NOW + after


def test_a_retry_after_that_is_neither_is_not_read() -> None:
    assert acme_protocol.later_of("soon", NOW) is None


RATE_LIMITED: Final = b'{"type": "urn:ietf:params:acme:error:rateLimited", "detail": "Too many orders."}'


@contextlib.contextmanager
def answering_with(status: int, headers: dict[str, str], body: bytes) -> Generator[str]:
    """Answer every request on a loopback port with one response, and return the address to ask."""

    class Answer(socketserver.StreamRequestHandler):
        @override
        def handle(self) -> None:
            while self.rfile.readline().strip():
                pass
            lines = [f"HTTP/1.1 {status} Answer", f"Content-Length: {len(body)}", "Connection: close"]
            lines += [f"{name}: {value}" for name, value in headers.items()]
            self.wfile.write(("\r\n".join(lines) + "\r\n\r\n").encode() + body)

    server = socketserver.ThreadingTCPServer(("127.0.0.1", 0), Answer)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        yield f"http://127.0.0.1:{server.server_address[1]}/directory"
    finally:
        server.shutdown()
        server.server_close()


def account_key() -> JWKEC:
    """Return an account key."""
    return JWKEC(key=ec.generate_private_key(ec.SECP256R1()))


def test_a_refusal_asking_to_wait_is_kept() -> None:
    problem = {"Content-Type": "application/problem+json", "Retry-After": "60"}
    network = acme_protocol.Network(account_key(), None)
    with (
        answering_with(429, problem, RATE_LIMITED) as address,
        pytest.raises(messages.Error, match="rateLimited"),
    ):
        network.get(address)
    waited = cast("datetime.datetime", network.retry_after) - datetime.datetime.now(datetime.UTC)
    assert datetime.timedelta(seconds=55) < waited <= datetime.timedelta(seconds=60)


@pytest.mark.parametrize(
    ("status", "headers"),
    [
        (200, {"Retry-After": "60", "Content-Type": "application/json"}),
        (503, {"Content-Type": "application/json"}),
    ],
)
def test_nothing_is_kept_of_an_answer_that_asks_no_wait(status: int, headers: dict[str, str]) -> None:
    network = acme_protocol.Network(account_key(), pathlib.Path("/srv/roots.pem"))
    assert network.verify_ssl == "/srv/roots.pem"
    with answering_with(status, headers, b"{}") as address, contextlib.suppress(errors.Error, messages.Error):
        network.get(address)
    assert network.retry_after is None


UNREACHABLE: Final = Acme("https://127.0.0.1:9/directory", None, None, None, Challenge.TLS_ALPN_01, None)


def test_a_kept_certificate_serves_until_a_third_is_left_where_the_authority_cannot_be_asked(
    tmp_path: pathlib.Path,
) -> None:
    source = source_of(tmp_path, UNREACHABLE)
    key = making.generated(KeyType.EC_P256)
    kept = making.pinned(NAMES, key, NOW)
    held = tmp_path / "state" / "certificates" / NAMES[0]
    state.write(held / "chain.pem", making.certificate_pem(kept))
    state.write(held / "key.pem", making.key_pem(key))
    served = source.obtain(NOW)
    assert served.leaf == kept
    assert (
        source.due(served)
        == kept.not_valid_after_utc - (kept.not_valid_after_utc - kept.not_valid_before_utc) / 3
    )
    assert source.renewal == held / "renewal.json"
    assert source.announced() == []
    assert source.waiting_until is None


def body_of(kind: str, *, valid: bool = False) -> types.SimpleNamespace:
    """Return a challenge as an authorization offers it."""
    return types.SimpleNamespace(chall=types.SimpleNamespace(typ=kind), error=None, valid=valid)


def order_of(*offered: tuple[str, str, bool]) -> messages.OrderResource:
    """Return an order whose authorizations offer one kind of challenge each, by name, valid or pending."""
    authorizations = [
        types.SimpleNamespace(
            body=types.SimpleNamespace(
                identifier=types.SimpleNamespace(value=name),
                challenges=[body_of(kind)],
                status=messages.STATUS_VALID if valid else messages.STATUS_PENDING,
            ),
        )
        for name, kind, valid in offered
    ]
    return cast("messages.OrderResource", types.SimpleNamespace(authorizations=authorizations))


def test_an_authority_offering_no_challenge_of_the_chosen_kind_is_refused_by_name() -> None:
    pending = alpn.Challenges(pathlib.Path())
    acme_client = cast("client.ClientV2", types.SimpleNamespace(net=types.SimpleNamespace(key=account_key())))
    order = order_of(("done.acme.test", "dns-01", True), ("mcp.acme.test", "dns-01", False))
    presenting = acme_protocol.Presenting(Challenge.TLS_ALPN_01, pending, acme_client, order)
    with (
        pytest.raises(CertificateError, match=r"offers no tls-alpn-01 challenge for mcp\.acme\.test"),
        presenting,
    ):
        pass


@pytest.mark.parametrize(
    ("failed", "said"),
    [
        (
            messages.Error.with_code("rateLimited", detail="Too many."),
            "refused: urn:ietf:params:acme:error:rateLimited",
        ),
        (requests.ConnectionError(), "could not be reached or answered unexpectedly: ConnectionError"),
    ],
)
def test_what_failed_is_said_with_the_authoritys_problem(failed: BaseException, said: str) -> None:
    assert said in acme_protocol.said_of(failed)
