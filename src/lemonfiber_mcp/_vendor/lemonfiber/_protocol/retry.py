# Copyright (c) 2026 NightWorksIO
"""Asking a read again before a passing failure is reported.

A read that met nothing, or a gateway in front of lemonfiber that could not
reach it, is asked again, a little later each time and within the wait its
call was given. Those are the failures a moment can clear: a phone waking its
radio, a proxy whose upstream is restarting. A read changes nothing, so asking
it again costs only the wait. Every other answer is lemonfiber's own and is
taken on the first attempt, and an action is never asked again.
"""

from dataclasses import dataclass
from http import HTTPStatus
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from lemonfiber._protocol.calls import Answer

ATTEMPTS: Final = 3
"""How many times a read is asked in all: once, and twice more."""

FIRST_PAUSE: Final = 0.25
"""Seconds before a read is asked again the first time; each time after waits twice as long."""

PASSED_ON: Final = frozenset(
    {HTTPStatus.BAD_GATEWAY, HTTPStatus.SERVICE_UNAVAILABLE, HTTPStatus.GATEWAY_TIMEOUT},
)
"""What a gateway in front of lemonfiber answers when it could not reach it, or is waiting for it."""


def is_passing(answer: Answer | None) -> bool:
    """Tell whether an attempt ended in a failure a moment can clear: nothing answered, or a gateway could not reach lemonfiber."""
    return answer is None or answer.status in PASSED_ON


@dataclass(slots=True)
class Attempts:
    """The attempts one call makes, all within the wait it was given."""

    again: bool
    """Whether the call is one that may be asked again: a read."""
    wait: float
    """Seconds every attempt together may take."""
    started: float
    """When the first attempt began, by the clock the call is timed with."""
    made: int = 0

    def left(self, now: float) -> float:
        """Return how many seconds of the wait are left at `now`."""
        return self.wait - (now - self.started)

    def pause(self, answer: Answer | None, now: float) -> float | None:
        """Count one attempt, and return how long to wait before the next, or None where this one's outcome stands.

        Another attempt is made only for a read, only after a passing failure,
        only while fewer than `ATTEMPTS` have been made, and only where the
        pause before it leaves some of the wait for the attempt itself.
        """
        self.made += 1
        if not self.again or self.made >= ATTEMPTS or not is_passing(answer):
            return None
        pause = FIRST_PAUSE * 2 ** (self.made - 1)
        if self.left(now) <= pause:
            return None
        return pause
