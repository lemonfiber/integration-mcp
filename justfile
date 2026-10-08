# Task runner for lemonfiber/integration-mcp. `just` with no argument lists these.
default:
    @just --list

# There is no package manager here, so there is no `npm ci` or `composer install`
# to hang `core.hooksPath` on the way the other repos do — it is this recipe or
# nothing, and `ci` depends on it so that running the checks once turns the hooks
# on for good. The setting is per-clone local config and no commit can carry it.
#
# Turn on this clone's git hooks. Once per clone.
hooks:
    git config core.hooksPath .githooks
    @echo "hooks on: .githooks/commit-msg, .githooks/pre-push"

# Every gate CI runs over the contents of this repository, in the order CI runs
# them, plus the hooks that answer for the commit message.
#
# This repository holds markdown and workflow files and no code yet, so what CI
# reads here is the hygiene set. What is not here, and what covers each:
#
#   commitlint, dco, spec-check                `.githooks/commit-msg` refuses all
#                                              three before the push, and `hooks`
#                                              above is what turns it on
#   shared-files, pins, workflow-pins          need a lemonfiber/spec checkout and
#                                              the forge to compare against
#   actionlint, markdown, invite               need tools this repository does not
#                                              otherwise ask for; `npx
#                                              markdownlint-cli2 "**/*.md"` and
#                                              `actionlint` are the two commands
#   osv-scanner, gitleaks, label, codeql       forge-side
#
# Spelling and links, which is what CI reads in this tree — not the whole of CI.
ci: hooks typos links

# Spell check.
typos:
    typos

# Link check.
links:
    lychee --no-progress .
