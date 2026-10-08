# Copyright (c) 2026 NightWorksIO
"""What each answer that is a success comes to, or the refusal it is."""

import datetime
import types
from http import HTTPStatus
from typing import TYPE_CHECKING, Final, cast

from lemonfiber._protocol.refusals import code_in, problem_in, refusal_of, sentence_in
from lemonfiber.capabilities import CapabilitySet, is_state
from lemonfiber.credential import Credential, Session
from lemonfiber.envelope import expect, parse_envelope
from lemonfiber.files import BundleFile
from lemonfiber.jobs import Ended, Finished, JobStanding, Running
from lemonfiber.problems import NoSuchJobError, PasswordRefusedError, UnreadableResponseError

if TYPE_CHECKING:
    from lemonfiber._generated import CapabilityState, Envelope, LogEnvelope
    from lemonfiber._protocol.calls import Answer

REFUSED_AT_THE_DOOR: Final = "That is not the password, or none is configured."
"""What a refused password is told where the stack said nothing readable."""


def succeeded(answer: Answer) -> bool:
    """Tell whether an answer is a success."""
    return HTTPStatus.OK <= answer.status < HTTPStatus.MULTIPLE_CHOICES


def envelope_of(answer: Answer) -> Envelope:
    """Read an answer as one envelope, or raise the refusal it is."""
    if not succeeded(answer):
        raise refusal_of(answer)
    return parse_envelope(answer.body)


def envelopes_of(answer: Answer) -> list[Envelope]:
    """Read an answer of one envelope a line, or raise the refusal it is."""
    if not succeeded(answer):
        raise refusal_of(answer)
    return [parse_envelope(line) for line in answer.body.splitlines() if line.strip()]


def log_lines_of(answer: Answer) -> list[LogEnvelope]:
    """Read an answer of one `log` envelope a line, refusing a line of another kind, or raise the refusal it is."""
    return [expect(envelope, "log") for envelope in envelopes_of(answer)]


def bundle_of(name: str, answer: Answer) -> BundleFile:
    """Keep a handed-over file as it arrived, or raise the refusal it is."""
    if not succeeded(answer):
        raise refusal_of(answer)
    return BundleFile(name, answer.body, answer.headers.get("content-type"))


def standing_of(job: str, answer: Answer) -> JobStanding:
    """Read where work stands from the status and the kind together."""
    if answer.status == HTTPStatus.NOT_FOUND and problem_in(answer.body) is None:
        raise NoSuchJobError(job)
    envelope = envelope_of(answer)
    if envelope["kind"] != "job":
        return Finished(job, envelope)
    started = expect(envelope, "job")
    return Running(job, started) if answer.status == HTTPStatus.ACCEPTED else Ended(job, started)


def capabilities_of(answer: Answer) -> CapabilitySet:
    """Read the stack's capabilities as they stood when the answer arrived, or raise the refusal it is.

    A capability name this client does not know is kept, never refused; a state the
    contract does not list is not a document lemonfiber writes.
    """
    arrived = datetime.datetime.now(datetime.UTC)
    data = cast("object", expect(envelope_of(answer), "capabilities")["data"])
    held = cast("dict[str, object]", data).get("capabilities") if isinstance(data, dict) else None
    if not isinstance(held, dict):
        msg = f"the capabilities are {held!r}, and they are an object keyed by path"
        raise UnreadableResponseError(msg)
    states: dict[str, CapabilityState] = {}
    for path, state in cast("dict[object, object]", held).items():
        if not isinstance(path, str) or not is_state(state):
            msg = f"{path!r} is {state!r}, which is not a state a capability can be in"
            raise UnreadableResponseError(msg)
        states[path] = state
    return CapabilitySet(types.MappingProxyType(states), arrived)


def session_of(answer: Answer) -> Session:
    """Read the door's answer as a session, or raise why there is none."""
    if answer.status == HTTPStatus.UNAUTHORIZED:
        raise PasswordRefusedError(
            sentence_in(answer.body) or REFUSED_AT_THE_DOOR,
            status=answer.status,
            code=code_in(answer.body),
            problem=problem_in(answer.body),
        )
    data = expect(envelope_of(answer), "admission")["data"]
    return Session(Credential(data["token"]), instant(data["until"]), data.get("member"))


def instant(written: str) -> datetime.datetime:
    """Read an instant as this product writes one, in UTC."""
    try:
        read = datetime.datetime.fromisoformat(written)
    except ValueError as unreadable:
        msg = f"{written!r} is not an instant"
        raise UnreadableResponseError(msg) from unreadable
    if read.tzinfo is None:
        return read.replace(tzinfo=datetime.UTC)
    if read.utcoffset() != datetime.timedelta(0):
        msg = f"{written!r} names an offset other than UTC"
        raise UnreadableResponseError(msg)
    return read.astimezone(datetime.UTC)
