# Copyright (c) 2026 NightWorksIO
"""Where the served certificate comes from: the operator's files, a pinned one, and a private root's."""

import datetime
import ipaddress
from typing import TYPE_CHECKING, Final

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

from lemonfiber_mcp.certificates import making, modes, state
from lemonfiber_mcp.certificates.modes import CertificateError
from lemonfiber_mcp.certificates.settings import KeyType, Mode, Name, Tls

if TYPE_CHECKING:
    import pathlib

NOW: Final = datetime.datetime(2026, 10, 9, tzinfo=datetime.UTC)
NAMES: Final[tuple[Name, ...]] = ("mcp.home.example", ipaddress.ip_address("192.168.1.42"))


def tls_of(root: pathlib.Path, mode: Mode, names: tuple[Name, ...] = NAMES, **files: pathlib.Path) -> Tls:
    """Return settings for a mode, keeping state under `root`."""
    return Tls(
        mode=mode,
        names=names,
        certificate=files.get("certificate"),
        private_key=files.get("private_key"),
        key_type=KeyType.EC_P256,
        state=state.kept(root / "state"),
    )


def operator_files(
    root: pathlib.Path,
    names: tuple[Name, ...] = NAMES,
    *,
    lifetime: int = 90,
) -> tuple[pathlib.Path, pathlib.Path]:
    """Write a certificate and key as an operator would bring them, and return their paths."""
    key = making.generated(KeyType.EC_P256)
    made = making.leaf_extensions(
        making.builder(making.named(str(names[0])), key, datetime.timedelta(days=lifetime), NOW),
        names,
    )
    leaf = made.issuer_name(x509.Name([x509.NameAttribute(x509.NameOID.COMMON_NAME, "operator")])).sign(
        key,
        making.hashes.SHA256(),
    )
    certificate, private_key = root / "operator.pem", root / "operator.key"
    certificate.write_bytes(making.certificate_pem(leaf))
    private_key.write_bytes(making.key_pem(key))
    return certificate, private_key


def files_tls(root: pathlib.Path, *, lifetime: int = 90) -> Tls:
    """Return settings for the operator's files, written for the names and valid for `lifetime` days."""
    certificate, private_key = operator_files(root, lifetime=lifetime)
    return tls_of(root, Mode.FILES, certificate=certificate, private_key=private_key)


def test_the_operators_files_are_served_as_they_are(tmp_path: pathlib.Path) -> None:
    source = modes.Files(files_tls(tmp_path))
    served = source.obtain(NOW)
    assert served.chain == tmp_path / "operator.pem"
    assert making.covered(served.leaf) == set(NAMES)
    assert source.announced() == []
    assert source.due(served) is None
    assert source.renewal is None


def test_a_wildcard_covers_one_label(tmp_path: pathlib.Path) -> None:
    certificate, private_key = operator_files(tmp_path, ("*.home.example",))
    covered = tls_of(
        tmp_path,
        Mode.FILES,
        ("mcp.home.example",),
        certificate=certificate,
        private_key=private_key,
    )
    assert modes.Files(covered).obtain(NOW)
    deeper = tls_of(
        tmp_path,
        Mode.FILES,
        ("a.mcp.home.example",),
        certificate=certificate,
        private_key=private_key,
    )
    source = modes.Files(deeper)
    with pytest.raises(CertificateError, match="does not cover"):
        source.obtain(NOW)


def test_files_that_cannot_be_read_are_refused(tmp_path: pathlib.Path) -> None:
    tls = files_tls(tmp_path)
    (tmp_path / "operator.key").write_text("not a key", encoding="utf-8")
    source = modes.Files(tls)
    with pytest.raises(CertificateError, match="could not be read as PEM"):
        source.obtain(NOW)


def test_a_key_that_is_not_the_certificates_is_refused(tmp_path: pathlib.Path) -> None:
    tls = files_tls(tmp_path)
    (tmp_path / "operator.key").write_bytes(making.key_pem(making.generated(KeyType.EC_P256)))
    source = modes.Files(tls)
    with pytest.raises(CertificateError, match="does not hold the key"):
        source.obtain(NOW)


def test_an_expired_certificate_is_refused(tmp_path: pathlib.Path) -> None:
    source = modes.Files(files_tls(tmp_path, lifetime=1))
    later = NOW + datetime.timedelta(days=2)
    with pytest.raises(CertificateError, match="expired on"):
        source.obtain(later)


def test_a_pinned_certificate_is_made_once_and_kept(tmp_path: pathlib.Path) -> None:
    source = modes.Pinned(tls_of(tmp_path, Mode.PINNED))
    assert source.announced() == []
    first = source.obtain(NOW)
    assert first.leaf.issuer == first.leaf.subject
    assert source.announced() == [
        f"The certificate's fingerprint, for each client to pin: {first.fingerprint}",
    ]
    again = modes.Pinned(tls_of(tmp_path, Mode.PINNED)).obtain(NOW + datetime.timedelta(days=400))
    assert again.fingerprint == first.fingerprint
    assert source.due(first) is None
    assert source.renewal == tmp_path / "state" / "certificates" / "mcp.home.example" / modes.RENEWAL


def test_a_pinned_certificate_for_other_names_is_made_anew_and_said_to_be_new(tmp_path: pathlib.Path) -> None:
    first = modes.Pinned(tls_of(tmp_path, Mode.PINNED)).obtain(NOW)
    source = modes.Pinned(tls_of(tmp_path, Mode.PINNED, ("mcp.home.example",)))
    second = source.obtain(NOW)
    assert second.fingerprint != first.fingerprint
    assert source.announced()[-1] == "This certificate is new: give every client this fingerprint again."


def test_a_pinned_certificate_is_replaced_on_command(tmp_path: pathlib.Path) -> None:
    source = modes.Pinned(tls_of(tmp_path, Mode.PINNED))
    first = source.obtain(NOW)
    replaced = source.replace(NOW)
    assert replaced.fingerprint != first.fingerprint
    assert source.obtain(NOW).fingerprint == replaced.fingerprint


def test_a_private_root_issues_the_served_certificate_and_keeps_both(tmp_path: pathlib.Path) -> None:
    source = modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA))
    served = source.obtain(NOW)
    root = x509.load_pem_x509_certificate(source.root_file.read_bytes())
    served.leaf.verify_directly_issued_by(root)
    assert making.covered(served.leaf) == set(NAMES)
    assert source.due(served) == served.expires - modes.ISSUED_RENEWED_WITH
    assert source.obtain(NOW + datetime.timedelta(days=5)).fingerprint == served.fingerprint
    said = source.announced()
    install = (
        f"Install the root at {source.root_file} on each device that is to connect; it is also served at "
        f"/root.pem. Its fingerprint: {making.fingerprint(root)}"
    )
    assert said == [install]
    assert source.renewal is not None


def test_a_private_root_says_nothing_before_it_is_made(tmp_path: pathlib.Path) -> None:
    assert modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA)).announced() == []


def test_the_next_certificate_is_issued_once_ten_days_are_left(tmp_path: pathlib.Path) -> None:
    source = modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA))
    served = source.obtain(NOW)
    renewed = source.obtain(NOW + making.ISSUED_LIFETIME - modes.ISSUED_RENEWED_WITH)
    assert renewed.fingerprint != served.fingerprint


def test_a_kept_certificate_another_root_issued_is_issued_again(tmp_path: pathlib.Path) -> None:
    source = modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA))
    served = source.obtain(NOW)
    (tmp_path / "state" / "ca" / modes.ROOT).unlink()
    reissued = modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA)).obtain(NOW)
    assert reissued.fingerprint != served.fingerprint


def test_a_name_the_root_does_not_cover_waits_for_a_replacement_root(tmp_path: pathlib.Path) -> None:
    modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA)).obtain(NOW)
    wider = (*NAMES, "assistant.home.example")
    source = modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA, wider))
    served = source.obtain(NOW)
    assert making.covered(served.leaf) == set(NAMES)
    said = source.announced()
    assert "A replacement root waits to be installed" in said[1]
    assert said[2].startswith("assistant.home.example is not served until the replacement root is in force")
    assert source.switch()
    after = source.obtain(NOW)
    assert making.covered(after.leaf) == set(wider)
    assert source.announced()[1:] == []


def test_names_none_of_which_the_root_covers_keep_the_roots_own(tmp_path: pathlib.Path) -> None:
    modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA, ("old.example",))).obtain(NOW)
    served = modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA, ("new.example",))).obtain(NOW)
    assert making.covered(served.leaf) == {"old.example"}


def test_a_root_with_a_year_left_makes_its_replacement_and_switches_a_month_before_it_ends(
    tmp_path: pathlib.Path,
) -> None:
    source = modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA))
    source.obtain(NOW)
    first_root = source.root_file.read_bytes()
    ageing = NOW + making.ROOT_LIFETIME - modes.ROOT_REPLACED_WITH
    source.obtain(ageing)
    assert (tmp_path / "state" / "ca" / modes.NEXT_ROOT).is_file()
    assert source.root_file.read_bytes() == first_root
    ending = NOW + making.ROOT_LIFETIME - modes.ROOT_SWITCHED_WITH
    served = source.obtain(ending)
    assert source.root_file.read_bytes() != first_root
    assert not (tmp_path / "state" / "ca" / modes.NEXT_ROOT).exists()
    served.leaf.verify_directly_issued_by(x509.load_pem_x509_certificate(source.root_file.read_bytes()))


def test_a_replacement_root_is_made_on_command_once(tmp_path: pathlib.Path) -> None:
    source = modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA))
    made = source.replace(NOW)
    assert source.replace(NOW) == made
    assert source.switch()
    assert not source.switch()


def test_a_key_of_a_kind_this_server_does_not_make_is_refused(tmp_path: pathlib.Path) -> None:
    path = tmp_path / "key.pem"
    path.write_bytes(
        ed25519.Ed25519PrivateKey.generate().private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        ),
    )
    with pytest.raises(CertificateError, match="does not make"):
        modes.private_key_of(path)


@pytest.mark.parametrize(
    ("mode", "kind"),
    [(Mode.PINNED, modes.Pinned), (Mode.PRIVATE_CA, modes.PrivateCa)],
)
def test_each_mode_has_its_source(tmp_path: pathlib.Path, mode: Mode, kind: type) -> None:
    assert isinstance(modes.source_of(tls_of(tmp_path, mode)), kind)


def test_the_operators_files_have_their_source(tmp_path: pathlib.Path) -> None:
    assert isinstance(modes.source_of(files_tls(tmp_path)), modes.Files)


def test_acme_is_refused_by_this_version(tmp_path: pathlib.Path) -> None:
    tls = tls_of(tmp_path, Mode.ACME, ("mcp.example.org",))
    with pytest.raises(CertificateError, match="does not serve yet"):
        modes.source_of(tls)
