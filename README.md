# driver joint CI replica

This private repository is a dry-run replica of the real ChipLTech `driver` repository.

- source `main` SHA: `44a09c8778ba2899310781ccb227ad9c82b3d2d7`
- source workflows/jobs: `12` / `24`
- active runner label: `replica-driver`
- matrix catalog: `test-catalog.json`

The original workflow YAML is retained under `.ci-source/workflows`. The active `.github/workflows` files preserve names, job IDs, needs edges, triggers, and matrix dimensions, but replace test bodies with `ci_sim/runner.py`. Push, release, and schedule side effects are disabled.

Dispatch `joint_ci_hook.yml` for the participant gate. Arsenal also exposes `joint_ci_replica.yml`, which consumes driver/synapse/sim reports and records a joint state artifact.

## PR smoke marker

This branch is used to observe the replica gate and joint-report flow on a real pull request.
