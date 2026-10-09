# integration-mcp

lemonfiber for AI assistants: a [Model Context Protocol](https://modelcontextprotocol.io)
server that lets an assistant read and control a [lemonfiber](https://github.com/lemonfiber/lemonfiber)
media stack. For an operator who wants to ask an assistant why a download is stuck, and for
household members who want to ask what they have asked for.

It reaches the stack only through [sdk-python](https://github.com/lemonfiber/sdk-python), with
an integration key the operator mints, so an assistant can do exactly what that key allows and
nothing more. It never asks for, accepts or stores the operator's password.

The server speaks stdio, for an assistant on your own machine. Streamable HTTP, for an
assistant on a phone or in a browser, is not in this repository yet.

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

## What the assistant sees and does

Every read the stack serves is a tool and a resource, and every action a key may call is a tool,
all generated from the contract the core publishes. The assistant is offered only what the
key's scope admits, as the stack itself says on every listing. An action that can be rehearsed
is two tools: the rehearsal writes nothing and answers with an offer, and the action takes that
offer as its yes. Every write tool says whether it disturbs the running system and whether
repeating it is safe, so your assistant's client can ask you first.

Until the stack has answered, the one tool is `connection`, which says why it has not. A key the
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
