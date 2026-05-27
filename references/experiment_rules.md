# Experiment Rules

Use this file for experiment design, code generation, execution, debugging, and result analysis.

## Non-negotiable rules

- Use real algorithms, real objectives, real datasets or explicitly described synthetic data generation.
- Do not fabricate results with random number generators.
- Do not hardcode final metrics.
- Do not create fake decreasing loss curves.
- Do not claim convergence without a real stopping criterion.
- Do not suppress NaN/Inf without finding and fixing the root cause.
- All experiments must be reproducible with recorded commands, seeds, environment, and hardware.

## Pilot first

Before a full experiment:

1. Run one small pilot condition.
2. Print or log `TIME_ESTIMATE: <seconds>`.
3. Estimate total runtime from the pilot.
4. Verify that metrics are computed correctly.
5. Save pilot output to `results/pilot_results.json` or equivalent.

Do not run the full experiment if the estimated runtime exceeds `compute_budget` in `paper_config.yaml`.

## Resource guard

Experiment code should implement a time guard:

- Periodically check elapsed runtime.
- Stop at `compute_budget.stop_at_budget_fraction` of the budget.
- Save partial results before stopping.
- Write a clear status field: `completed`, `partial`, or `failed`.

## Scaling rules

- If experiment conditions exceed 100, reduce seeds to 3-5 unless the user approves more.
- If runtime is too high, reduce optimization steps, dataset size, or conditions before reducing scientific controls.
- Baselines must receive comparable tuning effort to the proposed method.

## Required experiment evidence

Every experiment run should save:

- command line or configuration;
- timestamp;
- git commit if available;
- random seed;
- software versions;
- hardware summary;
- dataset or synthetic data specification;
- method and baseline configurations;
- metrics;
- convergence status;
- runtime;
- warnings or failures.

Recommended result keys:

```json
{
  "experiment_id": "...",
  "status": "completed",
  "created_at": "...",
  "command": "...",
  "seed": 0,
  "hardware": {},
  "software": {},
  "conditions": [],
  "metrics": {},
  "artifacts": [],
  "notes": ""
}
```

## Code quality requirements

- Prefer Python stdlib, NumPy, pandas, scipy, matplotlib, scikit-learn, and PyTorch only when needed.
- Keep code deterministic where feasible.
- Avoid hidden network calls during experiments unless explicitly part of data retrieval.
- Keep generated figures reproducible from data in `results/`.
- Store reusable code under `code/`; do not bury code in notebooks only.

## NumPy 2.x compatibility

- Use `np.trapezoid`, not `np.trapz`.
- Use `scipy.special.erfinv`, not `np.erfinv`.
- Use built-in `bool`, `int`, `float`, `complex`, not `np.bool`, `np.int`, `np.float`, `np.complex`.
- Use the standard `math` module, not `np.math`.

## Strong baselines and ablations

Before writing Results:

- Each baseline must be fairly tuned.
- Each claimed component must have an ablation.
- Ablations should remove one component at a time.
- If a component has no ablation, do not claim that it is effective.

## Debugging discipline

When a run fails:

1. Save the error log.
2. Identify the root cause.
3. Modify code minimally.
4. Re-run the smallest failing case.
5. Update `PROGRESS.md` and result notes.

Do not paper over warnings with broad try/except blocks.
