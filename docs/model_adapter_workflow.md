# Model Adapter Workflow

Use this workflow when you already have a model implementation and want Codex to
connect it to the experiment pipeline.

## 1. Inspect model code

```bash
python scripts/inspect_model_code.py --code-dir code --output docs/model_code_inventory.json
```

This produces a safe AST-based report. It lists imports, classes, functions,
possible model classes, and possible command-line entrypoints without importing
the model code.

## 2. Create an adapter spec

Copy the example:

```text
templates/model_adapter_spec.example.json
```

to:

```text
docs/model_adapter_spec.json
```

Then fill in the real model module, class or factory, input fields, target
field, task type, and metrics.

## 3. Generate adapter scaffold

```bash
python scripts/generate_model_adapter.py --spec docs/model_adapter_spec.json
```

The generated adapter is written under:

```text
code/adapters/
```

## 4. Review and complete project-specific logic

Codex or a human must implement real logic for:

- tensor or array conversion in `prepare_batch`;
- task objective in `compute_loss`;
- evaluation metrics in `compute_metrics`.

The generated adapter fails loudly until these functions are implemented. This
prevents fake training losses or fake metrics from entering the paper pipeline.

## 5. Connect to pilot

After the adapter passes a smoke test, reference it from the approved experiment
matrix and run pilot only. Do not run full experiments until the pilot and human
gate pass.
