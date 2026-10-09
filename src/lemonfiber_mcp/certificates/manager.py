# Copyright (c) 2026 NightWorksIO
"""The certificate in force: loaded at start, checked every minute, swapped in without dropping a connection.

Every check asks the source for the certificate to serve now. A new one is
loaded into the same TLS context, which new handshakes take as soon as it
lands while connections already open carry on. A check that fails is logged
with the time left on the certificate in force, and as critical once an hour
inside seven days of its expiry, when the health answer turns unhealthy too.
"""

import datetime
import json
import logging
import ssl
from typing import TYPE_CHECKING, Final

import anyio

from lemonfiber_mcp.certificates import state
from lemonfiber_mcp.certificates.alpn import Answering
from lemonfiber_mcp.certificates.modes import CertificateError
from lemonfiber_mcp.certificates.settings import WHO_CAN_CHECK

if TYPE_CHECKING:
    from collections.abc import Callable

    from lemonfiber_mcp.certificates.alpn import Challenges
    from lemonfiber_mcp.certificates.modes import Served, Source

CHECK_EVERY: Final = 60.0
"""Seconds between checks: a changed file or a due renewal is taken within a minute."""
CRITICAL_EVERY: Final = datetime.timedelta(hours=1)
UNHEALTHY_WITHIN: Final = datetime.timedelta(days=7)
"""How close to its expiry a certificate is when the health answer turns unhealthy."""
ALPN: Final = ("http/1.1",)
HEALTHY: Final = 200
UNHEALTHY: Final = 503
PENDING: Final = "pending"
"""The outcome while a certificate stands in for the first one an authority has yet to issue."""

logger = logging.getLogger(__name__)


def utc_now() -> datetime.datetime:
    """Return the time now, in UTC."""
    return datetime.datetime.now(datetime.UTC)


def server_context(pending: Challenges) -> Answering:
    """Return the TLS context every connection is answered with: TLS 1.2 at least, HTTP/1.1, and TLS-ALPN-01."""
    context = Answering(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.set_alpn_protocols(list(ALPN))
    context.pending = pending
    return context


class Certificates:
    """The certificate in force, where it came from, and how its last check went."""

    def __init__(
        self,
        source: Source,
        pending: Challenges,
        clock: Callable[[], datetime.datetime] = utc_now,
    ) -> None:
        """Hold the source, a context nothing has been loaded into yet, and the TLS-ALPN-01 answers it gives."""
        self._source = source
        self._clock = clock
        self.context = server_context(pending)
        self._served: Served | None = None
        self._last_attempt: datetime.datetime | None = None
        self._outcome = "none"
        self._last_critical: datetime.datetime | None = None

    @property
    def served(self) -> Served:
        """Return the certificate in force; `start` loads the first."""
        if self._served is None:
            msg = "No certificate is in force before the server starts."
            raise CertificateError(msg)
        return self._served

    def _load(self, served: Served) -> None:
        self.context.load_cert_chain(served.chain, served.key)
        self._served = served
        for line in self._source.announced():
            logger.info("%s", line)

    def _recorded(self) -> None:
        """Write the record of renewal where the source keeps one."""
        if self._source.renewal is not None:
            state.write(self._source.renewal, self.record())

    def start(self) -> Served:
        """Load the first certificate, refusing to start where there is none to serve, and say who can check it."""
        served = self._source.first(self._clock())
        logger.info(
            "serving the %s certificate. %s",
            self._source.mode.value,
            WHO_CAN_CHECK[self._source.mode],
        )
        self._load(served)
        self._last_attempt = self._clock()
        self._outcome = PENDING if served.standing_in else "obtained"
        self._recorded()
        return served

    def attempt(self) -> Served | None:
        """Ask the source for the certificate to serve now, and return it where it is not the one in force.

        Nothing is loaded here, so an attempt that waits on an authority runs in
        a thread of its own while the server answers.
        """
        now = self._clock()
        self._last_attempt = now
        left = self.served.expires - now
        try:
            served = self._source.obtain(now)
        except CertificateError, state.StateError, OSError, ValueError:
            self._outcome = "failed"
            logger.exception("The certificate could not be renewed. It has %s left.", left)
            self._critical(now, left)
            self._recorded()
            return None
        if served != self.served:
            return served
        self._outcome = PENDING if served.standing_in else "unchanged"
        self._critical(now, left)
        return None

    def apply(self, served: Served | None) -> None:
        """Put a new certificate in force, where an attempt returned one."""
        if served is None:
            return
        self._load(served)
        self._outcome = "renewed"
        logger.info("A new certificate is in force, valid until %s.", served.expires.isoformat())
        self._recorded()

    def check(self) -> None:
        """Ask the source for the certificate to serve now, swapping it in where it changed, logging where it failed."""
        self.apply(self.attempt())

    def _critical(self, now: datetime.datetime, left: datetime.timedelta) -> None:
        if left > UNHEALTHY_WITHIN:
            return
        if self._last_critical is not None and now - self._last_critical < CRITICAL_EVERY:
            return
        self._last_critical = now
        logger.critical("The certificate in force expires in %s and has not been renewed.", left)

    def health(self) -> tuple[int, dict[str, object]]:
        """Return the health answer: its status, and the mode, the expiry and the last check, nothing else."""
        now = self._clock()
        expires = self.served.expires
        body: dict[str, object] = {
            "mode": self._source.mode.value,
            "expires": expires.isoformat(),
            "renewal_due": None if (due := self._source.due(self.served)) is None else due.isoformat(),
            "last_attempt": None if self._last_attempt is None else self._last_attempt.isoformat(),
            "outcome": self._outcome,
        }
        ready = not self.served.standing_in and expires - now > UNHEALTHY_WITHIN
        return (HEALTHY if ready else UNHEALTHY), body

    def record(self) -> bytes:
        """Return what `renewal.json` holds of the certificate in force: its mode, when it is due, and the last check."""
        status, body = self.health()
        return json.dumps({**body, "healthy": status == HEALTHY}, indent=2).encode() + b"\n"

    async def watch(self) -> None:
        """Check at once, then every minute, for as long as the server runs, each attempt in a thread of its own."""
        while True:
            self.apply(await anyio.to_thread.run_sync(self.attempt))
            await anyio.sleep(CHECK_EVERY)
