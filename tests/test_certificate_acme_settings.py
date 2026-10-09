# Copyright (c) 2026 NightWorksIO
"""The `acme` mode's settings: Let's Encrypt and TLS-ALPN-01 where nothing is named, and each combination refused."""

import pathlib

import pytest

from lemonfiber_mcp.certificates import acme_settings
from lemonfiber_mcp.certificates.acme_settings import Binding, Challenge
from lemonfiber_mcp.certificates.settings import TlsSettingsError


def test_nothing_named_speaks_to_lets_encrypt_by_tls_alpn_01() -> None:
    settings = acme_settings.acme_from({})
    assert settings == acme_settings.Acme(
        acme_settings.LETS_ENCRYPT,
        None,
        None,
        None,
        Challenge.TLS_ALPN_01,
        None,
    )


def test_everything_named_is_taken_as_given() -> None:
    settings = acme_settings.acme_from(
        {
            acme_settings.DIRECTORY: "https://ca.home.example/acme/directory",
            acme_settings.ROOTS: "/srv/roots.pem",
            acme_settings.CONTACT: "mailto:operator@home.example",
            acme_settings.EAB_KID: "kid-1",
            acme_settings.EAB_HMAC_FILE: "/srv/hmac",
            acme_settings.CHALLENGE: "http-01",
            acme_settings.DNS_PROVIDER: "rfc2136",
        },
    )
    assert settings == acme_settings.Acme(
        "https://ca.home.example/acme/directory",
        pathlib.Path("/srv/roots.pem"),
        "mailto:operator@home.example",
        Binding("kid-1", pathlib.Path("/srv/hmac")),
        Challenge.HTTP_01,
        "rfc2136",
    )


@pytest.mark.parametrize(
    ("environment", "said"),
    [
        ({acme_settings.DIRECTORY: "http://ca.home.example/directory"}, "over HTTPS alone"),
        ({acme_settings.CONTACT: "operator@home.example"}, "`mailto:` address"),
        ({acme_settings.EAB_KID: "kid-1"}, "together or not at all"),
        ({acme_settings.EAB_HMAC_FILE: "/srv/hmac"}, "together or not at all"),
        ({acme_settings.CHALLENGE: "tls-sni-01"}, "is 'tls-sni-01'"),
    ],
)
def test_what_the_contract_does_not_offer_is_refused_by_name(environment: dict[str, str], said: str) -> None:
    with pytest.raises(TlsSettingsError, match=said):
        acme_settings.acme_from(environment)


def test_the_binding_key_is_read_from_its_file(tmp_path: pathlib.Path) -> None:
    held = tmp_path / "hmac"
    held.write_text("c2VjcmV0\n", encoding="utf-8")
    assert Binding("kid-1", held).hmac_key() == "c2VjcmV0"


@pytest.mark.parametrize("content", [b"", b"  \n", b"\xff\xfe"])
def test_a_binding_key_file_that_holds_nothing_readable_is_refused(
    tmp_path: pathlib.Path,
    content: bytes,
) -> None:
    held = tmp_path / "hmac"
    held.write_bytes(content)
    with pytest.raises(TlsSettingsError, match=acme_settings.EAB_HMAC_FILE):
        Binding("kid-1", held).hmac_key()


def test_a_missing_binding_key_file_is_refused(tmp_path: pathlib.Path) -> None:
    with pytest.raises(TlsSettingsError, match="could not be read"):
        Binding("kid-1", tmp_path / "missing").hmac_key()
