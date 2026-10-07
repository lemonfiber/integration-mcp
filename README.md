# integration-mcp

lemonfiber for AI assistants: a [Model Context Protocol](https://modelcontextprotocol.io)
server that lets an assistant read and control a [lemonfiber](https://github.com/lemonfiber/lemonfiber)
media stack. For an operator who wants to ask an assistant why a download is stuck, and for
household members who want to ask what they have requested.

**This repository has no code yet.** There is nothing to install or run. What the server
must do is set out in the specification:

- [F13 An assistant's way in](https://github.com/lemonfiber/spec/blob/main/10-functional/features/f-extensibility/f13-mcp.md):
  what an assistant can see and do, and what it cannot.
- [The `integration-mcp` repository page](https://github.com/lemonfiber/spec/blob/main/30-repos/integration-mcp.md):
  how it is built, run and released.

The specification requires the server to reach a stack only through
[sdk-python](https://github.com/lemonfiber/sdk-python), with an integration key the operator
mints, so an assistant can do exactly what that key allows and nothing more.

## Questions and contributing

Ask on [Discord](https://discord.nightworks.io). Every change cites a requirement in the
[specification](https://github.com/lemonfiber/spec); start with the
[contributing guide](https://github.com/lemonfiber/spec/blob/main/50-governance/contributing.md).

## Security

Report a vulnerability privately, as the
[security policy](https://github.com/lemonfiber/.github/blob/main/SECURITY.md) describes. Do
not open a public issue.

## Licence

[Hippocratic License 3.0](LICENSE): source-available and ethical-source, not OSI-approved. The
[licence rationale](https://github.com/lemonfiber/spec/blob/main/90-appendix/license-rationale.md)
explains what that means for you. Made by NightWorksIO.
