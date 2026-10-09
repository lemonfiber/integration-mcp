# Copyright (c) 2026 NightWorksIO
"""What an answer that is not a success says went wrong, each as the problem it is."""

from http import HTTPStatus
from typing import TYPE_CHECKING, Final, TypeIs

from lemonfiber._generated import REFUSAL_CODES, Problem, RefusalCode, is_refusal_code
from lemonfiber.envelope import expect, parse_envelope
from lemonfiber.problems import (
    BusyError,
    DeclinedError,
    FailedError,
    LemonfiberError,
    MisaskedError,
    MissingError,
    NotAdmittedError,
    RefusedError,
    TooManyAttemptsError,
    UnreachableError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from lemonfiber._protocol.calls import Answer

TURNED_AWAY: Final = frozenset({HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN})
"""The statuses a request is turned away with for who is asking or where from."""

THE_CREDENTIAL: Final = "NOT_ADMITTED"
"""The registry name of the refusal that is the credential itself, looked up rather than its code written here."""

MEANT_BY: Final[Mapping[int, type[RefusedError]]] = {
    HTTPStatus.BAD_REQUEST: MisaskedError,
    HTTPStatus.NOT_FOUND: MissingError,
    HTTPStatus.CONFLICT: BusyError,
}
"""What a status says the request got wrong; any other status is the machine's."""

REFUSED_OUTRIGHT: Final = frozenset(
    {HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND},
)
"""Statuses opening the stream is refused with that another attempt would only repeat."""

STRUCTURE: Final = ("{", "[", "<")
"""What opens a document rather than a sentence."""

CERTIFICATE_REFUSED: Final = "The stack's certificate is not the one pinned for it, or no trust store vouches for it, so nothing was sent."
"""What a transport says where the certificate was refused."""

NOT_ANSWERING: Final = "lemonfiber is not answering at that address. It may have been stopped."
"""What a transport says where nothing answered."""

NOT_ADMITTED: Final = (
    "lemonfiber does not admit the credential this client holds. Use the token it printed, sign in again, "
    "or use a key the operator minted."
)
"""What a request turned away for its credential is told, whatever the stack said."""


def problem_in(body: bytes) -> Problem | None:
    """Return the problem an `error` envelope carries, or None where the body is not one."""
    text = body.decode(errors="replace").strip()
    if not text.startswith(STRUCTURE):
        return None
    try:
        envelope = parse_envelope(text)
    except LemonfiberError:
        return None
    if envelope["kind"] != "error":
        return None
    data: object = expect(envelope, "error")["data"]
    return data if is_problem(data) else None


def is_problem(data: object) -> TypeIs[Problem]:
    """Tell whether an `error` envelope's data is an object, as a problem is."""
    return isinstance(data, dict)


def sentence_in(body: bytes) -> str | None:
    """Return the one sentence a refusal holds: an `error` envelope's summary, or prose."""
    text = body.decode(errors="replace").strip()
    if not text:
        return None
    if not text.startswith(STRUCTURE):
        return text
    problem = problem_in(body)
    summary: object = problem.get("summary") if problem is not None else None
    if not isinstance(summary, str) or not summary.strip():
        return None
    return summary.strip()


def code_in(body: bytes) -> RefusalCode | None:
    """Return the refusal's code where the contract lists it; any other code reads as none."""
    problem = problem_in(body)
    code: object = problem.get("code") if problem is not None else None
    return code if isinstance(code, str) and is_refusal_code(code) else None


def retry_after(answer: Answer) -> int | None:
    """Return the seconds a `Retry-After` header names, or None where it names none this can read."""
    said = answer.headers.get("retry-after")
    if said is None or not said.strip().isdecimal():
        return None
    return int(said)


def refusal_of(answer: Answer) -> LemonfiberError:
    """Return the problem an answer that is not a success is.

    A request turned away at 401 or 403 is read from its code: the credential's
    own code, no code, or a code the contract does not list is `NotAdmittedError`;
    any other listed code is `DeclinedError`, carrying lemonfiber's sentence. Any
    other status with no sentence this client can read did not come from
    lemonfiber, and is `UnreachableError`.
    """
    sentence = sentence_in(answer.body)
    code = code_in(answer.body)
    problem = problem_in(answer.body)
    if answer.status in TURNED_AWAY:
        if code is None or REFUSAL_CODES[code].name == THE_CREDENTIAL or sentence is None:
            return NotAdmittedError(NOT_ADMITTED, status=answer.status, code=code, problem=problem)
        return DeclinedError(sentence, status=answer.status, code=code, problem=problem)
    if answer.status == HTTPStatus.TOO_MANY_REQUESTS:
        said = sentence or "Too many wrong answers lately; wait before trying again."
        return TooManyAttemptsError(
            said,
            status=answer.status,
            retry_after=retry_after(answer),
            code=code,
            problem=problem,
        )
    if sentence is None:
        return UnreachableError(f"Something other than lemonfiber answered, with status {answer.status}.")
    meant = MEANT_BY.get(answer.status, FailedError)
    return meant(sentence, status=answer.status, code=code, problem=problem)


def opening_refusal(answer: Answer) -> LemonfiberError | None:
    """Return the refusal an answer to opening the stream is, or None where another attempt may succeed."""
    if answer.status in REFUSED_OUTRIGHT:
        return refusal_of(answer)
    return None
