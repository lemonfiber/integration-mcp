# integration-mcp

lemonfiber for AI assistants: a [Model Context Protocol](https://modelcontextprotocol.io)
server that lets an assistant read and control a [lemonfiber](https://github.com/lemonfiber/lemonfiber)
media stack. For an operator who wants to ask an assistant why a download is stuck, and for
household members who want to ask what they have asked for.

It reaches the stack only through [sdk-python](https://github.com/lemonfiber/sdk-python), with
an integration key the operator mints, so an assistant can do exactly what that key allows and
nothing more. It never asks for, accepts or stores the operator's password.

The server speaks stdio, for an assistant on your own machine, and Streamable HTTP over TLS,
for assistants elsewhere on your network or beyond it.

## Set it up

1. Mint a key on the stack, with the purpose `mcp`. `read` lets the assistant read everything
   the stack serves; `act` lets it also restart services, run the doctor, update the stack and
   pause or resume downloads:

   ```
   $ lemonfiber key mint assistant --scope read --purpose mcp
   ```

   The reply shows the key once, beside the stack's address and its certificate pin. Put the key
   in a file only you can read.

2. Add the server to your assistant's configuration. It runs straight from this repository with
   [uv](https://docs.astral.sh/uv/); nothing is installed from a package registry:

   ```json
   {
     "mcpServers": {
       "lemonfiber": {
         "command": "uvx",
         "args": ["--from", "git+https://github.com/lemonfiber/integration-mcp", "lemonfiber-mcp", "stdio"],
         "env": {
           "LEMONFIBER_ADDRESS": "https://192.168.1.42:8443",
           "LEMONFIBER_PIN": "the pin the mint printed",
           "LEMONFIBER_KEY_FILE": "/home/you/.config/lemonfiber/assistant.key"
         }
       }
     }
   }
   ```

| Setting | Holds |
|---|---|
| `LEMONFIBER_ADDRESS` | The stack's address, as the mint printed it |
| `LEMONFIBER_PIN` | The stack's certificate pin. Required for any address not on this machine; the server refuses to start without it |
| `LEMONFIBER_KEY_FILE` | A file holding the key. Preferred |
| `LEMONFIBER_KEY` | The key itself, where a file is not possible |

The key is never taken on the command line, where any process listing would show it, and
nothing but an integration key is accepted.

## Serve it over HTTP

The HTTP mode serves assistants anywhere, from the image each release publishes for amd64 and
arm64 at `ghcr.io/lemonfiber/integration-mcp`. It holds no key of its own: every request brings
the person's key as `Authorization: Bearer <key>`, the stack is asked with that key, and a
request without one is refused before the protocol sees it. It refuses to start where
`LEMONFIBER_KEY` or `LEMONFIBER_KEY_FILE` is set. It answers only over TLS.

```
$ docker run -d --name lemonfiber-mcp -p 8443:8443 \
    -e LEMONFIBER_ADDRESS=https://192.168.1.42:8443 -e LEMONFIBER_PIN=<the stack's pin> \
    -e LEMONFIBER_NAMES=mcp.home.example,192.168.1.50 \
    -v lemonfiber-mcp:/var/lib/lemonfiber-mcp ghcr.io/lemonfiber/integration-mcp:<version>
```

The protocol is served at `https://<name>:8443/mcp`. The image runs as a user of its own, keeps
its certificates in the volume, and checks its own health with `lemonfiber-mcp health`. Outside
the image, `lemonfiber-mcp http` serves the same way.

| Setting | Holds |
|---|---|
| `LEMONFIBER_ADDRESS`, `LEMONFIBER_PIN` | The stack, as for stdio |
| `LEMONFIBER_LISTEN` | Where to listen, as `0.0.0.0:8443` or `[::]:8443`. The image sets `0.0.0.0:8443`; outside it there is no default |
| `LEMONFIBER_NAMES` | Every host name and address assistants reach the server by, separated by commas. Required in every mode but `files`. A wildcard such as `*.home.example` is refused: a key for it would be good for every name under the domain |
| `LEMONFIBER_TLS_MODE` | How the certificate comes: `pinned` where nothing is chosen, `acme`, `private-ca`, or `files` |
| `LEMONFIBER_TLS_CERTIFICATE`, `LEMONFIBER_TLS_PRIVATE_KEY` | Your own certificate chain and key. Setting both chooses `files` |
| `LEMONFIBER_TLS_KEY_TYPE` | The served certificate's key: `ec-p256` by default, `ec-p384`, `rsa-2048` or `rsa-3072` |
| `LEMONFIBER_STATE` | Where certificates are kept: `/var/lib/lemonfiber-mcp` by default, a directory only the server's user may open |

### Who can check its certificate

The server says at every start which mode it serves and who can check its certificate.

| Mode | The certificate | Who can check it |
|---|---|---|
| `pinned` | Made by the server for `LEMONFIBER_NAMES`, valid for ten years, its fingerprint printed at every start | Only a client given that fingerprint |
| `private-ca` | Issued for 30 days by a root the server makes, which may sign only for `LEMONFIBER_NAMES` and only for TLS servers | Only a device that installed the root, printed at start and served at `/root.pem` |
| `acme` | Issued by an ACME authority, Let's Encrypt where none is named, and renewed by the server | Every client, where the authority is public; whoever trusts its root, where it is your own |
| `files` | Yours, read again when either file changes | Whoever trusts the authority that issued it |

An assistant on a phone or in a browser is reached through its provider's servers, and the
provider connects only to a certificate a public authority issued. With `pinned` or
`private-ca` it cannot connect; with `acme` from a public authority, or `files` holding a
publicly trusted certificate, it can.

### A certificate from an ACME authority

**Choosing `acme` is agreeing to the authority's terms of service.** The server writes their
address to its log when it registers its account.

| Setting | Holds |
|---|---|
| `LEMONFIBER_ACME_DIRECTORY` | Any RFC 8555 directory: `https://acme-v02.api.letsencrypt.org/directory` by default, or your own, such as step-ca |
| `LEMONFIBER_ACME_ROOTS` | A PEM file of the roots your own authority's directory is checked against |
| `LEMONFIBER_ACME_CONTACT` | A `mailto:` address the authority may write to |
| `LEMONFIBER_ACME_EAB_KID`, `LEMONFIBER_ACME_EAB_HMAC_FILE` | An External Account Binding, for an authority that requires one: its key identifier, and a file holding its HMAC key |
| `LEMONFIBER_ACME_CHALLENGE` | `tls-alpn-01` by default, answered on the port the server serves on; `http-01`, which needs port 80; or `dns-01`, which needs no inbound connection |
| `LEMONFIBER_ACME_DNS_PROVIDER` | With `dns-01`, the DNS provider the record is written through, from the table below |

With `http-01` the server opens port 80 while an order is pending, answers the challenge and
nothing else, and closes it again; publish it with `-p 80:80`.

With `dns-01` the server writes the challenge's TXT record through your DNS provider, follows a
`_acme-challenge` name you delegated by CNAME to where it points, and asks the authority to look
only once every authoritative server of the zone answers with the record. It is the challenge
for a host nothing on the internet reaches. Providers are named, and their settings spelled, as
[lego](https://go-acme.github.io/lego/dns/) names them:

| Provider | Settings |
|---|---|
| `rfc2136` | `RFC2136_NAMESERVER` (`host`, `host:port` or `[address]:port`), `RFC2136_TSIG_KEY`, `RFC2136_TSIG_ALGORITHM` (`hmac-sha256.` by default), `RFC2136_TSIG_SECRET_FILE` |
| `cloudflare` | `CLOUDFLARE_DNS_API_TOKEN_FILE` |
| `route53` | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY_FILE`, `AWS_HOSTED_ZONE_ID`, and `AWS_REGION` where your account is in AWS China or GovCloud |
| `gcloud` | `GCE_PROJECT`, `GCE_SERVICE_ACCOUNT_FILE` |
| `azuredns` | `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET_FILE`, `AZURE_SUBSCRIPTION_ID`, `AZURE_RESOURCE_GROUP` |
| `digitalocean` | `DO_AUTH_TOKEN_FILE` |
| `hetzner` | `HETZNER_API_TOKEN_FILE`, a Hetzner Console API token |
| `desec` | `DESEC_TOKEN_FILE` |
| `duckdns` | `DUCKDNS_TOKEN_FILE` |
| `exec` | `EXEC_PATH`: your program, run as `<program> present <name> <value>` and `<program> cleanup <name> <value>` |

Every secret is read from the file its `_FILE` setting names, never from a setting itself, so it
never sits in an environment that a process listing or a crash report shows; mount it as a Docker
secret. No credential is written to the log, an error or the health answer. The `exec` program is
given the record's name and value and `PATH`, and nothing else.

Until the first certificate is issued the server serves one standing in, which no
client trusts, and its health answer is `503`. A certificate is renewed when the authority's
renewal information says, or once a third of its lifetime is left; a failed attempt is tried
again after a minute, doubling to six hours, never sooner than the authority asks.

`lemonfiber-mcp pinned replace` makes a new pinned certificate, which every client must then be
given again. `lemonfiber-mcp ca replace` makes a replacement root beside the one in force, and
`lemonfiber-mcp ca switch` puts it in force once it is installed everywhere. A root with a year
of its life left makes its replacement itself, and switches to it 30 days before it ends.

`GET /health` answers the mode, when the certificate expires and how its last check went,
without a key: `200`, or `503` once the certificate in force has seven days or less left.
Renewal is tried every minute it is due, and a failure is logged as an error, then as critical
every hour inside those seven days.

## What the assistant sees and does

Every read the stack serves is a tool and a resource, and every action a key may call is a tool,
all generated from the contract the core publishes. The assistant is offered only what the
key's scope admits, as the stack itself says on every listing. A household member's key is
offered their requests, their shelf and what they are playing, described in the household's
words and never in technical ones. An action that can be rehearsed is two tools: the rehearsal
writes nothing and answers with an offer, and the action takes that offer as its yes. Where what
the offer was made on has changed before the action is called, the stack refuses it and the
assistant is told to rehearse again. Every write tool says whether it disturbs the running system and whether
repeating it is safe, so your assistant's client can ask you first.

Until the stack has answered, the one tool is `connection`, which says why it has not, in the
household's words, since whose key it is is not yet known. A key the
stack refuses is reported as refused by every tool, with the reminder that a new key is needed,
and is never sent again.

## Where what the assistant reads goes

An assistant sends everything a tool answers to the model provider its client uses. Asking
"why is this stuck?" sends the stack's answer, the titles, services and log lines in it
included, to that provider.

A household member can connect an assistant only with a key of their own, and members can mint
one only once the operator turns `LEMONFIBER_MEMBER_KEYS` on. Turning it on lets a member's
requests and what they watch reach a model provider of that member's choosing.

What the stack answers is handed to the assistant as data: each answer is a line from this
server saying that what follows is the stack's answer, then the answer as JSON. Text in it was
written by other people, such as a release's name in a log line, and it is never folded into the
server's own words. Even so, an assistant reads it, so the writes it may call are annotated for
your client to confirm and each takes the offer its rehearsal answered.

Nothing the server answers, logs or reports in an error carries the key or the pin.

## Working on it

```
uv run just ci        # lint, strict types, the generated tools, coverage
uv run just fix       # format and apply the fixes ruff can make
uv run just test      # the suite alone
uv run just generate  # write the tools again from the vendored contract
uv run just vendor <commit>  # take sdk-python and its contract at a commit
```

Mutation testing and `sdk-drift` run in CI.

## Questions and contributing

Ask on [Discord](https://discord.nightworks.io). Every change cites a requirement in the
[specification](https://github.com/lemonfiber/spec); start with the
[contributing guide](https://github.com/lemonfiber/spec/blob/main/50-governance/contributing.md).
What the server must do is set out in
[F13 An assistant's way in](https://github.com/lemonfiber/spec/blob/main/10-functional/features/f-extensibility/f13-mcp.md)
and [the repository page](https://github.com/lemonfiber/spec/blob/main/30-repos/integration-mcp.md).

## Security

Report a vulnerability privately, as the
[security policy](https://github.com/lemonfiber/.github/blob/main/SECURITY.md) describes. Do
not open a public issue.

## Licence

[Hippocratic License 3.0](LICENSE): source-available and ethical-source, not OSI-approved. The
[licence rationale](https://github.com/lemonfiber/spec/blob/main/90-appendix/license-rationale.md)
explains what that means for you. Made by NightWorksIO. The MCP specification's schema in
`vendor/mcp-schema/` is the Model Context Protocol project's, under the licence beside it.
