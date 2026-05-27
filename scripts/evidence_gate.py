#!/usr/bin/env python3
"""Run a conservative evidence gate over paper, results, code, and BibTeX."""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

NUMBER_RE = re.compile(r"(?<![A-Za-z])[-+]?\d+(?:\.\d+)?(?:e[-+]?\d+)?\s*%?", re.IGNORECASE)
CITE_RE = re.compile(r"\\cite\w*\{([^}]+)\}")
DATASET_HINT_RE = re.compile(r"\b([A-Z][A-Za-z0-9_.-]*(?:-[A-Za-z0-9_.]+)*)\b")
COMMAND_RE = re.compile(r"\\[a-zA-Z]+(?:\[[^\]]*\])?(?:\{[^}]*\})?")
EXCLUDE_NUMBERS = set(str(y) for y in range(1900, 2101))
COMMON_WORDS = {
    "Abstract", "Introduction", "Related", "Work", "Method", "Experiments",
    "Results", "Discussion", "Limitations", "Conclusion", "Table", "Figure",
    "Section", "Appendix", "Theorem", "Lemma", "Algorithm",
}


def read_texts(base: Path, suffixes: set[str]) -> dict[str, str]:
    texts = {}
    if not base.exists():
        return texts
    files = [base] if base.is_file() else [p for p in base.rglob("*") if p.is_file() and p.suffix in suffixes]
    for path in files:
        try:
            texts[path.as_posix()] = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
    return texts


def strip_tex(text: str) -> str:
    text = re.sub(r"%.*", "", text)
    return COMMAND_RE.sub(" ", text)


def normalize_number(num: str) -> str:
    return num.strip().replace(" ", "")


def collect_numbers(texts: dict[str, str], tex: bool = False) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for path, text in texts.items():
        if tex:
            text = strip_tex(text)
        for raw in NUMBER_RE.findall(text):
            num = normalize_number(raw)
            bare = num.rstrip("%")
            if bare in EXCLUDE_NUMBERS:
                continue
            found.setdefault(num, []).append(path)
    return found


def collect_cites(texts: dict[str, str]) -> dict[str, list[str]]:
    cites: dict[str, list[str]] = {}
    for path, text in texts.items():
        for group in CITE_RE.findall(text):
            for key in [part.strip() for part in group.split(",") if part.strip()]:
                cites.setdefault(key, []).append(path)
    return cites


def collect_bib_keys(texts: dict[str, str]) -> set[str]:
    keys = set()
    for text in texts.values():
        for match in re.finditer(r"@\w+\s*\{\s*([^,]+),", text):
            keys.add(match.group(1).strip())
    return keys


def collect_bib_identifier_issues(texts: dict[str, str]) -> list[str]:
    issues = []
    for path, text in texts.items():
        for match in re.finditer(r"@\w+\s*\{\s*([^,]+),(.*?)\n\s*\}", text, re.DOTALL):
            key = match.group(1).strip()
            body = match.group(2).lower()
            if not any(field in body for field in ["doi", "url", "eprint", "arxiv", "openalex", "semanticscholar", "dblp"]):
                issues.append(f"{path}:{key}: missing verifiable identifier")
    return issues


def collect_candidate_terms(texts: dict[str, str]) -> dict[str, list[str]]:
    terms: dict[str, list[str]] = {}
    for path, text in texts.items():
        plain = strip_tex(text)
        for match in DATASET_HINT_RE.finditer(plain):
            term = match.group(1)
            if len(term) < 4 or term in COMMON_WORDS:
                continue
            if term.isupper() or any(ch.isdigit() for ch in term) or "-" in term:
                terms.setdefault(term, []).append(path)
    return terms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--paper-dir", default="paper/mypaper")
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--code-dir", default="code")
    parser.add_argument("--bib-root", default="paper")
    parser.add_argument("--output", default="docs/evidence_gate_report.md")
    parser.add_argument("--json-output", default="results/evidence_gate_report.json")
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()

    paper_texts = read_texts(Path(args.paper_dir), {".tex", ".md"})
    result_texts = read_texts(Path(args.results_dir), {".json", ".jsonl", ".csv", ".log", ".txt", ".md"})
    code_texts = read_texts(Path(args.code_dir), {".py", ".yaml", ".yml", ".json", ".toml", ".ini"})
    bib_texts = read_texts(Path(args.bib_root), {".bib"})
    result_texts.pop(Path(args.json_output).as_posix(), None)
    paper_texts.pop(Path(args.output).as_posix(), None)

    paper_numbers = collect_numbers(paper_texts, tex=True)
    evidence_numbers = collect_numbers(result_texts, tex=False)
    unmatched_numbers = {num: paths for num, paths in paper_numbers.items() if num not in evidence_numbers}

    cites = collect_cites(paper_texts)
    bib_keys = collect_bib_keys(bib_texts)
    missing_cites = {key: paths for key, paths in cites.items() if key not in bib_keys}
    bib_identifier_issues = collect_bib_identifier_issues(bib_texts)

    paper_terms = collect_candidate_terms(paper_texts)
    evidence_blob = "\n".join(result_texts.values()) + "\n" + "\n".join(code_texts.values())
    unsupported_terms = {
        term: paths for term, paths in paper_terms.items()
        if term not in evidence_blob and term not in " ".join(bib_texts.values())
    }

    critical = bool(missing_cites)
    major = bool(unmatched_numbers or bib_identifier_issues or unsupported_terms)
    verdict = "PASS"
    if critical:
        verdict = "FAIL"
    elif major:
        verdict = "PASS_WITH_WARNINGS"

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "paper_files_checked": sorted(paper_texts),
        "result_files_checked": sorted(result_texts),
        "code_files_checked": sorted(code_texts),
        "bib_files_checked": sorted(bib_texts),
        "unmatched_numbers": unmatched_numbers,
        "missing_citations": missing_cites,
        "bib_identifier_issues": bib_identifier_issues,
        "unsupported_candidate_terms": unsupported_terms,
        "note": "This is a conservative guardrail. It flags suspicious evidence gaps but cannot prove scientific correctness.",
    }

    json_out = Path(args.json_output)
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Evidence Gate Report",
        "",
        "## Verdict",
        "",
        verdict,
        "",
        "## Checked files",
        "",
        f"- Paper files: {len(paper_texts)}",
        f"- Result files: {len(result_texts)}",
        f"- Code/config files: {len(code_texts)}",
        f"- BibTeX files: {len(bib_texts)}",
        "",
        "## Unsupported or risky claims",
        "",
    ]
    if unmatched_numbers:
        lines.append("### Numeric claims not found in results")
        for num, paths in list(unmatched_numbers.items())[:50]:
            lines.append(f"- `{num}` in {', '.join(sorted(set(paths))[:3])}")
        lines.append("")
    if unsupported_terms:
        lines.append("### Candidate dataset/method terms not found in evidence")
        for term, paths in list(unsupported_terms.items())[:50]:
            lines.append(f"- `{term}` in {', '.join(sorted(set(paths))[:3])}")
        lines.append("")
    if not unmatched_numbers and not unsupported_terms:
        lines.append("- No suspicious numeric or candidate term gaps were found.")
        lines.append("")

    lines.extend(["## Citation issues", ""])
    if missing_cites:
        for key, paths in missing_cites.items():
            lines.append(f"- Missing BibTeX entry for `{key}` used in {', '.join(sorted(set(paths))[:3])}")
    if bib_identifier_issues:
        for issue in bib_identifier_issues[:50]:
            lines.append(f"- {issue}")
    if not missing_cites and not bib_identifier_issues:
        lines.append("- No citation key or BibTeX identifier issues were found.")
    lines.extend([
        "",
        "## Required next actions",
        "",
        "- Review every warning manually before final submission.",
        "- Return to experiments if a result, baseline, ablation, or statistical claim lacks evidence.",
        f"- Machine-readable report: `{json_out.as_posix()}`",
        "",
    ])

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{verdict}: wrote evidence gate report to {out} and {json_out}")
    if args.fail_on_critical and critical:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
