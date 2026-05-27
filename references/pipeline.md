# Research Pipeline

Use this file when planning or executing a pipeline stage.

## Stage groups

| Group | Stages |
|---|---|
| A. Research definition | 1. `TOPIC_INIT`; 2. `PROBLEM_DECOMPOSE` |
| B. Literature discovery | 3. `SEARCH_STRATEGY`; 4. `LITERATURE_COLLECT`; 5. `LITERATURE_SCREEN`; 6. `KNOWLEDGE_EXTRACT` |
| C. Knowledge synthesis | 7. `SYNTHESIS`; 8. `HYPOTHESIS_GEN`; 8.5. `THEORETICAL_BOUNDS` |
| D. Experiment design | 9. `EXPERIMENT_DESIGN`; 10. `CODE_GENERATION`; 11. `RESOURCE_PLANNING` |
| E. Experiment execution | 12. `EXPERIMENT_RUN`; 13. `ITERATIVE_REFINE` |
| F. Analysis and decision | 14. `RESULT_ANALYSIS`; 15. `RESEARCH_DECISION` |
| G. Paper writing | 16. `PAPER_OUTLINE`; 17. `PAPER_DRAFT`; 18. `PEER_REVIEW`; 19. `PAPER_REVISION` |
| H. Manuscript | 20. `QUALITY_GATE`; 21. `KNOWLEDGE_ARCHIVE`; 22. `EXPORT_PUBLISH`; 23. `CITATION_VERIFY` |
| I. Review iteration | 24. `THIRD_PARTY_REVIEW`; 25. `REBUTTAL` |

## Standard stage protocol

For every major stage:

1. Read `paper_config.yaml`.
2. Read the relevant `docs/` inputs.
3. Create a plan in `plans/` before execution.
4. Execute only the requested stage or stage group.
5. Save outputs to the appropriate directory.
6. Validate outputs with scripts where possible.
7. Update `PROGRESS.md`.
8. Stop at gates unless the user explicitly approves continuation.

## Gate stages

- Stage 5: literature screening gate.
- Stage 9: experiment design gate.
- Stage 20: final quality gate.

Human approval is required unless the user explicitly provides `--auto-approve` and the current task is low-risk.

## Decision loops

Stage 15 may return:

- `PROCEED`: continue to writing.
- `REFINE`: return to Stage 13 and improve experiments.
- `PIVOT`: return to Stage 8 and revise hypotheses.

Stage 25 may return:

- to Stage 13 for additional experiments;
- to Stage 16 for structural paper revision;
- to Stage 20 for final quality gate.

Never run open-ended loops. Respect `constraints.max_research_loops` and `constraints.max_repair_attempts_per_stage` in `paper_config.yaml`.

## Required outputs by stage

| Stage | Expected output |
|---|---|
| 1-2 | `docs/research_definition.md` |
| 3 | `docs/search_strategy.md` |
| 4 | `results/literature_candidates.jsonl` |
| 5 | `results/literature_shortlist.json` |
| 6 | `docs/knowledge_cards.md` |
| 7-8.5 | `docs/synthesis_and_hypotheses.md` |
| 9 | `docs/final_experiment_design.md` |
| 10 | runnable code under `code/` |
| 11 | `docs/resource_plan.md` |
| 12-13 | JSON/CSV/logs under `results/` |
| 14-15 | `docs/result_analysis_and_decision.md` |
| 16 | `paper/mypaper/outline.md` |
| 17-19 | LaTeX files under `paper/mypaper/sections/` |
| 20 | `docs/quality_gate_report.md` |
| 21 | `docs/reproducibility_archive.md` |
| 22 | compiled paper under `paper/mypaper/` |
| 23 | `docs/citation_verification.md` |
| 24-25 | `docs/external_review_and_rebuttal.md` |

## Stage command surface

The pipeline is primarily executed by Codex reasoning plus repository files, but
the following command provides a stable stage entrypoint for plans and checks:

```bash
python scripts/run_stage.py <stage> --create-plan-only
python scripts/run_stage.py <stage> --run-checks
```

Supported stage keys:

- `readiness`
- `stage-a`
- `literature`
- `experiment-design`
- `model-adapter`
- `pilot`
- `full-experiment`
- `analysis`
- `writing`
- `quality-gate`

`run_stage.py` does not replace human approval or Codex execution. It creates
stage plans, lists expected outputs, and runs lightweight validation commands.
