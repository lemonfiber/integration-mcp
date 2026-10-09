# Copyright (c) 2026 NightWorksIO
"""The server driven through the protocol against the stand-in stack, every call through the vendored client."""

import base64
import datetime
import json
from typing import TYPE_CHECKING, Any, Final, cast

import mcp_types as types
import pytest
from lemonfiber import Address, AsyncClient, Credential
from mcp import Client
from mcp.server.session import ServerSession
from mcp.shared.exceptions import MCPError

from lemonfiber_mcp import catalogue, outcome, serving
from lemonfiber_mcp import connection as connection_module
from lemonfiber_mcp import stack as stack_module
from lemonfiber_mcp.connection import Connection
from lemonfiber_mcp.outcome import State
from tests.conftest import KEY, VERSION, capabilities
from tests.stack import LOOPBACK, Reply, Stack, envelope, problem

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from lemonfiber_mcp.withheld import Withholding

pytestmark = pytest.mark.anyio

NOT_ADMITTED: Final = Reply(status=403, body=problem("ADMIT-4", "Not admitted."))
STATUS: Final = Reply(body=envelope("status", {"services": []}))
JOB: Final = "9f2c1a7e04b3d815"
STARTED: Final = envelope("job", {"action": "restart", "job": JOB})


def texts(result: types.CallToolResult) -> list[str]:
    """Return every text block of a result, in order."""
    return [block.text for block in result.content if isinstance(block, types.TextContent)]


def data_of(result: types.CallToolResult) -> dict[str, Any]:
    """Return the data block of an answer, read back from its JSON."""
    line, data = texts(result)
    assert line == outcome.DATA
    return cast("dict[str, Any]", json.loads(data))


def names(listed: types.ListToolsResult) -> set[str]:
    """Return the name of every tool a listing offers."""
    return {tool.name for tool in listed.tools}


@pytest.fixture
async def elsewhere(withholding: Withholding) -> AsyncIterator[Client]:
    """Return a protocol client whose server reaches for a stack that is not there."""
    async with AsyncClient(Address(f"http://{LOOPBACK}:9", pin=None), Credential(KEY)) as client:
        lonely = Connection(client, withholding)
        async with Client(serving.build(serving.always(lonely), withholding, VERSION)) as protocol:
            yield protocol


async def test_an_act_key_is_offered_every_read_the_stack_names_every_write_and_the_job_tool(
    mcp_client: Client,
) -> None:
    offered = names(await mcp_client.list_tools())
    assert {"read_status", "read_requests", "rehearse_restart", "restart", "diagnose", "job"} <= offered
    assert "connection" not in offered


async def test_every_tool_carries_its_annotations(mcp_client: Client) -> None:
    for tool in (await mcp_client.list_tools()).tools:
        assert tool.annotations is not None
        assert tool.annotations.read_only_hint is not None
        assert tool.annotations.destructive_hint is not None
        assert tool.annotations.idempotent_hint is not None


async def test_a_read_key_is_offered_no_write(stack: Stack, mcp_client: Client) -> None:
    stack.reply("/api/capabilities", Reply(body=capabilities("read")))
    offered = names(await mcp_client.list_tools())
    assert "read_status" in offered
    assert not offered & {"restart", "rehearse_restart", "diagnose", "job"}


async def test_a_member_key_is_offered_no_technical_tool_and_reads_the_households_words(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/capabilities", Reply(body=capabilities("member")))
    listed = await mcp_client.list_tools()
    written = catalogue.words()
    assert names(listed) == {"read_requests", "read_held", "read_playing"}
    assert {tool.name: tool.description for tool in listed.tools} == {
        name: written[name].household for name in names(listed)
    }


async def test_an_operator_key_reads_the_operators_words(stack: Stack, mcp_client: Client) -> None:
    stack.reply("/api/capabilities", Reply(body=capabilities("operator")))
    listed = await mcp_client.list_tools()
    status = next(tool for tool in listed.tools if tool.name == "read_status")
    assert status.description == catalogue.words()["read_status"].operator


async def test_the_server_introduces_itself_with_its_version_and_how_to_read_its_answers(
    mcp_client: Client,
) -> None:
    assert mcp_client.server_info is not None
    assert mcp_client.server_info.version == VERSION
    assert mcp_client.instructions == serving.INSTRUCTIONS


async def test_before_the_stack_answers_the_one_tool_is_connection_in_the_households_words(
    elsewhere: Client,
) -> None:
    listed = await elsewhere.list_tools()
    assert names(listed) == {"connection"}
    assert listed.tools[0].description == catalogue.words()["connection"].household
    result = await elsewhere.call_tool("connection", {})
    assert result.is_error
    assert texts(result) == [outcome.UNANSWERED]


async def test_the_connection_tool_says_when_the_stack_answers(mcp_client: Client) -> None:
    offered = len((await mcp_client.list_tools()).tools)
    result = await mcp_client.call_tool("connection", {})
    assert data_of(result) == {"state": "connected", "tools": offered}


async def test_a_refused_key_is_told_by_every_tool_and_never_sent_again(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/capabilities", NOT_ADMITTED)
    assert names(await mcp_client.list_tools()) == {"connection"}
    sent = len(stack.arrived)
    for name in ("connection", "read_status", "restart"):
        result = await mcp_client.call_tool(name, {})
        assert result.is_error
        assert texts(result) == [outcome.REFUSED_KEY]
    await mcp_client.list_tools()
    assert len(stack.arrived) == sent


async def test_a_key_refused_after_a_listing_keeps_the_list_and_every_tool_says_refused(
    stack: Stack,
    mcp_client: Client,
    connection: Connection,
) -> None:
    listed = names(await mcp_client.list_tools())
    stack.reply("/api/status", NOT_ADMITTED)
    assert texts(await mcp_client.call_tool("read_status", {})) == [outcome.REFUSED_KEY]
    assert connection.state is State.REFUSED
    sent = len(stack.arrived)
    assert names(await mcp_client.list_tools()) == listed
    assert texts(await mcp_client.call_tool("read_version", {})) == [outcome.REFUSED_KEY]
    assert len(stack.arrived) == sent


async def test_a_stack_gone_after_a_listing_keeps_the_list_and_is_tried_again(
    stack: Stack,
    mcp_client: Client,
    connection: Connection,
) -> None:
    listed = names(await mcp_client.list_tools())
    stack.reply("/api/capabilities", Reply(status=502, body=""))
    assert names(await mcp_client.list_tools()) == listed
    assert connection.state is State.UNREACHABLE
    stack.reply("/api/capabilities", Reply(body=capabilities("act")))
    stack.reply("/api/status", STATUS)
    assert data_of(await mcp_client.call_tool("read_status", {}))["kind"] == "status"
    assert connection.state is State.CONNECTED


async def test_nothing_is_asked_before_the_first_listing(connection: Connection) -> None:
    assert connection.state is None


async def test_a_read_hands_the_answer_over_as_data_after_the_servers_line(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/status", STATUS)
    result = await mcp_client.call_tool("read_status", {})
    assert data_of(result) == envelope("status", {"services": []})
    assert result.structured_content == envelope("status", {"services": []})


async def test_a_reads_parameters_reach_the_stack_as_its_query(stack: Stack, mcp_client: Client) -> None:
    stack.reply("/api/forms", Reply(body=envelope("forms", [])))
    stack.reply("/api/checks", Reply(body=envelope("doctor", {})))
    await mcp_client.call_tool("read_forms", {"form": ["watching", "listening"]})
    await mcp_client.call_tool("read_checks", {"only": "storage"})
    assert stack.asked("/api/forms")[-1].query == {"form": ["watching", "listening"]}
    assert stack.asked("/api/checks")[-1].query == {"only": ["storage"]}


async def test_arguments_the_schema_refuses_never_reach_the_stack(stack: Stack, mcp_client: Client) -> None:
    result = await mcp_client.call_tool("read_checks", {"only": 5})
    assert result.is_error
    assert texts(result)[0].startswith(connection_module.ARGUMENTS_REFUSED)
    assert not stack.asked("/api/checks")


async def test_the_log_read_asks_for_lines_and_takes_a_whole_number_of_them(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/capabilities", Reply(body=capabilities("act", **{"/api/logs": "available"})))
    line = json.dumps(envelope("log", {"service": "sonarr", "line": "Imported."}))
    stack.reply("/api/logs", Reply(raw=f"{line}\n".encode(), content_type="application/x-ndjson"))
    await mcp_client.list_tools()
    result = await mcp_client.call_tool("read_logs", {"service": ["sonarr", "radarr"], "tail": "5"})
    assert data_of(result) == {"lines": [json.loads(line)]}
    assert stack.asked("/api/logs")[-1].query == {"service": ["sonarr", "radarr"], "tail": ["5"]}
    refused = await mcp_client.call_tool("read_logs", {"tail": "five"})
    assert texts(refused) == [f"{connection_module.ARGUMENTS_REFUSED}`tail` takes a whole number."]


async def test_the_log_read_asks_with_nothing_narrowed(stack: Stack, mcp_client: Client) -> None:
    stack.reply("/api/capabilities", Reply(body=capabilities("act", **{"/api/logs": "available"})))
    stack.reply("/api/logs", Reply(raw=b"", content_type="application/x-ndjson"))
    await mcp_client.list_tools()
    assert data_of(await mcp_client.call_tool("read_logs", {})) == {"lines": []}
    assert stack.asked("/api/logs")[-1].query == {}


async def test_a_bundle_is_handed_over_as_the_file_it_is(stack: Stack, mcp_client: Client) -> None:
    stack.reply("/api/capabilities", Reply(body=capabilities("act", **{"/api/bundle/{name}": "available"})))
    stack.reply("/api/bundle/support-1.tar.gz", Reply(raw=b"\x1f\x8bbundle", content_type="application/gzip"))
    await mcp_client.list_tools()
    result = await mcp_client.call_tool("read_bundle", {"name": "support-1.tar.gz"})
    line, embedded = result.content
    assert isinstance(line, types.TextContent)
    assert line.text == outcome.DATA
    assert isinstance(embedded, types.EmbeddedResource)
    assert isinstance(embedded.resource, types.BlobResourceContents)
    assert base64.b64decode(embedded.resource.blob) == b"\x1f\x8bbundle"
    assert embedded.resource.uri == "lemonfiber://bundle/support-1.tar.gz"
    assert embedded.resource.mime_type == "application/gzip"


async def test_a_rehearsal_asks_the_action_to_write_nothing(stack: Stack, mcp_client: Client) -> None:
    rehearsed = envelope("lifecycle", {"rehearsal": True, "offer": "o-1"})
    stack.reply("/api/actions/restart", Reply(body=rehearsed))
    result = await mcp_client.call_tool("rehearse_restart", {"services": ["sonarr"]})
    assert data_of(result) == rehearsed
    assert stack.asked("/api/actions/restart")[-1].body == {"services": ["sonarr"], "dry_run": True}


async def test_an_action_without_its_offer_is_refused_before_the_stack_is_asked(
    stack: Stack,
    mcp_client: Client,
) -> None:
    result = await mcp_client.call_tool("restart", {"services": ["sonarr"]})
    assert result.is_error
    assert texts(result) == [outcome.REHEARSE_FIRST]
    assert not stack.asked("/api/actions/restart")


async def test_an_action_carries_its_offer_and_answers_what_the_stack_said(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/actions/downloads-pause", Reply(body=envelope("pausing", {"paused": True})))
    result = await mcp_client.call_tool("downloads_pause", {"offer": "o-2"})
    assert data_of(result) == envelope("pausing", {"paused": True})
    assert stack.asked("/api/actions/downloads-pause")[-1].body == {"offer": "o-2"}


async def test_an_action_whose_work_runs_on_is_followed_to_its_outcome(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/actions/restart", Reply(status=202, body=STARTED))
    stack.reply(f"/api/jobs/{JOB}", Reply(body=envelope("lifecycle", {"restarted": ["sonarr"]})))
    result = await mcp_client.call_tool("restart", {"offer": "o-3"})
    assert data_of(result) == {
        "job": JOB,
        "standing": "finished",
        "envelope": envelope("lifecycle", {"restarted": ["sonarr"]}),
    }


async def test_work_still_going_after_a_while_is_answered_with_its_name(
    stack: Stack,
    mcp_client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(stack_module, "FOLLOWED_FOR", 0.0)
    stack.reply("/api/actions/restart", Reply(status=202, body=STARTED))
    stack.reply(f"/api/jobs/{JOB}", Reply(status=202, body=STARTED))
    result = await mcp_client.call_tool("restart", {"offer": "o-4"})
    assert data_of(result) == {"job": JOB, "standing": "running", "envelope": STARTED}


async def test_the_job_tool_says_where_work_stands_ended_included(stack: Stack, mcp_client: Client) -> None:
    ended = envelope("job", {"action": "restart", "job": JOB})
    stack.reply(f"/api/jobs/{JOB}", Reply(body=ended))
    assert data_of(await mcp_client.call_tool("job", {"job": JOB})) == {
        "job": JOB,
        "standing": "ended",
        "envelope": ended,
    }


async def test_a_job_this_run_never_started_is_said_to_be_none(stack: Stack, mcp_client: Client) -> None:
    stack.reply(f"/api/jobs/{JOB}", Reply(status=404, body=""))
    assert texts(await mcp_client.call_tool("job", {"job": JOB})) == [outcome.NO_SUCH_JOB]


async def test_a_refusal_is_the_servers_sentence_then_the_stacks_as_data(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/trace", Reply(status=400, body=problem("READ-4", "Name something to follow.")))
    result = await mcp_client.call_tool("read_trace", {})
    sentence, line, data = texts(result)
    assert (sentence, line) == (outcome.MISASKED, outcome.REFUSAL_DATA)
    assert json.loads(data)["name"] == "NO_TERM"


async def test_a_tool_not_offered_is_refused_without_asking_the_stack(
    stack: Stack,
    mcp_client: Client,
) -> None:
    result = await mcp_client.call_tool("read_logs", {})
    assert texts(result) == [outcome.NOT_OFFERED]
    assert not stack.asked("/api/logs")


async def test_a_tool_there_is_none_of_is_refused(mcp_client: Client) -> None:
    assert texts(await mcp_client.call_tool("uninstall", {})) == [outcome.UNKNOWN_TOOL]


async def test_reads_are_resources_and_resource_templates(mcp_client: Client) -> None:
    plain = {resource.uri for resource in (await mcp_client.list_resources()).resources}
    templates = {
        template.uri_template for template in (await mcp_client.list_resource_templates()).resource_templates
    }
    assert "lemonfiber://read/status" in plain
    assert "lemonfiber://read/forms{?form*}" in templates
    assert not any("actions" in address for address in plain | templates)


async def test_every_read_offered_is_a_resource_described_as_its_tool_is(mcp_client: Client) -> None:
    tools = {tool.name: tool for tool in (await mcp_client.list_tools()).tools}
    plain = (await mcp_client.list_resources()).resources
    templates = (await mcp_client.list_resource_templates()).resource_templates
    addressed = {name for name in tools if catalogue.SHAPES[name].resource is not None}
    assert {resource.name for resource in plain} | {template.name for template in templates} == addressed
    status = next(resource for resource in plain if resource.name == "read_status")
    assert (status.uri, status.description, status.mime_type) == (
        "lemonfiber://read/status",
        tools["read_status"].description,
        connection_module.JSON,
    )
    forms = next(template for template in templates if template.name == "read_forms")
    assert (forms.description, forms.mime_type) == (tools["read_forms"].description, connection_module.JSON)


async def test_a_resource_reads_as_the_tool_does(stack: Stack, mcp_client: Client) -> None:
    stack.reply("/api/status", STATUS)
    stack.reply("/api/forms", Reply(body=envelope("forms", [])))
    read = await mcp_client.read_resource("lemonfiber://read/status")
    contents = read.contents[0]
    assert isinstance(contents, types.TextResourceContents)
    assert json.loads(contents.text) == envelope("status", {"services": []})
    assert contents.mime_type == connection_module.JSON
    await mcp_client.read_resource("lemonfiber://read/forms?form=watching&form=listening")
    assert stack.asked("/api/forms")[-1].query == {"form": ["watching", "listening"]}


async def test_a_parameter_given_once_in_a_resource_address_is_its_last_value(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/checks", Reply(body=envelope("doctor", {})))
    await mcp_client.read_resource("lemonfiber://read/checks?only=storage")
    assert stack.asked("/api/checks")[-1].query == {"only": ["storage"]}


async def test_a_bundle_reads_as_a_blob_resource(stack: Stack, mcp_client: Client) -> None:
    stack.reply("/api/capabilities", Reply(body=capabilities("act", **{"/api/bundle/{name}": "available"})))
    stack.reply("/api/bundle/support-1.tar.gz", Reply(raw=b"bundle", content_type="application/gzip"))
    await mcp_client.list_tools()
    read = await mcp_client.read_resource("lemonfiber://bundle/support-1.tar.gz")
    contents = read.contents[0]
    assert isinstance(contents, types.BlobResourceContents)
    assert base64.b64decode(contents.blob) == b"bundle"
    assert contents.mime_type == "application/gzip"


async def test_a_parameter_given_empty_in_a_resource_address_reaches_the_stack_empty(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/checks", Reply(body=envelope("doctor", {})))
    await mcp_client.read_resource("lemonfiber://read/checks?only=")
    assert stack.asked("/api/checks")[-1].query == {"only": [""]}


async def test_a_parameter_a_read_does_not_take_is_refused_in_a_resource_address(
    stack: Stack,
    mcp_client: Client,
) -> None:
    with pytest.raises(MCPError, match=connection_module.ARGUMENTS_REFUSED):
        await mcp_client.read_resource("lemonfiber://read/status?verbose=1")
    assert not stack.asked("/api/status")


async def test_a_reading_is_acted_on_for_its_time_and_no_longer(
    stack: Stack,
    withholding: Withholding,
) -> None:
    moment = [datetime.datetime(2026, 10, 9, tzinfo=datetime.UTC)]
    stack.reply("/api/status", STATUS)
    async with AsyncClient(Address(stack.url, pin=stack.pin), Credential(KEY)) as client:
        held = Connection(client, withholding, clock=lambda: moment[0])
        await held.tools()
        moment[0] += connection_module.FRESH_FOR
        await held.call("read_status", {})
        assert len(stack.asked("/api/capabilities")) == 1
        moment[0] += datetime.timedelta(microseconds=1)
        await held.call("read_status", {})
        assert len(stack.asked("/api/capabilities")) == 2


def test_a_connections_clock_is_utc() -> None:
    assert connection_module.utc_now().tzinfo is datetime.UTC


@pytest.mark.parametrize(
    "address",
    [
        "lemonfiber://read/nothing",
        "lemonfiber://elsewhere/status",
        "https://read/status",
        "lemonfiber://read/",
    ],
)
async def test_an_address_naming_no_resource_is_the_protocols_error(mcp_client: Client, address: str) -> None:
    with pytest.raises(MCPError, match=connection_module.NOT_A_RESOURCE):
        await mcp_client.read_resource(address)


async def test_a_resource_the_stack_refuses_is_the_protocols_error_in_the_servers_words(
    stack: Stack,
    mcp_client: Client,
) -> None:
    stack.reply("/api/status", Reply(status=500, body=problem("SERVE-6", "Could not render.")))
    with pytest.raises(MCPError, match=outcome.FAILED):
        await mcp_client.read_resource("lemonfiber://read/status")


async def test_a_listing_that_moved_during_a_call_is_announced(
    stack: Stack,
    mcp_client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    announced: list[bool] = []

    async def announce(_: ServerSession) -> None:
        announced.append(True)

    monkeypatch.setattr(ServerSession, "send_tool_list_changed", announce)
    await mcp_client.call_tool("read_version", {})
    assert not announced
    await mcp_client.list_tools()
    monkeypatch.setattr(connection_module, "FRESH_FOR", datetime.timedelta(seconds=-1))
    stack.reply("/api/status", STATUS)
    await mcp_client.call_tool("read_status", {})
    assert not announced
    stack.reply("/api/capabilities", Reply(body=capabilities("read")))
    await mcp_client.call_tool("read_status", {})
    assert announced == [True]


async def test_nothing_unexpected_reaches_the_wire(
    stack: Stack,
    mcp_client: Client,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    async def broken(*_: object) -> object:
        raise RuntimeError(KEY)

    monkeypatch.setattr(Connection, "call", broken)
    monkeypatch.setattr(Connection, "tools", broken)
    monkeypatch.setattr(Connection, "resources", broken)
    monkeypatch.setattr(Connection, "read_resource", broken)
    result = await mcp_client.call_tool("read_status", {})
    assert texts(result) == [outcome.UNEXPECTED]
    for asking in (
        mcp_client.list_tools(),
        mcp_client.list_resources(),
        mcp_client.list_resource_templates(),
        mcp_client.read_resource("lemonfiber://read/status"),
    ):
        with pytest.raises(MCPError) as raised:
            await asking
        assert KEY not in str(raised.value)
    logged = [record.getMessage() for record in caplog.records if record.name == serving.__name__]
    assert logged == [
        "a tool call failed",
        "listing the tools failed",
        "listing the resources failed",
        "listing the resource templates failed",
        "reading a resource failed",
    ]


async def test_no_key_or_pin_leaves_in_any_answer_or_refusal(stack: Stack, mcp_client: Client) -> None:
    leaking = {"note": f"{KEY} {stack.pin} {stack.pin.upper()}"}
    stack.reply("/api/status", Reply(body=envelope("status", leaking)))
    stack.reply("/api/checks", Reply(status=400, body=problem("READ-11", f"{KEY} {stack.pin}")))
    said = [
        *texts(await mcp_client.call_tool("read_status", {})),
        *texts(await mcp_client.call_tool("read_checks", {"only": "x"})),
        json.dumps((await mcp_client.call_tool("read_status", {})).structured_content),
    ]
    contents = (await mcp_client.read_resource("lemonfiber://read/status")).contents[0]
    assert isinstance(contents, types.TextResourceContents)
    said.append(contents.text)
    for text in said:
        assert KEY not in text
        assert stack.pin not in text.lower()
