# Remote Execution Guide

Use this guide when experiments must run on a remote GPU server.

## Required information

Record these values in `docs/experiment_plan.md` or a project-specific remote
run note before asking Codex to execute remote experiments:

- SSH host alias, for example `paper-gpu`.
- Remote project directory.
- Remote data directory.
- Python or conda environment activation command.
- GPU type and expected CUDA version.
- Commands allowed during environment checks.
- Commands allowed for pilot runs.
- Where remote results should be saved.
- Whether results should be copied back to local `results/`.

Do not paste passwords, private keys, API tokens, or long-lived credentials into
project files. Configure SSH keys and host aliases outside the repository.

## Recommended first command

Ask Codex to verify the remote environment before training:

```text
Follow AGENTS.md strictly.

Use the configured remote server for environment verification only.
Check SSH connectivity, GPU availability, Python version, package versions,
project directory, and dataset directory.
Write docs/remote_environment_check.md.
Do not run training.
Update PROGRESS.md and stop.
```

## Pilot command shape

After the environment check passes:

```text
Follow AGENTS.md strictly.

Run one remote pilot condition only.
Use the approved remote project directory and Python environment.
Save pilot outputs under remote results/ and copy the pilot result back to local
results/pilot_results.json.
Do not run full experiments.
Update PROGRESS.md and stop.
```
