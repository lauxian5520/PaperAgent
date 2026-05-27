#!/usr/bin/env python3
"""Scan project files for unresolved placeholders."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

PATTERNS = [
    re.compile(r"REPLACE_ME"),
    re.compile(r"TODO", re.IGNORECASE),
    re.compile(r"TBD", re.IGNORECASE),
    re.compile(r"FIXME", re.IGNORECASE),
    re.compile(r"<[^>\n]{2,80}>"),
]

DEFAULT_EXTENSIONS = {".md", ".tex", ".bib", ".yaml", ".yml", ".json", ".jsonl", ".csv", ".py", ".sh"}
DEFAULT_EXCLUDES = {
    ".git",
    "__pycache__",
    "templates",
    "references/legacy_original_AGENTS.md",
    "paper_config.example.yaml",
}


def should_skip(path: Path, root: Path, excludes: set[str]) -> bool:
    rel = path.relative_to(root).as_posix() if path.is_absolute() else path.as_posix()
    parts = set(path.parts)
    if any(ex in rel for ex in excludes):
        return True
    if parts & {".git", "__pycache__"}:
        return True
    return False


def iter_files(paths: list[Path], root: Path, extensions: set[str], excludes: set[str]):
    for path in paths:
        if not path.exists():
            continue
        if path.is_file():
            if path.suffix in extensions and not should_skip(path, root, excludes):
                yield path
        else:
            for child in path.rglob("*"):
                if child.is_file() and child.suffix in extensions and not should_skip(child, root, excludes):
                    yield child


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=["docs", "paper", "code", "results", "paper_config.yaml", "AGENTS.md"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--exclude", action="append", default=[])
    args = parser.parse_args()

    root = Path(args.root).resolve()
    paths = [Path(p) for p in args.paths]
    excludes = DEFAULT_EXCLUDES | set(args.exclude)

    findings = []
    for file_path in iter_files(paths, root, DEFAULT_EXTENSIONS, excludes):
        try:
            text = file_path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern in PATTERNS:
                if pattern.search(line):
                    findings.append((file_path.as_posix(), lineno, line.strip()))
                    break

    if findings:
        print("Unresolved placeholders found:")
        for file_path, lineno, line in findings[:200]:
            print(f"  {file_path}:{lineno}: {line}")
        if len(findings) > 200:
            print(f"  ... {len(findings) - 200} more findings")
        return 1

    print("No unresolved placeholders found in scanned files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
