#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml>=6.0.2", "jsonschema>=4.23", "referencing>=0.35"]
# ///
"""Validate breeds/*.yaml and formations/*.yaml against specs/*.schema.json.

  uv run scripts/validate.py            # everything
  uv run scripts/validate.py FILE...    # only these files (cross-file rules still use all breeds)

Schema checks cover the shape of each file. The cross-file rules a JSON
Schema cannot express are checked here:

  breeds      file name = name; `extends` exists; the merged breed is complete
              (specs/breed.schema.json#/$defs/resolved); `may_spawn` and
              `handoff.next` name existing breeds
  formations  file name = name; lead and member breeds exist; count.min <= max;
              spawn_tree only narrows the breeds' may_spawn and only names
              participants; overrides only lower limits and only add denies;
              handoffs only between participants; max_agents >= lead + all max
"""
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parent.parent
SPECS = ROOT / "specs"
BREED_ID = "https://github.com/flokpit/formations/specs/breed.schema.json"
FORMATION_ID = "https://github.com/flokpit/formations/specs/formation.schema.json"


def load_schemas():
    breed = json.loads((SPECS / "breed.schema.json").read_text())
    formation = json.loads((SPECS / "formation.schema.json").read_text())
    registry = Registry().with_resources(
        [(BREED_ID, Resource.from_contents(breed)), (FORMATION_ID, Resource.from_contents(formation))]
    )
    return {
        "breed": Draft202012Validator(breed, registry=registry),
        "resolved": Draft202012Validator({"$ref": BREED_ID + "#/$defs/resolved"}, registry=registry),
        "formation": Draft202012Validator(formation, registry=registry),
    }


def merge(base, over):
    """Deep merge: maps merge, lists and scalars replace."""
    if isinstance(base, dict) and isinstance(over, dict):
        out = dict(base)
        for key, value in over.items():
            out[key] = merge(base[key], value) if key in base else value
        return out
    return over


def seconds(duration):
    value, unit = int(duration[:-1]), duration[-1]
    return value * {"s": 1, "m": 60, "h": 3600}[unit]


def schema_errors(validator, doc):
    return [
        f"{'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message}"
        for e in sorted(validator.iter_errors(doc), key=lambda e: list(map(str, e.absolute_path)))
    ]


def read_yaml(path, errors):
    try:
        doc = yaml.safe_load(path.read_text())
    except yaml.YAMLError as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None
    if not isinstance(doc, dict):
        errors.append(f"{path.relative_to(ROOT)}: top level must be a mapping")
        return None
    return doc


def check_breeds(schemas, errors):
    raw, resolved = {}, {}
    for path in sorted((ROOT / "breeds").glob("*.yaml")):
        rel = path.relative_to(ROOT)
        doc = read_yaml(path, errors)
        if doc is None:
            continue
        found = schema_errors(schemas["breed"], doc)
        errors += [f"{rel}: {e}" for e in found]
        if doc.get("name") != path.stem:
            errors.append(f"{rel}: name {doc.get('name')!r} does not match the file name")
        # Keep invalid breeds too, so references to them are checked against
        # what is there instead of cascading into "unknown breed" errors.
        raw[path.stem] = (rel, doc)

    for name, (rel, doc) in raw.items():
        if doc.get("kind") != "Breed":
            continue
        base = raw.get(doc.get("extends"))
        if base is None or base[1].get("kind") != "BreedBase":
            errors.append(f"{rel}: extends {doc.get('extends')!r}, which is not a BreedBase in breeds/")
            resolved[name] = (rel, doc)
            continue
        merged = merge(base[1], doc)
        reported = {e for e in errors if e.startswith(f"{rel}: ")}
        for e in schema_errors(schemas["resolved"], merged):
            if f"{rel}: {e}" not in reported:
                errors.append(f"{rel} (merged with {doc['extends']}): {e}")
        resolved[name] = (rel, merged)

    for name, (rel, breed) in resolved.items():
        for target in breed.get("privileges", {}).get("may_spawn", []):
            if target not in resolved:
                errors.append(f"{rel}: privileges/may_spawn names unknown breed {target!r}")
        nxt = breed.get("handoff", {}).get("next")
        if nxt and nxt not in resolved:
            errors.append(f"{rel}: handoff/next names unknown breed {nxt!r}")
    return {name: breed for name, (_, breed) in resolved.items()}


def check_overrides(rel, where, breed, overrides, errors):
    for key, value in overrides.get("limits", {}).items():
        current = breed.get("limits", {}).get(key)
        if key == "max_budget_usd" and current == 0:
            continue  # 0 = no cap, any cap narrows
        if isinstance(value, (int, float)) and isinstance(current, (int, float)) and value > current:
            errors.append(f"{rel}: {where}/overrides/limits/{key} = {value} widens the breed's {current}")
    for key, value in overrides.get("lifecycle", {}).items():
        current = breed.get("lifecycle", {}).get(key)
        if key != "hello" and current and seconds(value) > seconds(current):
            errors.append(f"{rel}: {where}/overrides/lifecycle/{key} = {value} widens the breed's {current}")
    for category, rules in overrides.get("tools", {}).items():
        decisions = [rules] if isinstance(rules, str) else list(rules.values())
        if any(d != "deny" for d in decisions):
            errors.append(f"{rel}: {where}/overrides/tools/{category} may only add deny rules")


def check_formations(schemas, breeds, errors):
    for path in sorted((ROOT / "formations").glob("*.yaml")):
        rel = path.relative_to(ROOT)
        doc = read_yaml(path, errors)
        if doc is None:
            continue
        found = schema_errors(schemas["formation"], doc)
        errors += [f"{rel}: {e}" for e in found]
        if found:
            continue
        if doc["name"] != path.stem:
            errors.append(f"{rel}: name {doc['name']!r} does not match the file name")

        lead = doc["lead"]["breed"]
        participants = [lead] + [m["breed"] for m in doc["members"]]
        for i, name in enumerate(participants):
            if name not in breeds:
                where = "lead" if i == 0 else f"members/{i - 1}"
                errors.append(f"{rel}: {where}/breed names unknown breed {name!r}")
        if any(name not in breeds for name in participants):
            continue
        if len(set(participants[1:])) != len(participants) - 1:
            errors.append(f"{rel}: members list a breed twice; use count instead")

        check_overrides(rel, "lead", breeds[lead], doc["lead"].get("overrides", {}), errors)
        for i, member in enumerate(doc["members"]):
            if member["count"]["min"] > member["count"]["max"]:
                errors.append(f"{rel}: members/{i}/count min > max")
            check_overrides(rel, f"members/{i}", breeds[member["breed"]], member.get("overrides", {}), errors)

        for spawner, targets in doc["spawn_tree"].items():
            if spawner not in participants:
                errors.append(f"{rel}: spawn_tree/{spawner} is not a participant")
                continue
            allowed = breeds[spawner].get("privileges", {}).get("may_spawn", [])
            for target in targets:
                if target not in allowed:
                    errors.append(f"{rel}: spawn_tree/{spawner} adds {target!r}, not in the breed's may_spawn {allowed}")
                if target not in participants:
                    errors.append(f"{rel}: spawn_tree/{spawner} names {target!r}, which is not a member")
        spawnable = {t for targets in doc["spawn_tree"].values() for t in targets}
        for i, member in enumerate(doc["members"]):
            if member["start"] == "on_demand" and member["breed"] not in spawnable:
                errors.append(f"{rel}: members/{i} starts on_demand but nobody may spawn {member['breed']!r}")

        for source, handoff in doc["handoffs"].items():
            for end, label in ((source, source), (handoff["to"], f"{source}/to")):
                if end not in participants:
                    errors.append(f"{rel}: handoffs/{label} names {end!r}, which is not a participant")

        needed = 1 + sum(m["count"]["max"] for m in doc["members"])
        if doc["limits"]["max_agents"] < needed:
            errors.append(f"{rel}: limits/max_agents = {doc['limits']['max_agents']} < lead + all members at max = {needed}")


def main(argv):
    only = {Path(a).resolve() for a in argv}
    schemas = load_schemas()
    errors = []
    breeds = check_breeds(schemas, errors)
    check_formations(schemas, breeds, errors)
    if only:
        errors = [e for e in errors if (ROOT / re.split(r"[: ]", e, maxsplit=1)[0]).resolve() in only]
    for error in errors:
        print(error)
    if not errors and only:
        print("ok: " + ", ".join(sorted(str(p.relative_to(ROOT)) for p in only)))
    elif not errors:
        print(f"ok: {len(breeds)} breeds, {len(list((ROOT / 'formations').glob('*.yaml')))} formations")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
