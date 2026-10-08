# Copyright (c) 2026 NightWorksIO
"""Each failure on the way to the stack, told in the server's words, with the stack's refusal as data after it."""

import json
from typing import Final

import mcp_types as types
import pytest
from lemonfiber import (
    ApiVersionMismatchError,
    BusyError,
    CertificateRefusedError,
    DeclinedError,
    FailedError,
    LemonfiberError,
    MisaskedError,
    MissingError,
    NoSuchJobError,
    NotAdmittedError,
    PasswordRefusedError,
    TooManyAttemptsError,
    UnreachableError,
    UnreadableResponseError,
)

from lemonfiber_mcp import outcome
from lemonfiber_mcp.outcome import Failure, State
from lemonfiber_mcp.withheld import WITHHELD, Withholding
from tests.conftest import KEY

WITHHOLDING: Final = Withholding()


def text_of(result: types.CallToolResult) -> list[str]:
    """Return every text block of a result, in order."""
    return [block.text for block in result.content if isinstance(block, types.TextContent)]


def test_a_refused_key_is_refused_for_good_and_says_a_new_key_is_needed() -> None:
    failure = outcome.failure_of(NotAdmittedError("x", status=403, code="ADMIT-4"))
    assert failure.state is State.REFUSED
    assert "A new key is needed" in failure.sentence
    assert failure.refusal is None


@pytest.mark.parametrize(
    ("error", "sentence"),
    [
        (UnreachableError("x"), outcome.UNANSWERED),
        (CertificateRefusedError("x"), outcome.NOT_THE_PINNED),
        (DeclinedError("x", status=403, code="ADMIT-11"), outcome.IN_THE_CLEAR),
    ],
)
def test_a_stack_that_cannot_be_reached_says_why_and_is_tried_again(
    error: LemonfiberError,
    sentence: str,
) -> None:
    failure = outcome.failure_of(error)
    assert (failure.state, failure.sentence) == (State.UNREACHABLE, sentence)
    assert failure.refusal is None


@pytest.mark.parametrize(
    ("error", "sentence"),
    [
        (DeclinedError("Not for a key.", status=403, code="ADMIT-12"), outcome.NOT_FOR_THIS_KEY),
        (DeclinedError("Not yours.", status=403, code="ADMIT-6"), outcome.DECLINED),
        (BusyError("Busy.", status=409), outcome.BUSY),
        (MissingError("Nothing.", status=404, code="READ-3"), outcome.MISSING),
        (MisaskedError("Asked wrong.", status=400, code="READ-4"), outcome.MISASKED),
        (FailedError("Broke.", status=500), outcome.FAILED),
        (PasswordRefusedError("Wrong.", status=401), outcome.DECLINED),
        (TooManyAttemptsError("Wait.", status=429, retry_after=None), outcome.TOO_MANY),
    ],
)
def test_a_refusal_is_told_in_the_servers_words_with_the_stacks_as_data(
    error: LemonfiberError,
    sentence: str,
) -> None:
    failure = outcome.failure_of(error)
    assert failure.state is None
    assert failure.sentence == sentence
    assert failure.refusal is not None
    assert failure.refusal["sentence"] == str(error)


def test_a_refusal_carries_its_codes_registry_name() -> None:
    failure = outcome.failure_of(MisaskedError("Asked wrong.", status=400, code="READ-4"))
    assert failure.refusal == {"status": 400, "code": "READ-4", "name": "NO_TERM", "sentence": "Asked wrong."}


def test_a_refusal_with_no_code_carries_none() -> None:
    failure = outcome.failure_of(FailedError("Broke.", status=500))
    assert failure.refusal is not None
    assert (failure.refusal["code"], failure.refusal["name"]) == (None, None)


def test_waiting_after_too_many_wrong_keys_says_how_long() -> None:
    failure = outcome.failure_of(TooManyAttemptsError("Wait.", status=429, retry_after=30))
    assert failure.sentence == f"{outcome.TOO_MANY} Wait 30 seconds before asking again."


def test_another_version_names_both() -> None:
    failure = outcome.failure_of(ApiVersionMismatchError(1, 2))
    assert failure.sentence.endswith("This server speaks version 1; the stack, 2.")


@pytest.mark.parametrize(
    ("error", "sentence"),
    [
        (NoSuchJobError("j1"), outcome.NO_SUCH_JOB),
        (UnreadableResponseError(f"it held {KEY}"), outcome.UNREADABLE),
    ],
)
def test_what_the_client_raised_otherwise_is_a_fixed_sentence(error: LemonfiberError, sentence: str) -> None:
    assert outcome.failure_of(error) == Failure(sentence)


def test_an_answer_is_a_line_saying_what_follows_is_data_then_the_data() -> None:
    result = outcome.answered({"kind": "status", "data": {"note": f"key {KEY}"}}, WITHHOLDING)
    first, second = text_of(result)
    assert first == outcome.DATA
    assert json.loads(second) == {"kind": "status", "data": {"note": f"key {WITHHELD}"}}
    assert result.structured_content == json.loads(second)
    assert not result.is_error


def test_a_failure_with_a_refusal_hands_the_refusal_on_as_data() -> None:
    result = outcome.failed(Failure(outcome.MISASKED, refusal={"sentence": f"bad {KEY}"}), WITHHOLDING)
    assert result.is_error
    sentence, line, data = text_of(result)
    assert (sentence, line) == (outcome.MISASKED, outcome.REFUSAL_DATA)
    assert json.loads(data) == {"sentence": f"bad {WITHHELD}"}


def test_a_failure_without_a_refusal_is_one_sentence() -> None:
    result = outcome.failed(Failure(f"held {KEY}"), WITHHOLDING)
    assert text_of(result) == [f"held {WITHHELD}"]
