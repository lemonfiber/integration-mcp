# Copyright (c) 2026 NightWorksIO
"""The `certificate` envelope, and the shapes only `certificate` carries.

Generated from the contract vendored in `contract/`. Do not edit: `just generate` rewrites it,
and CI fails on any difference.
"""

import typing


class CertificateEnvelope(typing.TypedDict):
    """The envelope carrying `certificate`."""

    api_version: int
    data: CertificateReport
    host: typing.NotRequired[str | None]
    job: typing.NotRequired[str | None]
    kind: typing.Literal["certificate"]


class CertificateReport(typing.TypedDict):
    """What asking for the certificate to be replaced came to."""

    consequence: str
    """What replacing it means for every phone already paired."""
    fingerprint: typing.NotRequired[str | None]
    """What a phone would pin now: the new certificate where it was replaced, the one
    kept where it was not, and nothing where none has been made.
    """
    rehearsed: bool
    """Whether this was a rehearsal: what would have happened, with none of it done.

    Said in a field of its own so that a rehearsal is never told from the real run by
    its wording alone.
    """
    replaced: bool
    """Whether it was replaced. Unconfirmed, it is not, and what replacing it costs is
    what is said.
    """


__all__ = [
    "CertificateEnvelope",
    "CertificateReport",
]
