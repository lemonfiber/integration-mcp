# Copyright (c) 2026 NightWorksIO
"""Generate every tool the server offers from the contract vendored in `contract/web-api/`.

Each read the web API serves becomes a tool and a resource, each action a key
may call becomes a tool, and each of those that can be rehearsed gains a
rehearsal tool beside it, with the protocol's annotations taken from what the
contract says of the action. Only the words are written by hand, in
`src/lemonfiber_mcp/descriptions.toml`.

The contract is read from disk and nothing else: generation reaches no network,
refuses an `api_version` it does not implement, refuses a reference it cannot
resolve or that could be read two ways, and writes nothing when it refuses.

    python3 scripts/generate_tools.py          write the module
    python3 scripts/generate_tools.py --check  fail where the module is not what the contract generates
"""

import argparse
import copy
import json
import pathlib
import pprint
import re
import sys
from dataclasses import dataclass
from typing import Final, cast

ROOT: Final = pathlib.Path(__file__).resolve().parent.parent
CONTRACT: Final = pathlib.Path("contract/web-api")
REVISION: Final = pathlib.Path("contract/VERSION")
OUTPUT: Final = pathlib.Path("src/lemonfiber_mcp/_generated/tools.py")
SPOKEN: Final = 1
"""The `api_version` this generator implements."""

API: Final = "/api/"
ACTIONS: Final = "/api/actions/"
LOGS: Final = "/api/logs"
STREAMING: Final = frozenset({"follow"})
"""What turns the log read into a stream, which a tool cannot hold open."""
OFFER: Final = "offer"
"""The argument an action takes its rehearsal's offer as."""
SCHEME: Final = "lemonfiber://"
PLACEHOLDER: Final = re.compile(r"\{([a-z_]+)\}")
DESCRIBED_ONLY: Final = frozenset({"$ref", "description"})
"""What may stand beside a reference: an annotation, never a constraint."""

type Json = dict[str, object]


class GenerationError(Exception):
    """The contract cannot be generated from as it stands; nothing was written."""


@dataclass(frozen=True, slots=True)
class Shape:
    """One tool, as the module writes it."""

    name: str
    reach: str
    target: str
    capability: str
    parameters: tuple[str, ...]
    input_schema: Json
    resource: str | None
    read_only: bool
    destructive: bool
    idempotent: bool


def loaded(path: pathlib.Path) -> object:
    """Return a contract file's JSON, refusing one that is missing or unreadable."""
    try:
        return cast("object", json.loads(path.read_text(encoding="utf-8")))
    except (OSError, ValueError) as fault:
        msg = f"{path} could not be read: {fault}"
        raise GenerationError(msg) from None


def table(value: object, where: pathlib.Path) -> Json:
    """Return a JSON object, refusing anything else."""
    if not isinstance(value, dict):
        msg = f"{where} does not hold an object where one is expected."
        raise GenerationError(msg)
    return cast("Json", value)


def rows(value: object, where: pathlib.Path) -> list[Json]:
    """Return a JSON list of objects, refusing anything else."""
    if not isinstance(value, list):
        msg = f"{where} does not hold a list where one is expected."
        raise GenerationError(msg)
    return [table(row, where) for row in cast("list[object]", value)]


def resolved(schema: object, where: pathlib.Path, seen: tuple[pathlib.Path, ...] = ()) -> object:
    """Return a schema with every reference replaced by the definition it names, read from its own file."""
    if isinstance(schema, list):
        return [resolved(item, where, seen) for item in cast("list[object]", schema)]
    if not isinstance(schema, dict):
        return schema
    held = cast("Json", schema)
    reference = held.get("$ref")
    if reference is None:
        return {key: resolved(value, where, seen) for key, value in held.items()}
    if not isinstance(reference, str) or set(held) - DESCRIBED_ONLY:
        msg = f"{where} has a reference with constraints beside it, which two readers read two ways."
        raise GenerationError(msg)
    target = (where.parent / reference).resolve()
    if target in seen:
        msg = f"{where} refers back to {target.name} through itself, which no tool input can describe."
        raise GenerationError(msg)
    if not target.is_file():
        msg = f"{where} refers to {reference}, which the vendored contract does not hold."
        raise GenerationError(msg)
    definition = table(resolved(loaded(target), target, (*seen, target)), target)
    definition.pop("$schema", None)
    if "description" in held:
        definition["description"] = held["description"]
    return definition


def read_shape(entry: Json, where: pathlib.Path) -> Shape:
    """Return the tool a read the contract lists becomes."""
    path = str(entry.get("path", ""))
    if not path.startswith(API):
        msg = f"{where} lists a read at {path!r}, which is not under {API}."
        raise GenerationError(msg)
    listed = rows(entry.get("parameters", []), where)
    if entry.get("file") is True:
        names = tuple(PLACEHOLDER.findall(path))
        target = path.removeprefix(API).split("/", 1)[0]
        properties: Json = {name: {"type": "string"} for name in names}
        return Shape(
            name=f"read_{snake(target)}",
            reach="file",
            target=target,
            capability=path,
            parameters=names,
            input_schema={
                "type": "object",
                "properties": properties,
                "required": list(names),
                "additionalProperties": False,
            },
            resource=f"{SCHEME}{target}/" + "/".join(f"{{{name}}}" for name in names),
            read_only=True,
            destructive=False,
            idempotent=True,
        )
    if path == LOGS:
        if not {str(row.get("name")) for row in listed} >= STREAMING:
            msg = f"{where} lists {LOGS} without {', '.join(sorted(STREAMING))}, so what makes it a stream has moved."
            raise GenerationError(msg)
        listed = [row for row in listed if row.get("name") not in STREAMING]
    target = path.removeprefix(API)
    names = tuple(str(row.get("name")) for row in listed)
    properties = {
        str(row.get("name")): (
            {"type": "array", "items": {"type": "string"}}
            if row.get("repeatable") is True
            else {"type": "string"}
        )
        for row in listed
    }
    template = ",".join(f"{row.get('name')}{'*' if row.get('repeatable') is True else ''}" for row in listed)
    return Shape(
        name=f"read_{snake(target)}",
        reach="logs" if path == LOGS else "read",
        target=target,
        capability=path,
        parameters=names,
        input_schema={"type": "object", "properties": properties, "additionalProperties": False},
        resource=f"{SCHEME}read/{target}" + (f"{{?{template}}}" if template else ""),
        read_only=True,
        destructive=False,
        idempotent=True,
    )


def action_shapes(entry: Json, contract: pathlib.Path, index: Json) -> list[Shape]:
    """Return the tools an action a key may call becomes: itself, and its rehearsal where it has one."""
    action = str(entry.get("action", ""))
    actions = table(index.get("actions", {}), contract / "index.json")
    if action not in actions:
        msg = f"{action!r} is listed as callable by a key, and the contract publishes no such action."
        raise GenerationError(msg)
    where = contract / str(actions[action])
    published = table(loaded(where), where)
    consent = {str(name) for name in cast("list[object]", published.get("consent", []))}
    arguments: list[tuple[str, Json]] = [
        (str(row.get("name")), table(resolved(row.get("type", {}), where), where))
        for row in rows(published.get("arguments", []), where)
    ]
    if any(name == OFFER for name, _ in arguments):
        msg = f"{where} takes an argument named {OFFER!r}, the name the rehearsal's offer is sent under."
        raise GenerationError(msg)
    capability = f"{ACTIONS}{action}"
    disturbs = entry.get("disturbs") is True
    idempotent = entry.get("idempotent") is True
    rehearsable = entry.get("rehearsal") is True
    taken: Json = dict(arguments)
    required = [name for name, schema in arguments if "default" not in schema]
    acting: Json = copy.deepcopy(taken)
    if rehearsable:
        acting[OFFER] = {"type": "string"}
        required = [*required, OFFER]
    shapes = [
        Shape(
            name=snake(action),
            reach="action",
            target=action,
            capability=capability,
            parameters=tuple(acting),
            input_schema={
                "type": "object",
                "properties": acting,
                "required": required,
                "additionalProperties": False,
            },
            resource=None,
            read_only=False,
            destructive=disturbs,
            idempotent=idempotent,
        ),
    ]
    if rehearsable:
        asked = {name: schema for name, schema in arguments if name not in consent}
        shapes.insert(
            0,
            Shape(
                name=f"rehearse_{snake(action)}",
                reach="rehearsal",
                target=action,
                capability=capability,
                parameters=tuple(asked),
                input_schema={
                    "type": "object",
                    "properties": copy.deepcopy(asked),
                    "required": [name for name in required if name in asked],
                    "additionalProperties": False,
                },
                resource=None,
                read_only=True,
                destructive=False,
                idempotent=True,
            ),
        )
    return shapes


def snake(name: str) -> str:
    """Return a contract name as a tool's name spells it."""
    return name.replace("-", "_")


def shapes(root: pathlib.Path) -> list[Shape]:
    """Return every tool the vendored contract generates, refusing a contract this generator cannot read."""
    contract = root / CONTRACT
    index = table(loaded(contract / "index.json"), contract / "index.json")
    spoken = index.get("api_version")
    if spoken != SPOKEN:
        msg = f"the vendored contract speaks api_version {spoken!r}, and this generator implements {SPOKEN}."
        raise GenerationError(msg)
    reads = contract / str(index.get("reads", "reads.json"))
    callable_by_a_key = contract / str(index.get("key_callable", "key-callable.json"))
    generated = [read_shape(entry, reads) for entry in rows(loaded(reads), reads)]
    for entry in rows(loaded(callable_by_a_key), callable_by_a_key):
        generated.extend(action_shapes(entry, contract, index))
    names = [shape.name for shape in generated]
    if len(set(names)) != len(names):
        twice = sorted({name for name in names if names.count(name) > 1})
        msg = f"the contract generates more than one tool named {', '.join(twice)}."
        raise GenerationError(msg)
    return generated


def module(generated: list[Shape], revision: str) -> str:
    """Return the module's source, the same bytes for the same contract."""
    lines = [
        "# Copyright (c) 2026 NightWorksIO",
        '"""Every tool the server offers, as the contract describes it.',
        "",
        f"Generated from the contract lemonfiber {revision} published, vendored in `contract/web-api/`.",
        "Do not edit: `just generate` rewrites it, and CI fails on any difference.",
        '"""',
        "",
        "from typing import Final",
        "",
        "from lemonfiber_mcp.shapes import Reach, ToolShape",
        "",
        f"API_VERSION: Final = {SPOKEN}",
        '"""The `api_version` the tools were generated for."""',
        "",
        f"CONTRACT: Final = {revision!r}",
        '"""The lemonfiber revision whose contract the tools were generated from."""',
        "",
        "TOOLS: Final[tuple[ToolShape, ...]] = (",
    ]
    for shape in generated:
        lines.append("    ToolShape(")
        lines.append(f"        name={shape.name!r},")
        lines.append(f"        reach=Reach.{shape.reach.upper()},")
        lines.append(f"        target={shape.target!r},")
        lines.append(f"        capability={shape.capability!r},")
        lines.append(f"        parameters={shape.parameters!r},")
        schema = pprint.pformat(shape.input_schema, width=100, sort_dicts=False)
        lines.append("        input_schema=" + schema.replace("\n", "\n" + " " * 21) + ",")
        lines.append(f"        resource={shape.resource!r},")
        lines.append(f"        read_only={shape.read_only!r},")
        lines.append(f"        destructive={shape.destructive!r},")
        lines.append(f"        idempotent={shape.idempotent!r},")
        lines.append("    ),")
    lines.append(")")
    lines.append(
        '"""Each tool, reads first in the order the contract lists them, then the actions a key may call."""',
    )
    return "\n".join(lines) + "\n"


def run(arguments: list[str], root: pathlib.Path = ROOT) -> int:
    """Write the module, or check it, as the arguments say, and say what was done."""
    parser = argparse.ArgumentParser(description="Generate the server's tools from the vendored contract.")
    parser.add_argument("--check", action="store_true", help="fail where the module is not what is generated")
    asked = parser.parse_args(arguments)
    try:
        revision = (root / REVISION).read_text(encoding="ascii").strip()
        source = module(shapes(root), revision)
    except (GenerationError, OSError) as fault:
        sys.stderr.write(f"::error::{fault}\n")
        return 1
    output = root / OUTPUT
    if asked.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != source:
            sys.stderr.write(
                f"::error::{OUTPUT} is not what the vendored contract generates. Run `just generate`.\n",
            )
            return 1
        sys.stdout.write(f"{OUTPUT} is what the vendored contract generates.\n")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(source, encoding="utf-8")
    (output.parent / "__init__.py").write_text(
        '# Copyright (c) 2026 NightWorksIO\n"""What `scripts/generate_tools.py` writes from the vendored contract."""\n',
        encoding="utf-8",
    )
    sys.stdout.write(f"wrote {OUTPUT}.\n")
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1:]))
