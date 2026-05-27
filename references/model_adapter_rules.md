# Model Adapter Rules

Use this file when adapting an existing model implementation to this paper
pipeline.

## Goal

Create a thin, inspectable adapter layer between project-specific model code and
the standard experiment runner. Prefer adapters over direct edits to the original
model unless the model code itself is broken.

## Workflow

1. Inspect the model code without importing it:

```bash
python scripts/inspect_model_code.py --code-dir code --output docs/model_code_inventory.json
```

2. Create `docs/model_adapter_spec.json` from:

```text
templates/model_adapter_spec.example.json
```

3. Generate an adapter scaffold:

```bash
python scripts/generate_model_adapter.py --spec docs/model_adapter_spec.json
```

4. Complete project-specific logic in the generated adapter:

- `prepare_batch`;
- `compute_loss`;
- `compute_metrics`.

5. Run a smoke test before pilot execution.

## Hard constraints

- Do not fabricate losses or metrics inside adapters.
- Do not silently catch model errors and return dummy outputs.
- Do not weaken baselines by giving them less careful adapters.
- Preserve the original model implementation where possible.
- If the adapter changes model inputs, log the transformation in the experiment configuration.
- If the model requires special preprocessing, store reusable preprocessing code under `code/`.

## Required adapter evidence

Before full experiments, record:

- adapter path;
- model import path;
- model class or factory;
- input fields;
- target field;
- loss function;
- metrics;
- smoke-test command and result;
- any preprocessing assumptions.
