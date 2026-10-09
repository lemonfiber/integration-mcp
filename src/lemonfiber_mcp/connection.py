# Copyright (c) 2026 NightWorksIO
"""One credential's way to the stack: what it is offered, and every tool and resource it calls.

The tools are what the stack's capabilities say this credential may ask for,
read again on every listing and before a call where the reading is older than
`FRESH_FOR`. Until a reading has arrived the one tool is `connection`. Once the
key is refused nothing is sent with it again, and every tool says so.
"""

import datetime
import urllib.parse
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Final, cast

import jsonschema
import mcp_types as types
from lemonfiber import LemonfiberError
from mcp.shared.exceptions import MCPError

from lemonfiber_mcp import catalogue, outcome, stack
from lemonfiber_mcp.outcome import Failure, State
from lemonfiber_mcp.shapes import Reach

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from lemonfiber import AsyncClient, CapabilitySet

    from lemonfiber_mcp.shapes import ToolShape
    from lemonfiber_mcp.withheld import Withholding

FRESH_FOR: Final = datetime.timedelta(seconds=30)
"""How long a reading of the capabilities is acted on before a call reads it again."""
SCHEME: Final = "lemonfiber"
JSON: Final = "application/json"
NOT_A_RESOURCE: Final = "There is no resource at that address."
ARGUMENTS_REFUSED: Final = "The arguments were refused: "


def utc_now() -> datetime.datetime:
    """Return the time now, in UTC, as the client stamps a reading of the capabilities."""
    return datetime.datetime.now(datetime.UTC)


@dataclass(slots=True)
class Held:
    """What is known of one credential between its calls: the stack's last word on it, and never the credential.

    Over stdio one is held for the life of the process. Over HTTP one is held
    for each key a request brings, by its digest, so a refused key stays
    refused and a reading of the capabilities is not asked for on every call.
    """

    capabilities: CapabilitySet | None = None
    read_at: datetime.datetime | None = None
    tools: dict[str, types.Tool] = field(default_factory=dict[str, types.Tool])
    failure: Failure | None = None


class Connection:
    """What one credential is offered, and its calls to the stack."""

    def __init__(
        self,
        client: AsyncClient,
        withholding: Withholding,
        held: Held | None = None,
        clock: Callable[[], datetime.datetime] = utc_now,
    ) -> None:
        """Hold the client the credential asks through and what is known of it; nothing is asked until a tool is listed or called."""
        self._client = client
        self._clock = clock
        self._withholding = withholding
        self._audience = catalogue.UNKNOWN
        self._held = Held() if held is None else held

    @property
    def state(self) -> State | None:
        """Return where this credential stands with the stack, or None before it has been asked anything."""
        if self._held.failure is not None and self._held.failure.state is not None:
            return self._held.failure.state
        return None if self._held.capabilities is None else State.CONNECTED

    async def refresh(self) -> Failure | None:
        """Read the capabilities again, unless the key was refused; return why not, where they could not be read."""
        if self.state is State.REFUSED:
            return self._held.failure
        try:
            capabilities = await self._client.capabilities()
        except LemonfiberError as error:
            self._held.failure = outcome.failure_of(error)
            return self._held.failure
        self._held.capabilities = capabilities
        self._held.read_at = self._clock()
        self._held.failure = None
        self._audience = catalogue.audience_of(capabilities.scope)
        self._held.tools = catalogue.offered(capabilities, self._audience)
        return None

    def offered(self) -> dict[str, types.Tool]:
        """Return the tools the last listing offered, by name, without asking the stack."""
        return dict(self._held.tools)

    async def tools(self) -> list[types.Tool]:
        """Return the tools offered now: the capabilities' answer, the last list, or `connection` alone."""
        await self.refresh()
        return list((self._held.tools or catalogue.connection_only(self._audience)).values())

    async def resources(self) -> tuple[list[types.Resource], list[types.ResourceTemplate]]:
        """Return the resource and the resource template of every read tool offered now."""
        await self.refresh()
        addressed = [
            (name, tool.description, address)
            for name, tool in self._held.tools.items()
            if (address := catalogue.SHAPES[name].resource) is not None
        ]
        plain = [
            types.Resource(name=name, uri=address, description=description, mime_type=JSON)
            for name, description, address in addressed
            if "{" not in address
        ]
        templates = [
            types.ResourceTemplate(name=name, uri_template=address, description=description, mime_type=JSON)
            for name, description, address in addressed
            if "{" in address
        ]
        return plain, templates

    async def _fresh(self) -> Failure | None:
        if self._held.read_at is None or self._clock() - self._held.read_at > FRESH_FOR:
            return await self.refresh()
        return None

    async def call(self, name: str, arguments: Mapping[str, object]) -> types.CallToolResult:
        """Call a tool by name and return its answer, never raising."""
        shape = catalogue.SHAPES.get(name)
        if shape is None:
            return outcome.failed(Failure(outcome.UNKNOWN_TOOL), self._withholding)
        if name == catalogue.CONNECTION:
            return await self._connection()
        answer = await self._asked(shape, arguments)
        if isinstance(answer, Failure):
            return outcome.failed(answer, self._withholding)
        if isinstance(answer, stack.Bundle):
            return types.CallToolResult(
                content=[
                    types.TextContent(text=outcome.DATA),
                    types.EmbeddedResource(
                        resource=types.BlobResourceContents(
                            uri=f"{SCHEME}://bundle/{urllib.parse.quote(answer.name)}",
                            mime_type=answer.content_type,
                            blob=answer.encoded(),
                        ),
                    ),
                ],
            )
        return outcome.answered(answer, self._withholding)

    async def _connection(self) -> types.CallToolResult:
        failure = await self.refresh()
        if failure is None:
            return outcome.answered(
                {"state": State.CONNECTED.value, "tools": len(self._held.tools)},
                self._withholding,
            )
        return outcome.failed(failure, self._withholding)

    async def _ready(self, shape: ToolShape, arguments: Mapping[str, object]) -> Failure | None:
        """Return why a call cannot be sent, or None where it can: refused, unread, not offered, or misasked."""
        if self.state is State.REFUSED:
            return self._held.failure
        stale = await self._fresh()
        tool = self._held.tools.get(shape.name)
        if stale is not None or tool is None:
            return stale or Failure(outcome.NOT_OFFERED)
        if shape.reach is Reach.ACTION and stack.OFFER in shape.parameters and stack.OFFER not in arguments:
            return Failure(outcome.REHEARSE_FIRST)
        try:
            jsonschema.validate(dict(arguments), tool.input_schema)
        except jsonschema.ValidationError as refused:
            return Failure(ARGUMENTS_REFUSED + refused.message)
        return None

    async def _asked(self, shape: ToolShape, arguments: Mapping[str, object]) -> object:
        """Return what a tool's call comes to: the stack's answer, or why there is none."""
        not_sent = await self._ready(shape, arguments)
        if not_sent is not None:
            return not_sent
        try:
            answer = await self._dispatch(shape, arguments)
        except stack.NotAWholeNumberError as refused:
            return Failure(ARGUMENTS_REFUSED + str(refused))
        except LemonfiberError as error:
            self._held.failure = outcome.failure_of(error)
            return self._held.failure
        self._held.failure = None
        return answer

    async def _dispatch(self, shape: ToolShape, arguments: Mapping[str, object]) -> object:
        match shape.reach:
            case Reach.REHEARSAL:
                return await stack.rehearse(self._client, shape, arguments)
            case Reach.ACTION:
                return await stack.act(self._client, shape, arguments)
            case _ if shape.name == catalogue.JOB:
                return await stack.job(self._client, str(arguments[catalogue.JOB]))
            case _:
                return await stack.read(self._client, shape, arguments)

    async def read_resource(self, uri: str) -> types.ReadResourceResult:
        """Read a resource by its address, raising the protocol's error where it has no answer."""
        shape, arguments = self._addressed(uri)
        answer = await self._asked(shape, arguments)
        if isinstance(answer, Failure):
            raise MCPError(types.INVALID_PARAMS, self._withholding.withhold(answer.sentence))
        if isinstance(answer, stack.Bundle):
            contents: types.TextResourceContents | types.BlobResourceContents = types.BlobResourceContents(
                uri=uri,
                mime_type=answer.content_type,
                blob=answer.encoded(),
            )
        else:
            text, _ = outcome.as_json(answer, self._withholding)
            contents = types.TextResourceContents(uri=uri, mime_type=JSON, text=text)
        return types.ReadResourceResult(contents=[contents])

    def _addressed(self, uri: str) -> tuple[ToolShape, dict[str, object]]:
        """Return the read tool an address names and the arguments it carries."""
        parts = urllib.parse.urlsplit(uri)
        target = urllib.parse.unquote(parts.path.removeprefix("/"))
        if parts.scheme == SCHEME and parts.netloc == "bundle" and target:
            return catalogue.SHAPES[catalogue.BUNDLE], {"name": target}
        shape = catalogue.READABLE.get(target)
        if parts.scheme != SCHEME or parts.netloc != "read" or shape is None:
            raise MCPError(types.INVALID_PARAMS, NOT_A_RESOURCE)
        given = urllib.parse.parse_qs(parts.query, keep_blank_values=True)
        properties = cast("dict[str, dict[str, object]]", shape.input_schema.get("properties", {}))
        arguments: dict[str, object] = {
            name: values if properties.get(name, {}).get("type") == "array" else values[-1]
            for name, values in given.items()
        }
        return shape, arguments
