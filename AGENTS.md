# AGENTS.md — integration-mcp

Guidance for any AI agent working in this repo.

> **Start at the report** of where every unreleased version stands: the summary
> of the newest run of the spec's [`state` workflow](https://github.com/lemonfiber/spec/actions/workflows/state.yml),
> or `just goals <version>` in a spec checkout.
> **Then the rules every repository shares:**
> [working in the repositories](https://github.com/lemonfiber/spec/blob/main/50-governance/working-in-the-repositories.md)
> and [the rules for agents](https://github.com/lemonfiber/spec/blob/main/50-governance/ai-contributors.md).
> This file holds only what is true of `integration-mcp`.

## What this repo is

The Model Context Protocol server that lets an assistant read and control a
lemonfiber stack. It holds no code yet. What it must do is
[F13](https://github.com/lemonfiber/spec/blob/main/10-functional/features/f-extensibility/f13-mcp.md),
and how it is built, run and released is its
[repository page](https://github.com/lemonfiber/spec/blob/main/30-repos/integration-mcp.md).

## The rule you cannot break here

It reaches a stack only through [sdk-python](https://github.com/lemonfiber/sdk-python),
with an integration key the operator mints, so an assistant can do exactly what
that key allows and nothing more.
