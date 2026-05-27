#!/usr/bin/env python3
"""Approximate word counts for LaTeX files."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

COMMAND_RE = re.compile(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{[^}]*\})?")
MATH_RE = re.compile(r"\$.*?\$|\\\[.*?\\\]|\\\(.*?\\\)", re.DOTALL)
WORD_RE = re.compile(r"[A-Za-z][A-Za-z0-9\-']+")


def clean_tex(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = MATH_RE.sub(" ", text)
    text = COMMAND_RE.sub(" ", text)
    text = text.replace("~", " ")
    return text


def count_words(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="ignore")
    return len(WORD_RE.findall(clean_tex(text)))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-dir", default="paper/mypaper")
    args = parser.parse_args()

    paper_dir = Path(args.paper_dir)
    files = sorted(paper_dir.rglob("*.tex")) if paper_dir.exists() else []
    if not files:
        print(f"WARNING: no .tex files found in {paper_dir}")
        return 0

    total = 0
    for path in files:
        n = count_words(path)
        total += n
        print(f"{path}: {n} words")
    print(f"TOTAL: {total} words")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
