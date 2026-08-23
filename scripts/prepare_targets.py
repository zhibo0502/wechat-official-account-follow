#!/usr/bin/env python3
"""Normalize a public WeChat account list and emit deterministic batches."""

from __future__ import annotations

import argparse
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
    return {normalize(key): normalize(value) for key, value in payload.items()}


def prepare(names: list[str], aliases: dict[str, str], batch_size: int) -> dict[str, object]:
    targets = [{"configured_name": name, "search_name": aliases.get(name, name)} for name in names]
    batches = [targets[index : index + batch_size] for index in range(0, len(targets), batch_size)]
    return {"target_count": len(targets), "batch_size": batch_size, "batch_count": len(batches), "batches": batches}


def self_test() -> None:
    payload = prepare(["Alpha", "Beta"], {"Beta": "Beta Official"}, 1)
    assert payload["target_count"] == 2
    assert payload["batch_count"] == 2
    assert payload["batches"][1][0]["search_name"] == "Beta Official"  # type: ignore[index]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path, help="UTF-8 .txt or JSON string array")
    parser.add_argument("--aliases", type=Path, help="optional JSON configured-name to actual-name map")
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        self_test()
        print("ok")
        return 0
    if args.input is None:
        parser.error("input is required unless --self-test is used")
    if not 1 <= args.batch_size <= 25:
        parser.error("--batch-size must be between 1 and 25")

    try:
        payload = prepare(load_names(args.input), load_aliases(args.aliases), args.batch_size)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
