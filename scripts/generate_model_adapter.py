#!/usr/bin/env python3
"""Generate a project-specific adapter scaffold from a JSON specification."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def safe_identifier(name: str) -> str:
    cleaned = re.sub(r"\W+", "_", name.strip().lower()).strip("_")
    return cleaned or "model"


def class_name(name: str) -> str:
    return "".join(part.capitalize() for part in safe_identifier(name).split("_")) + "Adapter"


def load_spec(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_adapter(spec: dict[str, Any]) -> str:
    adapter_name = safe_identifier(str(spec.get("adapter_name", "project_model")))
    cls_name = class_name(adapter_name)
    model = spec.get("model") or {}
    task = spec.get("task") or {}
    data = spec.get("data") or {}
    metrics = spec.get("metrics") or {}

    import_module = str(model.get("module", "code.models.project_model"))
    import_symbol = str(model.get("class_or_factory", "ProjectModel"))
    constructor_kwargs = model.get("constructor_kwargs", {})
    input_fields = data.get("input_fields", ["inputs"])
    target_field = data.get("target_field", "target")
    primary_metric = metrics.get("primary", "primary_metric")
    task_type = task.get("type", "supervised")

    return f'''"""Generated adapter for {adapter_name}.

Review this file before running experiments. The generated code preserves a
standard interface but project-specific tensor conversion, loss computation, and
metric computation may need revision.
"""
from __future__ import annotations

import importlib
from typing import Any

from code.adapters.base import BaseModelAdapter, Batch, Metrics


class {cls_name}(BaseModelAdapter):
    adapter_name = "{adapter_name}"
    task_type = "{task_type}"
    input_fields = {input_fields!r}
    target_field = "{target_field}"
    primary_metric = "{primary_metric}"

    def build_model(self) -> Any:
        module = importlib.import_module("{import_module}")
        factory = getattr(module, "{import_symbol}")
        return factory(**{constructor_kwargs!r})

    def prepare_batch(self, raw_batch: Batch) -> Batch:
        """Map raw dataset fields to the model input contract.

        Keep this method deterministic. Convert arrays/tensors here and validate
        that required input and target fields are present.
        """
        missing = [field for field in self.input_fields if field not in raw_batch]
        if missing:
            raise KeyError(f"Missing input fields: {{missing}}")
        if self.target_field and self.target_field not in raw_batch:
            raise KeyError(f"Missing target field: {{self.target_field}}")
        return raw_batch

    def forward(self, model: Any, batch: Batch) -> Any:
        prepared = self.prepare_batch(batch)
        if len(self.input_fields) == 1:
            return model(prepared[self.input_fields[0]])
        kwargs = {{field: prepared[field] for field in self.input_fields}}
        return model(**kwargs)

    def compute_loss(self, model_output: Any, batch: Batch) -> Any:
        """Return a real training loss for this project.

        Replace this implementation with the task's actual objective before
        full experiments. The default fails loudly to prevent fake metrics.
        """
        raise NotImplementedError("Project-specific loss computation is required.")

    def compute_metrics(self, model_output: Any, batch: Batch) -> Metrics:
        """Return real evaluation metrics computed from model outputs and labels."""
        raise NotImplementedError("Project-specific metric computation is required.")
'''


def render_spec_markdown(spec: dict[str, Any], adapter_path: Path) -> str:
    return f"""# Model Adapter Report

Generated adapter:

```text
{adapter_path.as_posix()}
```

## Required Human Review

- Confirm the model import path and class or factory name.
- Implement the project-specific loss in `compute_loss`.
- Implement real metrics in `compute_metrics`.
- Confirm data fields in `input_fields` and `target_field`.
- Run a smoke test before pilot training.

## Source Spec

```json
{json.dumps(spec, indent=2, ensure_ascii=False)}
```
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", default="docs/model_adapter_spec.json")
    parser.add_argument("--output-dir", default="code/adapters")
    parser.add_argument("--report", default="docs/model_adapter_report.md")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"ERROR: missing adapter spec: {spec_path}")
        return 2
    spec = load_spec(spec_path)
    adapter_name = safe_identifier(str(spec.get("adapter_name", "project_model")))
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"{adapter_name}_adapter.py"
    if out.exists() and not args.force:
        print(f"ERROR: refusing to overwrite existing adapter without --force: {out}")
        return 2
    out.write_text(render_adapter(spec), encoding="utf-8")

    report = Path(args.report)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(render_spec_markdown(spec, out), encoding="utf-8")
    print(f"Generated adapter: {out}")
    print(f"Wrote report: {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
