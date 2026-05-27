#!/usr/bin/env python3
"""Validate BibTeX entries for basic completeness and identifiers."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ENTRY_RE = re.compile(r"@(?P<type>\w+)\s*\{\s*(?P<key>[^,]+),(?P<body>.*?)\n\s*\}", re.DOTALL)
FIELD_RE = re.compile(r"(?P<field>\w+)\s*=\s*[\{\"](?P<value>.*?)[\}\"]\s*,?\s*$", re.MULTILINE)

IDENTIFIER_FIELDS = {"doi", "url", "eprint", "arxivid", "openalex", "semanticscholar", "dblp"}
REQUIRED_FIELDS = {"title", "year"}


def parse_entries(text: str):
    for match in ENTRY_RE.finditer(text):
        fields = {}
        for field in FIELD_RE.finditer(match.group("body")):
            fields[field.group("field").lower()] = field.group("value").strip()
        yield match.group("key").strip(), match.group("type").lower(), fields


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bibfiles", nargs="*")
    args = parser.parse_args()

    bibfiles = [Path(p) for p in args.bibfiles]
    if not bibfiles:
        bibfiles = list(Path("paper").rglob("*.bib"))

    if not bibfiles:
        print("WARNING: no .bib files found.")
        return 0

    errors: list[str] = []
    seen: set[str] = set()
    entry_count = 0

    for path in bibfiles:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for key, entry_type, fields in parse_entries(text):
            entry_count += 1
            if key in seen:
                errors.append(f"Duplicate citation key: {key}")
            seen.add(key)
            missing = [field for field in REQUIRED_FIELDS if field not in fields]
            if missing:
                errors.append(f"{path}:{key}: missing required fields: {', '.join(missing)}")
            if not any(field in fields and fields[field] for field in IDENTIFIER_FIELDS):
                errors.append(f"{path}:{key}: missing verifiable identifier field: doi/url/eprint/openalex/semanticscholar/dblp")
            if "author" not in fields and "editor" not in fields:
                errors.append(f"{path}:{key}: missing author or editor")

    if entry_count == 0:
        print("WARNING: no BibTeX entries found.")
        return 0

    if errors:
        print("BibTeX validation failed:")
        for error in errors[:200]:
            print(f"  - {error}")
        if len(errors) > 200:
            print(f"  ... {len(errors) - 200} more errors")
        return 1

    print(f"Checked {entry_count} BibTeX entries; all passed basic validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
