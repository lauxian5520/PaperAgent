#!/usr/bin/env python3
"""Install this Codex paper agent template into another repository.

Usage:
  python scripts/bootstrap_agent.py --target /path/to/repo
  python scripts/bootstrap_agent.py --target /path/to/repo --force

By default, existing files are not overwritten.
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

COPY_ITEMS = [
    "AGENTS.md",
    "paper_config.yaml",
    "paper_config.example.yaml",
    "references",
    "scripts",
    "templates",
    "docs",
    "PROGRESS.md",
    ".gitignore",
]
OPTIONAL_DIRS = [
    "code",
    "data",
    "results",
    "plans",
    "paper/mypaper/sections",
    "paper/mypaper/figures",
    "paper/venue_template",
]


def copy_item(src: Path, dst: Path, force: bool) -> str:
    if dst.exists():
        if not force:
            return f"skip existing: {dst}"
        if dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    if src.is_dir():
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    return f"copied: {dst}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, help="Target repository root.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing files.")
    args = parser.parse_args()

    source_root = Path(__file__).resolve().parents[1]
    target = Path(args.target).resolve()
    target.mkdir(parents=True, exist_ok=True)

    messages = []
    for rel in COPY_ITEMS:
        src = source_root / rel
        if src.exists():
            messages.append(copy_item(src, target / rel, args.force))

    for rel in OPTIONAL_DIRS:
        path = target / rel
        path.mkdir(parents=True, exist_ok=True)
        messages.append(f"ensured dir: {path}")

    print("Codex paper agent bootstrap complete.")
    for msg in messages:
        print("- " + msg)
    print("\nNext steps:")
    print("1. Edit paper_config.yaml and replace every REPLACE_ME.")
    print("2. Add real project notes under docs/.")
    print("3. Run: python scripts/validate_config.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
