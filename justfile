# Task runner for lemonfiber/integration-mcp. `uv run just` with no argument lists the tasks.
#
# `just` is a dev dependency, so `uv run just <task>` works in any clone after
# `uv sync`. Every task runs its tools through `uv run`, so the versions are the
# ones `uv.lock` pins.
default:
    @just --list

# Turn on the repository's own git hooks. Once per clone; `ci` does it too.
hooks:
    git config core.hooksPath .githooks
    @echo "hooks on: .githooks/pre-commit, .githooks/commit-msg, .githooks/pre-push"

# Everything the `checks` and `tests and coverage` jobs run. Mutation, the
# vendored client's drift, the image and the shared workflows are CI's alone.
ci: hooks lint types generated coverage

# Formatting and every lint rule, changing nothing.
lint:
    uv run ruff format --check .
    uv run ruff check .

# Format, apply the fixes ruff can make, and format what they changed.
fix:
    uv run ruff format .
    uv run ruff check --fix .
    uv run ruff format .

# Pyright in strict mode over the server, the tests and the scripts.
types:
    uv run pyright

# The suite alone.
test *args:
    uv run pytest {{args}}

# The suite with 100% line and branch coverage required, and the report CI reads
# written to `coverage.xml`.
coverage:
    uv run pytest --cov --cov-report=term-missing --cov-report=xml

# Write the tools from the vendored contract.
generate:
    uv run python scripts/generate_tools.py

# Fail where the tools are not what the vendored contract generates.
generated:
    uv run python scripts/generate_tools.py --check

# Replace the vendored client and its contract with sdk-python at a full commit
# hash, and write the tools again from that contract.
vendor commit:
    uv run python scripts/vendor_sdk.py take {{commit}}
    uv run python scripts/generate_tools.py

# The vendored client and contract against the commit they record, and against
# sdk-python's main.
vendor-check:
    uv run python scripts/vendor_sdk.py check

# Mutation testing and the minimum score. Slow: CI runs it on every pull request.
mutation:
    uv run mutmut run
    uv run mutmut export-cicd-stats
    uv run python scripts/mutation_score.py

# One shard of the mutation run, by its index from 0 and the number of shards,
# held to the minimum score on its own. CI runs each shard as a job of its own.
mutation-shard index total:
    set -f; uv run mutmut run $(uv run python scripts/mutation_shard.py {{index}} {{total}})
    uv run mutmut export-cicd-stats
    uv run python scripts/mutation_score.py
