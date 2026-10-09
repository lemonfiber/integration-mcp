# Copyright (c) 2026 NightWorksIO
"""Starting the server over stdio, and refusing a start with a sentence that names the setting."""

import contextlib
import logging
import re
import runpy
import sys
from typing import TYPE_CHECKING

import anyio
import anyio.lowlevel
import pytest
import uvicorn
from cryptography import x509
from mcp import ClientSession
from mcp.shared.message import SessionMessage

from lemonfiber_mcp import cli, serving, settings, web
from lemonfiber_mcp.certificates import making, modes
from lemonfiber_mcp.certificates import settings as tls
from lemonfiber_mcp.withheld import WITHHELD
from tests.conftest import KEY
from tests.stack import Reply, Stack, envelope

if TYPE_CHECKING:
    import pathlib
    from collections.abc import AsyncGenerator, Iterator


@pytest.fixture(autouse=True)
def logging_kept() -> Iterator[None]:
    """Put the root logger back as it was, since starting replaces its handlers."""
    root = logging.getLogger()
    kept = list(root.handlers), root.level
    yield
    root.handlers[:] = kept[0]
    root.setLevel(kept[1])


@contextlib.asynccontextmanager
async def closed_at_once() -> AsyncGenerator[tuple[object, object]]:
    """Stand in for standard input and output: an input already at its end, and an output nobody reads."""
    reading_in, reading = anyio.create_memory_object_stream[SessionMessage | Exception](1)
    writing, writing_out = anyio.create_memory_object_stream[SessionMessage](8)
    await reading_in.aclose()
    async with reading, writing, writing_out:
        yield reading, writing


def test_the_server_serves_stdio_until_its_input_ends(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "stdio_server", closed_at_once)
    environment = {settings.ADDRESS: "http://127.0.0.1:9", settings.KEY: KEY}
    assert cli.main(["stdio"], environment) == 0


@pytest.mark.anyio
async def test_the_server_answers_over_stdio_with_the_key_and_pin_it_was_given(
    stack: Stack,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    to_server, server_reads = anyio.create_memory_object_stream[SessionMessage | Exception](8)
    server_writes, from_server = anyio.create_memory_object_stream[SessionMessage](8)

    @contextlib.asynccontextmanager
    async def standing_in() -> AsyncGenerator[tuple[object, object]]:
        async with server_reads, server_writes:
            yield server_reads, server_writes

    monkeypatch.setattr(cli, "stdio_server", standing_in)
    stack.reply("/api/status", Reply(body=envelope("status", {"note": f"{KEY} {stack.pin}"})))
    environment = {settings.ADDRESS: stack.url, settings.PIN: stack.pin, settings.KEY: KEY}
    async with anyio.create_task_group() as group:
        group.start_soon(cli.serve_stdio, environment)
        async with to_server, from_server, ClientSession(from_server, to_server) as session:
            started = await session.initialize()
            listed = await session.list_tools()
            answered = await session.call_tool("read_status", {})
            logging.getLogger("t").info("key %s pin %s", KEY, stack.pin)
            assert started.instructions == serving.INSTRUCTIONS
            assert started.server_info.version == cli.version()
            assert started.capabilities.tools is not None
            assert started.capabilities.tools.list_changed is True
            assert "read_status" in {tool.name for tool in listed.tools}
            said = " ".join(block.text for block in answered.content if block.type == "text")
            assert KEY not in said
            assert stack.pin not in said
    assert {arrival.headers["X-Lemonfiber-Token"] for arrival in stack.arrived} == {KEY}
    logged = capsys.readouterr().err
    assert re.search(r"^\S+ \S+ INFO lemonfiber_mcp\.cli: serving over stdio$", logged, re.MULTILINE)
    assert f"key {WITHHELD} pin {WITHHELD}" in logged


def test_the_server_reads_the_process_environment_where_given_none(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cli, "stdio_server", closed_at_once)
    monkeypatch.setenv(settings.ADDRESS, "http://127.0.0.1:9")
    monkeypatch.setenv(settings.KEY, KEY)
    monkeypatch.delenv(settings.KEY_FILE, raising=False)
    assert cli.main(["stdio"]) == 0


def test_the_help_says_what_the_command_is_and_how_it_serves(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        cli.main(["--help"], {})
    said = capsys.readouterr().out
    assert said.startswith(
        "usage: lemonfiber-mcp [-h] {stdio,http,ca,pinned,health} ...\n\nlemonfiber for AI assistants.\n",
    )
    words = " ".join(said.split())
    for line in (
        "stdio serve one assistant on this machine over standard input and output",
        "http serve assistants anywhere over Streamable HTTP and TLS",
        "ca act on the private root",
        "pinned act on the pinned certificate",
        "health whether the HTTP mode beside this answers healthy",
    ):
        assert line in words


def test_a_start_with_a_refused_setting_names_it_and_not_its_value(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert (
        cli.main(["stdio"], {settings.ADDRESS: "http://127.0.0.1:9", settings.KEY: "hunter2"})
        == cli.REFUSED_TO_START
    )
    said = capsys.readouterr().err
    assert said.startswith("lemonfiber-mcp: LEMONFIBER_KEY does not hold an integration key")
    assert "hunter2" not in said


def test_the_version_is_the_installed_packages(monkeypatch: pytest.MonkeyPatch) -> None:
    def installed(_: str) -> str:
        return "1.2.3"

    monkeypatch.setattr(cli.importlib.metadata, "version", installed)
    assert cli.version() == "1.2.3"


def test_a_server_run_from_a_checkout_says_it_is_unreleased() -> None:
    assert cli.version() == cli.UNINSTALLED


def test_a_mode_is_required() -> None:
    with pytest.raises(SystemExit):
        cli.main([], {})


def test_the_module_runs_as_the_command(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", ["lemonfiber-mcp"])
    with pytest.raises(SystemExit):
        runpy.run_module("lemonfiber_mcp", run_name="__main__")


def http_environment(root: pathlib.Path, **more: str) -> dict[str, str]:
    """Return settings the HTTP mode starts with, its state kept under `root`."""
    held = root / "state"
    held.mkdir(mode=0o700, exist_ok=True)
    return {
        settings.ADDRESS: "http://127.0.0.1:9",
        web.LISTEN: "127.0.0.1:8443",
        tls.NAMES: "mcp.home.example",
        tls.STATE: str(held),
        **more,
    }


@pytest.mark.parametrize("key", [settings.KEY, settings.KEY_FILE])
def test_the_http_mode_refuses_a_key_of_its_own(key: str, tmp_path: pathlib.Path) -> None:
    environment = http_environment(tmp_path, **{key: KEY})
    with pytest.raises(settings.SettingsError) as refused:
        cli.http_server(environment)
    assert str(refused.value) == cli.HOLDS_NO_KEY


@pytest.mark.parametrize(
    "listen",
    ["", "8443", "mcp.home.example:", ":8443", "host:0", "host:65536", "host:84a3"],
)
def test_the_http_mode_refuses_to_guess_where_to_listen(listen: str, tmp_path: pathlib.Path) -> None:
    environment = http_environment(tmp_path, **{web.LISTEN: listen})
    with pytest.raises(settings.SettingsError) as refused:
        cli.http_server(environment)
    assert str(refused.value) == cli.LISTEN_NEEDED


@pytest.mark.parametrize(
    ("listen", "where"),
    [
        ("0.0.0.0:8443", ("0.0.0.0", 8443)),
        ("[::]:443", ("::", 443)),
        ("mcp.home.example:65535", ("mcp.home.example", 65535)),
        (" 192.0.2.1:1 ", ("192.0.2.1", 1)),
    ],
)
def test_where_the_http_mode_listens_is_read_as_given(listen: str, where: tuple[str, int]) -> None:
    assert cli.listen_from({web.LISTEN: listen}) == where


def test_the_address_is_shown_as_a_person_types_it() -> None:
    assert cli.shown("::", 8443) == "https://[::]:8443/mcp"
    assert cli.shown("192.0.2.1", 443) == "https://192.0.2.1:443/mcp"
    assert cli.shown("mcp.home.example", 8443) == "https://mcp.home.example:8443/mcp"


def test_the_operators_files_need_no_state(tmp_path: pathlib.Path) -> None:
    environment = {
        tls.CERTIFICATE: str(tmp_path / "c.pem"),
        tls.PRIVATE_KEY: str(tmp_path / "k.pem"),
        tls.STATE: str(tmp_path / "never"),
    }
    assert cli.kept_tls(environment).mode is tls.Mode.FILES
    assert not (tmp_path / "never").exists()


def test_the_http_mode_serves_until_stopped_and_stops_its_watch(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    async def stopped(_: uvicorn.Server) -> None:
        await anyio.lowlevel.checkpoint()

    monkeypatch.setattr(uvicorn.Server, "serve", stopped)
    assert cli.main(["http"], http_environment(tmp_path)) == 0
    assert "serving over HTTPS at https://127.0.0.1:8443/mcp" in capsys.readouterr().err


def test_a_private_root_is_replaced_and_switched_on_command(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    environment = http_environment(tmp_path, **{tls.MODE: "private-ca"})
    assert cli.main(["ca", "switch"], environment) == 0
    assert capsys.readouterr().out == "No replacement root waits; `lemonfiber-mcp ca replace` makes one.\n"
    assert cli.main(["ca", "replace"], environment) == 0
    replaced = capsys.readouterr().out
    waiting = x509.load_pem_x509_certificate((tmp_path / "state" / modes.CA / modes.NEXT_ROOT).read_bytes())
    assert replaced == (
        f"A replacement root waits to be installed; its fingerprint is {making.fingerprint(waiting)}. "
        "Install it on every device, then run `lemonfiber-mcp ca switch`.\n"
    )
    assert cli.main(["ca", "switch"], environment) == 0
    assert capsys.readouterr().out == (
        "The replacement root is in force, and the old root's key is deleted. "
        "A running server takes it within a minute.\n"
    )
    assert (tmp_path / "state" / modes.CA / modes.ROOT).read_bytes() == making.certificate_pem(waiting)


def test_a_pinned_certificate_is_replaced_on_command(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["pinned", "replace"], http_environment(tmp_path)) == 0
    chain = tmp_path / "state" / modes.CERTIFICATES / "mcp.home.example" / modes.CHAIN
    made = x509.load_pem_x509_certificate(chain.read_bytes())
    assert capsys.readouterr().out == (
        f"A new pinned certificate is made; give every client its fingerprint: {making.fingerprint(made)}\n"
    )


@pytest.mark.parametrize(
    ("command", "mode", "said"),
    [
        (["ca", "replace"], "pinned", "replaced or switched only where LEMONFIBER_TLS_MODE is private-ca."),
        (["ca", "switch"], "pinned", "replaced or switched only where LEMONFIBER_TLS_MODE is private-ca."),
        (["pinned", "replace"], "private-ca", "replaced only where LEMONFIBER_TLS_MODE is pinned or unset."),
    ],
)
def test_a_command_for_another_mode_is_refused_by_name(
    command: list[str],
    mode: str,
    said: str,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(command, http_environment(tmp_path, **{tls.MODE: mode})) == cli.REFUSED_TO_START
    assert capsys.readouterr().err.endswith(f"{said}\n")


def test_an_unhealthy_server_is_a_failed_check(tmp_path: pathlib.Path) -> None:
    assert cli.main(["health"], http_environment(tmp_path, **{web.LISTEN: "127.0.0.1:9"})) == cli.UNHEALTHY
