#!/usr/bin/env python3
"""Detect local experiment hardware and Python software versions.

The output is intentionally plain JSON so it can be attached to experiment
records under results/.
"""
from __future__ import annotations

import argparse
import json
import platform
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run(cmd: list[str], timeout: int = 15) -> tuple[int, str]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)
    return proc.returncode, (proc.stdout or proc.stderr or "").strip()


def detect_nvidia() -> dict[str, object]:
    if not shutil.which("nvidia-smi"):
        return {"available": False, "reason": "nvidia-smi not found"}
    query = "name,memory.total,driver_version"
    code, out = run(["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader"])
    if code != 0:
        return {"available": False, "reason": out}
    gpus = []
    for line in out.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) >= 3:
            gpus.append({"name": parts[0], "memory_total": parts[1], "driver_version": parts[2]})
    return {"available": bool(gpus), "gpus": gpus}


def detect_python_packages() -> dict[str, str]:
    packages = {}
    for name in ["numpy", "scipy", "pandas", "sklearn", "torch", "matplotlib"]:
        try:
            module = __import__(name)
        except Exception:
            continue
        version = getattr(module, "__version__", "unknown")
        packages[name] = str(version)
    return packages


def detect_torch_devices() -> dict[str, object]:
    try:
        import torch  # type: ignore
    except Exception as exc:
        return {"torch_available": False, "reason": str(exc)}
    cuda_available = bool(torch.cuda.is_available())
    devices = []
    if cuda_available:
        for idx in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(idx)
            devices.append({
                "index": idx,
                "name": props.name,
                "total_memory_bytes": props.total_memory,
            })
    mps_available = bool(getattr(torch.backends, "mps", None) and torch.backends.mps.is_available())
    return {
        "torch_available": True,
        "torch_version": torch.__version__,
        "cuda_available": cuda_available,
        "cuda_version": torch.version.cuda,
        "mps_available": mps_available,
        "devices": devices,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="results/hardware_report.json")
    parser.add_argument("--print", action="store_true", dest="print_report")
    args = parser.parse_args()

    report = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "executable": sys.executable,
            "version": sys.version,
        },
        "packages": detect_python_packages(),
        "nvidia_smi": detect_nvidia(),
        "torch_devices": detect_torch_devices(),
    }

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.print_report:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print(f"Wrote hardware report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
