#!/usr/bin/env python3
"""Collect candidate papers from OpenAlex.

This script uses only the Python standard library. It requires network access.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def reconstruct_abstract(index):
    if not index:
        return ""
    positions = []
    for word, locs in index.items():
        for loc in locs:
            positions.append((loc, word))
    return " ".join(word for _, word in sorted(positions))


def fetch_page(query: str, page: int, per_page: int, from_year: int | None, mailto: str | None):
    params = {
        "search": query,
        "page": page,
        "per-page": per_page,
        "sort": "relevance_score:desc",
    }
    filters = []
    if from_year:
        filters.append(f"from_publication_date:{from_year}-01-01")
    if filters:
        params["filter"] = ",".join(filters)
    if mailto:
        params["mailto"] = mailto
    url = "https://api.openalex.org/works?" + urlencode(params)
    req = Request(url, headers={"User-Agent": "codex-paper-agent/1.0"})
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def normalize_work(work):
    primary_location = work.get("primary_location") or {}
    source_info = primary_location.get("source") or {}
    authors = []
    for auth in work.get("authorships") or []:
        author = auth.get("author") or {}
        name = author.get("display_name")
        if name:
            authors.append(name)
    ids = work.get("ids") or {}
    doi = work.get("doi") or ids.get("doi")
    arxiv_id = None
    for location in work.get("locations") or []:
        landing = location.get("landing_page_url") or ""
        if "arxiv.org/abs/" in landing:
            arxiv_id = landing.rsplit("/", 1)[-1]
            break
    return {
        "id": work.get("id"),
        "openalex_id": work.get("id"),
        "title": work.get("title") or work.get("display_name"),
        "authors": authors,
        "venue": source_info.get("display_name"),
        "year": work.get("publication_year"),
        "abstract": reconstruct_abstract(work.get("abstract_inverted_index")),
        "doi": doi,
        "arxiv_id": arxiv_id,
        "semantic_scholar_id": None,
        "url": work.get("landing_page_url") or ids.get("doi") or work.get("id"),
        "source": "OpenAlex",
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", required=True)
    parser.add_argument("--from-year", type=int, default=None)
    parser.add_argument("--max-results", type=int, default=50)
    parser.add_argument("--per-page", type=int, default=25)
    parser.add_argument("--mailto", default=None)
    parser.add_argument("--output", default="results/literature_candidates.jsonl")
    args = parser.parse_args()

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    written = 0
    seen = set()
    page = 1
    with out.open("w", encoding="utf-8") as f:
        while written < args.max_results:
            data = fetch_page(args.query, page, args.per_page, args.from_year, args.mailto)
            results = data.get("results") or []
            if not results:
                break
            for work in results:
                item = normalize_work(work)
                key = item.get("openalex_id") or item.get("doi") or item.get("title")
                if not key or key in seen:
                    continue
                seen.add(key)
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
                written += 1
                if written >= args.max_results:
                    break
            page += 1
            time.sleep(0.2)

    print(f"Wrote {written} OpenAlex candidates to {out}")
    return 0 if written else 1


if __name__ == "__main__":
    raise SystemExit(main())
