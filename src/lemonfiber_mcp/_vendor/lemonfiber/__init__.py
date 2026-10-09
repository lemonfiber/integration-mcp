# Copyright (c) 2026 NightWorksIO
"""The Python client for lemonfiber's web API.

`AsyncClient` (aiohttp) and `SyncClient` (urllib3) speak the same contract with
the same behaviour. Each is built with an `Address` — loopback, or anywhere a
`CertificatePin` vouches for — and a `Credential`: the per-run token, a
session's secret, or an integration key. Every answer is an envelope typed by
its kind (`lemonfiber.contract` holds each shape), and every failure is a
`LemonfiberError`.
"""

from lemonfiber._aio import AsyncClient, AsyncStream, admit_async
from lemonfiber._generated import (
    KEY_CALLABLE,
    KINDS,
    REFUSAL_CODES,
    Envelope,
    KeyCallable,
    KeyCallableAction,
    Kind,
    ListedRefusal,
    RefusalCode,
    is_key_callable,
    is_refusal_code,
)
from lemonfiber._protocol.calls import Json, Query
from lemonfiber._sync import SyncClient, SyncStream, admit
from lemonfiber.address import Address, CertificatePin, Route
from lemonfiber.capabilities import CapabilitySet
from lemonfiber.credential import CREDENTIAL_HEADER, Credential, Session
from lemonfiber.envelope import SPOKEN_API_VERSION, expect, parse_envelope, read_envelope
from lemonfiber.files import BundleFile
from lemonfiber.jobs import Ended, Finished, JobStanding, Running
from lemonfiber.problems import (
    AddressRefusedError,
    ApiVersionMismatchError,
    BusyError,
    CertificateRefusedError,
    ConfigurationError,
    CredentialRefusedError,
    DeclinedError,
    FailedError,
    LemonfiberError,
    MisaskedError,
    MissingError,
    NoSuchJobError,
    NotAdmittedError,
    PasswordRefusedError,
    RefusedError,
    StillRunningError,
    StreamLostError,
    TooManyAttemptsError,
    UnexpectedKindError,
    UnknownKindError,
    UnreachableError,
    UnreadableResponseError,
)
from lemonfiber.reads import Read
from lemonfiber.stream import HEARTBEAT, SILENCE_ALLOWED, Arrival, Break, Gap, Live, Stale, Unrecognised

__all__ = [
    "CREDENTIAL_HEADER",
    "HEARTBEAT",
    "KEY_CALLABLE",
    "KINDS",
    "REFUSAL_CODES",
    "SILENCE_ALLOWED",
    "SPOKEN_API_VERSION",
    "Address",
    "AddressRefusedError",
    "ApiVersionMismatchError",
    "Arrival",
    "AsyncClient",
    "AsyncStream",
    "Break",
    "BundleFile",
    "BusyError",
    "CapabilitySet",
    "CertificatePin",
    "CertificateRefusedError",
    "ConfigurationError",
    "Credential",
    "CredentialRefusedError",
    "DeclinedError",
    "Ended",
    "Envelope",
    "FailedError",
    "Finished",
    "Gap",
    "JobStanding",
    "Json",
    "KeyCallable",
    "KeyCallableAction",
    "Kind",
    "LemonfiberError",
    "ListedRefusal",
    "Live",
    "MisaskedError",
    "MissingError",
    "NoSuchJobError",
    "NotAdmittedError",
    "PasswordRefusedError",
    "Query",
    "Read",
    "RefusalCode",
    "RefusedError",
    "Route",
    "Running",
    "Session",
    "Stale",
    "StillRunningError",
    "StreamLostError",
    "SyncClient",
    "SyncStream",
    "TooManyAttemptsError",
    "UnexpectedKindError",
    "UnknownKindError",
    "UnreachableError",
    "UnreadableResponseError",
    "Unrecognised",
    "admit",
    "admit_async",
    "expect",
    "is_key_callable",
    "is_refusal_code",
    "parse_envelope",
    "read_envelope",
]
