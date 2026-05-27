#!/usr/bin/env python3
"""Collect candidate papers from Semantic Scholar Graph API."""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


FIELDS = ",".join([
    "paperId",
    "title",
    "abstract",
    "year",
    "venue",
    "url",
    "authors",
    "externalIds",
])


def fetch(query: str, offset: int, limit: int, api_key: str | None) -> dict[str, object]:
    params = urllib.parse.urlencode({
        "query": query,
        "offset": offset,
        "limit": limit,
        "fields": FIELDS,
    })
    url = "https://api.semanticscholar.org/graph/v1/paper/search?" + params
    headers = {"User-Agent": "codex-paper-agent/1.0"}
    if api_key:
        headers["x-api-key"] = api_key
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_paper(paper: dict[str, object]) -> dict[str, object]:
    external = paper.get("externalIds") or {}
    if not isinstance(external, dict):
        external = {}
    authors = []
    for author in paper.get("authors") or []:
        if isinstance(author, dict) and author.get("name"):
            authors.append(author["name"])
    arxiv_id = external.get("ArXiv")
    doi = external.get("DOI")
    return {
        "id": paper.get("paperId"),
        "openalex_id": None,
        "title": paper.get("title"),
        "authors": authors,
        "venue": paper.get("venue"),
        "year": paper.get("year"),
        "abstract": paper.get("abstract") or "",
        "doi": doi,
        "arxiv_id": arxiv_id,
        "semantic_scholar_id": paper.get("paperId"),
        "url": paper.get("url"),
        "source": "Semantic Scholar",
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--from-year", type=int, default=None)
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument("--page-size", type=int, default=25)
    parser.add_argument("--api-key", default=os.environ.get("SEMANTIC_SCHOLAR_API_KEY"))
    parser.add_argument("--output", default="results/literature_candidates_semantic_scholar.jsonl")
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    written = 0
    offset = 0
    seen: set[str] = set()
    with out.open("w", encoding="utf-8") as f:
        while written < args.max_results:
            data = fetch(args.query, offset, min(args.page_size, args.max_results - written), args.api_key)
            rows = data.get("data") or []
            if not isinstance(rows, list) or not rows:
                break
            for paper in rows:
                if not isinstance(paper, dict):
                    continue
                row = normalize_paper(paper)
                if args.from_year and row.get("year") and int(row["year"]) < args.from_year:
                    continue
                key = str(row.get("semantic_scholar_id") or row.get("doi") or row.get("title"))
                if key in seen:
                    continue
                seen.add(key)
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
                if written >= args.max_results:
                    break
            offset += len(rows)
            time.sleep(1.2 if args.api_key else 3.5)

    print(f"Wrote {written} Semantic Scholar candidates to {out}")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
