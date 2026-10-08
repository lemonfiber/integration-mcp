# Copyright (c) 2026 NightWorksIO
"""Every read and key-callable action has its tools, every tool its words, and a credential is offered what it may use."""

import datetime
import json
import pathlib
import types as builtin_types
from typing import TYPE_CHECKING, Final, cast

import pytest
from lemonfiber import CapabilitySet

from lemonfiber_mcp import catalogue
from lemonfiber_mcp._generated.tools import TOOLS
from lemonfiber_mcp.catalogue import Audience
from lemonfiber_mcp.shapes import Reach, ToolShape

if TYPE_CHECKING:
    from lemonfiber._generated import CapabilityState

ROOT: Final = pathlib.Path(__file__).resolve().parent.parent
CONTRACT: Final = ROOT / "contract" / "web-api"
HOUSEHOLD_TOOLS: Final = frozenset({"read_requests", "read_held", "read_playing", "connection"})
"""The tools a household member is offered words for: their requests, their shelf, what they are playing, and the connection."""


def capability_set(states: dict[str, CapabilityState]) -> CapabilitySet:
    """Return a capability set as the client reads one."""
    return CapabilitySet(builtin_types.MappingProxyType(states), datetime.datetime.now(datetime.UTC))


def contract(name: str) -> list[dict[str, object]]:
    """Return one of the vendored contract's lists."""
    return json.loads((CONTRACT / name).read_text(encoding="utf-8"))


def test_every_read_the_contract_lists_has_a_tool_and_a_resource() -> None:
    reads = {str(entry["path"]) for entry in contract("reads.json")}
    tools = {
        shape.capability: shape for shape in TOOLS if shape.reach in {Reach.READ, Reach.LOGS, Reach.FILE}
    }
    assert set(tools) == reads
    assert all(shape.resource for shape in tools.values())


def test_every_action_a_key_may_call_has_a_tool_and_a_rehearsable_one_its_rehearsal() -> None:
    for entry in contract("key-callable.json"):
        action = str(entry["action"])
        reaches = {shape.reach for shape in TOOLS if shape.target == action}
        assert Reach.ACTION in reaches, action
        assert (Reach.REHEARSAL in reaches) is (entry["rehearsal"] is True), action


def test_every_write_tool_states_whether_it_is_destructive_and_idempotent() -> None:
    listed = {str(entry["action"]): entry for entry in contract("key-callable.json")}
    for shape in TOOLS:
        if shape.reach is Reach.ACTION:
            assert (shape.destructive, shape.idempotent) == (
                listed[shape.target]["disturbs"],
                listed[shape.target]["idempotent"],
            )
            assert not shape.read_only


def test_a_rehearsable_action_takes_its_offer_and_its_rehearsal_does_not() -> None:
    for shape in TOOLS:
        if shape.reach is Reach.REHEARSAL:
            assert "offer" not in shape.parameters
        if shape.reach is Reach.ACTION and any(
            other.reach is Reach.REHEARSAL and other.target == shape.target for other in TOOLS
        ):
            assert "offer" in shape.parameters
            assert "offer" in cast("list[str]", shape.input_schema["required"])


@pytest.mark.parametrize("shape", catalogue.SHAPES.values(), ids=lambda shape: shape.name)
def test_every_tool_and_every_parameter_has_operator_words(shape: ToolShape) -> None:
    made = catalogue.tool(shape, Audience.OPERATOR)
    assert made is not None
    assert made.description
    assert set(made.input_schema["properties"]) == set(shape.parameters)
    for name, schema in made.input_schema["properties"].items():
        assert schema["description"], f"{shape.name}.{name} has no description"


def test_the_words_name_only_tools_there_are() -> None:
    assert set(catalogue.words()) == set(catalogue.SHAPES)
    for name, written in catalogue.words().items():
        assert set(written.parameters) <= set(catalogue.SHAPES[name].parameters), name
        assert set(written.household_parameters) <= set(catalogue.SHAPES[name].parameters), name


def test_only_what_a_member_may_reach_has_household_words() -> None:
    assert {name for name, written in catalogue.words().items() if written.household} == HOUSEHOLD_TOOLS


@pytest.mark.parametrize("name", sorted(HOUSEHOLD_TOOLS))
def test_a_member_is_offered_household_words_and_only_the_parameters_they_describe(name: str) -> None:
    shape = catalogue.SHAPES[name]
    made = catalogue.tool(shape, Audience.HOUSEHOLD)
    assert made is not None
    written = catalogue.words()[name]
    assert made.description == written.household
    assert set(made.input_schema["properties"]) == set(written.household_parameters)
    assert set(made.input_schema.get("required", [])) <= set(written.household_parameters)


def test_a_member_is_not_offered_the_household_or_another_members_name() -> None:
    held = catalogue.tool(catalogue.SHAPES["read_held"], Audience.HOUSEHOLD)
    assert held is not None
    assert set(held.input_schema["properties"]) == {"most"}


def test_a_tool_with_no_household_words_is_not_offered_to_a_member() -> None:
    assert catalogue.tool(catalogue.SHAPES["read_status"], Audience.HOUSEHOLD) is None


def test_the_contract_describes_an_action_argument_where_nothing_is_written() -> None:
    made = catalogue.tool(catalogue.SHAPES["diagnose"], Audience.OPERATOR)
    assert made is not None
    assert made.input_schema["properties"]["disruptive"]["description"].startswith("Whether the checks")


def test_annotations_carry_what_the_contract_says() -> None:
    made = catalogue.tool(catalogue.SHAPES["update"], Audience.OPERATOR)
    assert made is not None
    assert made.annotations is not None
    assert (
        made.annotations.read_only_hint,
        made.annotations.destructive_hint,
        made.annotations.idempotent_hint,
    ) == (
        False,
        True,
        False,
    )
    assert made.annotations.open_world_hint is False


def test_an_unconfigured_capability_is_offered_saying_a_setting_is_off() -> None:
    made = catalogue.tool(catalogue.SHAPES["read_status"], Audience.OPERATOR, "unconfigured")
    assert made is not None
    assert made.description is not None
    assert made.description.endswith(catalogue.UNCONFIGURED_NOTE)


def test_a_read_key_is_offered_the_reads_and_no_write() -> None:
    states: dict[str, CapabilityState] = {shape.capability: "available" for shape in TOOLS if shape.read_only}
    states |= {shape.capability: "unpermitted" for shape in TOOLS if not shape.read_only}
    offered = catalogue.offered(capability_set(states), Audience.OPERATOR)
    assert not any(name.startswith("rehearse_") for name in offered)
    assert catalogue.JOB not in offered
    assert "read_status" in offered


def test_an_act_key_is_offered_the_actions_and_the_job_tool() -> None:
    states: dict[str, CapabilityState] = {shape.capability: "available" for shape in TOOLS}
    offered = catalogue.offered(capability_set(states), Audience.OPERATOR)
    assert {"restart", "rehearse_restart", "diagnose", catalogue.JOB} <= set(offered)


def test_what_the_stack_does_not_have_or_does_not_permit_is_not_offered() -> None:
    offered = catalogue.offered(capability_set({"/api/status": "unpermitted"}), Audience.OPERATOR)
    assert offered == {}


def test_a_member_is_offered_only_their_own_reads() -> None:
    states: dict[str, CapabilityState] = {shape.capability: "available" for shape in TOOLS}
    offered = catalogue.offered(capability_set(states), Audience.HOUSEHOLD)
    assert set(offered) == HOUSEHOLD_TOOLS - {"connection"}


@pytest.mark.parametrize("audience", list(Audience))
def test_before_the_stack_answers_the_one_tool_is_connection(audience: Audience) -> None:
    assert list(catalogue.connection_only(audience)) == [catalogue.CONNECTION]


@pytest.mark.parametrize(
    "written",
    [
        '[a]\noperator = "x"\nparameters = "not a table"\n',
        '[a]\noperator = "x"\n[a.parameters]\nb = 1\n',
    ],
)
def test_words_that_are_not_text_are_refused(written: str) -> None:
    with pytest.raises(TypeError):
        catalogue.read_words(written)
