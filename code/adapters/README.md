# Model Adapters

Adapters connect project-specific model code to the paper experiment pipeline.

The adapter boundary keeps generated experiment code from modifying the original
model implementation directly. A generated adapter should be reviewed before any
pilot or full experiment.

Typical workflow:

```bash
python scripts/inspect_model_code.py --code-dir code --output docs/model_code_inventory.json
python scripts/generate_model_adapter.py --spec docs/model_adapter_spec.json
```

Each adapter should implement:

- `build_model`
- `prepare_batch`
- `forward`
- `compute_loss`
- `compute_metrics`

Generated adapters intentionally fail loudly for project-specific loss and
metric functions until those are implemented with real task logic.
