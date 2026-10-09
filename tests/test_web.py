# Copyright (c) 2026 NightWorksIO
"""The HTTP mode served for real over TLS: each request with its own key, health and the root without one."""

import datetime
import hashlib
import logging
import socket
from typing import TYPE_CHECKING, Any, Final

import anyio
import httpx2
import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes

from lemonfiber_mcp import cli, web
from lemonfiber_mcp.certificates import making, modes, probe
from lemonfiber_mcp.certificates.settings import KeyType, Mode
from tests.conftest import KEY
from tests.stack import LOOPBACK, Reply, Stack, problem

if TYPE_CHECKING:
    import pathlib
    from collections.abc import AsyncIterator

    import uvicorn

pytestmark = pytest.mark.anyio

OTHER_KEY: Final = "lfk_" + "f" * 64
ACCEPT: Final = {"Accept": "application/json, text/event-stream"}
GREETING: Final[dict[str, Any]] = {
    "protocolVersion": "2025-11-25",
    "capabilities": {},
    "clientInfo": {"name": "test", "version": "1"},
}
INITIALISE: Final[dict[str, Any]] = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": GREETING}
STARTING_CHECKS: Final = 500
EVERYWHERE: Final = ("0.0.0.0", "::")


def free_port() -> int:
    """Return a loopback port nothing listens on."""
    with socket.socket() as probe_socket:
        probe_socket.bind((LOOPBACK, 0))
        return int(probe_socket.getsockname()[1])


def environment_for(stack: Stack, root: pathlib.Path, port: int, **more: str) -> dict[str, str]:
    """Return the HTTP mode's settings for the stand-in stack."""
    held = root / "state"
    held.mkdir(mode=0o700, exist_ok=True)
    return {
        "LEMONFIBER_ADDRESS": stack.url,
        "LEMONFIBER_PIN": stack.pin,
        web.LISTEN: f"{LOOPBACK}:{port}",
        "LEMONFIBER_NAMES": "localhost,127.0.0.1",
        "LEMONFIBER_STATE": str(held),
        **more,
    }


class Served:
    """The HTTP mode running, and a client to ask it with."""

    def __init__(self, port: int, client: httpx2.AsyncClient, environment: dict[str, str]) -> None:
        """Hold where it serves, the client, and the settings it was started with."""
        self.port = port
        self.client = client
        self.environment = environment

    @property
    def base(self) -> str:
        """Return the address it serves at."""
        return f"https://{LOOPBACK}:{self.port}"

    async def rpc(
        self,
        method: str,
        params: dict[str, Any] | None = None,
        key: str | None = KEY,
    ) -> httpx2.Response:
        """Send one JSON-RPC request to the protocol's endpoint, with a key where given."""
        headers = {**ACCEPT, "MCP-Protocol-Version": "2025-11-25"}
        if key is not None:
            headers["Authorization"] = f"Bearer {key}"
        body: dict[str, Any] = {"jsonrpc": "2.0", "id": 2, "method": method}
        if params is not None:
            body["params"] = params
        return await self.client.post(f"{self.base}{web.PATH}", json=body, headers=headers)


async def started(server: uvicorn.Server) -> None:
    """Return once the server listens."""
    for _ in range(STARTING_CHECKS):
        if server.started:
            return
        await anyio.sleep(0.01)
    msg = "The HTTP mode did not start."
    raise AssertionError(msg)


@pytest.fixture
async def serving(
    stack: Stack,
    tmp_path: pathlib.Path,
    request: pytest.FixtureRequest,
) -> AsyncIterator[Served]:
    """Return the HTTP mode running in the mode a test parametrises it with, `pinned` by default."""
    mode: str = getattr(request, "param", Mode.PINNED.value)
    port = free_port()
    environment = environment_for(stack, tmp_path, port, LEMONFIBER_TLS_MODE=mode)
    server, _certificates = cli.http_server(environment)
    async with anyio.create_task_group() as group:
        group.start_soon(server.serve)
        try:
            await started(server)
            async with httpx2.AsyncClient(verify=False) as client:
                yield Served(port, client, environment)
        finally:
            server.should_exit = True


async def test_health_answers_without_a_key_and_says_nothing_of_the_stack(
    serving: Served,
    stack: Stack,
) -> None:
    answer = await serving.client.get(f"{serving.base}{web.HEALTH}")
    assert answer.status_code == 200
    assert set(answer.json()) == {"mode", "expires", "renewal_due", "last_attempt", "outcome"}
    assert not stack.arrived


@pytest.mark.parametrize("authorization", [None, "Bearer hunter2", f"Basic {KEY}", f"Bearer {KEY}x!"])
async def test_a_request_without_an_integration_key_is_refused_before_the_protocol(
    serving: Served,
    stack: Stack,
    authorization: str | None,
) -> None:
    headers = {**ACCEPT} if authorization is None else {**ACCEPT, "Authorization": authorization}
    answer = await serving.client.post(f"{serving.base}{web.PATH}", json=INITIALISE, headers=headers)
    assert answer.status_code == 401
    assert answer.headers["WWW-Authenticate"] == "Bearer"
    assert answer.json() == {"error": web.REFUSED_WITHOUT_A_KEY}
    assert not stack.arrived


async def test_each_request_reaches_the_stack_with_its_own_key(serving: Served, stack: Stack) -> None:
    assert (await serving.rpc("initialize", GREETING)).status_code == 200
    listed = (await serving.rpc("tools/list")).json()["result"]["tools"]
    assert "read_status" in {tool["name"] for tool in listed}
    await serving.rpc("tools/list", key=OTHER_KEY)
    sent = [arrival.headers["X-Lemonfiber-Token"] for arrival in stack.asked("/api/capabilities")]
    assert sent == [KEY, OTHER_KEY]


async def test_a_refused_key_is_refused_by_every_tool_and_not_sent_again(
    serving: Served,
    stack: Stack,
) -> None:
    stack.reply("/api/capabilities", Reply(status=403, body=problem("ADMIT-4", "Not admitted.")))
    await serving.rpc("tools/list", key=OTHER_KEY)
    sent = len(stack.arrived)
    called = (await serving.rpc("tools/call", {"name": "read_status", "arguments": {}}, key=OTHER_KEY)).json()
    assert called["result"]["isError"]
    assert "A new key is needed" in called["result"]["content"][0]["text"]
    assert len(stack.arrived) == sent


async def test_no_key_reaches_the_log(serving: Served, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    await serving.rpc("tools/list")
    assert KEY not in caplog.text


async def test_the_root_is_not_served_where_there_is_none(serving: Served) -> None:
    assert (await serving.client.get(f"{serving.base}{web.ROOT}")).status_code == 404


@pytest.mark.parametrize("serving", [Mode.PRIVATE_CA.value], indirect=True)
async def test_a_private_root_is_served_to_install(serving: Served, tmp_path: pathlib.Path) -> None:
    answer = await serving.client.get(f"{serving.base}{web.ROOT}")
    assert answer.status_code == 200
    assert answer.headers["content-type"] == web.PEM
    assert answer.content == (tmp_path / "state" / modes.CA / modes.ROOT).read_bytes()


async def test_the_probe_holds_the_server_to_the_certificate_it_keeps(
    serving: Served,
    tmp_path: pathlib.Path,
) -> None:
    chain = tmp_path / "state" / modes.CERTIFICATES / "localhost" / modes.CHAIN
    assert await anyio.to_thread.run_sync(probe.healthy, LOOPBACK, serving.port, chain)
    assert await anyio.to_thread.run_sync(cli.checked_health, serving.environment)
    other = tmp_path / "other.pem"
    other.write_bytes(
        making.certificate_pem(
            making.pinned(
                ("localhost",),
                making.generated(KeyType.EC_P256),
                datetime.datetime.now(datetime.UTC),
            ),
        ),
    )
    assert not await anyio.to_thread.run_sync(probe.healthy, LOOPBACK, serving.port, other)
    assert await anyio.to_thread.run_sync(cli.main, ["health"], serving.environment) == 0


async def test_a_probe_that_reaches_nothing_says_unhealthy(tmp_path: pathlib.Path, serving: Served) -> None:
    chain = tmp_path / "state" / modes.CERTIFICATES / "localhost" / modes.CHAIN
    assert not await anyio.to_thread.run_sync(probe.healthy, LOOPBACK, free_port(), chain)


def test_a_server_listening_everywhere_is_probed_from_beside_it() -> None:
    assert [probe.reached(address) for address in EVERYWHERE] == ["127.0.0.1", "::1"]
    assert probe.reached("192.0.2.1") == "192.0.2.1"
    assert probe.reached("mcp.home.example") == "mcp.home.example"


def test_the_pool_lets_the_least_lately_used_key_go() -> None:
    pool = web.Pool(size=2)
    first = pool.held(KEY)
    pool.held(OTHER_KEY)
    assert pool.held(KEY) is first
    pool.held("lfk_" + "1" * 64)
    assert len(pool) == 2
    assert KEY in pool
    assert OTHER_KEY not in pool


def test_the_pool_holds_digests_and_never_a_key() -> None:
    pool = web.Pool()
    pool.held(KEY)
    assert list(pool) == [hashlib.sha256(KEY.encode()).hexdigest()]


def test_a_chain_that_cannot_be_read_holds_the_server_to_nothing_and_is_unhealthy(
    tmp_path: pathlib.Path,
) -> None:
    empty = tmp_path / "empty.pem"
    empty.write_text("no certificate here", encoding="utf-8")
    assert not probe.healthy(LOOPBACK, free_port(), empty)
    assert not probe.healthy(LOOPBACK, free_port(), tmp_path / "missing.pem")


@pytest.mark.parametrize("scheme", ["Bearer", "bearer", "BEARER"])
def test_the_bearer_scheme_is_read_in_any_case(scheme: str) -> None:
    scope: dict[str, Any] = {"headers": [(b"authorization", f"{scheme} {KEY}".encode())]}
    assert web.bearer(scope) == KEY


def test_a_request_without_an_authorization_header_carries_no_key() -> None:
    assert web.bearer({"headers": [(b"accept", b"application/json")]}) is None


def leaf_for(*names: str) -> x509.Certificate:
    """Return a certificate covering these names, or none."""
    key = making.generated(KeyType.EC_P256)
    built = making.builder(
        making.named("probe"),
        key,
        making.ISSUED_LIFETIME,
        datetime.datetime.now(datetime.UTC),
    )
    if names:
        built = built.add_extension(
            x509.SubjectAlternativeName(making.general_names(names)),
            critical=False,
        )
    return built.issuer_name(making.named("probe")).sign(key, hashes.SHA256())


def test_the_probe_checks_a_certificate_for_a_name_it_covers() -> None:
    assert probe.named(leaf_for("b.example", "*.home.example", "a.example")) == "a.example"
    assert probe.named(leaf_for("*.home.example")) == "health.home.example"
    assert probe.named(leaf_for()) is None


def test_a_chain_whose_certificate_covers_no_name_is_unhealthy(tmp_path: pathlib.Path) -> None:
    bare = tmp_path / "bare.pem"
    bare.write_bytes(making.certificate_pem(leaf_for()))
    assert not probe.healthy(LOOPBACK, free_port(), bare)
