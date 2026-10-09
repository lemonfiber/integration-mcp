# Copyright (c) 2026 NightWorksIO
"""Where the certificate comes from, in the mode the settings chose."""

from typing import TYPE_CHECKING, Final

from lemonfiber_mcp.certificates.acme import AcmeSource
from lemonfiber_mcp.certificates.acme_settings import Challenge, acme_from
from lemonfiber_mcp.certificates.modes import CertificateError, Files, Pinned, PrivateCa
from lemonfiber_mcp.certificates.settings import Mode

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from lemonfiber_mcp.certificates.alpn import Challenges
    from lemonfiber_mcp.certificates.modes import Source
    from lemonfiber_mcp.certificates.settings import Tls

NOT_YET: Final = (
    "LEMONFIBER_ACME_CHALLENGE is dns-01, which this version of the server does not answer yet. Choose "
    "tls-alpn-01 or http-01."
)
OWN: Final[Mapping[Mode, Callable[[Tls], Source]]] = {
    Mode.FILES: Files,
    Mode.PRIVATE_CA: PrivateCa,
    Mode.PINNED: Pinned,
}
"""Where the certificate comes from in each mode that needs no authority."""


def source_of(tls: Tls, environment: Mapping[str, str], pending: Challenges) -> Source:
    """Return where the certificate comes from, refusing a challenge this version does not answer."""
    if tls.mode is not Mode.ACME:
        return OWN[tls.mode](tls)
    settings = acme_from(environment)
    if settings.challenge is Challenge.DNS_01:
        raise CertificateError(NOT_YET)
    return AcmeSource(tls, settings, pending)
