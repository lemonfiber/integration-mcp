# Copyright (c) 2026 NightWorksIO
"""Start the server: over stdio on a person's own machine, configured from the environment.

    lemonfiber-mcp stdio

A setting that is missing or refused stops the start with a sentence naming
the setting and never its value.
"""

import argparse
import importlib.metadata
import logging
import os
import sys
from typing import TYPE_CHECKING, Final

import anyio
from lemonfiber import AsyncClient
from mcp.server.stdio import stdio_server

from lemonfiber_mcp import serving, settings
from lemonfiber_mcp.connection import Connection
from lemonfiber_mcp.withheld import Withholding, install

if TYPE_CHECKING:
    from collections.abc import Mapping, Sequence


PACKAGE: Final = "lemonfiber-mcp"
REFUSED_TO_START: Final = 2
"""The exit status of a start refused for what it was given."""

logger = logging.getLogger(__name__)


def version() -> str:
    """Return this server's version, as the package it was installed from says."""
    return importlib.metadata.version(PACKAGE)


async def serve_stdio(environment: Mapping[str, str]) -> None:
    """Serve one person's assistant over standard input and output until it closes them."""
    stack = settings.stack_from(environment)
    key, written = settings.key_of(environment)
    withholding = Withholding([written, *([] if stack.pin is None else [stack.pin.hex])])
    install(withholding)
    async with AsyncClient(stack.address, key) as client:
        server = serving.build(serving.always(Connection(client, withholding)), withholding, version())
        logger.info("serving over stdio")
        async with stdio_server() as (reading, writing):
            await server.run(reading, writing, serving.initialization(server))


def main(arguments: Sequence[str] | None = None, environment: Mapping[str, str] | None = None) -> int:
    """Start the server as the arguments say, and return the exit status."""
    parser = argparse.ArgumentParser(prog=PACKAGE, description="lemonfiber for AI assistants.")
    modes = parser.add_subparsers(dest="mode", required=True)
    modes.add_parser("stdio", help="serve one assistant on this machine over standard input and output")
    parser.parse_args(arguments)
    try:
        anyio.run(serve_stdio, os.environ if environment is None else environment)
    except settings.SettingsError as refused:
        sys.stderr.write(f"lemonfiber-mcp: {refused}\n")
        return REFUSED_TO_START
    return 0
