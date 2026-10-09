# Copyright (c) 2026 NightWorksIO
"""Each DNS provider talking to a remote API, against a stand-in of that API: what it writes, what it removes, and how it refuses."""

import base64
import datetime
import json
import time
from http import HTTPMethod
from typing import TYPE_CHECKING, Final, cast

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from lemonfiber_mcp.certificates.dns import api as api_module
from lemonfiber_mcp.certificates.dns import (
    azuredns,
    cloudflare,
    desec,
    digitalocean,
    duckdns,
    gcloud,
    hetzner,
    route53,
)
from lemonfiber_mcp.certificates.dns.api import Api
from lemonfiber_mcp.certificates.dns.provider import ProviderError
from lemonfiber_mcp.certificates.settings import TlsSettingsError
from tests.standins import JSON, Answer, Asked, HttpStandIn, answered, routed

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Callable

    from lemonfiber_mcp.certificates.dns.provider import Provider

NAME: Final = "_acme-challenge.mcp.home.example."
VALUE: Final = "digest-of-the-key-authorization"
CREDENTIAL: Final = "credential-" + "7" * 24


def credential_file(tmp_path: pathlib.Path) -> str:
    """Write the credential to a file only this user reads, and return its path."""
    path = tmp_path / "credential"
    path.write_text(f"{CREDENTIAL}\n", encoding="utf-8")
    path.chmod(0o600)
    return str(path)


type Exchange = tuple[str, str, dict[str, list[str]], object]
"""One request as the stand-in saw it: its method, path, query, and body."""

ZONES: Final = ["_acme-challenge.mcp.home.example", "mcp.home.example", "home.example"]
"""The zones a name is looked for in, longest first."""
BARE: Final = NAME.rstrip(".")


def body_of(one: Asked) -> object:
    """Return a request's body read as JSON or as a form, its bytes where neither, or None where it has none."""
    kind = one.headers.get("content-type", "")
    if not one.body:
        return None
    if kind.startswith("application/json"):
        return one.json()
    if kind.startswith("application/x-www-form-urlencoded"):
        return one.form()
    return one.body


def exchanges(asked: list[Asked]) -> list[Exchange]:
    """Return every request the stand-in saw, in order."""
    return [(one.method, one.path, one.query, body_of(one)) for one in asked]


def test_cloudflare_writes_into_the_zone_it_finds_and_removes_what_it_wrote(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if asked.path == "/zones":
            return answered(
                200,
                {"result": [{"id": "z1"}] if asked.query["name"] == ["home.example"] else []},
            )
        if asked.method == "GET":
            return answered(200, {"result": [{"id": "r1"}]})
        return answered(200, {"result": {}})

    with HttpStandIn(answer) as api:
        monkeypatch.setattr(cloudflare, "ENDPOINT", api.url)
        provider = cloudflare.Cloudflare.from_environment(
            {cloudflare.CREDENTIAL_FILE: credential_file(tmp_path)},
        )
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
    zones: list[Exchange] = [("GET", "/zones", {"name": [zone]}, None) for zone in ZONES]
    assert exchanges(api.asked) == [
        *zones,
        (
            "POST",
            "/zones/z1/dns_records",
            {},
            {"type": "TXT", "name": BARE, "content": VALUE, "ttl": cloudflare.TTL},
        ),
        *zones,
        ("GET", "/zones/z1/dns_records", {"type": ["TXT"], "name": [BARE], "content": [VALUE]}, None),
        ("DELETE", "/zones/z1/dns_records/r1", {}, None),
    ]
    assert {one.headers["authorization"] for one in api.asked} == {f"Bearer {CREDENTIAL}"}


def test_digitalocean_writes_relative_to_its_domain_and_removes_the_record_holding_the_value(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    held = {"domain_records": [{"id": 7, "data": VALUE}, {"id": 8, "data": "another"}]}
    routes: dict[tuple[str, str], Answer] = {
        ("GET", "/domains/home.example"): answered(200, {"domain": {}}),
        ("POST", "/domains/home.example/records"): answered(201, {}),
        ("GET", "/domains/home.example/records"): answered(200, held),
        ("DELETE", "/domains/home.example/records/7"): (204, {}, b""),
    }
    with HttpStandIn(routed(routes)) as api:
        monkeypatch.setattr(digitalocean, "ENDPOINT", api.url)
        provider = digitalocean.DigitalOcean.from_environment(
            {digitalocean.CREDENTIAL_FILE: credential_file(tmp_path)},
        )
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
    domains: list[Exchange] = [("GET", f"/domains/{zone}", {}, None) for zone in ZONES]
    record = {"type": "TXT", "name": "_acme-challenge.mcp", "data": VALUE, "ttl": digitalocean.TTL}
    assert exchanges(api.asked) == [
        *domains,
        ("POST", "/domains/home.example/records", {}, record),
        *domains,
        ("GET", "/domains/home.example/records", {"type": ["TXT"], "name": [BARE]}, None),
        ("DELETE", "/domains/home.example/records/7", {}, None),
    ]
    assert {one.headers["authorization"] for one in api.asked} == {f"Bearer {CREDENTIAL}"}


def test_hetzner_adds_the_value_to_the_record_set_and_removes_it_again(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if asked.path == "/zones":
            found = [{"id": 7, "name": "home.example"}] if asked.query["name"] == ["home.example"] else []
            return answered(200, {"zones": found})
        if asked.method == "GET":
            return answered(200, {"action": {"id": 9, "status": "success"}})
        return answered(201, {"action": {"id": 9, "status": "running"}})

    monkeypatch.setattr(hetzner, "ACTION_INTERVAL", 0.0)
    with HttpStandIn(answer) as api:
        monkeypatch.setattr(hetzner, "ENDPOINT", api.url)
        provider = hetzner.Hetzner.from_environment({hetzner.CREDENTIAL_FILE: credential_file(tmp_path)})
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
    zones: list[Exchange] = [("GET", "/zones", {"name": [zone]}, None) for zone in ZONES]
    rrset = "/zones/home.example/rrsets/_acme-challenge.mcp/TXT/actions"
    records = [{"value": f'"{VALUE}"'}]
    assert exchanges(api.asked) == [
        *zones,
        ("POST", f"{rrset}/add_records", {}, {"records": records, "ttl": hetzner.TTL}),
        ("GET", "/actions/9", {}, None),
        *zones,
        ("POST", f"{rrset}/remove_records", {}, {"records": records}),
        ("GET", "/actions/9", {}, None),
    ]
    assert {one.headers["authorization"] for one in api.asked} == {f"Bearer {CREDENTIAL}"}


@pytest.mark.parametrize(("status", "checks"), [("error", 30), ("running", 3)])
def test_a_hetzner_action_that_fails_or_does_not_end_is_refused(
    monkeypatch: pytest.MonkeyPatch,
    status: str,
    checks: int,
) -> None:
    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if asked.path == "/zones":
            return answered(200, {"zones": [{"id": 7, "name": "home.example"}]})
        return answered(200, {"action": {"id": 9, "status": status if asked.method == "GET" else "running"}})

    monkeypatch.setattr(hetzner, "ACTION_INTERVAL", 0.0)
    monkeypatch.setattr(hetzner, "ACTION_CHECKS", checks)
    with HttpStandIn(answer) as api:
        monkeypatch.setattr(hetzner, "ENDPOINT", api.url)
        provider = hetzner.Hetzner(CREDENTIAL)
        with pytest.raises(ProviderError, match=f"The Hetzner action 9 ended as {status}"):
            provider.present(NAME, VALUE)
    assert sum(one.method == "GET" and one.path == "/actions/9" for one in api.asked) == (
        1 if status == "error" else checks
    )


def test_desec_adds_the_value_to_the_record_set_and_takes_it_out_again(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    held: list[str] = ['"another"']

    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if asked.path == "/domains/":
            return answered(200, [{"name": "home.example"}])
        if asked.method == "GET":
            return answered(200, {"records": held})
        held[:] = cast("list[dict[str, list[str]]]", asked.json())[0]["records"]
        return answered(200, [])

    with HttpStandIn(answer) as api:
        monkeypatch.setattr(desec, "ENDPOINT", api.url)
        provider = desec.Desec.from_environment({desec.CREDENTIAL_FILE: credential_file(tmp_path)})
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
        provider.present("home.example.", VALUE)

    def rrset(subname: str, *records: str) -> list[dict[str, object]]:
        return [{"subname": subname, "type": "TXT", "ttl": desec.TTL, "records": list(records)}]

    owner: Exchange = ("GET", "/domains/", {"owns_qname": [BARE]}, None)
    held_at: Exchange = ("GET", "/domains/home.example/rrsets/_acme-challenge.mcp/TXT/", {}, None)
    assert exchanges(api.asked) == [
        owner,
        held_at,
        (
            "PATCH",
            "/domains/home.example/rrsets/",
            {},
            rrset("_acme-challenge.mcp", '"another"', f'"{VALUE}"'),
        ),
        owner,
        held_at,
        ("PATCH", "/domains/home.example/rrsets/", {}, rrset("_acme-challenge.mcp", '"another"')),
        ("GET", "/domains/", {"owns_qname": ["home.example"]}, None),
        ("GET", "/domains/home.example/rrsets/@/TXT/", {}, None),
        ("PATCH", "/domains/home.example/rrsets/", {}, rrset("", '"another"', f'"{VALUE}"')),
    ]
    assert {one.headers["authorization"] for one in api.asked} == {f"Token {CREDENTIAL}"}


def test_duckdns_sets_and_clears_its_domains_one_record(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with HttpStandIn(lambda _: (200, {"Content-Type": "text/plain"}, b"OK")) as api:
        monkeypatch.setattr(duckdns, "ENDPOINT", api.url)
        provider = duckdns.DuckDns.from_environment({duckdns.CREDENTIAL_FILE: credential_file(tmp_path)})
        provider.present("_acme-challenge.myhome.duckdns.org.", VALUE)
        provider.cleanup("_acme-challenge.myhome.duckdns.org.", VALUE)
    assert exchanges(api.asked) == [
        ("GET", "/update", {"domains": ["myhome"], "token": [CREDENTIAL], "txt": [VALUE]}, None),
        (
            "GET",
            "/update",
            {"domains": ["myhome"], "token": [CREDENTIAL], "txt": [VALUE], "clear": ["true"]},
            None,
        ),
    ]


def test_duckdns_refuses_a_name_that_is_not_its_own_and_an_update_it_did_not_take(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with HttpStandIn(lambda _: (200, {"Content-Type": "text/plain"}, b"KO")) as api:
        monkeypatch.setattr(duckdns, "ENDPOINT", api.url)
        provider = duckdns.DuckDns(CREDENTIAL)
        with pytest.raises(ProviderError, match="not a Duck DNS name"):
            provider.present(NAME, VALUE)
        with pytest.raises(ProviderError, match="refused the update") as refused:
            provider.present("_acme-challenge.myhome.duckdns.org.", VALUE)
    assert CREDENTIAL not in str(refused.value)


MOMENT: Final = datetime.datetime(2026, 10, 9, 12, tzinfo=datetime.UTC)
KEY: Final = route53.AccessKey("AKIDEXAMPLE", CREDENTIAL)


def test_route53_upserts_and_deletes_each_change_signed_with_version_4(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with HttpStandIn(lambda _: (200, {"Content-Type": "text/xml"}, b"<ChangeInfo/>")) as api:
        monkeypatch.setattr(route53, "ENDPOINT", api.url)
        provider = route53.Route53(KEY, "Z123", "eu-west-1", clock=lambda: MOMENT)
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
    upsert = api.asked[0]

    def change(action: str) -> bytes:
        return (
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<ChangeResourceRecordSetsRequest xmlns="https://route53.amazonaws.com/doc/2013-04-01/">'
            f"<ChangeBatch><Changes><Change><Action>{action}</Action><ResourceRecordSet>"
            f"<Name>{NAME}</Name><Type>TXT</Type><TTL>10</TTL><ResourceRecords><ResourceRecord>"
            f'<Value>"{VALUE}"</Value></ResourceRecord></ResourceRecords></ResourceRecordSet>'
            "</Change></Changes></ChangeBatch></ChangeResourceRecordSetsRequest>"
        ).encode()

    rrset = "/2013-04-01/hostedzone/Z123/rrset/"
    assert exchanges(api.asked) == [
        ("POST", rrset, {}, change("UPSERT")),
        ("POST", rrset, {}, change("DELETE")),
    ]
    assert upsert.headers["content-type"] == "text/xml"
    expected = route53.signed_headers(KEY, api.url + upsert.path, upsert.body, MOMENT)
    assert upsert.headers["authorization"] == expected["Authorization"]
    assert upsert.headers["authorization"].startswith(
        "AWS4-HMAC-SHA256 Credential=AKIDEXAMPLE/20261009/us-east-1/route53/aws4_request, "
        "SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=",
    )
    assert CREDENTIAL not in upsert.headers["authorization"]
    assert CREDENTIAL not in repr(KEY)


def test_route53_signs_as_amazon_documents_it() -> None:
    signed = route53.signed_headers(
        route53.AccessKey("AKIDEXAMPLE", "wJalrXUtnFEMI/K7MDENG+bPxRfiCYEXAMPLEKEY"),
        "https://route53.amazonaws.com/2013-04-01/hostedzone/Z123/rrset/",
        b"",
        datetime.datetime(2015, 8, 30, 12, 36, tzinfo=datetime.UTC),
    )
    assert signed["X-Amz-Date"] == "20150830T123600Z"
    assert (
        signed["X-Amz-Content-Sha256"] == "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )


def test_route53_is_made_from_its_settings(tmp_path: pathlib.Path) -> None:
    environment = {
        route53.ACCESS_KEY_ID: "AKIDEXAMPLE",
        route53.ACCESS_KEY_FILE: credential_file(tmp_path),
        route53.HOSTED_ZONE_ID: "Z123",
    }
    assert isinstance(route53.Route53.from_environment(environment), route53.Route53)
    assert route53.utc_now().tzinfo is datetime.UTC


@pytest.mark.parametrize(
    ("region", "endpoint", "signed_for"),
    [
        ("", "https://route53.amazonaws.com", "us-east-1"),
        ("eu-central-1", "https://route53.amazonaws.com", "us-east-1"),
        ("cn-north-1", "https://route53.amazonaws.com.cn", "cn-northwest-1"),
        ("us-gov-east-1", "https://route53.us-gov.amazonaws.com", "us-gov-west-1"),
    ],
)
def test_route53_is_reached_and_signed_for_in_the_partition_its_region_sits_in(
    region: str,
    endpoint: str,
    signed_for: str,
) -> None:
    assert route53.partition_of(region) == route53.Partition(endpoint, signed_for)
    signed = route53.signed_headers(KEY, f"{endpoint}/", b"", MOMENT, signed_for)
    assert f"/{signed_for}/route53/aws4_request" in signed["Authorization"]


PEM: Final = (
    rsa.generate_private_key(public_exponent=65537, key_size=2048)
    .private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    .decode()
)
"""A service account's private key."""


def service_account(tmp_path: pathlib.Path, token_uri: str) -> str:
    """Write a service account's key file, and return its path."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem = key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )
    path = tmp_path / "account.json"
    account = {"client_email": "dns@project.iam.example", "private_key": pem.decode(), "token_uri": token_uri}
    path.write_text(json.dumps(account), encoding="utf-8")
    return str(path)


def test_gcloud_asks_for_a_token_and_replaces_the_record_set(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    another: dict[str, object] = {"name": NAME, "type": "TXT", "ttl": 60, "rrdatas": ['"another"']}
    held: list[dict[str, object]] = [another]

    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if asked.path == "/token":
            return answered(200, {"access_token": "short-lived", "token_type": "Bearer"})
        if asked.path.endswith("/managedZones"):
            found = [{"name": "home"}] if asked.query["dnsName"] == ["home.example."] else []
            return answered(200, {"managedZones": found})
        if asked.path.endswith("/rrsets"):
            return answered(200, {"rrsets": held})
        change = cast("dict[str, list[dict[str, object]]]", asked.json())
        held[:] = change["additions"]
        return answered(200, {})

    with HttpStandIn(answer) as api:
        monkeypatch.setattr(gcloud, "ENDPOINT", api.url)
        environment = {
            gcloud.PROJECT: "project",
            gcloud.SERVICE_ACCOUNT_FILE: service_account(tmp_path, f"{api.url}/token"),
        }
        provider = gcloud.Gcloud.from_environment(environment)
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
        with pytest.raises(ProviderError, match="Cloud DNS holds no managed zone for"):
            provider.present("_acme-challenge.elsewhere.test.", VALUE)

    def with_values(*values: str) -> dict[str, object]:
        return {"name": NAME, "type": "TXT", "ttl": gcloud.TTL, "rrdatas": list(values)}

    zones: list[Exchange] = [
        ("GET", "/projects/project/managedZones", {"dnsName": [f"{zone}."]}, None) for zone in ZONES
    ]
    rrsets = ("GET", "/projects/project/managedZones/home/rrsets", {"name": [NAME], "type": ["TXT"]}, None)
    changes = "/projects/project/managedZones/home/changes"
    both = with_values('"another"', f'"{VALUE}"')
    token, *rest = exchanges(api.asked)
    assert rest[:10] == [
        *zones,
        rrsets,
        ("POST", changes, {}, {"deletions": [another], "additions": [both]}),
        *zones,
        rrsets,
        ("POST", changes, {}, {"deletions": [both], "additions": [with_values('"another"')]}),
    ]
    assert (token[0], token[1], token[2]) == ("POST", "/token", {})
    form = cast("dict[str, list[str]]", token[3])
    assert set(form) == {"grant_type", "assertion"}
    assert form["grant_type"] == [gcloud.GRANT]
    signed = form["assertion"][0]
    assert "=" not in signed
    header, payload, _ = signed.split(".")
    assert json.loads(gcloud_decoded(header)) == {"alg": "RS256", "typ": "JWT"}
    claims = json.loads(gcloud_decoded(payload))
    assert claims == {
        "iss": "dns@project.iam.example",
        "scope": gcloud.SCOPE,
        "aud": f"{api.url}/token",
        "iat": claims["iat"],
        "exp": claims["iat"] + gcloud.TOKEN_LIFETIME,
    }
    assert {one.headers.get("authorization") for one in api.asked[1:]} == {"Bearer short-lived"}


def test_a_record_set_left_with_no_value_is_deleted_whole_from_cloud_dns(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    only: dict[str, object] = {"name": NAME, "type": "TXT", "ttl": 60, "rrdatas": [f'"{VALUE}"']}

    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if asked.path == "/token":
            return answered(200, {"access_token": "short-lived"})
        if asked.path.endswith("/managedZones"):
            return answered(200, {"managedZones": [{"name": "home"}]})
        return answered(200, {"rrsets": [only]} if asked.path.endswith("/rrsets") else {})

    with HttpStandIn(answer) as api:
        monkeypatch.setattr(gcloud, "ENDPOINT", api.url)
        service_account(tmp_path, f"{api.url}/token")
        account = gcloud.account_of(tmp_path / "account.json")
        gcloud.Gcloud("project", account).cleanup(NAME, VALUE)
    assert exchanges(api.asked)[-1] == (
        "POST",
        "/projects/project/managedZones/home/changes",
        {},
        {"deletions": [only], "additions": []},
    )


def gcloud_decoded(part: str) -> bytes:
    """Return an unpadded base64url part decoded."""
    return base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))


@pytest.mark.parametrize("content", ["not json", '{"client_email": "x"}'])
def test_gcloud_refuses_a_file_that_is_not_a_service_accounts_key(
    tmp_path: pathlib.Path,
    content: str,
) -> None:
    path = tmp_path / "account.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(TlsSettingsError, match=gcloud.SERVICE_ACCOUNT_FILE):
        gcloud.account_of(path)


def azure_environment(tmp_path: pathlib.Path) -> dict[str, str]:
    """Return the settings of an Azure DNS provider."""
    return {
        azuredns.TENANT_ID: "tenant",
        azuredns.CLIENT_ID: "client",
        azuredns.CLIENT_CREDENTIAL_FILE: credential_file(tmp_path),
        azuredns.SUBSCRIPTION_ID: "sub",
        azuredns.RESOURCE_GROUP: "group",
    }


def test_azuredns_asks_for_a_token_and_sets_the_record_set(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    zones = "/subscriptions/sub/resourceGroups/group/providers/Microsoft.Network/dnsZones"
    record = f"{zones}/home.example/TXT/_acme-challenge.mcp"
    held: list[list[str]] = [["another"]]

    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if asked.path.endswith("/token"):
            return answered(200, {"access_token": "short-lived"})
        if asked.path.endswith("/dnsZones"):
            return answered(200, {"value": [{"name": "home.example"}, {"name": "other.example"}]})
        if asked.method == "GET":
            entries = [{"value": value} for value in held]
            return answered(200, {"properties": {"TXTRecords": entries}}) if held else answered(404, {})
        if asked.method == "PUT":
            body = cast("dict[str, dict[str, list[dict[str, list[str]]]]]", asked.json())
            held[:] = [entry["value"] for entry in body["properties"]["TXTRecords"]]
            return answered(200, {})
        held.clear()
        return 200, JSON, b""

    with HttpStandIn(answer) as api:
        monkeypatch.setattr(azuredns, "LOGIN", api.url)
        monkeypatch.setattr(azuredns, "MANAGEMENT", api.url)
        provider = azuredns.AzureDns.from_environment(azure_environment(tmp_path))
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
        held.clear()
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
        with pytest.raises(ProviderError, match="Azure DNS holds no zone for"):
            provider.present("_acme-challenge.elsewhere.test.", VALUE)

    def records(*values: str) -> dict[str, object]:
        return {"properties": {"TTL": azuredns.TTL, "TXTRecords": [{"value": [value]} for value in values]}}

    version = {"api-version": ["2018-05-01"]}
    listed = ("GET", zones, version, None)
    looked = ("GET", record, version, None)
    token = {
        "grant_type": ["client_credentials"],
        "client_id": ["client"],
        "client_secret": [CREDENTIAL],
        "scope": [azuredns.SCOPE],
    }
    assert exchanges(api.asked)[:13] == [
        ("POST", "/tenant/oauth2/v2.0/token", {}, token),
        listed,
        looked,
        ("PUT", record, version, records("another", VALUE)),
        listed,
        looked,
        ("PUT", record, version, records("another")),
        listed,
        looked,
        ("PUT", record, version, records(VALUE)),
        listed,
        looked,
        ("DELETE", record, version, None),
    ]


@pytest.mark.parametrize(
    ("made", "routes"),
    [
        (lambda: cloudflare.Cloudflare(CREDENTIAL), {}),
        (lambda: digitalocean.DigitalOcean(CREDENTIAL), {}),
        (lambda: hetzner.Hetzner(CREDENTIAL), {}),
        (lambda: desec.Desec(CREDENTIAL), {("GET", "/domains/"): answered(200, [])}),
    ],
)
def test_a_name_in_no_zone_the_provider_holds_is_refused(
    monkeypatch: pytest.MonkeyPatch,
    made: Callable[[], Provider],
    routes: dict[tuple[str, str], tuple[int, dict[str, str], bytes]],
) -> None:
    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if (asked.method, asked.path) in routes:
            return routes[(asked.method, asked.path)]
        return answered(200, {"result": [], "zones": []}) if asked.path == "/zones" else answered(404, {})

    with HttpStandIn(answer) as api:
        for module in (cloudflare, digitalocean, hetzner, desec):
            monkeypatch.setattr(module, "ENDPOINT", api.url)
        with pytest.raises(ProviderError, match="holds no"):
            made().present(NAME, VALUE)


SIGN_IN: Final = "sign-in"
"""Where the refusal comes: at the sign-in, or at the API once signed in."""
API: Final = "api"


def refusing(at: str) -> Callable[[Asked], Answer]:
    """Return an API that refuses, quoting the credential, at the sign-in or at the API once signed in."""

    def answer(asked: Asked) -> Answer:
        if at == API and asked.path.endswith("/token"):
            return answered(200, {"access_token": "short-lived"})
        return answered(403, {"errors": [CREDENTIAL]})

    return answer


def google(url: str) -> Provider:
    """Return Cloud DNS signing in at the stand-in."""
    return gcloud.Gcloud("project", {"client_email": "x", "private_key": PEM, "token_uri": f"{url}/token"})


def azure(_: str) -> Provider:
    """Return Azure DNS, its sign-in and its API set to the stand-in."""
    return azuredns.AzureDns("tenant", "client", CREDENTIAL, "sub", "group")


REFUSALS: Final[list[tuple[Callable[[str], Provider], str, str, str]]] = [
    (
        lambda _: cloudflare.Cloudflare(CREDENTIAL),
        NAME,
        API,
        "The Cloudflare API answered 403 to GET /zones.",
    ),
    (
        lambda _: digitalocean.DigitalOcean(CREDENTIAL),
        NAME,
        API,
        f"The DigitalOcean API answered 403 to GET /domains/{BARE}.",
    ),
    (lambda _: hetzner.Hetzner(CREDENTIAL), NAME, API, "The Hetzner API answered 403 to GET /zones."),
    (lambda _: desec.Desec(CREDENTIAL), NAME, API, "The deSEC API answered 403 to GET /domains/."),
    (
        lambda _: duckdns.DuckDns(CREDENTIAL),
        "_acme-challenge.myhome.duckdns.org.",
        API,
        "The Duck DNS API answered 403 to GET /update.",
    ),
    (
        lambda _: route53.Route53(KEY, "Z123"),
        NAME,
        API,
        "The Route 53 API answered 403 to POST /2013-04-01/hostedzone/Z123/rrset/.",
    ),
    (google, NAME, SIGN_IN, "The Google API answered 403 to POST /token."),
    (google, NAME, API, "The Cloud DNS API answered 403 to GET /projects/project/managedZones."),
    (azure, NAME, SIGN_IN, "The Microsoft Entra API answered 403 to POST /tenant/oauth2/v2.0/token."),
    (
        azure,
        NAME,
        API,
        (
            "The Azure DNS API answered 403 to GET "
            "/subscriptions/sub/resourceGroups/group/providers/Microsoft.Network/dnsZones."
        ),
    ),
]
"""Each provider, the name it is asked to write, where the stand-in refuses, and what the refusal says."""


@pytest.mark.parametrize(("made", "name", "at", "said"), REFUSALS)
def test_a_refusal_names_the_api_the_status_and_the_path_and_never_the_credential(
    monkeypatch: pytest.MonkeyPatch,
    made: Callable[[str], Provider],
    name: str,
    at: str,
    said: str,
) -> None:
    with HttpStandIn(refusing(at)) as api:
        for module in (cloudflare, digitalocean, hetzner, desec, duckdns, route53, gcloud):
            monkeypatch.setattr(module, "ENDPOINT", api.url)
        monkeypatch.setattr(azuredns, "LOGIN", api.url)
        monkeypatch.setattr(azuredns, "MANAGEMENT", api.url)
        with pytest.raises(ProviderError) as refused:
            made(api.url).present(name, VALUE)
    assert str(refused.value) == said


def test_an_api_that_cannot_be_reached_says_so(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(cloudflare, "ENDPOINT", "http://127.0.0.1:9")
    with pytest.raises(ProviderError, match="could not be reached: ConnectionError"):
        cloudflare.Cloudflare(CREDENTIAL).present(NAME, VALUE)


def test_an_access_token_is_asked_for_again_five_minutes_before_it_ends(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    now = [1000.0]
    answers = iter([{"access_token": "first", "expires_in": "600"}, {"access_token": "second"}])
    monkeypatch.setattr(api_module, "monotonic", lambda: now[0])
    leased = api_module.Leased("Stand-in", "http://127.0.0.1:9", lambda: next(answers))
    first = leased.api()
    now[0] += 600 - api_module.EARLY - 1
    assert leased.api() is first
    now[0] += 1
    second = leased.api()
    assert second is not first
    now[0] += api_module.LIFETIME - api_module.EARLY - 1
    assert leased.api() is second
    now[0] += 1
    with pytest.raises(StopIteration):
        leased.api()


def test_a_404_where_a_document_a_listing_or_text_is_needed_is_refused_naming_what_was_asked() -> None:
    with HttpStandIn(lambda _: answered(404, {})) as api:
        reached = Api("Stand-in", f"{api.url}/")
        for asking in (reached.document, reached.listing, reached.text):
            with pytest.raises(ProviderError) as refused:
                asking(HTTPMethod.GET, "/anything")
            assert str(refused.value) == "The Stand-in API answered 404 to GET /anything."
        assert reached.found(HTTPMethod.GET, "/anything") is None
    assert {one.path for one in api.asked} == {"/anything"}
    with HttpStandIn(lambda _: (204, {}, b"")) as api:
        assert Api("Stand-in", api.url).found(HTTPMethod.DELETE, "/anything") == {}


@pytest.mark.parametrize("status", [400, 500])
def test_a_status_of_400_or_more_is_refused(status: int) -> None:
    with HttpStandIn(lambda _: (status, JSON, b"{}")) as api:
        reached = Api("Stand-in", api.url)
        with pytest.raises(ProviderError, match=f"answered {status} to GET /anything"):
            reached.send(HTTPMethod.GET, "/anything")


@pytest.mark.parametrize("status", [399, 404])
def test_a_status_below_400_and_a_404_are_answered(status: int) -> None:
    with HttpStandIn(lambda _: (status, JSON, b"{}")) as api:
        assert Api("Stand-in", api.url).send(HTTPMethod.GET, "/anything").status_code == status


def test_an_api_that_does_not_answer_in_time_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    def slow(_: Asked) -> Answer:
        time.sleep(1)
        return answered(200, {})

    monkeypatch.setattr(api_module, "TIMEOUT_SECONDS", 0.1)
    with HttpStandIn(slow) as api, pytest.raises(ProviderError, match="could not be reached: ReadTimeout"):
        Api("Stand-in", api.url).send(HTTPMethod.GET, "/anything")


@pytest.mark.parametrize(
    "made",
    [
        cloudflare.Cloudflare.from_environment,
        digitalocean.DigitalOcean.from_environment,
        hetzner.Hetzner.from_environment,
        desec.Desec.from_environment,
        duckdns.DuckDns.from_environment,
    ],
)
def test_a_provider_without_its_credential_file_is_refused_by_name(
    made: Callable[[dict[str, str]], Provider],
) -> None:
    with pytest.raises(TlsSettingsError, match="_FILE is not set"):
        made({})


def test_a_credential_file_that_holds_nothing_is_refused(tmp_path: pathlib.Path) -> None:
    empty = tmp_path / "empty"
    empty.write_text("\n", encoding="utf-8")
    with pytest.raises(TlsSettingsError, match="could not be read, or holds nothing"):
        cloudflare.Cloudflare.from_environment({cloudflare.CREDENTIAL_FILE: str(empty)})
    with pytest.raises(TlsSettingsError, match="could not be read"):
        cloudflare.Cloudflare.from_environment({cloudflare.CREDENTIAL_FILE: str(tmp_path / "missing")})
