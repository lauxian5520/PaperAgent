#!/usr/bin/env python3
"""Run an approved experiment matrix with logging and time guards.

The matrix is JSON so the runner has no external dependencies. Commands are run
only from explicit condition entries in the matrix.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def command_to_string(command: list[str]) -> str:
    return " ".join(command)


def run_condition(condition: dict[str, Any], logs_dir: Path, timeout_seconds: int | None, dry_run: bool) -> dict[str, Any]:
    condition_id = str(condition.get("id") or condition.get("condition_id") or "unnamed_condition")
    command = condition.get("command")
    if not isinstance(command, list) or not all(isinstance(part, str) for part in command):
        return {
            "condition_id": condition_id,
            "status": "failed",
            "error": "condition command must be a list of strings",
        }

    record: dict[str, Any] = {
        "condition_id": condition_id,
        "kind": condition.get("kind", "unspecified"),
        "method": condition.get("method"),
        "dataset": condition.get("dataset"),
        "seed": condition.get("seed"),
        "command": command_to_string(command),
        "started_at": datetime.now(timezone.utc).isoformat(),
        "timeout_seconds": timeout_seconds,
    }
    if dry_run:
        record.update({"status": "dry_run", "runtime_seconds": 0.0})
        return record

    logs_dir.mkdir(parents=True, exist_ok=True)
    log_path = logs_dir / f"{condition_id}.log"
    start = time.monotonic()
    try:
        proc = subprocess.run(
            command,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        runtime = time.monotonic() - start
        log_path.write_text(
            "COMMAND: " + command_to_string(command) + "\n\n"
            "STDOUT:\n" + (proc.stdout or "") + "\n\n"
            "STDERR:\n" + (proc.stderr or ""),
            encoding="utf-8",
        )
        record.update({
            "status": "completed" if proc.returncode == 0 else "failed",
            "returncode": proc.returncode,
            "runtime_seconds": runtime,
            "log_path": log_path.as_posix(),
        })
    except subprocess.TimeoutExpired as exc:
        runtime = time.monotonic() - start
        log_path.write_text(
            "COMMAND: " + command_to_string(command) + "\n\n"
            "TIMEOUT\n"
            f"stdout:\n{exc.stdout or ''}\n\nstderr:\n{exc.stderr or ''}",
            encoding="utf-8",
        )
        record.update({
            "status": "partial",
            "error": "timeout",
            "runtime_seconds": runtime,
            "log_path": log_path.as_posix(),
        })
    return record


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--matrix", default="configs/experiment_matrix.example.json")
    parser.add_argument("--output", default="results/experiment_matrix_summary.json")
    parser.add_argument("--pilot-only", action="store_true")
    parser.add_argument("--approve-full", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    matrix_path = Path(args.matrix)
    if not matrix_path.exists():
        print(f"ERROR: missing matrix file: {matrix_path}")
        return 2

    matrix = load_json(matrix_path)
    conditions = matrix.get("conditions")
    if not isinstance(conditions, list):
        print("ERROR: matrix must contain a conditions list")
        return 2

    if not args.pilot_only and not args.approve_full:
        print("ERROR: full matrix execution requires --approve-full. Use --pilot-only for pilot runs.")
        return 2

    budget = matrix.get("budget") or {}
    max_single_run_minutes = budget.get("max_single_run_minutes")
    timeout_seconds = int(float(max_single_run_minutes) * 60) if max_single_run_minutes else None
    selected = []
    for condition in conditions:
        if not isinstance(condition, dict):
            continue
        if condition.get("enabled") is False:
            continue
        if args.pilot_only and condition.get("kind") != "pilot":
            continue
        selected.append(condition)

    if not selected:
        print("ERROR: no enabled conditions selected")
        return 2

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    logs_dir = out.parent / "logs" / out.stem

    records = []
    overall_status = "completed"
    for condition in selected:
        record = run_condition(condition, logs_dir, timeout_seconds, args.dry_run)
        records.append(record)
        if record["status"] in {"failed", "partial"}:
            overall_status = "partial" if record["status"] == "partial" else "failed"
        summary = {
            "experiment_id": matrix.get("experiment_id", matrix_path.stem),
            "status": overall_status,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "matrix": matrix_path.as_posix(),
            "pilot_only": args.pilot_only,
            "dry_run": args.dry_run,
            "conditions": records,
        }
        out.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Wrote matrix run summary to {out}")
    if overall_status == "failed":
        return 1
    if overall_status == "partial":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
