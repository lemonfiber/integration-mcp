# Copyright (c) 2026 NightWorksIO
"""What the server is told at start, and what it refuses to start with, never repeating a value."""

from typing import TYPE_CHECKING

import pytest

from lemonfiber_mcp import settings
from tests.conftest import KEY

if TYPE_CHECKING:
    import pathlib

PIN = "cd" * 32


def test_a_loopback_address_needs_no_pin() -> None:
    stack = settings.stack_from({settings.ADDRESS: "http://127.0.0.1:8080"})
    assert stack.pin is None
    assert stack.address.base == "http://127.0.0.1:8080"


def test_an_address_elsewhere_is_held_to_its_pin() -> None:
    stack = settings.stack_from({settings.ADDRESS: "https://192.0.2.7:8443", settings.PIN: PIN.upper()})
    assert stack.pin is not None
    assert stack.pin.hex == PIN
    assert stack.address.pin == stack.pin


def test_an_address_elsewhere_without_a_pin_is_refused() -> None:
    with pytest.raises(settings.SettingsError, match="LEMONFIBER_PIN"):
        settings.stack_from({settings.ADDRESS: "https://192.0.2.7:8443"})


def test_a_pin_that_is_not_one_is_refused_without_repeating_it() -> None:
    with pytest.raises(settings.SettingsError) as refused:
        settings.stack_from({settings.ADDRESS: "https://192.0.2.7:8443", settings.PIN: "not-a-pin-value"})
    assert "not-a-pin-value" not in str(refused.value)


def test_no_address_is_refused() -> None:
    with pytest.raises(settings.SettingsError, match="LEMONFIBER_ADDRESS is not set"):
        settings.stack_from({})


def test_the_key_is_taken_from_the_environment() -> None:
    credential, written = settings.key_of({settings.KEY: f" {KEY}\n"})
    assert written == KEY
    assert credential.header() == {"X-Lemonfiber-Token": KEY}


def test_the_key_is_taken_from_a_file(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "key"
    path.write_text(f"{KEY}\n", encoding="utf-8")
    credential, written = settings.key_of({settings.KEY_FILE: str(path)})
    assert written == KEY
    assert credential.header() == {"X-Lemonfiber-Token": KEY}


def test_a_key_file_that_cannot_be_read_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(settings.SettingsError, match="could not be read"):
        settings.key_of({settings.KEY_FILE: str(tmp_path / "missing")})


def test_the_key_given_two_ways_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(settings.SettingsError, match="both set"):
        settings.key_of({settings.KEY: KEY, settings.KEY_FILE: str(tmp_path / "key")})


def test_no_key_is_refused() -> None:
    with pytest.raises(settings.SettingsError, match="Neither"):
        settings.key_of({})


@pytest.mark.parametrize("setting", [settings.KEY, settings.KEY_FILE])
def test_a_refused_key_names_where_it_was_given_and_what_to_give(
    setting: str,
    tmp_path: pathlib.Path,
) -> None:
    path = tmp_path / "key"
    path.write_text("hunter2", encoding="utf-8")
    given = {settings.KEY: "hunter2"} if setting == settings.KEY else {settings.KEY_FILE: str(path)}
    with pytest.raises(settings.SettingsError) as refused:
        settings.key_of(given)
    assert str(refused.value) == (
        f"{setting} does not hold an integration key. Mint one for this server, with the purpose `mcp`, and give "
        "it here; nothing else is accepted, the operator's password least of all."
    )


def test_a_key_file_that_is_not_text_is_refused(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "key"
    path.write_bytes(b"\xff" + KEY.encode())
    with pytest.raises(settings.SettingsError, match="could not be read"):
        settings.key_of({settings.KEY_FILE: str(path)})


@pytest.mark.parametrize("given", ["hunter2", "lfk_NOT-HEX", "lfk_", "a session secret"])
def test_anything_not_shaped_as_an_integration_key_is_refused_without_repeating_it(given: str) -> None:
    with pytest.raises(settings.SettingsError, match="does not hold an integration key") as refused:
        settings.key_of({settings.KEY: given})
    assert given not in str(refused.value)
