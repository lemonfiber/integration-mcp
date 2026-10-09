# Copyright (c) 2026 NightWorksIO
"""No key, pin or configured secret leaves in anything the server says or logs."""

import json
import logging
import re
import sys
from typing import TYPE_CHECKING

from lemonfiber_mcp.withheld import WITHHELD, Withholding, WithholdingFormatter, install
from tests.conftest import KEY

if TYPE_CHECKING:
    import pytest

PIN = "ab" * 32


def test_a_key_is_withheld_whether_or_not_it_was_configured() -> None:
    other = "lfk_" + "f" * 64
    assert Withholding().withhold(f"sent {other} and {KEY}") == f"sent {WITHHELD} and {WITHHELD}"


def test_a_configured_value_is_withheld_in_any_letter_case() -> None:
    withholding = Withholding([PIN])
    assert withholding.withhold(f"pin {PIN.upper()}.") == f"pin {WITHHELD}."


def test_a_longer_value_is_withheld_before_one_it_contains() -> None:
    withholding = Withholding(["secret", "secret-and-more", ""])
    assert withholding.withhold("secret-and-more") == WITHHELD


def test_the_longer_value_goes_first_whatever_its_letters() -> None:
    assert Withholding(["b", "ab"]).withhold("ab") == WITHHELD


def test_a_formatter_formats_as_it_is_told_before_withholding() -> None:
    record = logging.LogRecord("t", logging.INFO, __file__, 1, "said %s", ("hello",), None)
    assert (
        WithholdingFormatter(Withholding(), "%(levelname)s: %(message)s").format(record) == "INFO: said hello"
    )


def test_a_key_inside_json_leaves_the_document_whole() -> None:
    withheld = Withholding().withhold(json.dumps({"key": KEY, "next": "x"}))
    assert json.loads(withheld) == {"key": WITHHELD, "next": "x"}


def test_what_it_holds_is_counted_not_shown() -> None:
    assert repr(Withholding([PIN])) == "Withholding(1 values)"
    assert PIN not in repr(Withholding([PIN]))


def fail() -> None:
    """Fail, saying the pin."""
    raise ValueError(PIN)


def raised() -> logging.LogRecord:
    """Return a record of a failure whose message and argument both hold a secret, with its traceback."""
    try:
        fail()
    except ValueError:
        information = sys.exc_info()
    else:
        information = None
    return logging.LogRecord("t", logging.ERROR, __file__, 1, "with %s", (KEY,), information)


def test_a_log_line_and_its_traceback_are_withheld() -> None:
    said = WithholdingFormatter(Withholding([PIN]), "%(message)s").format(raised())
    assert KEY not in said
    assert PIN not in said
    assert said.startswith(f"with {WITHHELD}")


def test_installing_replaces_every_handler_with_one_that_withholds(
    capsys: pytest.CaptureFixture[str],
) -> None:
    root = logging.getLogger()
    kept = list(root.handlers), root.level
    try:
        root.addHandler(logging.NullHandler())
        handler = install(Withholding([PIN]))
        assert root.handlers == [handler]
        logging.getLogger("x").info("pin %s", PIN)
        said = capsys.readouterr().err
        assert re.fullmatch(
            rf"\d{{4}}-\d\d-\d\d \d\d:\d\d:\d\d,\d{{3}} INFO x: pin {re.escape(WITHHELD)}\n",
            said,
        )
    finally:
        root.handlers[:] = kept[0]
        root.setLevel(kept[1])
