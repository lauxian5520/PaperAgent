#!/usr/bin/env python3
"""Create a stage plan file from the template."""
from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("stage_id")
    parser.add_argument("stage_name")
    parser.add_argument("--version", default="1")
    parser.add_argument("--output-dir", default="plans")
    parser.add_argument("--template", default="templates/stage_plan.template.md")
    args = parser.parse_args()

    template_path = Path(args.template)
    if template_path.exists():
        text = template_path.read_text(encoding="utf-8")
    else:
        text = "# Stage Plan: REPLACE_ME_STAGE_NAME\n\n## Goal\n\nREPLACE_ME_GOAL\n"

    text = text.replace("REPLACE_ME_STAGE_ID", args.stage_id)
    text = text.replace("REPLACE_ME_STAGE_NAME", args.stage_name)
    text = text.replace("vREPLACE_ME", f"v{args.version}")
    text = text.replace("REPLACE_ME_DATE", datetime.now().isoformat(timespec="seconds"))

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = args.stage_name.lower().replace(" ", "_").replace("/", "_")
    out = out_dir / f"stage_{args.stage_id}_{safe_name}.md"
    if out.exists():
        print(f"Refusing to overwrite existing plan: {out}")
        return 1
    out.write_text(text, encoding="utf-8")
    print(f"Created {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
