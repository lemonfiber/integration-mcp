# Copyright (c) 2026 NightWorksIO
"""Generating the tools from the vendored contract, and refusing a contract that cannot be read one way."""

import json
import shutil
from typing import TYPE_CHECKING

import pytest
from lemonfiber.reads import LOGS

from lemonfiber_mcp import connection, stack
from scripts import generate_tools

if TYPE_CHECKING:
    import pathlib

PAUSE = {"action": "downloads-pause", "disturbs": False, "rehearsal": True, "idempotent": True}
NONE: list[object] = []
"""A list the contract leaves empty."""
DIAGNOSE = {"action": "diagnose", "disturbs": True, "rehearsal": False, "idempotent": False}


def write(root: pathlib.Path, path: str, content: object) -> None:
    """Write a contract file as JSON under the stand-in tree."""
    target = root / "contract" / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(content), encoding="utf-8")


@pytest.fixture
def root(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a stand-in tree holding a small contract: three reads, two actions a key may call."""
    write(
        tmp_path,
        "web-api/index.json",
        {
            "api_version": 1,
            "actions": {
                "downloads-pause": "actions/downloads-pause.json",
                "diagnose": "actions/diagnose.json",
            },
            "reads": "reads.json",
            "key_callable": "key-callable.json",
        },
    )
    write(
        tmp_path,
        "web-api/reads.json",
        [
            {"path": "/api/front-door", "parameters": NONE, "kinds": ["front-door"], "file": False},
            {
                "path": "/api/logs",
                "parameters": [
                    {"name": "service", "repeatable": True},
                    {"name": "tail", "repeatable": False},
                    {"name": "follow", "repeatable": False},
                ],
                "kinds": ["job", "log"],
                "file": False,
            },
            {"path": "/api/bundle/{name}", "parameters": NONE, "kinds": NONE, "file": True},
        ],
    )
    write(tmp_path, "web-api/key-callable.json", [PAUSE, DIAGNOSE])
    write(
        tmp_path,
        "web-api/actions/downloads-pause.json",
        {
            "action": "downloads-pause",
            "arguments": [
                {
                    "name": "clients",
                    "type": {"$ref": "../defs/Clients.json", "description": "Which clients."},
                },
                {"name": "confirm", "type": {"type": "boolean", "default": False}},
            ],
            "consent": ["confirm"],
            "rehearsal": True,
        },
    )
    write(
        tmp_path,
        "web-api/defs/Clients.json",
        {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "type": "array",
            "items": {"$ref": "Name.json"},
        },
    )
    write(tmp_path, "web-api/defs/Name.json", {"type": "string", "description": "A client's name."})
    write(
        tmp_path,
        "web-api/actions/diagnose.json",
        {"action": "diagnose", "arguments": [{"name": "only", "type": {"type": "string"}}], "consent": []},
    )
    (tmp_path / "contract/VERSION").write_text("a" * 40 + "\n", encoding="ascii")
    return tmp_path


def shapes(root: pathlib.Path) -> dict[str, generate_tools.Shape]:
    """Return what the stand-in contract generates, by tool name."""
    return {shape.name: shape for shape in generate_tools.shapes(root)}


def test_a_read_becomes_a_tool_and_a_resource(root: pathlib.Path) -> None:
    door = shapes(root)["read_front_door"]
    assert (door.reach, door.target, door.capability) == ("read", "front-door", "/api/front-door")
    assert door.resource == "lemonfiber://read/front-door"
    assert door.input_schema == {"type": "object", "properties": {}, "additionalProperties": False}
    assert (door.read_only, door.destructive, door.idempotent) == (True, False, True)


def test_the_log_read_takes_its_parameters_but_not_the_one_that_makes_it_a_stream(root: pathlib.Path) -> None:
    logs = shapes(root)["read_logs"]
    assert logs.reach == "logs"
    assert logs.parameters == ("service", "tail")
    assert logs.input_schema["properties"] == {
        "service": {"type": "array", "items": {"type": "string"}},
        "tail": {"type": "string"},
    }
    assert logs.resource == "lemonfiber://read/logs{?service*,tail}"


def test_a_read_answering_with_a_file_takes_its_path_placeholders(root: pathlib.Path) -> None:
    bundle = shapes(root)["read_bundle"]
    assert (bundle.reach, bundle.target, bundle.capability) == ("file", "bundle", "/api/bundle/{name}")
    assert bundle.parameters == ("name",)
    assert bundle.input_schema["required"] == ["name"]
    assert bundle.resource == "lemonfiber://bundle/{name}"


def test_a_rehearsable_action_becomes_a_rehearsal_and_an_action_taking_its_offer(root: pathlib.Path) -> None:
    generated = shapes(root)
    rehearsal, action = generated["rehearse_downloads_pause"], generated["downloads_pause"]
    clients = {
        "type": "array",
        "items": {"type": "string", "description": "A client's name."},
        "description": "Which clients.",
    }
    assert rehearsal.reach == "rehearsal"
    assert rehearsal.parameters == ("clients",)
    assert rehearsal.input_schema["properties"] == {"clients": clients}
    assert (rehearsal.read_only, rehearsal.destructive, rehearsal.idempotent) == (True, False, True)
    assert action.reach == "action"
    assert action.parameters == ("clients", "confirm", "offer")
    assert action.input_schema["required"] == ["clients", "offer"]
    assert (action.read_only, action.destructive, action.idempotent) == (False, False, True)
    assert action.capability == rehearsal.capability == "/api/actions/downloads-pause"
    assert action.resource is None


def test_an_action_with_no_rehearsal_is_one_tool_with_its_annotations(root: pathlib.Path) -> None:
    generated = shapes(root)
    assert "rehearse_diagnose" not in generated
    diagnose = generated["diagnose"]
    assert diagnose.parameters == ("only",)
    assert diagnose.input_schema["required"] == ["only"]
    assert (diagnose.read_only, diagnose.destructive, diagnose.idempotent) == (False, True, False)


def test_the_module_is_written_and_then_checks_clean(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert generate_tools.run([], root) == 0
    written = (root / generate_tools.OUTPUT).read_text(encoding="utf-8")
    assert f"lemonfiber {'a' * 40} published" in written
    assert "name='rehearse_downloads_pause'" in written
    assert (root / generate_tools.OUTPUT).with_name("__init__.py").is_file()
    assert generate_tools.run(["--check"], root) == 0
    assert "is what the vendored contract generates" in capsys.readouterr().out


def test_a_module_the_contract_no_longer_generates_fails_the_check(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert generate_tools.run(["--check"], root) == 1
    assert generate_tools.run([], root) == 0
    write(root, "web-api/key-callable.json", [PAUSE])
    assert generate_tools.run(["--check"], root) == 1
    assert "Run `just generate`" in capsys.readouterr().err


def test_the_module_in_this_tree_is_what_its_contract_generates() -> None:
    assert generate_tools.run(["--check"]) == 0


def refused(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> str:
    """Generate, expecting a refusal that writes nothing, and return what it said."""
    assert generate_tools.run([], root) == 1
    assert not (root / generate_tools.OUTPUT).exists()
    return capsys.readouterr().err


def test_an_api_version_not_implemented_is_refused_naming_both(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write(root, "web-api/index.json", {"api_version": 2})
    said = refused(root, capsys)
    assert "api_version 2" in said
    assert "implements 1" in said


def test_a_reference_to_nothing_is_refused_naming_it(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (root / "contract/web-api/defs/Name.json").unlink()
    assert "refers to Name.json" in refused(root, capsys)


def test_a_reference_with_a_constraint_beside_it_is_refused(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write(root, "web-api/defs/Clients.json", {"$ref": "Name.json", "minItems": 1})
    assert "constraints beside it" in refused(root, capsys)


def test_a_reference_back_through_itself_is_refused(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write(root, "web-api/defs/Name.json", {"anyOf": [{"$ref": "Clients.json"}]})
    assert "through itself" in refused(root, capsys)


def test_a_read_outside_the_api_is_refused(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(root, "web-api/reads.json", [{"path": "/elsewhere", "parameters": NONE}])
    assert "not under /api/" in refused(root, capsys)


def test_a_log_read_without_what_made_it_a_stream_is_refused(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write(
        root,
        "web-api/reads.json",
        [{"path": "/api/logs", "parameters": [{"name": "tail", "repeatable": False}]}],
    )
    assert "has moved" in refused(root, capsys)


def test_an_action_the_contract_does_not_publish_is_refused(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write(root, "web-api/key-callable.json", [{**PAUSE, "action": "uninstall"}])
    assert "'uninstall'" in refused(root, capsys)


def test_an_action_already_taking_an_offer_argument_is_refused(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write(
        root,
        "web-api/actions/diagnose.json",
        {"action": "diagnose", "arguments": [{"name": "offer", "type": {"type": "string"}}]},
    )
    assert "named 'offer'" in refused(root, capsys)


def test_two_tools_of_one_name_are_refused(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    write(
        root,
        "web-api/reads.json",
        [{"path": "/api/front-door", "parameters": NONE}, {"path": "/api/front_door", "parameters": NONE}],
    )
    assert "more than one tool named read_front_door" in refused(root, capsys)


@pytest.mark.parametrize(
    ("path", "content", "said"),
    [
        ("web-api/index.json", [], "does not hold an object"),
        ("web-api/reads.json", {}, "does not hold a list"),
        ("web-api/reads.json", [1], "does not hold an object"),
    ],
)
def test_a_file_of_the_wrong_shape_is_refused(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
    path: str,
    content: object,
    said: str,
) -> None:
    write(root, path, content)
    assert said in refused(root, capsys)


def test_an_unreadable_file_is_refused(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    (root / "contract/web-api/reads.json").write_text("{", encoding="utf-8")
    assert "could not be read" in refused(root, capsys)


def test_a_contract_with_no_revision_is_refused(
    root: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    (root / "contract/VERSION").unlink()
    refused(root, capsys)


def test_a_missing_contract_is_refused(root: pathlib.Path, capsys: pytest.CaptureFixture[str]) -> None:
    shutil.rmtree(root / "contract/web-api")
    assert "could not be read" in refused(root, capsys)


def test_the_generator_spells_what_the_server_reads_as_the_server_does() -> None:
    assert generate_tools.OFFER == stack.OFFER
    assert f"{connection.SCHEME}://" == generate_tools.SCHEME
    assert generate_tools.LOGS == LOGS
