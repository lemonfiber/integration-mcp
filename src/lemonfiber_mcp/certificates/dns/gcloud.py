# Copyright (c) 2026 NightWorksIO
"""Google Cloud DNS, by a service account allowed to change the managed zone."""

import base64
import json
import pathlib
import time
from typing import TYPE_CHECKING, Final, cast

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from lemonfiber_mcp.certificates.dns.api import Api, Asking, Document, Leased
from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, candidates, needed
from lemonfiber_mcp.certificates.settings import TlsSettingsError

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

ENDPOINT: Final = "https://dns.googleapis.com/dns/v1"
PROJECT: Final = "GCE_PROJECT"
SERVICE_ACCOUNT_FILE: Final = "GCE_SERVICE_ACCOUNT_FILE"
SCOPE: Final = "https://www.googleapis.com/auth/ndev.clouddns.readwrite"
GRANT: Final = "urn:ietf:params:oauth:grant-type:jwt-bearer"
TOKEN_LIFETIME: Final = 3600
TTL: Final = 60

type Changing = Callable[[list[str]], list[str]]
"""What a change does to a record set's values."""


def encoded(data: bytes) -> str:
    """Return bytes in unpadded URL-safe base64."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def assertion(account: Mapping[str, str], now: int) -> str:
    """Return the signed JWT a service account asks for an access token with."""
    header = encoded(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = {"iss": account["client_email"], "scope": SCOPE, "aud": account["token_uri"], "iat": now}
    payload = encoded(json.dumps({**claims, "exp": now + TOKEN_LIFETIME}).encode())
    key = cast(
        "rsa.RSAPrivateKey",
        serialization.load_pem_private_key(account["private_key"].encode(), password=None),
    )
    signature = key.sign(f"{header}.{payload}".encode(), padding.PKCS1v15(), hashes.SHA256())
    return f"{header}.{payload}.{encoded(signature)}"


def account_of(path: pathlib.Path) -> dict[str, str]:
    """Return a service account's key file, refusing one that is not one."""
    try:
        account = cast("dict[str, str]", json.loads(path.read_bytes()))
        _ = (account["client_email"], account["private_key"], account["token_uri"])
    except OSError, ValueError, KeyError, TypeError:
        msg = f"{SERVICE_ACCOUNT_FILE} names a file that is not a service account's key."
        raise TlsSettingsError(msg) from None
    return account


class Gcloud:
    """TXT records written through Cloud DNS, the record set holding every value at once."""

    timing = Timing(propagation=180.0, interval=5.0)

    def __init__(self, project: str, account: Mapping[str, str]) -> None:
        """Hold the project and the service account."""
        self._project = project
        self._account = dict(account)
        self._leased = Leased("Cloud DNS", ENDPOINT, self._token)

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> Gcloud:
        """Return the provider its settings describe."""
        return cls(
            needed(environment, PROJECT),
            account_of(pathlib.Path(needed(environment, SERVICE_ACCOUNT_FILE))),
        )

    def _token(self) -> Document:
        form = {"grant_type": GRANT, "assertion": assertion(self._account, int(time.time()))}
        return Api("Google", self._account["token_uri"]).document("POST", "", Asking(form=form))

    def _asked(self) -> Api:
        return self._leased.api()

    def _zone(self, name: str) -> str:
        for candidate in candidates(name):
            asked = Asking(params={"dnsName": f"{candidate}."})
            found = self._asked().document("GET", f"/projects/{self._project}/managedZones", asked)[
                "managedZones"
            ]
            if found:
                return str(cast("list[Document]", found)[0]["name"])
        msg = f"Cloud DNS holds no managed zone for {name}."
        raise ProviderError(msg)

    def _replace(self, name: str, change: Changing) -> None:
        base = f"/projects/{self._project}/managedZones/{self._zone(name)}"
        asked = Asking(params={"name": name, "type": "TXT"})
        held = cast("list[Document]", self._asked().document("GET", f"{base}/rrsets", asked)["rrsets"])
        after = change([value for record in held for value in cast("list[str]", record["rrdatas"])])
        additions = [{"name": name, "type": "TXT", "ttl": TTL, "rrdatas": after}] if after else []
        self._asked().document(
            "POST",
            f"{base}/changes",
            Asking(body={"deletions": held, "additions": additions}),
        )

    def present(self, name: str, value: str) -> None:
        """Add the value to the name's TXT record set."""
        self._replace(name, lambda values: [*values, f'"{value}"'])

    def cleanup(self, name: str, value: str) -> None:
        """Take the value out of the name's TXT record set."""
        self._replace(name, lambda values: [held for held in values if held != f'"{value}"'])
