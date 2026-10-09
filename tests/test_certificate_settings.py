# Copyright (c) 2026 NightWorksIO
"""How the certificate comes: the mode chosen, the names given, and each combination refused."""

import ipaddress
import pathlib

import pytest

from lemonfiber_mcp.certificates import settings
from lemonfiber_mcp.certificates.settings import KeyType, Mode, TlsSettingsError


def test_nothing_chosen_serves_pinned_with_the_secure_defaults() -> None:
    tls = settings.tls_from({settings.NAMES: "mcp.home.example, 192.168.1.42"})
    assert tls.mode is Mode.PINNED
    assert tls.names == ("mcp.home.example", ipaddress.ip_address("192.168.1.42"))
    assert tls.key_type is KeyType.EC_P256
    assert tls.state == settings.DEFAULT_STATE
    assert tls.first == "mcp.home.example"


def test_both_files_choose_files_and_need_no_names() -> None:
    tls = settings.tls_from({settings.CERTIFICATE: "/c.pem", settings.PRIVATE_KEY: "/k.pem"})
    assert tls.mode is Mode.FILES
    assert (tls.certificate, tls.private_key) == (pathlib.Path("/c.pem"), pathlib.Path("/k.pem"))


@pytest.mark.parametrize("mode", [Mode.PRIVATE_CA, Mode.ACME])
def test_a_mode_that_extends_what_is_trusted_is_served_where_it_is_named(mode: Mode) -> None:
    tls = settings.tls_from({settings.MODE: mode.value, settings.NAMES: "mcp.example.org"})
    assert tls.mode is mode


def test_the_state_and_key_kind_are_taken_as_given() -> None:
    tls = settings.tls_from(
        {settings.NAMES: "a.example", settings.STATE: "/srv/state", settings.KEY_TYPE: "rsa-3072"},
    )
    assert (tls.state, tls.key_type) == (pathlib.Path("/srv/state"), KeyType.RSA_3072)


def test_names_are_lower_cased_and_given_once() -> None:
    assert settings.names_of("A.Example., a.example,, b.example") == ("a.example", "b.example")


@pytest.mark.parametrize(
    ("environment", "said"),
    [
        ({settings.CERTIFICATE: "/c.pem"}, "together or not at all"),
        (
            {settings.CERTIFICATE: "/c.pem", settings.PRIVATE_KEY: "/k.pem", settings.MODE: "pinned"},
            "chose pinned",
        ),
        ({settings.MODE: "files", settings.NAMES: "a.example"}, "chose files"),
        ({settings.MODE: "self-signed", settings.NAMES: "a.example"}, "is 'self-signed'"),
        ({}, "LEMONFIBER_NAMES is not set"),
        ({settings.NAMES: "not a name!"}, "neither a host name nor an address"),
        (
            {settings.NAMES: "mcp.home.example, *.Home.example"},
            r"holds '\*\.Home\.example', a wildcard\. .* would be good for every name under home\.example\.",
        ),
        ({settings.MODE: "acme", settings.NAMES: "192.168.1.42"}, "issues for host names"),
        ({settings.NAMES: "a.example", settings.KEY_TYPE: "dsa"}, "is 'dsa'"),
    ],
)
def test_what_the_contract_does_not_offer_is_refused_by_name(environment: dict[str, str], said: str) -> None:
    with pytest.raises(TlsSettingsError, match=said):
        settings.tls_from(environment)


def test_every_mode_says_who_can_check_it_and_the_two_of_our_own_say_assistants_cannot() -> None:
    assert set(settings.WHO_CAN_CHECK) == set(Mode)
    for mode in (Mode.PRIVATE_CA, Mode.PINNED):
        assert "cannot connect" in settings.WHO_CAN_CHECK[mode]
