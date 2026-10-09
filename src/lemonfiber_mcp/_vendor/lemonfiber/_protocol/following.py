# Copyright (c) 2026 NightWorksIO
"""How work is followed until it is no longer going: by name, at an interval, within a limit."""

from typing import TYPE_CHECKING, Final

from lemonfiber.problems import StillRunningError

if TYPE_CHECKING:
    from lemonfiber._generated import JobEnvelope

DEFAULT_EVERY: Final = 1.0
"""How many seconds apart work being followed is asked about."""


def job_name(job: str | JobEnvelope) -> str:
    """Return the name work goes by, given the name or the envelope that answered with it."""
    return job if isinstance(job, str) else job["data"]["job"]


def next_wait(job: str, started: float, now: float, every: float, within: float | None) -> float:
    """Return how long to wait before asking about work again, or raise once `within` has passed."""
    if within is None:
        return every
    waited = now - started
    if waited >= within:
        raise StillRunningError(job, waited)
    return min(every, within - waited)
