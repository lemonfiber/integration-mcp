# Copyright (c) 2026 NightWorksIO
"""The one place a key or a pin is taken out of anything the server says.

Every tool result, error, resource and log line passes through `withhold`
before it leaves. A key is recognised by the prefix the core gives every key
it mints, so a key is withheld whether or not this process was told it; the
pin is withheld because it was configured, in any letter case.
"""

import logging
import re
from typing import TYPE_CHECKING, Final, override

if TYPE_CHECKING:
    from collections.abc import Iterable

WITHHELD: Final = "[withheld]"
"""What stands where a secret was."""

KEY: Final = re.compile(r"lfk_[0-9A-Za-z]*")
"""A value shaped like an integration key: the core's prefix and the letters and digits after it.

Letters and digits only, so a key inside a JSON string is replaced without its
closing quote, and what is withheld stays the document it was.
"""


class Withholding:
    """What this process withholds beyond every key: the values it was configured with."""

    __slots__ = ("_known",)

    def __init__(self, known: Iterable[str] = ()) -> None:
        """Hold the configured values to withhold, longest first so none is left half-replaced."""
        self._known: tuple[re.Pattern[str], ...] = tuple(
            re.compile(re.escape(value), re.IGNORECASE)
            for value in sorted({value for value in known if value}, key=len, reverse=True)
        )

    def withhold(self, text: str) -> str:
        """Return the text with every key and every configured value replaced."""
        for known in self._known:
            text = known.sub(WITHHELD, text)
        return KEY.sub(WITHHELD, text)

    @override
    def __repr__(self) -> str:
        return f"Withholding({len(self._known)} values)"


class WithholdingFormatter(logging.Formatter):
    """A formatter whose every line, traceback included, has passed through `withhold`."""

    def __init__(self, withholding: Withholding, fmt: str | None = None) -> None:
        """Format as `logging.Formatter` does, then withhold."""
        super().__init__(fmt)
        self._withholding = withholding

    @override
    def format(self, record: logging.LogRecord) -> str:
        return self._withholding.withhold(super().format(record))


def install(withholding: Withholding) -> logging.Handler:
    """Send every log line to standard error through `withhold`, replacing whatever handlers were there.

    Standard error, because over stdio standard output is the protocol itself.
    """
    handler = logging.StreamHandler()
    handler.setFormatter(WithholdingFormatter(withholding, "%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()
    for existing in list(root.handlers):
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    return handler
