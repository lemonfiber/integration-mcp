# Copyright (c) 2026 NightWorksIO
"""What can go wrong between a caller and lemonfiber, each as its own type.

Every exception this package raises is a `LemonfiberError`. Each subclass is one
thing a caller can act on, and its message is a plain sentence for a person. A
refusal is read from its code where the contract lists it, and from its status
alone where it carries none.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lemonfiber._generated import Problem, RefusalCode


class LemonfiberError(Exception):
    """Something stood between the caller and an answer from lemonfiber."""


class ConfigurationError(LemonfiberError, ValueError):
    """A client was given something it cannot be built with, and nothing was sent."""


class AddressRefusedError(ConfigurationError):
    """An address, or the pin given with it, is not one this client will reach."""


class CredentialRefusedError(ConfigurationError):
    """A credential is not one a header can carry."""


class UnreachableError(LemonfiberError):
    """Nothing answered at the address, or what answered was not lemonfiber."""


class CertificateRefusedError(LemonfiberError):
    """The stack presented a certificate other than the one this client holds it to, and nothing was sent."""


class UnreadableResponseError(LemonfiberError):
    """An answer arrived that is not a document lemonfiber writes."""

    def __init__(self, what: str) -> None:
        """Say which part of the answer could not be read."""
        super().__init__(f"That answer did not come from lemonfiber: {what}.")
        self.what = what


class ApiVersionMismatchError(LemonfiberError):
    """The stack answered in a version of the interface this package does not speak."""

    def __init__(self, spoken: int, served: int) -> None:
        """Name the version this package speaks and the one the stack answered in."""
        super().__init__(
            f"This client speaks version {spoken} of lemonfiber's interface and the stack answered "
            f"in version {served}. Nothing from that answer was used; update whichever of the two is older.",
        )
        self.spoken = spoken
        self.served = served


class UnknownKindError(LemonfiberError):
    """The stack answered with a kind of document this package was not generated with."""

    def __init__(self, kind: str) -> None:
        """Name the kind that arrived."""
        super().__init__(
            f"The stack answered with a {kind!r} document, which this client does not know. "
            "The stack is newer than this client; update the client.",
        )
        self.kind = kind


class UnexpectedKindError(LemonfiberError):
    """An answer was a different kind of document from the one it was read as."""

    def __init__(self, expected: str, received: str) -> None:
        """Name the kind that was expected and the kind that arrived."""
        super().__init__(
            f"The stack answered with a {received!r} document where a {expected!r} one was expected.",
        )
        self.expected = expected
        self.received = received


class RefusedError(LemonfiberError):
    """lemonfiber answered, and turned the request down.

    `code` is why, where the contract lists the code it carried; a caller
    decides what a refusal means from it and never from the sentence, which is
    written for a person. `problem` is the whole problem document, where the
    refusal carried one: its `detail` quotes what a service said and is fit to
    show the person who asked, not to forward.
    """

    def __init__(
        self,
        sentence: str,
        *,
        status: int,
        code: RefusalCode | None = None,
        problem: Problem | None = None,
    ) -> None:
        """Carry the sentence lemonfiber refused with, the status, and the code and problem where there were any."""
        super().__init__(sentence)
        self.sentence = sentence
        self.status = status
        self.code = code
        self.problem = problem


class NotAdmittedError(RefusedError):
    """The credential is not one this stack admits: absent, wrong, expired, revoked or from another run."""


class DeclinedError(RefusedError):
    """The credential was read, and what it objects to is who is asking or where from; a new one would not help."""


class MissingError(RefusedError):
    """What the request named, this product does not have. Asking again unchanged will not succeed."""


class MisaskedError(RefusedError):
    """The request could not be answered as it was asked."""


class BusyError(RefusedError):
    """Other work held the stack; the same request may be sent again once it is done."""


class FailedError(RefusedError):
    """Nothing about the request was wrong; the machine could not answer it."""


class TooManyAttemptsError(RefusedError):
    """Too many wrong answers lately. `retry_after` is how many seconds are left, where the stack said."""

    def __init__(
        self,
        sentence: str,
        *,
        status: int,
        retry_after: int | None,
        code: RefusalCode | None = None,
        problem: Problem | None = None,
    ) -> None:
        """Carry the refusal and how long is left, where the stack said."""
        super().__init__(sentence, status=status, code=code, problem=problem)
        self.retry_after = retry_after


class PasswordRefusedError(RefusedError):
    """The password offered at the door was wrong, or none is configured."""


class NoSuchJobError(LemonfiberError):
    """The name is not one this run of lemonfiber issued; names do not outlive the run that issued them."""

    def __init__(self, job: str) -> None:
        """Name the job that was asked about."""
        super().__init__(f"lemonfiber has no work by the name {job!r} in this run.")
        self.job = job


class StillRunningError(LemonfiberError):
    """Work was followed for as long as the caller allowed, and it is still going."""

    def __init__(self, job: str, waited: float) -> None:
        """Name the job and how long it was followed for."""
        super().__init__(f"The work {job!r} was still going after {waited:g} seconds.")
        self.job = job
        self.waited = waited


class StreamLostError(LemonfiberError):
    """The live stream broke and could not be reopened; everything held is the last thing confirmed."""

    def __init__(self, attempts: int) -> None:
        """Say how many attempts to reopen it failed."""
        super().__init__(
            f"The live stream broke and {attempts} attempts to reopen it failed. Everything shown is the "
            "last thing confirmed, not what is true now.",
        )
        self.attempts = attempts
