# Copyright (c) 2026 NightWorksIO
"""The stand-in stack, what it answers with, and a server reaching it through the vendored client."""

from typing import TYPE_CHECKING, Final

import pytest
from lemonfiber import KEY_CALLABLE, Address, AsyncClient, Credential, Read
from lemonfiber.reads import ACTIONS
from mcp import Client

from lemonfiber_mcp import serving
from lemonfiber_mcp.connection import Connection
from lemonfiber_mcp.withheld import Withholding
from tests.stack import Reply, Stack, envelope

if TYPE_CHECKING:
    from collections.abc import AsyncIterator


KEY: Final = "lfk_" + "0123456789abcdef" * 4
"""A key shaped as the core mints one, so a test can look for it in everything the server says."""
VERSION: Final = "0.0.0-test"
MEMBER_READS: Final = frozenset({Read.REQUESTS, Read.HELD, Read.HELD_ID, Read.WATCHING, Read.PLAYING})
"""The reads a member's key reaches: their own row of the household, their own shelf and each title on it, what
they are part-way through, and their own sessions."""
EVERY_READ: Final = frozenset(Read)


STACK_ID: Final = "stack-1f6a"
"""The stand-in stack's own identifier."""


def capabilities(scope: str, **overrides: str) -> dict[str, object]:
    """Return what the stack says a key of a scope may ask for, each read and each action a key may call."""
    reads = {
        read.path: "unpermitted" if scope == "member" and read not in MEMBER_READS else "available"
        for read in EVERY_READ
    }
    acting = "available" if scope == "act" else "unpermitted"
    actions = {f"{ACTIONS}/{action}": acting for action in KEY_CALLABLE}
    return envelope(
        "capabilities",
        {
            "capabilities": {**reads, **actions, f"{ACTIONS}/repair": "unpermitted", **overrides},
            "scope": scope,
            "stack": STACK_ID,
        },
    )


@pytest.fixture
def anyio_backend() -> str:
    """Run every asynchronous test on asyncio, which the client's aiohttp needs."""
    return "asyncio"


@pytest.fixture
async def stack() -> AsyncIterator[Stack]:
    """Return a running stand-in stack answering for an `act` key."""
    async with Stack() as running:
        running.reply("/api/capabilities", Reply(body=capabilities("act")))
        yield running


@pytest.fixture
def withholding(stack: Stack) -> Withholding:
    """Return what the server withholds: the key and the stand-in's pin."""
    return Withholding([KEY, stack.pin])


@pytest.fixture
async def connection(stack: Stack, withholding: Withholding) -> AsyncIterator[Connection]:
    """Return a connection to the stand-in through the vendored client, holding the key."""
    async with AsyncClient(Address(stack.url, pin=stack.pin), Credential(KEY)) as client:
        yield Connection(client, withholding)


@pytest.fixture
async def mcp_client(connection: Connection, withholding: Withholding) -> AsyncIterator[Client]:
    """Return a protocol client talking to the server in-process, the server answering from `connection`."""
    async with Client(serving.build(serving.always(connection), withholding, VERSION)) as client:
        yield client
