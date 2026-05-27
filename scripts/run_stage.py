#!/usr/bin/env python3
"""Create stage plans and run lightweight checks for the paper pipeline.

This is not a replacement for Codex reasoning. It provides a stable command
surface that mirrors the pipeline stages in references/pipeline.md.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


STAGES = {
    "readiness": {
        "name": "READINESS",
        "plan": "readiness_check",
        "outputs": ["plans/readiness_check.md"],
        "checks": [["python", "scripts/validate_config.py", "--strict-paths"]],
        "instructions": [
            "Check paper_config.yaml for placeholders and path validity.",
            "Check docs/ and paper/venue_template/ for missing project inputs.",
            "Do not write paper sections or run experiments.",
        ],
    },
    "stage-a": {
        "name": "TOPIC_INIT_AND_PROBLEM_DECOMPOSE",
        "plan": "stage_A_research_definition",
        "outputs": ["docs/research_definition.md"],
        "checks": [["python", "scripts/validate_config.py"]],
        "instructions": [
            "Read paper_config.yaml and docs/*.md.",
            "Write docs/research_definition.md with problem tree and risks.",
            "Update PROGRESS.md after completion.",
        ],
    },
    "literature": {
        "name": "SEARCH_STRATEGY_TO_KNOWLEDGE_EXTRACT",
        "plan": "stage_B_literature",
        "outputs": [
            "docs/search_strategy.md",
            "results/literature_candidates.jsonl",
            "results/literature_shortlist.json",
            "docs/knowledge_cards.md",
        ],
        "checks": [["python", "scripts/validate_config.py"], ["python", "scripts/validate_bib.py"]],
        "instructions": [
            "Use real retrieval sources only.",
            "Save raw candidates before screening.",
            "Preserve DOI, arXiv, OpenAlex, or Semantic Scholar identifiers.",
        ],
    },
    "experiment-design": {
        "name": "EXPERIMENT_DESIGN_CODE_AND_RESOURCE_PLANNING",
        "plan": "stage_D_experiment_design",
        "outputs": ["docs/final_experiment_design.md", "docs/resource_plan.md", "results/hardware_report.json"],
        "checks": [["python", "scripts/validate_config.py"], ["python", "scripts/detect_hardware.py"]],
        "instructions": [
            "Design proposed, baseline, ablation, and downstream task conditions.",
            "Estimate runtime and compute budget.",
            "Stop before full experiments unless explicitly approved.",
        ],
    },
    "model-adapter": {
        "name": "MODEL_ADAPTER_GENERATION",
        "plan": "stage_D_model_adapter",
        "outputs": [
            "docs/model_code_inventory.json",
            "docs/model_adapter_spec.json",
            "docs/model_adapter_report.md",
            "code/adapters/",
        ],
        "checks": [["python", "scripts/inspect_model_code.py", "--code-dir", "code"]],
        "instructions": [
            "Inspect existing model code without importing it.",
            "Create or update docs/model_adapter_spec.json from the template.",
            "Generate an adapter under code/adapters/.",
            "Complete only project-specific loss, metric, and batch conversion logic needed for a smoke test.",
            "Do not run full experiments.",
        ],
    },
    "pilot": {
        "name": "PILOT_EXPERIMENT_RUN",
        "plan": "stage_E_pilot",
        "outputs": ["results/pilot_results.json"],
        "checks": [["python", "scripts/check_results_schema.py"]],
        "instructions": [
            "Run one small condition only.",
            "Print or log TIME_ESTIMATE.",
            "Save pilot result with command, seed, hardware, software, metrics, and runtime.",
        ],
    },
    "full-experiment": {
        "name": "FULL_EXPERIMENT_RUN",
        "plan": "stage_E_full_experiment",
        "outputs": ["results/"],
        "checks": [["python", "scripts/check_results_schema.py"]],
        "instructions": [
            "Run only the approved experiment plan.",
            "Use comparable tuning effort for baselines.",
            "Save partial results on time guard stop.",
            "Stop before writing paper claims.",
        ],
    },
    "analysis": {
        "name": "RESULT_ANALYSIS_AND_RESEARCH_DECISION",
        "plan": "stage_F_analysis",
        "outputs": ["docs/result_analysis_and_decision.md"],
        "checks": [["python", "scripts/check_results_schema.py"]],
        "instructions": [
            "Analyze actual result files only.",
            "Decide PROCEED, REFINE, or PIVOT.",
            "Do not hide failed runs.",
        ],
    },
    "writing": {
        "name": "PAPER_OUTLINE_DRAFT_REVIEW_REVISION",
        "plan": "stage_G_writing",
        "outputs": ["paper/mypaper/outline.md", "paper/mypaper/sections/"],
        "checks": [["python", "scripts/check_claims_against_results.py"], ["python", "scripts/validate_bib.py"]],
        "instructions": [
            "Use only verified citations and actual results.",
            "Keep all source files under paper/mypaper/.",
            "Run evidence gate before final revision.",
        ],
    },
    "quality-gate": {
        "name": "QUALITY_GATE_EXPORT_AND_CITATION_VERIFY",
        "plan": "stage_H_quality_gate",
        "outputs": ["docs/quality_gate_report.md", "docs/citation_verification.md"],
        "checks": [["python", "scripts/evidence_gate.py"], ["python", "scripts/validate_bib.py"]],
        "instructions": [
            "Check claims, citations, figures, tables, and LaTeX build.",
            "Do not move to final package without human approval.",
        ],
    },
}


def run_command(cmd: list[str]) -> int:
    print("+ " + " ".join(cmd))
    return subprocess.call(cmd)


def write_plan(stage_key: str, overwrite: bool = False) -> Path:
    stage = STAGES[stage_key]
    out_dir = Path("plans")
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{stage['plan']}.md"
    if out.exists() and not overwrite:
        return out
    lines = [
        f"# Stage Plan: {stage['name']}",
        "",
        f"- Stage key: `{stage_key}`",
        f"- Created: {datetime.now().isoformat(timespec='seconds')}",
        "- Status: planned",
        "",
        "## Instructions",
        "",
    ]
    lines.extend(f"- {item}" for item in stage["instructions"])
    lines.extend(["", "## Expected outputs", ""])
    lines.extend(f"- `{item}`" for item in stage["outputs"])
    lines.extend(["", "## Validation commands", ""])
    for cmd in stage["checks"]:
        lines.append(f"- `{' '.join(cmd)}`")
    lines.extend(["", "## Notes", "", "- Fill this section during execution.", ""])
    out.write_text("\n".join(lines), encoding="utf-8")
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=sorted(STAGES))
    parser.add_argument("--create-plan-only", action="store_true")
    parser.add_argument("--run-checks", action="store_true")
    parser.add_argument("--overwrite-plan", action="store_true")
    args = parser.parse_args()

    plan = write_plan(args.stage, overwrite=args.overwrite_plan)
    print(f"Plan ready: {plan}")

    stage = STAGES[args.stage]
    print("\nExpected outputs:")
    for output in stage["outputs"]:
        print(f"  - {output}")
    print("\nInstructions:")
    for item in stage["instructions"]:
        print(f"  - {item}")

    if args.create_plan_only:
        return 0
    if args.run_checks:
        status = 0
        for cmd in stage["checks"]:
            code = run_command(cmd)
            if code != 0:
                status = code
        return status
    print("\nNo checks were run. Pass --run-checks to execute this stage's validation commands.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
