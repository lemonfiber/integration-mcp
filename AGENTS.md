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
operator mints. It holds no code yet. Spec:
[F13](https://github.com/lemonfiber/spec/blob/main/10-functional/features/f-extensibility/f13-mcp.md)
and [`30-repos/integration-mcp.md`](https://github.com/lemonfiber/spec/blob/main/30-repos/integration-mcp.md).

## The rule you cannot break

**The stack is reached through sdk-python alone, with an integration key.** An
assistant can do exactly what that key's scope allows and nothing more; the
server never asks for, accepts or stores the operator password.
