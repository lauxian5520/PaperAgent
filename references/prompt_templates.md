# Codex Prompt Templates

Use these templates when instructing Codex. Replace bracketed parts with concrete details.

## Readiness check

```text
Follow AGENTS.md strictly.

Read paper_config.yaml, PROGRESS.md, docs/, and only the necessary references.
Validate whether this repository is ready for the paper pipeline.
Do not write the paper yet.
Check missing files, unresolved placeholders, path validity, unclear constraints, and missing LaTeX template files.
Create plans/readiness_check.md and update PROGRESS.md.
Stop after the readiness report.
```

## Stage A

```text
Follow AGENTS.md strictly.

Run stages 1-2 only: TOPIC_INIT and PROBLEM_DECOMPOSE.
Read paper_config.yaml and docs/*.md.
Create plans/stage_A_research_definition.md.
Write outputs to docs/research_definition.md.
Update PROGRESS.md.
Stop after completing stage 2.
```

## Literature retrieval

```text
Follow AGENTS.md strictly.

Run stages 3-6 only.
Use real literature retrieval sources where available.
Do not invent citations.
Save retrieved metadata to results/literature_candidates.jsonl.
Save screened papers to results/literature_shortlist.json.
Save knowledge cards to docs/knowledge_cards.md.
Update PROGRESS.md.
Stop before synthesis.
```

## Experiment design and pilot

```text
Follow AGENTS.md strictly.

Run experiment design and pilot only.
Do not run the full experiment.
Create a small pilot that estimates runtime and validates metrics.
Write pilot outputs to results/pilot_results.json.
Update PROGRESS.md.
Stop and summarize whether full execution is feasible.
```

## Full experiment run

```text
Follow AGENTS.md strictly.

Run the approved experiment plan only.
Use deterministic seeds and log all commands.
Implement time_guard and save partial results if the budget is reached.
Save outputs to results/ in JSON/CSV plus logs.
Run scripts/check_results_schema.py after completion.
Update PROGRESS.md.
Stop before writing paper claims.
```

## Paper draft section

```text
Follow AGENTS.md strictly.

Draft only [SECTION_NAME].
Use only verified citations and actual experiment outputs.
Do not invent results, datasets, or citations.
Write to paper/mypaper/sections/[section_file].tex.
Update PROGRESS.md.
Stop after this section.
```

## Evidence gate

```text
Follow AGENTS.md strictly.

Run the evidence gate for the current paper draft.
Compare paper claims against results, logs, code configuration, figures, and BibTeX.
Run relevant scripts.
Write docs/evidence_gate_report.md.
Mark unsupported claims clearly.
Update PROGRESS.md.
Stop after the report.
```
