# Copyright (c) 2026 NightWorksIO
"""Start the server, configured from the environment, or act on the certificate it keeps.

    lemonfiber-mcp stdio            one assistant on this machine, over standard input and output
    lemonfiber-mcp http             assistants anywhere, over Streamable HTTP and TLS
    lemonfiber-mcp ca replace       make a replacement private root beside the one in force
    lemonfiber-mcp ca switch        put the replacement root in force
    lemonfiber-mcp pinned replace   make a new pinned certificate
    lemonfiber-mcp health           whether the HTTP mode running beside this answers healthy

A setting that is missing or refused stops the start with a sentence naming
the setting and never its value.
"""

import argparse
import importlib.metadata
import ipaddress
import logging
import os
import sys
from typing import TYPE_CHECKING, Final

import anyio
import uvicorn
from lemonfiber import AsyncClient
from mcp.server.stdio import stdio_server

from lemonfiber_mcp import serving, settings, web
from lemonfiber_mcp.certificates import making, modes, probe, state
from lemonfiber_mcp.certificates.manager import Certificates, utc_now
from lemonfiber_mcp.certificates.settings import Mode, Tls, TlsSettingsError, tls_from
from lemonfiber_mcp.connection import Connection
from lemonfiber_mcp.withheld import Withholding, install

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Mapping, Sequence

PACKAGE: Final = "lemonfiber-mcp"
REFUSED_TO_START: Final = 2
"""The exit status of a start refused for what it was given."""
UNHEALTHY: Final = 1
UNINSTALLED: Final = "unreleased"
"""The version a server run from a checkout says it is, where no installed package names one."""
HOLDS_NO_KEY: Final = (
    "The HTTP mode holds no key of its own: each request brings the person's. Unset LEMONFIBER_KEY "
    "and LEMONFIBER_KEY_FILE."
)
LISTEN_NEEDED: Final = (
    f"{web.LISTEN} is not set, or is not an address and a port: give where to listen, as "
    "0.0.0.0:8443 or [::]:8443. There is no default port."
)
PORTS: Final = range(1, 2**16)
REFUSALS: Final = (settings.SettingsError, TlsSettingsError, modes.CertificateError, state.StateError)
"""Every refusal a start or a command ends with, each a sentence naming what to change."""

logger = logging.getLogger(__name__)


def version() -> str:
    """Return this server's version, as the package it was installed from says."""
    try:
        return importlib.metadata.version(PACKAGE)
    except importlib.metadata.PackageNotFoundError:
        return UNINSTALLED


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


def listen_from(environment: Mapping[str, str]) -> tuple[str, int]:
    """Return where the HTTP mode listens, refusing anything but an address or a name and a port."""
    host, _, port = environment.get(web.LISTEN, "").strip().rpartition(":")
    host = host.removeprefix("[").removesuffix("]")
    if not host or not port.isdigit() or int(port) not in PORTS:
        raise settings.SettingsError(LISTEN_NEEDED)
    return host, int(port)


def shown(host: str, port: int) -> str:
    """Return the address the HTTP mode serves the protocol at, as a person would type it."""
    try:
        bracketed = f"[{host}]" if isinstance(ipaddress.ip_address(host), ipaddress.IPv6Address) else host
    except ValueError:
        bracketed = host
    return f"https://{bracketed}:{port}{web.PATH}"


def kept_tls(environment: Mapping[str, str]) -> Tls:
    """Return how the certificate comes, the state directory made and held to `0700` where the mode keeps state."""
    tls = tls_from(environment)
    if tls.mode is not Mode.FILES:
        state.kept(tls.state)
    return tls


def http_server(environment: Mapping[str, str]) -> tuple[uvicorn.Server, Certificates]:
    """Return the HTTP mode ready to serve, its first certificate loaded, refusing a start the settings do not allow."""
    stack = settings.stack_from(environment)
    if environment.get(settings.KEY) or environment.get(settings.KEY_FILE):
        raise settings.SettingsError(HOLDS_NO_KEY)
    host, port = listen_from(environment)
    tls = kept_tls(environment)
    withholding = Withholding([] if stack.pin is None else [stack.pin.hex])
    install(withholding)
    source = modes.source_of(tls)
    certificates = Certificates(source)
    certificates.start()
    root = source.root_file if isinstance(source, modes.PrivateCa) else None
    gate = web.Gate(
        web.protocol(withholding, version(), host),
        stack.address,
        withholding,
        web.Pool(),
        certificates,
        root,
    )
    config = uvicorn.Config(
        gate,
        host=host,
        port=port,
        ssl_context_factory=lambda _config, _default: certificates.context,
        log_config=None,
        access_log=False,
        server_header=False,
        proxy_headers=False,
        lifespan="on",
    )
    logger.info("serving over HTTPS at %s", shown(host, port))
    return uvicorn.Server(config), certificates


async def serve_http(environment: Mapping[str, str]) -> None:
    """Serve assistants over Streamable HTTP and TLS, each request with its own key, until stopped."""
    server, certificates = http_server(environment)
    async with anyio.create_task_group() as group:
        group.start_soon(certificates.watch)
        await server.serve()
        group.cancel_scope.cancel()


def private_ca(environment: Mapping[str, str]) -> modes.PrivateCa:
    """Return the private root's source, refusing where the settings do not choose `private-ca`."""
    tls = kept_tls(environment)
    if tls.mode is not Mode.PRIVATE_CA:
        msg = "A private root is replaced or switched only where LEMONFIBER_TLS_MODE is private-ca."
        raise modes.CertificateError(msg)
    return modes.PrivateCa(tls)


def replace_root(environment: Mapping[str, str]) -> str:
    """Make a replacement private root, and say how to recognise it."""
    made = private_ca(environment).replace(utc_now())
    return (
        f"A replacement root waits to be installed; its fingerprint is {making.fingerprint(made)}. "
        "Install it on every device, then run `lemonfiber-mcp ca switch`."
    )


def switch_root(environment: Mapping[str, str]) -> str:
    """Put the replacement private root in force, and say so."""
    if private_ca(environment).switch():
        return (
            "The replacement root is in force, and the old root's key is deleted. "
            "A running server takes it within a minute."
        )
    return "No replacement root waits; `lemonfiber-mcp ca replace` makes one."


def replace_pinned(environment: Mapping[str, str]) -> str:
    """Make a new pinned certificate, and say its fingerprint."""
    tls = kept_tls(environment)
    if tls.mode is not Mode.PINNED:
        msg = "A pinned certificate is replaced only where LEMONFIBER_TLS_MODE is pinned or unset."
        raise modes.CertificateError(msg)
    made = modes.Pinned(tls).replace(utc_now())
    return f"A new pinned certificate is made; give every client its fingerprint: {made.fingerprint}"


def checked_health(environment: Mapping[str, str]) -> bool:
    """Tell whether the HTTP mode beside this answers healthy, holding it to the certificate it keeps."""
    host, port = listen_from(environment)
    tls = tls_from(environment)
    chain = tls.certificate if tls.certificate is not None else modes.leaf_dir(tls) / modes.CHAIN
    return probe.healthy(host, port, chain)


type Run = Callable[[Mapping[str, str]], int]
"""A command: given the environment, do it and return the exit status."""


def served(serve: Callable[[Mapping[str, str]], Awaitable[None]]) -> Run:
    """Return a command serving until stopped."""

    def run(environment: Mapping[str, str]) -> int:
        anyio.run(serve, environment)
        return 0

    return run


def said(sentence: Callable[[Mapping[str, str]], str]) -> Run:
    """Return a command printing the sentence it comes to."""

    def run(environment: Mapping[str, str]) -> int:
        sys.stdout.write(f"{sentence(environment)}\n")
        return 0

    return run


def health(environment: Mapping[str, str]) -> int:
    """Return the exit status a health check comes to: 0 where the HTTP mode answers healthy."""
    return 0 if checked_health(environment) else UNHEALTHY


def parser() -> argparse.ArgumentParser:
    """Return the command line's parser, each command carrying what it runs."""
    made = argparse.ArgumentParser(prog=PACKAGE, description="lemonfiber for AI assistants.")
    commands = made.add_subparsers(required=True)
    stdio = commands.add_parser(
        "stdio",
        help="serve one assistant on this machine over standard input and output",
    )
    stdio.set_defaults(run=served(serve_stdio))
    http = commands.add_parser("http", help="serve assistants anywhere over Streamable HTTP and TLS")
    http.set_defaults(run=served(serve_http))
    ca = commands.add_parser("ca", help="act on the private root").add_subparsers(required=True)
    ca.add_parser("replace", help="make a replacement root beside the one in force").set_defaults(
        run=said(replace_root),
    )
    ca.add_parser("switch", help="put the replacement root in force").set_defaults(run=said(switch_root))
    pinned = commands.add_parser("pinned", help="act on the pinned certificate").add_subparsers(required=True)
    pinned.add_parser("replace", help="make a new pinned certificate").set_defaults(run=said(replace_pinned))
    commands.add_parser("health", help="whether the HTTP mode beside this answers healthy").set_defaults(
        run=health,
    )
    return made


def main(arguments: Sequence[str] | None = None, environment: Mapping[str, str] | None = None) -> int:
    """Run the command the arguments name, and return the exit status."""
    run: Run = parser().parse_args(arguments).run
    try:
        return run(os.environ if environment is None else environment)
    except REFUSALS as refused:
        sys.stderr.write(f"lemonfiber-mcp: {refused}\n")
        return REFUSED_TO_START
