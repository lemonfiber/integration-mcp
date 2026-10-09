# Copyright (c) 2026 NightWorksIO
"""Amazon Route 53, by an access key allowed to change the hosted zone, each request signed with Signature Version 4."""

import datetime
import hashlib
import hmac
import urllib.parse
from dataclasses import dataclass, field
from http import HTTPMethod
from typing import TYPE_CHECKING, Final
from xml.sax.saxutils import escape

from lemonfiber_mcp.certificates.dns.api import Api, Asking
from lemonfiber_mcp.certificates.dns.provider import Timing, needed, secret

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping

ENDPOINT: Final = "https://route53.amazonaws.com"
PROVIDER: Final = "Route 53"
SIGNING_REGION: Final = "us-east-1"
"""Where Route 53, a global service, is reached and the region it is signed for, in AWS's commercial regions."""
ACCESS_KEY_ID: Final = "AWS_ACCESS_KEY_ID"
ACCESS_KEY_FILE: Final = "AWS_SECRET_ACCESS_KEY_FILE"
REGION: Final = "AWS_REGION"
HOSTED_ZONE_ID: Final = "AWS_HOSTED_ZONE_ID"
SERVICE: Final = "route53"
TTL: Final = 10
NAMESPACE: Final = "https://route53.amazonaws.com/doc/2013-04-01/"


@dataclass(frozen=True, slots=True)
class Partition:
    """Where Route 53 is reached in one AWS partition, and the region its requests are signed for."""

    endpoint: str
    region: str


PARTITIONS: Final = {
    "cn-": Partition("https://route53.amazonaws.com.cn", "cn-northwest-1"),
    "us-gov-": Partition("https://route53.us-gov.amazonaws.com", "us-gov-west-1"),
}
"""The partitions apart from the commercial one, by the prefix their regions' names start with."""


def partition_of(region: str) -> Partition:
    """Return the partition a region sits in, the commercial one where it names none of the others."""
    for prefix, partition in PARTITIONS.items():
        if region.startswith(prefix):
            return partition
    return Partition(ENDPOINT, SIGNING_REGION)


@dataclass(frozen=True, slots=True)
class AccessKey:
    """An AWS access key: its identifier, and the secret requests are signed with."""

    identifier: str
    secret: str = field(repr=False)


def utc_now() -> datetime.datetime:
    """Return the time now, in UTC."""
    return datetime.datetime.now(datetime.UTC)


def digest(data: bytes) -> str:
    """Return a SHA-256 digest in lower-case hex."""
    return hashlib.sha256(data).hexdigest()


def keyed(key: bytes, message: str) -> bytes:
    """Return an HMAC-SHA256 of a message."""
    return hmac.new(key, message.encode(), hashlib.sha256).digest()


def signed_headers(
    key: AccessKey,
    url: str,
    body: bytes,
    now: datetime.datetime,
    region: str = SIGNING_REGION,
) -> dict[str, str]:
    """Return the headers a POST is signed with, as Signature Version 4 sets out."""
    parts = urllib.parse.urlsplit(url)
    stamp, day = now.strftime("%Y%m%dT%H%M%SZ"), now.strftime("%Y%m%d")
    headers = {"host": parts.netloc, "x-amz-date": stamp, "x-amz-content-sha256": digest(body)}
    names = ";".join(sorted(headers))
    canonical = "\n".join(
        [
            "POST",
            parts.path or "/",
            parts.query,
            "".join(f"{name}:{headers[name]}\n" for name in sorted(headers)),
            names,
            headers["x-amz-content-sha256"],
        ],
    )
    scope = f"{day}/{region}/{SERVICE}/aws4_request"
    to_sign = "\n".join(["AWS4-HMAC-SHA256", stamp, scope, digest(canonical.encode())])
    signing = keyed(
        keyed(keyed(keyed(f"AWS4{key.secret}".encode(), day), region), SERVICE),
        "aws4_request",
    )
    signature = hmac.new(signing, to_sign.encode(), hashlib.sha256).hexdigest()
    authorization = (
        f"AWS4-HMAC-SHA256 Credential={key.identifier}/{scope}, SignedHeaders={names}, Signature={signature}"
    )
    return {
        "X-Amz-Date": stamp,
        "X-Amz-Content-Sha256": headers["x-amz-content-sha256"],
        "Authorization": authorization,
    }


def change(action: str, name: str, value: str) -> bytes:
    """Return a change batch that upserts or deletes one TXT record."""
    return (
        f'<?xml version="1.0" encoding="UTF-8"?><ChangeResourceRecordSetsRequest xmlns="{NAMESPACE}">'
        f"<ChangeBatch><Changes><Change><Action>{action}</Action><ResourceRecordSet>"
        f"<Name>{escape(name)}</Name><Type>TXT</Type><TTL>{TTL}</TTL><ResourceRecords><ResourceRecord>"
        f"<Value>{escape(f'"{value}"')}</Value></ResourceRecord></ResourceRecords></ResourceRecordSet>"
        "</Change></Changes></ChangeBatch></ChangeResourceRecordSetsRequest>"
    ).encode()


class Route53:
    """TXT records written into one hosted zone through Route 53's API."""

    timing = Timing(propagation=120.0, interval=4.0)

    def __init__(
        self,
        key: AccessKey,
        zone: str,
        region: str = "",
        clock: Callable[[], datetime.datetime] = utc_now,
    ) -> None:
        """Hold the access key, the hosted zone, the partition its region sits in, and the clock requests are dated by."""
        self._key = key
        self._zone = zone
        self._partition = partition_of(region)
        self._clock = clock
        self._api = Api(PROVIDER, self._partition.endpoint)

    @classmethod
    def from_environment(cls, environment: Mapping[str, str]) -> Route53:
        """Return the provider its settings describe."""
        return cls(
            AccessKey(needed(environment, ACCESS_KEY_ID), secret(environment, ACCESS_KEY_FILE)),
            needed(environment, HOSTED_ZONE_ID),
            environment.get(REGION, "").strip(),
        )

    def _change(self, action: str, name: str, value: str) -> None:
        path = f"/2013-04-01/hostedzone/{self._zone}/rrset/"
        body = change(action, name, value)
        headers = signed_headers(
            self._key,
            self._partition.endpoint + path,
            body,
            self._clock(),
            self._partition.region,
        )
        self._api.text(
            HTTPMethod.POST,
            path,
            Asking(raw=body, headers={**headers, "Content-Type": "text/xml"}),
        )

    def present(self, name: str, value: str) -> None:
        """Write the TXT record."""
        self._change("UPSERT", name, value)

    def cleanup(self, name: str, value: str) -> None:
        """Remove the TXT record."""
        self._change("DELETE", name, value)
