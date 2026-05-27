#!/usr/bin/env python3
"""Validate paper_config.yaml without external dependencies.

This script intentionally performs conservative checks. It does not fully parse all
YAML features, but it catches common configuration problems that cause Codex to
write unresolved placeholders into the paper.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

PLACEHOLDER_PATTERNS = [
    re.compile(r"REPLACE_ME"),
    re.compile(r"TODO", re.IGNORECASE),
    re.compile(r"TBD", re.IGNORECASE),
    re.compile(r"<[^>]+>"),
]

REQUIRED_KEYS = [
    "project_name",
    "paper.title",
    "paper.target_conference",
    "paper.deadline",
    "paper.page_limit",
    "research.topic_short_name",
    "research.topic_description",
    "paths.latex_template",
    "paths.paper_dir",
    "paths.results_dir",
    "input_documents.paper_idea",
    "input_documents.experiment_plan",
    "input_documents.literature_questions",
    "constraints.min_references",
    "constraints.reference_year_after",
    "constraints.max_research_loops",
]

PATH_KEYS = [
    "paths.latex_template",
    "paths.paper_dir",
    "paths.results_dir",
    "paths.code_dir",
    "paths.data_dir",
    "input_documents.paper_idea",
    "input_documents.experiment_plan",
    "input_documents.literature_questions",
]


def parse_simple_yaml(text: str) -> dict[str, Any]:
    root: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(-1, root)]
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.lstrip().startswith("-"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        if ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value == "":
            child: dict[str, Any] = {}
            parent[key] = child
            stack.append((indent, child))
        else:
            parent[key] = value
    return root


def get_nested(data: dict[str, Any], dotted: str) -> Any:
    cur: Any = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def has_placeholder(value: str) -> bool:
    return any(p.search(value) for p in PLACEHOLDER_PATTERNS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="paper_config.yaml")
    parser.add_argument("--strict-paths", action="store_true", help="Fail if referenced paths do not exist.")
    args = parser.parse_args()

    path = Path(args.config)
    errors: list[str] = []
    warnings: list[str] = []

    if not path.exists():
        print(f"ERROR: missing config file: {path}")
        return 2

    text = path.read_text(encoding="utf-8")
    data = parse_simple_yaml(text)

    for key in REQUIRED_KEYS:
        value = get_nested(data, key)
        if value is None or str(value).strip() == "":
            errors.append(f"Missing required key: {key}")
        elif has_placeholder(str(value)):
            errors.append(f"Unresolved placeholder in {key}: {value}")

    for lineno, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if has_placeholder(line):
            warnings.append(f"Line {lineno}: placeholder-like text remains: {stripped}")

    if args.strict_paths:
        base = path.parent
        for key in PATH_KEYS:
            value = get_nested(data, key)
            if value and not has_placeholder(str(value)):
                p = Path(str(value))
                if not p.is_absolute():
                    p = base / p
                if not p.exists():
                    errors.append(f"Configured path does not exist for {key}: {value}")

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if errors:
        print("Configuration validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Configuration looks usable: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
