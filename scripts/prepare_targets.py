#!/usr/bin/env python3
"""Normalize a public WeChat account list and emit deterministic batches."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import unicodedata
from pathlib import Path


def normalize(value: str) -> str:
    return " ".join(unicodedata.normalize("NFC", value).strip().split())


def load_names(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8-sig")
    if path.suffix.lower() == ".json":
        payload = json.loads(text)
        if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
            raise ValueError("JSON input must be an array of strings")
        raw_names = payload
    else:
        raw_names = [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]

    names: list[str] = []
    seen: set[str] = set()
    for raw_name in raw_names:
        name = normalize(raw_name)
        if not name or name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names


def load_aliases(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    payload = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(payload, dict) or not all(isinstance(key, str) and isinstance(value, str) for key, value in payload.items()):
        raise ValueError("aliases must be a JSON object of string pairs")

    aliases: dict[str, str] = {}
    for raw_key, raw_value in payload.items():
        key = normalize(raw_key)
        value = normalize(raw_value)
        if not key or not value:
            raise ValueError("alias names must not be empty")
        if key in aliases and aliases[key] != value:
            raise ValueError(f"conflicting aliases after normalization: {key}")
        aliases[key] = value
    return aliases


def prepare(names: list[str], aliases: dict[str, str], batch_size: int) -> dict[str, object]:
    if not 1 <= batch_size <= 25:
        raise ValueError("batch_size must be between 1 and 25")
    if not names:
        raise ValueError("target list must not be empty")
    if any(not key or not value for key, value in aliases.items()):
        raise ValueError("alias names must not be empty")

    unknown_aliases = sorted(set(aliases) - set(names))
    if unknown_aliases:
        raise ValueError(f"aliases not present in target list: {', '.join(unknown_aliases)}")

    targets_by_search_name: dict[str, dict[str, object]] = {}
    for configured_name in names:
        search_name = aliases.get(configured_name, configured_name)
        target = targets_by_search_name.get(search_name)
        if target is None:
            targets_by_search_name[search_name] = {
                "configured_name": configured_name,
                "configured_names": [configured_name],
                "search_name": search_name,
            }
        else:
            configured_names = target["configured_names"]
            assert isinstance(configured_names, list)
            configured_names.append(configured_name)

    targets = list(targets_by_search_name.values())
    batches = [targets[index : index + batch_size] for index in range(0, len(targets), batch_size)]
    payload: dict[str, object] = {
        "requested_count": len(names),
        "target_count": len(targets),
        "alias_mapped_count": sum(aliases.get(name, name) != name for name in names),
        "duplicate_search_count": len(names) - len(targets),
        "batch_size": batch_size,
        "batch_count": len(batches),
        "batches": batches,
    }
    canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    payload["manifest_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return payload


def write_payload(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def self_test() -> None:
    payload = prepare(["Alpha", "Beta", "Beta Legacy"], {"Beta": "Beta Official", "Beta Legacy": "Beta Official"}, 1)
    assert payload["requested_count"] == 3
    assert payload["target_count"] == 2
    assert payload["batch_count"] == 2
    assert payload["duplicate_search_count"] == 1
    assert payload["batches"][1][0]["search_name"] == "Beta Official"  # type: ignore[index]
    assert payload["batches"][1][0]["configured_names"] == ["Beta", "Beta Legacy"]  # type: ignore[index]
    assert payload["manifest_sha256"] == prepare(
        ["Alpha", "Beta", "Beta Legacy"],
        {"Beta": "Beta Official", "Beta Legacy": "Beta Official"},
        1,
    )["manifest_sha256"]

    for invalid_aliases in ({"": "Alpha"}, {"Alpha": ""}, {"Missing": "Alpha"}):
        try:
            prepare(["Alpha"], invalid_aliases, 1)
        except ValueError:
            pass
        else:
            raise AssertionError("invalid aliases must fail")

    try:
        prepare([], {}, 1)
    except ValueError:
        pass
    else:
        raise AssertionError("empty target lists must fail")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="UTF-8 .txt or JSON string array")
    parser.add_argument("--aliases", type=Path, help="optional JSON configured-name to actual-name map")
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--output", type=Path, help="also atomically write the prepared manifest to this path")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        print("ok")
        return 0
    if args.input is None:
        parser.error("input is required unless --self-test is used")
    try:
        payload = prepare(load_names(args.input), load_aliases(args.aliases), args.batch_size)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    if args.output is not None:
        protected_paths = [args.input, args.aliases]
        if any(path is not None and args.output.resolve() == path.resolve() for path in protected_paths):
            print("error: --output must not overwrite an input file", file=sys.stderr)
            return 2
        try:
            write_payload(args.output, payload)
        except OSError as error:
            print(f"error: {error}", file=sys.stderr)
            return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
