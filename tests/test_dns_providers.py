# Copyright (c) 2026 NightWorksIO
"""Each DNS provider talking to a remote API, against a stand-in of that API: what it writes, what it removes, and how it refuses."""

import base64
import datetime
import json
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


def said(asked: list[Asked]) -> list[tuple[str, str]]:
    """Return each request's method and path, in order."""
    return [(one.method, one.path) for one in asked]


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
    looked_up = [("GET", "/zones")] * 3
    assert said(api.asked) == [
        *looked_up,
        ("POST", "/zones/z1/dns_records"),
        *looked_up,
        ("GET", "/zones/z1/dns_records"),
        ("DELETE", "/zones/z1/dns_records/r1"),
    ]
    assert [query["name"] for query in (one.query for one in api.asked[:3])] == [
        ["_acme-challenge.mcp.home.example"],
        ["mcp.home.example"],
        ["home.example"],
    ]
    assert api.asked[3].json() == {
        "type": "TXT",
        "name": NAME.rstrip("."),
        "content": VALUE,
        "ttl": cloudflare.TTL,
    }
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
    posted = next(one for one in api.asked if one.method == "POST")
    assert posted.json() == {
        "type": "TXT",
        "name": "_acme-challenge.mcp",
        "data": VALUE,
        "ttl": digitalocean.TTL,
    }
    assert ("DELETE", "/domains/home.example/records/7") in said(api.asked)
    assert ("DELETE", "/domains/home.example/records/8") not in said(api.asked)


def test_hetzner_adds_the_value_to_the_record_set_and_removes_it_again(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    looked: list[str] = []

    def answer(asked: Asked) -> tuple[int, dict[str, str], bytes]:
        if asked.path == "/zones":
            found = [{"id": 7, "name": "home.example"}] if asked.query["name"] == ["home.example"] else []
            return answered(200, {"zones": found})
        if asked.method == "GET":
            looked.append(asked.path)
            return answered(200, {"action": {"id": 9, "status": "success"}})
        return answered(201, {"action": {"id": 9, "status": "running"}})

    monkeypatch.setattr(hetzner, "ACTION_INTERVAL", 0.0)
    with HttpStandIn(answer) as api:
        monkeypatch.setattr(hetzner, "ENDPOINT", api.url)
        provider = hetzner.Hetzner.from_environment({hetzner.CREDENTIAL_FILE: credential_file(tmp_path)})
        provider.present(NAME, VALUE)
        provider.cleanup(NAME, VALUE)
    posted = [one for one in api.asked if one.method == "POST"]
    rrset = "/zones/home.example/rrsets/_acme-challenge.mcp/TXT/actions"
    assert [one.path for one in posted] == [f"{rrset}/add_records", f"{rrset}/remove_records"]
    assert posted[0].json() == {"records": [{"value": f'"{VALUE}"'}], "ttl": hetzner.TTL}
    assert posted[1].json() == {"records": [{"value": f'"{VALUE}"'}]}
    assert looked == ["/actions/9", "/actions/9"]
    assert {one.headers["authorization"] for one in api.asked} == {f"Bearer {CREDENTIAL}"}


@pytest.mark.parametrize(("status", "checks"), [("error", 30), ("running", 3)])
def test_a_hetzner_action_that_fails_or_does_not_end_is_refused(
    tmp_path: pathlib.Path,
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
        assert held == ['"another"', f'"{VALUE}"']
        provider.cleanup(NAME, VALUE)
        assert held == ['"another"']
        provider.present("home.example.", VALUE)
    patched = [
        cast("list[dict[str, str]]", one.json())[0]["subname"] for one in api.asked if one.method == "PATCH"
    ]
    assert patched == ["_acme-challenge.mcp", "_acme-challenge.mcp", ""]
    assert [one.path for one in api.asked if one.method == "GET" and one.path != "/domains/"] == [
        "/domains/home.example/rrsets/_acme-challenge.mcp/TXT/",
        "/domains/home.example/rrsets/_acme-challenge.mcp/TXT/",
        "/domains/home.example/rrsets/@/TXT/",
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
    assert [one.query for one in api.asked] == [
        {"domains": ["myhome"], "token": [CREDENTIAL], "txt": [VALUE]},
        {"domains": ["myhome"], "token": [CREDENTIAL], "txt": [VALUE], "clear": ["true"]},
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
    upsert, delete = api.asked
    assert (upsert.method, upsert.path) == ("POST", "/2013-04-01/hostedzone/Z123/rrset/")
    assert b"<Action>UPSERT</Action>" in upsert.body
    assert b"<Action>DELETE</Action>" in delete.body
    assert f"<Name>{NAME}</Name><Type>TXT</Type><TTL>10</TTL>".encode() in upsert.body
    assert f'<Value>"{VALUE}"</Value>'.encode() in upsert.body
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
    held: list[dict[str, object]] = [{"name": NAME, "type": "TXT", "ttl": 60, "rrdatas": ['"another"']}]

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
        assert held[0]["rrdatas"] == ['"another"', f'"{VALUE}"']
        provider.cleanup(NAME, VALUE)
        assert held[0]["rrdatas"] == ['"another"']
        held[0]["rrdatas"] = [f'"{VALUE}"']
        provider.cleanup(NAME, VALUE)
        assert held == []
        with pytest.raises(
            ProviderError,
            match="Cloud DNS holds no managed zone for",
        ):
            provider.present("_acme-challenge.elsewhere.test.", VALUE)
    token = api.asked[0]
    assert token.form()["grant_type"] == [gcloud.GRANT]
    header, payload, _ = token.form()["assertion"][0].split(".")
    assert json.loads(gcloud_decoded(header)) == {"alg": "RS256", "typ": "JWT"}
    assert json.loads(gcloud_decoded(payload))["scope"] == gcloud.SCOPE
    assert {one.headers.get("authorization") for one in api.asked[1:]} == {"Bearer short-lived"}


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


def test_azuredns_asks_for_a_token_and_sets_the_record_set(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    record = "/subscriptions/sub/resourceGroups/group/providers/Microsoft.Network/dnsZones/home.example/TXT/_acme-challenge.mcp"
    held: list[list[str]] = []

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
        environment = {
            azuredns.TENANT_ID: "tenant",
            azuredns.CLIENT_ID: "client",
            azuredns.CLIENT_CREDENTIAL_FILE: credential_file(tmp_path),
            azuredns.SUBSCRIPTION_ID: "sub",
            azuredns.RESOURCE_GROUP: "group",
        }
        provider = azuredns.AzureDns.from_environment(environment)
        provider.present(NAME, VALUE)
        assert held == [[VALUE]]
        provider.cleanup(NAME, VALUE)
        assert held == []
        with pytest.raises(
            ProviderError,
            match="Azure DNS holds no zone for",
        ):
            provider.present("_acme-challenge.elsewhere.test.", VALUE)
    assert api.asked[0].form()["client_secret"] == [CREDENTIAL]
    assert ("PUT", record) in said(api.asked)
    assert ("DELETE", record) in said(api.asked)


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


def test_a_refusal_names_the_status_and_the_path_and_never_the_credential(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    with HttpStandIn(lambda _: answered(403, {"errors": [CREDENTIAL]})) as api:
        monkeypatch.setattr(cloudflare, "ENDPOINT", api.url)
        with pytest.raises(ProviderError) as refused:
            cloudflare.Cloudflare(CREDENTIAL).present(NAME, VALUE)
    assert str(refused.value) == "The Cloudflare API answered 403 to GET /zones."


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


def test_a_404_where_a_document_or_a_listing_is_needed_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    with HttpStandIn(lambda _: answered(404, {})) as api:
        reached = Api("Stand-in", api.url)
        for asking in (reached.document, reached.listing, reached.text):
            with pytest.raises(ProviderError, match="answered 404"):
                asking("GET", "/anything")
        assert reached.found("GET", "/anything") is None
    with HttpStandIn(lambda _: (204, {}, b"")) as api:
        assert Api("Stand-in", api.url).found("DELETE", "/anything") == {}


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
