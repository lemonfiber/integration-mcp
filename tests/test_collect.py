# Copyright (c) 2026 NightWorksIO
"""Setting the server up with a key link: its claim collects the key once into a new file, and nothing else is kept."""

import stat
import urllib.parse
from typing import TYPE_CHECKING, Final

import pytest

from lemonfiber_mcp import cli, settings
from tests.conftest import KEY
from tests.stack import Reply, envelope, problem

if TYPE_CHECKING:
    import pathlib

    from tests.stack import Stack

CLAIM: Final = "lfc_" + "c" * 43
LATER: Final = 4102444800
"""2100-01-01, a lapse no test reaches."""
EARLIER: Final = 946684800
"""2000-01-01, a lapse every test is past."""
OTHER_PIN: Final = "0" * 64
ELSEWHERE: Final = "https://192.0.2.10:7777"


def link(address: str, pin: str, *, expires: int = LATER) -> str:
    """Return a key link as a claim's mint writes one."""
    said = {"address": address, "fingerprint": pin, "stack": "stack-1f6a", "expires": expires, "claim": CLAIM}
    return "lemonfiber://key?" + urllib.parse.urlencode(said, quote_via=urllib.parse.quote)


def minted(stack: Stack) -> dict[str, object]:
    """Return what collecting the claim answers with."""
    return envelope(
        "minted-key",
        {
            "name": "assistant",
            "scope": "read",
            "purpose": "mcp",
            "secret": KEY,
            "pin": stack.pin,
            "address": stack.url,
        },
    )


def asked(written: str, file: pathlib.Path) -> dict[str, str]:
    """Return the environment a collection is asked with."""
    return {settings.KEY_LINK: written, settings.KEY_FILE: str(file)}


@pytest.mark.anyio
async def test_a_key_link_collects_its_key_once_into_a_new_file_only_its_owner_reads(
    stack: Stack,
    tmp_path: pathlib.Path,
) -> None:
    stack.reply("/api/keys/claim", Reply(body=minted(stack)))
    file = tmp_path / "keys" / "assistant.key"
    said = await cli.collected_key(asked(link(stack.url, stack.pin), file))
    assert file.read_text() == f"{KEY}\n"
    assert stat.S_IMODE(file.stat().st_mode) == 0o600
    assert said == (
        f"The key is in {file}. Give the server LEMONFIBER_ADDRESS={stack.url}, "
        f"LEMONFIBER_PIN={stack.pin} and LEMONFIBER_KEY_FILE={file}."
    )
    assert KEY not in said
    assert CLAIM not in said
    collecting = stack.asked("/api/keys/claim")
    assert [arrival.body for arrival in collecting] == [{"claim": CLAIM}]
    assert "X-Lemonfiber-Token" not in collecting[0].headers


@pytest.mark.anyio
async def test_a_reply_that_names_no_address_or_pin_is_given_the_links(
    stack: Stack,
    tmp_path: pathlib.Path,
) -> None:
    bare = envelope("minted-key", {"name": "assistant", "scope": "read", "purpose": "mcp", "secret": KEY})
    stack.reply("/api/keys/claim", Reply(body=bare))
    file = tmp_path / "assistant.key"
    said = await cli.collected_key(asked(link(stack.url, stack.pin), file))
    assert f"LEMONFIBER_ADDRESS={stack.url}, LEMONFIBER_PIN={stack.pin}" in said


@pytest.mark.anyio
async def test_a_claim_the_stack_turns_away_says_why_in_its_words_and_writes_nothing(
    stack: Stack,
    tmp_path: pathlib.Path,
) -> None:
    stack.reply("/api/keys/claim", Reply(401, problem("KEY-12", "That claim collects no key.")))
    file = tmp_path / "assistant.key"
    with pytest.raises(settings.SettingsError) as refused:
        await cli.collected_key(asked(link(stack.url, stack.pin), file))
    assert str(refused.value) == (
        "The stack collected no key with LEMONFIBER_KEY_LINK: That claim collects no key. "
        "Mint the key as a claim again."
    )
    assert not file.exists()


@pytest.mark.anyio
async def test_a_claim_goes_nowhere_but_the_certificate_the_link_pins(
    stack: Stack,
    tmp_path: pathlib.Path,
) -> None:
    file = tmp_path / "assistant.key"
    with pytest.raises(settings.SettingsError) as refused:
        await cli.collected_key(asked(link(stack.url, OTHER_PIN), file))
    assert str(refused.value).startswith(
        "The key could not be collected: The stack's certificate is not the one",
    )
    assert stack.asked("/api/keys/claim") == []
    assert not file.exists()


@pytest.mark.anyio
async def test_a_key_that_cannot_be_written_is_said_to_be_lost(stack: Stack, tmp_path: pathlib.Path) -> None:
    stack.reply("/api/keys/claim", Reply(body=minted(stack)))
    blocked = tmp_path / "taken"
    blocked.write_text("")
    with pytest.raises(settings.SettingsError) as refused:
        await cli.collected_key(asked(link(stack.url, stack.pin), blocked / "assistant.key"))
    assert str(refused.value) == (
        "LEMONFIBER_KEY_FILE names a file that could not be written; the key it would have held is lost."
    )


def test_a_lapsed_link_sends_nothing_and_says_to_mint_again(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    file = tmp_path / "assistant.key"
    status = cli.main(["collect"], asked(link(ELSEWHERE, OTHER_PIN, expires=EARLIER), file))
    assert status == cli.REFUSED_TO_START
    assert capsys.readouterr().err == f"lemonfiber-mcp: {cli.CLAIM_LAPSED}\n"
    assert not file.exists()


@pytest.mark.parametrize(
    ("written", "said"),
    [
        (
            "",
            "LEMONFIBER_KEY_LINK is not set: give the key link the stack showed when the key was minted as a claim.",
        ),
        (
            "lemonfiber://pair?x=1",
            "LEMONFIBER_KEY_LINK was refused: A key link begins with lemonfiber://key; this one does not.",
        ),
    ],
)
def test_a_key_link_missing_or_not_one_is_named(written: str, said: str) -> None:
    with pytest.raises(settings.SettingsError) as refused:
        settings.link_from({settings.KEY_LINK: written})
    assert str(refused.value) == said


def test_a_collection_with_nowhere_to_write_the_key_is_named() -> None:
    with pytest.raises(settings.SettingsError) as refused:
        settings.collected_into({})
    assert str(refused.value) == (
        "LEMONFIBER_KEY_FILE is not set: name the new file the collected key is written to, which only you can read."
    )


def test_a_collected_key_is_never_written_over_a_file_already_there(tmp_path: pathlib.Path) -> None:
    held = tmp_path / "assistant.key"
    held.write_text("lfk_kept\n")
    with pytest.raises(settings.SettingsError) as refused:
        settings.collected_into({settings.KEY_FILE: str(held)})
    assert str(refused.value) == (
        "LEMONFIBER_KEY_FILE names a file that is already there; a collected key is written to a new file, never "
        "over one."
    )
    assert held.read_text() == "lfk_kept\n"
