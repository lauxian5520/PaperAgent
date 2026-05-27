#!/usr/bin/env python3
"""Check that result files are parseable and do not contain obvious invalid values."""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path
from typing import Any

PLACEHOLDERS = ["REPLACE_ME", "TODO", "TBD", "fake", "fabricated"]


def iter_values(obj: Any, path: str = "$"):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from iter_values(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_values(v, f"{path}[{i}]")
    else:
        yield path, obj


def check_json_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        if path.suffix == ".jsonl":
            rows = []
            for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not line.strip():
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    errors.append(f"{path}:{lineno}: invalid JSONL: {exc}")
            data: Any = rows
        else:
            data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [f"{path}: cannot parse JSON: {exc}"]

    for value_path, value in iter_values(data):
        if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
            errors.append(f"{path}:{value_path}: NaN or Inf")
        if isinstance(value, str):
            upper = value.upper()
            if any(tok in upper for tok in PLACEHOLDERS):
                errors.append(f"{path}:{value_path}: placeholder or suspicious text: {value}")
    return errors


def check_csv_file(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                errors.append(f"{path}: missing header")
            for idx, row in enumerate(reader, 2):
                for key, value in row.items():
                    if value and any(tok in value.upper() for tok in PLACEHOLDERS):
                        errors.append(f"{path}:{idx}:{key}: placeholder or suspicious text: {value}")
    except Exception as exc:
        errors.append(f"{path}: cannot parse CSV: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results")
    args = parser.parse_args()

    results_dir = Path(args.results_dir)
    if not results_dir.exists():
        print(f"WARNING: results directory does not exist: {results_dir}")
        return 0

    files = list(results_dir.rglob("*.json")) + list(results_dir.rglob("*.jsonl")) + list(results_dir.rglob("*.csv"))
    if not files:
        print(f"WARNING: no JSON/JSONL/CSV result files found in {results_dir}")
        return 0

    errors: list[str] = []
    for path in files:
        if path.suffix in {".json", ".jsonl"}:
            errors.extend(check_json_file(path))
        elif path.suffix == ".csv":
            errors.extend(check_csv_file(path))

    if errors:
        print("Result validation failed:")
        for error in errors[:200]:
            print(f"  - {error}")
        if len(errors) > 200:
            print(f"  ... {len(errors) - 200} more errors")
        return 1

    print(f"Checked {len(files)} result files; no obvious schema/value errors found.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
