# Copyright (c) 2026 NightWorksIO
"""Every DNS provider, by the name `LEMONFIBER_ACME_DNS_PROVIDER` gives it, as lego names it."""

from typing import TYPE_CHECKING, Final

from lemonfiber_mcp.certificates.acme_settings import DNS_PROVIDER
from lemonfiber_mcp.certificates.dns.azuredns import AzureDns
from lemonfiber_mcp.certificates.dns.cloudflare import Cloudflare
from lemonfiber_mcp.certificates.dns.desec import Desec
from lemonfiber_mcp.certificates.dns.digitalocean import DigitalOcean
from lemonfiber_mcp.certificates.dns.duckdns import DuckDns
from lemonfiber_mcp.certificates.dns.exec import Exec
from lemonfiber_mcp.certificates.dns.gcloud import Gcloud
from lemonfiber_mcp.certificates.dns.hetzner import Hetzner
from lemonfiber_mcp.certificates.dns.rfc2136 import Rfc2136
from lemonfiber_mcp.certificates.dns.route53 import Route53
from lemonfiber_mcp.certificates.settings import TlsSettingsError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

    from lemonfiber_mcp.certificates.dns.provider import Provider

PROVIDERS: Final[Mapping[str, Callable[[Mapping[str, str]], Provider]]] = {
    "rfc2136": Rfc2136.from_environment,
    "cloudflare": Cloudflare.from_environment,
    "route53": Route53.from_environment,
    "gcloud": Gcloud.from_environment,
    "azuredns": AzureDns.from_environment,
    "digitalocean": DigitalOcean.from_environment,
    "hetzner": Hetzner.from_environment,
    "desec": Desec.from_environment,
    "duckdns": DuckDns.from_environment,
    "exec": Exec.from_environment,
}
"""Each provider's name, to how it is made from its settings."""


def provider_of(name: str | None, environment: Mapping[str, str]) -> Provider:
    """Return the provider a name chooses, made from its settings, refusing a name that is none of them."""
    if name not in PROVIDERS:
        msg = f"{DNS_PROVIDER} is {name!r}; for dns-01 it is one of {', '.join(PROVIDERS)}."
        raise TlsSettingsError(msg)
    return PROVIDERS[name](environment)
