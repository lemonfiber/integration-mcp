# Copyright (c) 2026 NightWorksIO
"""Starting the server over stdio, and refusing a start with a sentence that names the setting."""

import contextlib
import logging
import runpy
import sys
from typing import TYPE_CHECKING

import anyio
import pytest
from mcp.shared.message import SessionMessage

from lemonfiber_mcp import cli, settings
from tests.conftest import KEY

if TYPE_CHECKING:
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
