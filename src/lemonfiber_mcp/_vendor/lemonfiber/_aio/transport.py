# Copyright (c) 2026 NightWorksIO
"""Sending one call to a stack over aiohttp: each route in turn, its pin or verifying context, no proxy, no redirect."""

import asyncio
import ssl
from typing import TYPE_CHECKING, Final

import aiohttp

from lemonfiber._protocol.calls import Answer, Call, declared_over, received
from lemonfiber._protocol.refusals import CERTIFICATE_REFUSED, NOT_ANSWERING
from lemonfiber.problems import (
    CertificateRefusedError,
    ConfigurationError,
    LemonfiberError,
    UnreachableError,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from lemonfiber._protocol.retry import Attempts
    from lemonfiber.address import Address, Route


type TlsSetting = aiohttp.Fingerprint | ssl.SSLContext | bool

NOT_PROXIED: Final = "The session given would send through a proxy, and a credential goes to the stack alone, so nothing was sent."
"""Why a request a caller's session would send through a proxy is refused."""


async def unproxied(
    request: aiohttp.ClientRequest,
    handler: aiohttp.ClientHandlerType,
) -> aiohttp.ClientResponse:
    """Send a request straight to the stack, refusing one the session would send through a proxy.

    A session the caller gave may carry a proxy of its own, or read one from the
    environment; either would hand the credential to the proxy, in the clear over
    http. This runs once aiohttp has chosen the proxy and before anything is
    sent, and as the request's only middleware it also keeps the session's own
    middlewares from ever seeing the credential.
    """
    if request.proxy is not None:
        raise ConfigurationError(NOT_PROXIED)
    return await handler(request)


STRAIGHT: Final = (unproxied,)
"""The middlewares every request is sent through: this one, in place of any the session holds."""


def tls_for(address: Address) -> TlsSetting:
    """Return what every request to an address is checked with: its pin, a verifying context, or nothing."""
    if address.pin is not None:
        return aiohttp.Fingerprint(address.pin.digest)
    if address.scheme == "https":
        return ssl.create_default_context()
    return True


def checked(session: aiohttp.ClientSession) -> aiohttp.ClientSession:
    """Return a caller's session, refusing one whose connector would not check a pin."""
    if not isinstance(session.connector, aiohttp.TCPConnector):
        msg = "A session given to the client connects over TCP, so the certificate pin can be checked."
        raise ConfigurationError(msg)
    return session


async def attempt(
    session: aiohttp.ClientSession,
    route: Route,
    tls: TlsSetting,
    call: Call,
    limit: aiohttp.ClientTimeout,
) -> Answer | None:
    """Send one call over one route, or return nothing where no connection could be made there.

    A route that reaches a named stack by an address it resolved to names the
    stack in the TLS handshake, and the certificate is checked against that name.
    A failure is raised once aiohttp's error is let go, since that error holds
    the request's headers, credential included, and would ride along as the
    failure's cause.
    """
    try:
        async with session.request(
            call.method,
            route.url(call.path),
            data=call.body,
            headers={**call.headers, **route.headers()},
            ssl=tls,
            server_hostname=route.named,
            middlewares=STRAIGHT,
            allow_redirects=False,
            raise_for_status=False,
            timeout=limit,
        ) as response:
            body = (
                await response.read()
                if call.most is None
                else await capped(response.headers, response.content, call.most)
            )
    except aiohttp.ServerFingerprintMismatch, aiohttp.ClientSSLError:
        failure: LemonfiberError = CertificateRefusedError(CERTIFICATE_REFUSED)
    except aiohttp.ClientConnectorError:
        return None
    except aiohttp.ClientError, TimeoutError:
        failure = UnreachableError(NOT_ANSWERING)
    else:
        return received(response.status, response.headers, body)
    raise failure


async def capped(headers: Mapping[str, str], content: aiohttp.StreamReader, most: int) -> bytes:
    """Return at most one byte past `most` of an answer's body, and none of one whose headers declare more.

    What is left unread is aiohttp's to deal with: a connection whose answer was not
    read to its end is closed when the answer is let go, not kept for the next request.
    """
    if declared_over(headers, most):
        return b""
    kept = bytearray()
    while len(kept) <= most and (chunk := await content.read(most + 1 - len(kept))):
        kept += chunk
    return bytes(kept)


async def exchange(
    session: aiohttp.ClientSession,
    address: Address,
    tls: TlsSetting,
    call: Call,
    limit: aiohttp.ClientTimeout,
) -> Answer:
    """Send one call over the first route a connection can be made on, following no redirect.

    A route is passed over only where no connection could be made, so nothing
    was sent; once a connection is made, its outcome is the call's.
    """
    for route in address.routes:
        answer = await attempt(session, route, tls, call, limit)
        if answer is not None:
            return answer
    raise UnreachableError(NOT_ANSWERING)


async def asked(
    session: aiohttp.ClientSession,
    address: Address,
    tls: TlsSetting,
    call: Call,
    attempts: Attempts,
) -> Answer:
    """Send a call, and send a read again after a passing failure, as `attempts` allows.

    The last attempt's outcome is the call's: its answer, or the failure that
    nothing answered.
    """
    loop = asyncio.get_running_loop()
    while True:
        outcome: Answer | UnreachableError
        limit = aiohttp.ClientTimeout(total=attempts.left(loop.time()))
        try:
            outcome = await exchange(session, address, tls, call, limit)
        except UnreachableError as unanswered:
            outcome = unanswered
        pause = attempts.pause(outcome if isinstance(outcome, Answer) else None, loop.time())
        if pause is None:
            break
        await asyncio.sleep(pause)
    if isinstance(outcome, UnreachableError):
        raise outcome
    return outcome
