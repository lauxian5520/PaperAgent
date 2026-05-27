#!/usr/bin/env python3
"""Collect candidate papers from arXiv Atom API using only stdlib."""
from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ATOM = "{http://www.w3.org/2005/Atom}"
ARXIV = "{http://arxiv.org/schemas/atom}"


def text(node: ET.Element | None) -> str:
    return "" if node is None or node.text is None else " ".join(node.text.split())


def normalize_entry(entry: ET.Element) -> dict[str, object]:
    entry_id = text(entry.find(f"{ATOM}id"))
    arxiv_id = entry_id.rsplit("/", 1)[-1] if entry_id else None
    authors = [text(author.find(f"{ATOM}name")) for author in entry.findall(f"{ATOM}author")]
    categories = [cat.attrib.get("term", "") for cat in entry.findall(f"{ATOM}category")]
    doi_node = entry.find(f"{ARXIV}doi")
    published = text(entry.find(f"{ATOM}published"))
    year = None
    match = re.match(r"(\d{4})", published)
    if match:
        year = int(match.group(1))
    return {
        "id": entry_id,
        "openalex_id": None,
        "title": text(entry.find(f"{ATOM}title")),
        "authors": [author for author in authors if author],
        "venue": "arXiv",
        "year": year,
        "abstract": text(entry.find(f"{ATOM}summary")),
        "doi": text(doi_node) or None,
        "arxiv_id": arxiv_id,
        "semantic_scholar_id": None,
        "url": entry_id,
        "source": "arXiv",
        "categories": categories,
        "published": published,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def fetch(query: str, start: int, max_results: int) -> list[dict[str, object]]:
    params = urllib.parse.urlencode({
        "search_query": f"all:{query}",
        "start": start,
        "max_results": max_results,
        "sortBy": "relevance",
        "sortOrder": "descending",
    })
    url = "https://export.arxiv.org/api/query?" + params
    req = urllib.request.Request(url, headers={"User-Agent": "codex-paper-agent/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        root = ET.fromstring(resp.read())
    return [normalize_entry(entry) for entry in root.findall(f"{ATOM}entry")]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--from-year", type=int, default=None)
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument("--page-size", type=int, default=25)
    parser.add_argument("--output", default="results/literature_candidates_arxiv.jsonl")
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    seen: set[str] = set()
    start = 0
    with out.open("w", encoding="utf-8") as f:
        while written < args.max_results:
            rows = fetch(args.query, start, min(args.page_size, args.max_results - written))
            if not rows:
                break
            for row in rows:
                if args.from_year and row.get("year") and int(row["year"]) < args.from_year:
                    continue
                key = str(row.get("arxiv_id") or row.get("url") or row.get("title"))
                if key in seen:
                    continue
                seen.add(key)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
                if written >= args.max_results:
                    break
            start += len(rows)
            time.sleep(3.0)

    print(f"Wrote {written} arXiv candidates to {out}")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
