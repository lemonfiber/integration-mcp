# Copyright (c) 2026 NightWorksIO
"""The certificate in force: started, checked, swapped, logged when renewal fails, and answered for in health."""

import dataclasses
import datetime
import json
import logging
import threading
from typing import TYPE_CHECKING, Final

import anyio
import pytest

from lemonfiber_mcp.certificates import manager, modes
from lemonfiber_mcp.certificates.alpn import Challenges
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

    def first(self, now: datetime.datetime) -> modes.Served:
        """Obtain, as the first time."""
        return self.obtain(now)

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


class StandingIn:
    """A source whose first certificate stands in, until one is issued."""

    mode = Mode.ACME

    def __init__(self, source: modes.Source) -> None:
        """Wrap a source whose certificate is issued once `issued` is set."""
        self._source = source
        self.issued = False

    def first(self, now: datetime.datetime) -> modes.Served:
        """Return the wrapped source's certificate, standing in."""
        return dataclasses.replace(self._source.first(now), standing_in=True)

    def obtain(self, now: datetime.datetime) -> modes.Served:
        """Return the certificate standing in, or the one issued once it is."""
        return self._source.obtain(now) if self.issued else self.first(now)

    def announced(self) -> list[str]:
        """Say nothing more."""
        return []

    def due(self, _: modes.Served, /) -> datetime.datetime | None:
        """Say nothing is due."""
        return None

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
    certificates = Certificates(source, Challenges(tmp_path), Clock())
    served = certificates.start()
    assert certificates.served == served
    assert caplog.messages[0].startswith(
        "serving the pinned certificate. Only a client given its fingerprint",
    )
    assert f"The certificate's fingerprint, for each client to pin: {served.fingerprint}" in caplog.messages
    written = (tmp_path / "state" / "certificates" / "mcp.home.example" / modes.RENEWAL).read_text()
    recorded = json.loads(written)
    assert (recorded["mode"], recorded["outcome"], recorded["healthy"]) == ("pinned", "obtained", True)
    assert recorded["last_attempt"] == NOW.isoformat()
    assert written == json.dumps(recorded, indent=2) + "\n"


def test_nothing_is_in_force_before_the_start(tmp_path: pathlib.Path) -> None:
    certificates = Certificates(modes.Pinned(tls_of(tmp_path, Mode.PINNED)), Challenges(tmp_path))
    with pytest.raises(modes.CertificateError, match="before the server starts"):
        _ = certificates.served


def test_a_check_with_nothing_due_changes_nothing(tmp_path: pathlib.Path) -> None:
    certificates = Certificates(modes.Pinned(tls_of(tmp_path, Mode.PINNED)), Challenges(tmp_path), Clock())
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
    certificates = Certificates(
        modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA)),
        Challenges(tmp_path),
        clock,
    )
    first = certificates.start()
    clock.now = first.expires - modes.ISSUED_RENEWED_WITH
    certificates.check()
    assert certificates.served.fingerprint != first.fingerprint
    status, body = certificates.health()
    assert (status, body["outcome"]) == (manager.HEALTHY, "renewed")
    assert body["last_attempt"] == clock.now.isoformat()
    valid_until = certificates.served.expires.isoformat()
    assert f"A new certificate is in force, valid until {valid_until}." in caplog.messages
    assert body["renewal_due"] == (certificates.served.expires - modes.ISSUED_RENEWED_WITH).isoformat()
    assert "A new certificate is in force" in caplog.text


def test_a_failed_renewal_is_logged_and_critical_hourly_inside_seven_days(
    tmp_path: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    clock = Clock()
    certificates = Certificates(
        Failing(modes.PrivateCa(tls_of(tmp_path, Mode.PRIVATE_CA))),
        Challenges(tmp_path),
        clock,
    )
    served = certificates.start()
    certificates.check()
    assert f"The certificate could not be renewed. It has {served.expires - NOW} left." in caplog.messages
    assert not [record for record in caplog.records if record.levelno == logging.CRITICAL]
    clock.now = served.expires - manager.UNHEALTHY_WITHIN
    certificates.check()
    clock.now += HOUR / 2
    certificates.check()
    clock.now += HOUR / 2
    certificates.check()
    critical_lines = [record.getMessage() for record in caplog.records if record.levelno == logging.CRITICAL]
    assert critical_lines == [
        f"The certificate in force expires in {left} and has not been renewed."
        for left in (manager.UNHEALTHY_WITHIN, manager.UNHEALTHY_WITHIN - HOUR)
    ]
    status, body = certificates.health()
    assert (status, body["outcome"]) == (manager.UNHEALTHY, "failed")


def test_a_certificate_nobody_renews_turns_unhealthy_inside_seven_days(
    tmp_path: pathlib.Path,
    caplog: pytest.LogCaptureFixture,
) -> None:
    clock = Clock()
    certificates = Certificates(modes.Files(files_tls(tmp_path, lifetime=30)), Challenges(tmp_path), clock)
    served = certificates.start()
    assert certificates.health()[0] == manager.HEALTHY
    assert certificates.health()[1]["renewal_due"] is None
    clock.now = served.expires - datetime.timedelta(days=3)
    certificates.check()
    assert certificates.health()[0] == manager.UNHEALTHY
    assert "has not been renewed" in caplog.text


@pytest.mark.anyio
async def test_the_watch_attempts_at_once_and_then_every_minute_each_in_a_thread_of_its_own(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(manager, "CHECK_EVERY", 0.0)
    certificates = Certificates(modes.Pinned(tls_of(tmp_path, Mode.PINNED)), Challenges(tmp_path), Clock())
    certificates.start()
    threads: list[int] = []
    original = certificates.attempt

    def counted() -> modes.Served | None:
        threads.append(threading.get_ident())
        return original()

    monkeypatch.setattr(certificates, "attempt", counted)
    with anyio.move_on_after(0.2):
        await certificates.watch()
    assert len(threads) > 1
    assert threading.get_ident() not in threads


def test_a_certificate_standing_in_is_served_and_unhealthy_until_the_first_is_issued(
    tmp_path: pathlib.Path,
) -> None:
    standing = StandingIn(modes.Pinned(tls_of(tmp_path, Mode.PINNED)))
    certificates = Certificates(standing, Challenges(tmp_path), Clock())
    assert certificates.start().standing_in
    status, body = certificates.health()
    assert (status, body["outcome"]) == (manager.UNHEALTHY, manager.PENDING)
    certificates.check()
    assert certificates.health()[1]["outcome"] == manager.PENDING
    standing.issued = True
    certificates.check()
    assert certificates.health() == (manager.HEALTHY, certificates.health()[1])
    assert certificates.health()[1]["outcome"] == "renewed"


def test_the_tls_context_is_a_servers_answering_the_challenges_pending(tmp_path: pathlib.Path) -> None:
    pending = Challenges(tmp_path)
    context = manager.server_context(pending)
    assert context.minimum_version is manager.ssl.TLSVersion.TLSv1_2
    assert context.protocol is manager.ssl.PROTOCOL_TLS_SERVER
    assert context.pending is pending
    certificates = Certificates(StandingIn(modes.Pinned(tls_of(tmp_path, Mode.PINNED))), pending)
    assert certificates.context.pending is pending


def test_the_clock_is_utc() -> None:
    assert manager.utc_now().tzinfo is datetime.UTC
