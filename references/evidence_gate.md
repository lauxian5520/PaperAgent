# Evidence Gate

Use this file before peer review, revision, final quality gate, and export.

## Goal

Ensure that the paper's claims, numbers, citations, experiments, baselines, ablations, and statistical statements are supported by actual evidence.

## Evidence sources

Acceptable evidence includes:

- `results/*.json`
- `results/*.jsonl`
- `results/*.csv`
- experiment logs under `results/`
- code configurations under `code/`
- generated figure data
- verified literature metadata
- BibTeX entries with identifiers

## Required checks

1. Extract quantitative claims from paper files.
2. Verify that each number appears in results, logs, or figure data.
3. Verify that each dataset or benchmark named in the paper appears in experiment configuration or logs.
4. Verify that each baseline named in the paper appears in code or results.
5. Verify that each ablation claim has corresponding ablation data.
6. Verify that every statistical test claimed in the paper appears in code or analysis scripts.
7. Verify that every citation key used in LaTeX appears in a `.bib` file.
8. Verify that every BibTeX entry has a DOI, arXiv/eprint, URL, OpenAlex ID, or similar identifier.

## Critical fabrication examples

Mark as `CRITICAL_FABRICATION` and return to experiment or writing stage if:

- The paper says 10 datasets but logs show only 2.
- The paper reports a t-test but no code implements one.
- The paper reports an ablation that was never run.
- The paper claims SOTA but no strong baseline comparison exists.
- The paper cites a nonexistent paper.
- The paper reports a metric not present in results.

## Useful commands

```bash
python scripts/evidence_gate.py
python scripts/check_claims_against_results.py
python scripts/validate_bib.py
python scripts/check_results_schema.py
```

The numeric evidence checker is conservative: it can find suspicious unmatched numbers, but it cannot prove scientific correctness. Human review remains required.

`scripts/evidence_gate.py` combines several conservative checks:

- paper numbers that do not appear in result files;
- citation keys missing from BibTeX;
- BibTeX entries missing verifiable identifiers;
- candidate dataset or method terms not found in results, code, configs, or BibTeX.

It writes both `docs/evidence_gate_report.md` and
`results/evidence_gate_report.json`.

## Evidence report format

Write reports with this structure:

```md
# Evidence Gate Report

## Verdict
PASS / PASS_WITH_WARNINGS / FAIL

## Checked files
- ...

## Supported claims
- Claim: ...
  Evidence: ...

## Unsupported or risky claims
- Claim: ...
  Severity: warning / major / critical
  Required action: ...

## Citation issues
- ...

## Experiment consistency issues
- ...

## Required next actions
- ...
```
