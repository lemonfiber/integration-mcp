# Copyright (c) 2026 NightWorksIO
"""The certificate in force: started, checked, swapped, logged when renewal fails, and answered for in health."""

import datetime
import json
import logging
from typing import TYPE_CHECKING, Final

import anyio
import pytest

from lemonfiber_mcp.certificates import manager, modes
from lemonfiber_mcp.certificates.manager import Certificates
from lemonfiber_mcp.certificates.settings import Mode
from tests.test_certificate_modes import NOW, files_tls, tls_of

if TYPE_CHECKING:
    import pathlib


class Clock:
    """A clock a test moves by hand."""

    def __init__(self) -> None:
        """Start at the suite's now."""
        self.now = NOW

    def __call__(self) -> datetime.datetime:
        """Return the time it was set to."""
        return self.now


class Failing:
    """A source whose every obtain after the first fails, as a renewal that cannot reach what it needs."""

    mode = Mode.PRIVATE_CA

    def __init__(self, source: modes.Source) -> None:
        """Wrap a source that obtains once."""
        self._source = source
        self._asked = 0

    def obtain(self, now: datetime.datetime) -> modes.Served:
        """Obtain the first time, and fail every time after."""
        self._asked += 1
        if self._asked > 1:
            msg = "The private root's state could not be written."
            raise modes.CertificateError(msg)
        return self._source.obtain(now)

    def announced(self) -> list[str]:
        """Say nothing more."""
        return []

    def due(self, served: modes.Served, /) -> datetime.datetime | None:
        """Say what the wrapped source says."""
        return self._source.due(served)

    @property
    def renewal(self) -> pathlib.Path | None:
        """Keep the record where the wrapped source does."""
        return self._source.renewal


HOUR: Final = datetime.timedelta(hours=1)


def test_starting_loads_the_first_certificate_and_says_who_can_check_it(
    tmp_path: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    source = modes.Pinned(tls_of(tmp_path, Mode.PINNED))
    certificates = Certificates(source, Clock())
    served = certificates.start()
    assert certificates.served == served
    assert "Only a client given its fingerprint can check it" in caplog.text
    assert served.fingerprint in caplog.text
    recorded = json.loads(
        (tmp_path / "state" / "certificates" / "mcp.home.example" / modes.RENEWAL).read_text(),
    )
    assert (recorded["mode"], recorded["outcome"], recorded["healthy"]) == ("pinned", "obtained", True)


def test_nothing_is_in_force_before_the_start(tmp_path: pathlib.Path) -> None:
    certificates = Certificates(modes.Pinned(tls_of(tmp_path, Mode.PINNED)))
    with pytest.raises(modes.CertificateError, match="before the server starts"):
        _ = certificates.served


def test_a_check_with_nothing_due_changes_nothing(tmp_path: pathlib.Path) -> None:
    certificates = Certificates(modes.Pinned(tls_of(tmp_path, Mode.PINNED)), Clock())
    served = certificates.start()
    certificates.check()
    assert certificates.served == served
    assert certificates.health()[1]["outcome"] == "unchanged"


def test_a_renewed_certificate_is_swapped_in(
    tmp_path: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.INFO)
    clock = Clock()
    certificates = Certificates(modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA)), clock)
    first = certificates.start()
    clock.now = first.expires - modes.ISSUED_RENEWED_WITH
    certificates.check()
    assert certificates.served.fingerprint != first.fingerprint
    status, body = certificates.health()
    assert (status, body["outcome"]) == (manager.HEALTHY, "renewed")
    assert body["renewal_due"] == (certificates.served.expires - modes.ISSUED_RENEWED_WITH).isoformat()
    assert "A new certificate is in force" in caplog.text


def test_a_failed_renewal_is_logged_and_critical_hourly_inside_seven_days(
    tmp_path: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    clock = Clock()
    certificates = Certificates(Failing(modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA))), clock)
    served = certificates.start()
    certificates.check()
    assert "could not be renewed" in caplog.text
    assert not [record for record in caplog.records if record.levelno == logging.CRITICAL]
    clock.now = served.expires - manager.UNHEALTHY_WITHIN
    certificates.check()
    clock.now += HOUR / 2
    certificates.check()
    clock.now += HOUR
    certificates.check()
    critical_lines = [record for record in caplog.records if record.levelno == logging.CRITICAL]
    assert len(critical_lines) == 2
    status, body = certificates.health()
    assert (status, body["outcome"]) == (manager.UNHEALTHY, "failed")


def test_a_certificate_nobody_renews_turns_unhealthy_inside_seven_days(
    tmp_path: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    clock = Clock()
    certificates = Certificates(modes.Files(files_tls(tmp_path, lifetime=30)), clock)
    served = certificates.start()
    assert certificates.health()[0] == manager.HEALTHY
    assert certificates.health()[1]["renewal_due"] is None
    clock.now = served.expires - datetime.timedelta(days=3)
    certificates.check()
    assert certificates.health()[0] == manager.UNHEALTHY
    assert "has not been renewed" in caplog.text


@pytest.mark.anyio
async def test_the_watch_checks_until_stopped(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(manager, "CHECK_EVERY", 0.0)
    certificates = Certificates(modes.Pinned(tls_of(tmp_path, Mode.PINNED)), Clock())
    certificates.start()
    checked: list[bool] = []
    original = certificates.check

    def counted() -> None:
        checked.append(True)
        original()

    monkeypatch.setattr(certificates, "check", counted)
    with anyio.move_on_after(0.2):
        await certificates.watch()
    assert checked


def test_the_tls_context_speaks_tls_1_2_at_least() -> None:
    context = manager.server_context()
    assert context.minimum_version is manager.ssl.TLSVersion.TLSv1_2


def test_the_clock_is_utc() -> None:
    assert manager.utc_now().tzinfo is datetime.UTC
