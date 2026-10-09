# Copyright (c) 2026 NightWorksIO
"""The `acme` mode against Pebble: first issuance by each challenge, renewal, a binding, and an order that fails.

Pebble and its challenge test server are started by `scripts/pebble.sh`, which
says where they are; without them these tests are skipped. Every name resolves
to this machine, where TLS-ALPN-01 is answered on 5001 and HTTP-01 on 5002.
"""

import asyncio
import contextlib
import datetime
import json
import logging
import os
import pathlib
import random
import socket
import socketserver
import stat
import threading
import types
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
    from collections.abc import AsyncIterator, Generator

NAMES: Final = ("mcp.acme.test",)
TLS_PORT: Final = 5001
HTTP_PORT: Final = 5002
EVERYWHERE: Final = "0.0.0.0"  # The tests' TLS-ALPN-01 server, reached by Pebble from wherever it runs.
NOW: Final = datetime.datetime(2026, 10, 9, tzinfo=datetime.UTC)
PEBBLE: Final = os.environ.get("PEBBLE_DIRECTORY", "")
ROOTS: Final = os.environ.get("PEBBLE_ROOTS", "")
needs_pebble = pytest.mark.skipif(not PEBBLE, reason="Pebble is not running: start it with scripts/pebble.sh")


def tls_of(root: pathlib.Path) -> Tls:
    """Return settings for the `acme` mode, keeping state under `root`."""
    return Tls(Mode.ACME, NAMES, None, None, KeyType.EC_P256, state.kept(root / "state"))


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


def source_of(root: pathlib.Path, settings: Acme, pending: alpn.Challenges | None = None) -> acme.AcmeSource:
    """Return the `acme` source, its jitter fixed so a wait is the wait itself."""
    return acme.AcmeSource(tls_of(root), settings, pending or alpn.Challenges(root), random.Random(0))


@pytest.fixture
async def answering(tmp_path: pathlib.Path) -> AsyncIterator[alpn.Challenges]:
    """Serve TLS on 5001 as the server does, answering TLS-ALPN-01 for whatever challenge is pending."""
    pending = alpn.Challenges(tmp_path)
    key = making.generated(KeyType.EC_P256)
    state.write(tmp_path / "standing.pem", making.certificate_pem(making.pinned(NAMES, key, NOW)))
    state.write(tmp_path / "standing-key.pem", making.key_pem(key))
    context = server_context(pending)
    context.load_cert_chain(tmp_path / "standing.pem", tmp_path / "standing-key.pem")

    async def closed(_: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        writer.close()

    server = await asyncio.start_server(closed, EVERYWHERE, TLS_PORT, ssl=context)
    async with server:
        yield pending


async def obtained(source: acme.AcmeSource, now: datetime.datetime) -> Served:
    """Obtain in a thread, as the server does, while this loop answers the authority."""
    return await anyio.to_thread.run_sync(source.obtain, now)


def making_covered(served: Served) -> set[object]:
    """Return every name a served certificate covers."""
    return set(making.covered(served.leaf))


def acme_hello() -> hello.Hello:
    """Return what a validator's ClientHello asks for, for the tests' name."""
    return hello.Hello(NAMES[0], (alpn.ACME_TLS,))


def closed(port: int) -> bool:
    """Tell whether nothing listens on a loopback port."""
    try:
        socket.create_connection(("127.0.0.1", port), timeout=2).close()
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
    answering: alpn.Challenges,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    source = source_of(tmp_path, settings_of(), answering)
    now = datetime.datetime.now(datetime.UTC)
    assert source.first(now).standing_in
    served = await obtained(source, now)
    assert not served.standing_in
    assert making_covered(served) == set(NAMES)
    assert "agreeing to the authority's terms: data:text/plain" in caplog.text
    account = next((tmp_path / "state" / acme.ACCOUNT).iterdir())
    assert private(account / acme.ACCOUNT_KEY)
    assert private(account / acme.ACCOUNT_RECORD)
    assert private(served.key)
    assert source.obtain(now) == served
    assert source_of(tmp_path, settings_of()).first(now).fingerprint == served.fingerprint
    assert answering.context_for(acme_hello()) is None


@needs_pebble
@pytest.mark.anyio
async def test_the_first_certificate_is_issued_by_http_01_on_port_80_opened_for_it(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(http01, "PORT", HTTP_PORT)
    source = source_of(tmp_path, settings_of(Challenge.HTTP_01))
    served = await obtained(source, datetime.datetime.now(datetime.UTC))
    assert making_covered(served) == set(NAMES)
    assert closed(HTTP_PORT)


@needs_pebble
@pytest.mark.anyio
async def test_the_authority_is_asked_when_to_renew(
    tmp_path: pathlib.Path,
    answering: alpn.Challenges,
) -> None:
    source = source_of(tmp_path, settings_of(), answering)
    first = await obtained(source, datetime.datetime.now(datetime.UTC))
    due = cast("datetime.datetime", source.due(first))
    assert first.leaf.not_valid_before_utc < due < first.expires


@needs_pebble
@pytest.mark.anyio
async def test_a_certificate_is_renewed_when_the_authority_says(
    tmp_path: pathlib.Path,
    answering: alpn.Challenges,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    said = datetime.datetime.now(datetime.UTC) + datetime.timedelta(days=2)

    def saying(_: client.ClientV2, __: bytes) -> tuple[datetime.datetime | None, datetime.datetime]:
        return said, said - datetime.timedelta(days=1)

    monkeypatch.setattr(client.ClientV2, "renewal_time", saying)
    source = source_of(tmp_path, settings_of(), answering)
    first = await obtained(source, datetime.datetime.now(datetime.UTC))
    assert source.due(first) == said
    assert await obtained(source, said - datetime.timedelta(seconds=1)) == first
    renewed = await obtained(source, said)
    assert renewed.fingerprint != first.fingerprint


@needs_pebble
@pytest.mark.anyio
async def test_a_certificate_is_renewed_with_a_third_left_where_the_authority_says_nothing(
    tmp_path: pathlib.Path,
    answering: alpn.Challenges,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def silent(_: client.ClientV2, __: bytes) -> tuple[datetime.datetime | None, datetime.datetime]:
        return None, datetime.datetime.now(datetime.UTC) + datetime.timedelta(hours=6)

    monkeypatch.setattr(client.ClientV2, "renewal_time", silent)
    source = source_of(tmp_path, settings_of(), answering)
    first = await obtained(source, datetime.datetime.now(datetime.UTC))
    lifetime = first.leaf.not_valid_after_utc - first.leaf.not_valid_before_utc
    assert source.due(first) == first.leaf.not_valid_after_utc - lifetime / 3


@needs_pebble
def test_an_authority_requiring_a_binding_refuses_a_start_without_one(tmp_path: pathlib.Path) -> None:
    source = source_of(tmp_path, settings_of(bound=False))
    with pytest.raises(CertificateError, match="LEMONFIBER_ACME_EAB_KID and LEMONFIBER_ACME_EAB_HMAC_FILE"):
        source.first(NOW)


@needs_pebble
@pytest.mark.anyio
async def test_an_authority_requiring_a_binding_issues_with_one(
    tmp_path: pathlib.Path,
    answering: alpn.Challenges,
) -> None:
    source = source_of(tmp_path, settings_of(bound=True), answering)
    now = datetime.datetime.now(datetime.UTC)
    assert source.first(now).standing_in
    assert not (await obtained(source, now)).standing_in


@needs_pebble
@pytest.mark.anyio
async def test_an_order_that_fails_is_tried_again_after_a_minute_then_two(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(http01, "PORT", HTTP_PORT + 1000)
    source = source_of(tmp_path, settings_of(Challenge.HTTP_01))
    now = datetime.datetime.now(datetime.UTC)
    with pytest.raises(
        CertificateError,
        match=r"could not validate mcp\.acme\.test: urn:ietf:params:acme:error",
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
    answering: alpn.Challenges,
) -> None:
    now = datetime.datetime.now(datetime.UTC)
    await obtained(source_of(tmp_path, settings_of(), answering), now)
    record = next((tmp_path / "state" / acme.ACCOUNT).iterdir()) / acme.ACCOUNT_RECORD
    known = json.loads(record.read_text(encoding="utf-8"))
    record.unlink()
    (tmp_path / "state" / "certificates" / NAMES[0] / "chain.pem").unlink()
    await obtained(source_of(tmp_path, settings_of(), answering), now)
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
