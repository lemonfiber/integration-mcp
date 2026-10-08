# AGENTS.md — integration-mcp

> **Start at the roadmap and board on [lemonfiber.app](https://lemonfiber.app),
> rendered from the report of where every unreleased version stands. Then the
> rules** every repository shares:
> [working in the repositories](https://github.com/lemonfiber/spec/blob/main/50-governance/working-in-the-repositories.md)
> and [the rules for agents](https://github.com/lemonfiber/spec/blob/main/50-governance/ai-contributors.md).
> This file holds only what is true of this repository.

## What this repo is

lemonfiber for AI assistants: a Model Context Protocol server that reads and
controls a lemonfiber stack through sdk-python, with an integration key the
operator mints. Python, on the official `mcp` package's low-level server. Spec:
[F13](https://github.com/lemonfiber/spec/blob/main/10-functional/features/f-extensibility/f13-mcp.md),
[the certificates contract](https://github.com/lemonfiber/spec/blob/main/20-architecture/contracts/certificates.md)
and [`30-repos/integration-mcp.md`](https://github.com/lemonfiber/spec/blob/main/30-repos/integration-mcp.md).

## The rules you cannot break

- **The stack is reached through sdk-python alone, with an integration key.**
  No module imports an HTTP client, and nothing asks for, accepts or stores the
  operator password; the architecture tests refuse both.
- **Nothing secret leaves.** Every tool result, error, resource and log line
  passes through `withheld.py`; a key or the pin in any of them is a defect.
- **What the stack says is data.** A tool answers with the server's line, then
  the stack's answer as JSON in a block of its own; the stack's text is never
  written into the server's sentences.
- **`src/lemonfiber_mcp/_vendor/` and `contract/` are not edited by hand.** They
  are sdk-python and its contract at the commit `_vendor/lemonfiber/REVISION`
  names, written by `uv run just vendor <commit>`; `sdk-drift` fails on any
  difference, and `sdk-bump` takes sdk-python's `main` on its own pull request.
- **`src/lemonfiber_mcp/_generated/` is not edited by hand.** `uv run just
  generate` writes it from `contract/`, and CI fails on any difference. Only
  `descriptions.toml` is written: every tool's words, in the household's words
  for what a member reaches.
- **No suppressions.** No `# type: ignore`, `# pyright:`, `# noqa` or
  `# pragma: no cover`; the architecture tests refuse each of them.

## Checks

```
uv run just ci        # lint, strict types, the generated tools, coverage
uv run just fix       # format and apply the fixes ruff can make
uv run just test      # the suite alone
```

Mutation testing (`just mutation`) and `sdk-drift` are merge gates that run in
CI. `vendor/mcp-schema/` is the MCP specification's schema the conformance
suite reads, taken by `scripts/vendor_mcp_schema.py take <revision>`.
