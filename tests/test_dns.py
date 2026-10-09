# Copyright (c) 2026 NightWorksIO
"""DNS-01 apart from the providers' APIs: a server of the operator's own, a program of theirs, and waiting to be seen."""

import stat
from typing import TYPE_CHECKING, Final

import dns.rdatatype
import dns.resolver
import pytest

from lemonfiber_mcp.certificates.dns import propagation, registry, rfc2136
from lemonfiber_mcp.certificates.dns.challenge import Dns01
from lemonfiber_mcp.certificates.dns.exec import Exec
from lemonfiber_mcp.certificates.dns.provider import ProviderError, Timing, candidates, relative
from lemonfiber_mcp.certificates.modes import CertificateError
from lemonfiber_mcp.certificates.settings import TlsSettingsError
from tests.standins import LOOPBACK, DnsStandIn, keyring_of

if TYPE_CHECKING:
    import pathlib
    from collections.abc import Iterator

NAME: Final = "_acme-challenge.mcp.home.example."
VALUE: Final = "digest-of-the-key-authorization"
TSIG_NAME: Final = "lemonfiber-mcp."
TSIG_KEY: Final = "c2VjcmV0LWtleS1mb3ItdGhlLXRlc3Rz"


@pytest.fixture
def server() -> Iterator[DnsStandIn]:
    """Return a DNS server for `home.example`, taking updates signed with the tests' key."""
    with DnsStandIn(keyring=keyring_of(TSIG_NAME, TSIG_KEY)) as running:
        running.add("home.example.", "SOA", "ns.home.example. hostmaster.home.example. 1 3600 600 86400 60")
        running.add("home.example.", "NS", "ns.home.example.")
        running.add("ns.home.example.", "A", LOOPBACK)
        yield running


def resolver_of(stand_in: DnsStandIn) -> dns.resolver.Resolver:
    """Return a resolver asking only the stand-in."""
    asking = dns.resolver.Resolver(configure=False)
    asking.nameservers = [LOOPBACK]
    asking.port = stand_in.port
    return asking


def key_file(tmp_path: pathlib.Path, key: str = TSIG_KEY) -> str:
    """Write the TSIG key to a file only this user reads."""
    path = tmp_path / "tsig"
    path.write_text(key, encoding="utf-8")
    return str(path)


def test_names_are_looked_up_in_every_zone_they_may_sit_in_and_written_relative_to_theirs() -> None:
    assert candidates(NAME) == ["_acme-challenge.mcp.home.example", "mcp.home.example", "home.example"]
    assert relative(NAME, "home.example") == "_acme-challenge.mcp"
    assert relative("home.example.", "home.example") == "@"


def test_rfc2136_adds_and_deletes_the_record_by_signed_update(
    tmp_path: pathlib.Path,
    server: DnsStandIn,
) -> None:
    provider = rfc2136.Rfc2136.from_environment(
        {
            rfc2136.NAMESERVER: f"{LOOPBACK}:{server.port}",
            rfc2136.TSIG_KEY: TSIG_NAME,
            rfc2136.TSIG_CREDENTIAL_FILE: key_file(tmp_path),
        },
    )
    provider.present(NAME, VALUE)
    assert server.records[(NAME, dns.rdatatype.TXT)] == [f'"{VALUE}"']
    provider.cleanup(NAME, VALUE)
    assert server.records[(NAME, dns.rdatatype.TXT)] == []
    assert all(update.had_tsig for update in server.updates)


def test_rfc2136_refuses_a_name_its_server_holds_no_zone_for(
    tmp_path: pathlib.Path,
    server: DnsStandIn,
) -> None:
    provider = rfc2136.Rfc2136((LOOPBACK, server.port), TSIG_NAME, rfc2136.DEFAULT_ALGORITHM, TSIG_KEY)
    with pytest.raises(ProviderError, match="holds no zone for"):
        provider.present("_acme-challenge.elsewhere.example.", VALUE)


def test_rfc2136_says_when_its_server_refuses_the_update(server: DnsStandIn) -> None:
    server.refusing = True
    provider = rfc2136.Rfc2136((LOOPBACK, server.port), TSIG_NAME, rfc2136.DEFAULT_ALGORITHM, TSIG_KEY)
    with pytest.raises(ProviderError, match="refused the update: REFUSED"):
        provider.present(NAME, VALUE)


def test_rfc2136_refuses_an_update_signed_with_another_key(server: DnsStandIn) -> None:
    provider = rfc2136.Rfc2136((LOOPBACK, server.port), TSIG_NAME, rfc2136.DEFAULT_ALGORITHM, "b3RoZXIta2V5")
    with pytest.raises(ProviderError, match="could not be updated"):
        provider.present(NAME, VALUE)


def test_rfc2136_that_cannot_reach_its_server_finds_no_zone_there(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(rfc2136, "TIMEOUT_SECONDS", 0.1)
    provider = rfc2136.Rfc2136((LOOPBACK, 9), TSIG_NAME, rfc2136.DEFAULT_ALGORITHM, TSIG_KEY)
    with pytest.raises(ProviderError, match="holds no zone"):
        provider.present(NAME, VALUE)


def test_rfc2136_refuses_a_key_that_is_not_base64(tmp_path: pathlib.Path) -> None:
    with pytest.raises(TlsSettingsError, match="does not hold a TSIG secret"):
        rfc2136.Rfc2136((LOOPBACK, 53), TSIG_NAME, rfc2136.DEFAULT_ALGORITHM, "not base64!")


@pytest.mark.parametrize(
    ("written", "server"),
    [
        ("ns.home.example", ("ns.home.example", 53)),
        ("ns.home.example:5353", ("ns.home.example", 5353)),
        ("192.0.2.53", ("192.0.2.53", 53)),
        ("2001:db8::53", ("2001:db8::53", 53)),
        ("[2001:db8::53]:5353", ("2001:db8::53", 5353)),
        ("[2001:db8::53]", ("2001:db8::53", 53)),
    ],
)
def test_the_nameserver_is_read_with_or_without_a_port(written: str, server: tuple[str, int]) -> None:
    assert rfc2136.nameserver_of(written) == server


def program(tmp_path: pathlib.Path, body: str) -> pathlib.Path:
    """Write a program the `exec` provider runs, and return its path."""
    path = tmp_path / "dns-hook"
    path.write_text(f"#!/bin/sh\n{body}\n", encoding="utf-8")
    path.chmod(stat.S_IRWXU)
    return path


def test_exec_runs_the_operators_program_with_the_name_and_the_value_and_nothing_else(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("LEMONFIBER_ACME_EAB_HMAC_FILE", "/srv/hmac")
    told = tmp_path / "told"
    hook = program(
        tmp_path,
        f'echo "$@" >> {told}; env | grep -v "^PATH=" | grep -v "^PWD=" | grep -v "^SHLVL=" | grep -v "^_=" >> {told}; true',
    )
    provider = Exec.from_environment({"EXEC_PATH": str(hook)})
    provider.present(NAME, VALUE)
    provider.cleanup(NAME, VALUE)
    assert told.read_text(encoding="utf-8").splitlines() == [
        f"present {NAME} {VALUE}",
        f"cleanup {NAME} {VALUE}",
    ]


def test_exec_says_when_the_program_fails(tmp_path: pathlib.Path) -> None:
    provider = Exec(program(tmp_path, "exit 3"))
    with pytest.raises(ProviderError, match="present failed: CalledProcessError"):
        provider.present(NAME, VALUE)


def test_exec_refuses_a_program_it_cannot_run(tmp_path: pathlib.Path) -> None:
    plain = tmp_path / "plain"
    plain.write_text("", encoding="utf-8")
    with pytest.raises(TlsSettingsError, match="not a program this user can run"):
        Exec(plain)


def test_every_provider_is_named_as_lego_names_it() -> None:
    assert set(registry.PROVIDERS) == {
        "rfc2136",
        "cloudflare",
        "route53",
        "gcloud",
        "azuredns",
        "digitalocean",
        "hetzner",
        "desec",
        "duckdns",
        "exec",
    }


@pytest.mark.parametrize("name", [None, "bind9"])
def test_a_provider_that_is_none_of_them_is_refused_by_name(name: str | None) -> None:
    with pytest.raises(TlsSettingsError, match="LEMONFIBER_ACME_DNS_PROVIDER is"):
        registry.provider_of(name, {})


def test_a_named_provider_is_made_from_its_settings(tmp_path: pathlib.Path) -> None:
    hook = program(tmp_path, "true")
    assert isinstance(registry.provider_of("exec", {"EXEC_PATH": str(hook)}), Exec)


def test_a_challenge_name_delegated_by_cname_is_followed_to_where_it_points(server: DnsStandIn) -> None:
    server.add(NAME, "CNAME", "challenge.dns.example.")
    server.add("challenge.dns.example.", "CNAME", "final.dns.example.")
    assert propagation.delegated(NAME, resolver_of(server)) == "final.dns.example."
    assert propagation.delegated("plain.home.example.", resolver_of(server)) == "plain.home.example."


def test_a_loop_of_cnames_is_followed_no_further_than_eight(server: DnsStandIn) -> None:
    server.add("a.home.example.", "CNAME", "b.home.example.")
    server.add("b.home.example.", "CNAME", "a.home.example.")
    assert propagation.delegated("a.home.example.", resolver_of(server)) in {
        "a.home.example.",
        "b.home.example.",
    }


def test_the_zones_authoritative_servers_are_found_by_its_name_servers(
    server: DnsStandIn,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    server.add("home.example.", "NS", "gone.home.example.")
    monkeypatch.setattr(propagation, "PORT", server.port)
    assert propagation.authoritative(NAME, resolver_of(server)) == [(LOOPBACK, server.port)]


class Ticking:
    """A clock that moves a second each time it is read, and a sleep that only counts."""

    def __init__(self) -> None:
        """Start at nothing."""
        self.now = 0.0
        self.slept = 0

    def clock(self) -> float:
        """Return the time, then move it on."""
        self.now += 1.0
        return self.now

    def sleep(self, _: float) -> None:
        """Count a sleep."""
        self.slept += 1


def test_a_record_is_waited_for_until_every_server_answers_with_it(server: DnsStandIn) -> None:
    ticking = Ticking()
    waiting = propagation.Waiting(sleep=ticking.sleep, clock=ticking.clock)
    servers = [(LOOPBACK, server.port)]
    assert not propagation.seen_everywhere(
        NAME,
        VALUE,
        servers,
        Timing(propagation=3.0, interval=1.0),
        waiting,
    )
    assert ticking.slept == 2
    server.add(NAME, "TXT", f'"{VALUE}"')
    assert propagation.seen_everywhere(NAME, VALUE, servers, Timing(), waiting)


def test_a_server_answering_with_another_name_has_not_seen_the_record(server: DnsStandIn) -> None:
    server.add(NAME, "CNAME", "elsewhere.home.example.")
    assert not propagation.answers_with((LOOPBACK, server.port), NAME, VALUE)


def test_a_server_that_does_not_answer_has_not_seen_the_record(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(propagation, "QUERY_TIMEOUT", 0.1)
    assert not propagation.answers_with((LOOPBACK, 9), NAME, VALUE)


class Recording:
    """A provider keeping what it was asked to write and remove."""

    timing = Timing(propagation=2.0, interval=1.0)

    def __init__(self) -> None:
        """Hold nothing yet."""
        self.written: list[tuple[str, str]] = []

    def present(self, name: str, value: str) -> None:
        """Keep what was written."""
        self.written.append((name, value))

    def cleanup(self, name: str, value: str) -> None:
        """Forget what was written."""
        self.written.remove((name, value))


def test_a_dns_01_answer_is_written_where_the_name_points_and_waited_for(server: DnsStandIn) -> None:
    provider = Recording()
    ticking = Ticking()
    answering = Dns01(
        provider,
        resolver=lambda: resolver_of(server),
        servers=lambda _, __: [(LOOPBACK, server.port)],
        waiting=propagation.Waiting(sleep=ticking.sleep, clock=ticking.clock),
    )
    assert answering.where("mcp.home.example") == NAME
    server.add(NAME, "TXT", f'"{VALUE}"')
    answering.wait_for(NAME, VALUE)
    with pytest.raises(CertificateError, match="not answered by every authoritative server within 2 seconds"):
        answering.wait_for(NAME, "another")


def test_names_that_cannot_be_looked_up_are_refused() -> None:
    def unconfigured() -> dns.resolver.Resolver:
        raise dns.resolver.NoResolverConfiguration

    with pytest.raises(CertificateError, match="could not be looked up to answer DNS-01 for"):
        Dns01(Recording(), resolver=unconfigured).where("mcp.home.example")


def test_a_record_that_is_not_text_is_not_the_value(server: DnsStandIn) -> None:
    server.add(NAME, "TXT", '"\\255\\254"')
    assert not propagation.answers_with((LOOPBACK, server.port), NAME, VALUE)


def test_a_dns_01_answer_whose_zone_cannot_be_found_is_refused(server: DnsStandIn) -> None:
    answering = Dns01(Recording(), resolver=lambda: resolver_of(server))
    with pytest.raises(
        CertificateError,
        match=r"authoritative servers of _acme-challenge\.elsewhere\.test\. could not be found",
    ):
        answering.wait_for("_acme-challenge.elsewhere.test.", VALUE)
