# Copyright (c) 2026 NightWorksIO
"""What a client proves itself with: a per-run token, a session's secret or an integration key, and a session itself."""

import re
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final, override

from lemonfiber.problems import CredentialRefusedError

if TYPE_CHECKING:
    import datetime

CREDENTIAL_HEADER: Final = "X-Lemonfiber-Token"
"""The one header every credential travels in, and never a URL."""

VISIBLE: Final = re.compile(r"^[\x21-\x7e]+$")
"""What a credential is written in: visible ASCII, nothing a header could be split on."""


class Credential:
    """A secret the stack admits, carried in `X-Lemonfiber-Token` and shown nowhere else.

    The per-run token lemonfiber prints, the secret a session was opened with,
    and an integration key the operator minted are all one of these: the stack
    reads one credential header, and what it admits is its own decision.
    """

    __slots__ = ("_secret",)

    def __init__(self, secret: str) -> None:
        """Hold a secret, refusing one a header cannot carry."""
        if not VISIBLE.match(secret):
            msg = "A credential is written in visible ASCII with no spaces; what was given is not one."
            raise CredentialRefusedError(msg)
        self._secret = secret

    def header(self) -> dict[str, str]:
        """Return the header the credential travels in."""
        return {CREDENTIAL_HEADER: self._secret}

    @override
    def __repr__(self) -> str:
        return "Credential(hidden)"


@dataclass(frozen=True, slots=True)
class Session:
    """A session opened at the door: the credential it is carried by, when it stops being one, and whose it is.

    `member` is the household member the session is for; absent is the operator.
    """

    credential: Credential
    until: datetime.datetime
    member: str | None
