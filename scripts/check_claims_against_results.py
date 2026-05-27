#!/usr/bin/env python3
"""Conservative numeric claim audit.

The script extracts numbers from paper text and checks whether each number also
appears in result/log/csv/json evidence. This is not a proof of correctness; it
is a guardrail that catches many unsupported quantitative claims.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?\s*%?", re.IGNORECASE)
COMMAND_RE = re.compile(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{[^}]*\})?")

EXCLUDE_NUMBERS = set(str(y) for y in range(1900, 2101))


def normalize(num: str) -> str:
    return num.strip().replace(" ", "")


def strip_tex(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    text = COMMAND_RE.sub(" ", text)
    return text


def collect_numbers_from_files(paths: list[Path], suffixes: set[str]) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for base in paths:
        if not base.exists():
            continue
        files = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file() and p.suffix in suffixes]
        for path in files:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            if path.suffix == ".tex":
                text = strip_tex(text)
            for raw in NUMBER_RE.findall(text):
                num = normalize(raw)
                bare = num.rstrip("%")
                if bare in EXCLUDE_NUMBERS:
                    continue
                found.setdefault(num, []).append(path.as_posix())
    return found


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-dir", default="paper/mypaper")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--output", default="results/claim_numeric_audit.json")
    parser.add_argument("--fail-on-unmatched", action="store_true")
    args = parser.parse_args()

    paper_numbers = collect_numbers_from_files([Path(args.paper_dir)], {".tex", ".md"})
    evidence_numbers = collect_numbers_from_files([Path(args.results_dir)], {".json", ".jsonl", ".csv", ".log", ".txt", ".md"})

    unmatched = {num: srcs for num, srcs in paper_numbers.items() if num not in evidence_numbers}
    report = {
        "paper_dir": args.paper_dir,
        "results_dir": args.results_dir,
        "paper_number_count": len(paper_numbers),
        "evidence_number_count": len(evidence_numbers),
        "unmatched_numbers": unmatched,
        "note": "This is a conservative numeric audit, not a semantic proof of evidence consistency."
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    if unmatched:
        print(f"WARNING: {len(unmatched)} numeric claims were not found in evidence. Report: {out}")
        for num, srcs in list(unmatched.items())[:50]:
            print(f"  - {num}: {', '.join(sorted(set(srcs))[:3])}")
        if args.fail_on_unmatched:
            return 1
    else:
        print(f"All paper numbers appeared somewhere in evidence. Report: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
