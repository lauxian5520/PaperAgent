# Literature Rules

Use this file for search strategy, retrieval, screening, knowledge extraction, BibTeX, and citation verification.

## Core rule

Candidate papers must come from real sources. Do not ask the LLM to generate paper metadata from memory.

Allowed retrieval sources include:

- OpenAlex
- Semantic Scholar
- arXiv
- ACL Anthology
- DBLP
- official conference proceedings
- publisher pages
- project pages linked from papers

Available helper scripts:

```bash
python scripts/literature_collect_openalex.py --query "your topic" --from-year 2020 --max-results 50 --output results/literature_candidates_openalex.jsonl
python scripts/literature_collect_semantic_scholar.py --query "your topic" --from-year 2020 --max-results 50 --output results/literature_candidates_semantic_scholar.jsonl
python scripts/literature_collect_arxiv.py --query "your topic" --from-year 2020 --max-results 50 --output results/literature_candidates_arxiv.jsonl
```

These scripts only retrieve raw candidates. Screening, deduplication, relevance
judgment, and BibTeX generation still require review and verification.

## Required metadata

Each paper should include as many of these fields as possible:

```json
{
  "id": "source-specific-id",
  "title": "...",
  "authors": ["..."],
  "venue": "...",
  "year": 2024,
  "abstract": "...",
  "doi": "...",
  "arxiv_id": "...",
  "openalex_id": "...",
  "semantic_scholar_id": "...",
  "url": "...",
  "source": "OpenAlex",
  "collected_at": "..."
}
```

A paper should have at least one verifiable identifier: DOI, arXiv ID, OpenAlex ID, Semantic Scholar ID, DBLP URL, official proceedings URL, or publisher URL.

## Retrieval process

1. Create a search strategy with at least 8 diverse queries.
2. Retrieve candidate papers from real sources.
3. Save raw candidates to `results/literature_candidates.jsonl`.
4. Screen for relevance and quality.
5. Save shortlisted papers to `results/literature_shortlist.json`.
6. Extract knowledge cards to `docs/knowledge_cards.md`.
7. Generate or update BibTeX only from verified metadata.

## Screening criteria

Screen by:

- topical relevance;
- methodological relevance;
- recency relative to `constraints.reference_year_after`;
- venue or source quality;
- availability of reproducibility details;
- direct relationship to the paper's claims.

Reject papers that are high quality but off topic.

## Citation discipline

- Preserve original citation keys once created.
- Do not cite a paper for a claim it does not support.
- Do not include unrelated references just to increase count.
- Do not use unavailable or unverifiable papers.
- If a citation is only weakly related, move it to background or remove it.

## BibTeX rules

Each BibTeX entry should include:

- `title`
- `author`
- `year`
- `url` or `doi` or `eprint`
- venue field where available: `booktitle`, `journal`, or `archivePrefix`

Run:

```bash
python scripts/validate_bib.py
```

before final export.

## Forbidden literature behavior

- Do not write "Smith et al. (2024)" unless the source was actually retrieved or provided.
- Do not fabricate DOI, arXiv ID, conference name, page number, or title.
- Do not create a candidate list from LLM memory.
- Do not use citation keys that have no BibTeX entries.
