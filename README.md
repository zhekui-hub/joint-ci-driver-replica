# driver joint CI replica

This private repository is a dry-run replica of the real ChipLTech `driver` repository.

- source `main` SHA: `44a09c8778ba2899310781ccb227ad9c82b3d2d7`
- source workflows/jobs: `12` / `24`
- active runner label: `replica-driver`
- matrix catalog: `test-catalog.json`

The original workflow YAML is retained under `.ci-source/workflows`. The active `.github/workflows` files preserve names, job IDs, needs edges, triggers, and matrix dimensions, but replace test bodies with `ci_sim/runner.py`. Push, release, and schedule side effects are disabled.

Dispatch `joint_ci_hook.yml` for the participant gate. Arsenal also exposes `joint_ci_replica.yml`, which consumes driver/synapse/sim reports and records a joint state artifact.

## PR smoke retry

This branch is used to observe the replica gate and joint-report flow on a fresh real pull request.

## Joint CI wait-state observation

This test branch intentionally opens the Driver participant first. The Synapse participant is omitted so `Joint CI readiness` should remain pending until its report arrives.

## Joint CI third experiment

This branch intentionally opens the Driver participant without submitting a Synapse PR. Joint CI readiness must remain pending and Arsenal must not start the public matrix.
## Joint CI fourth experiment

This branch starts the fourth experiment from the merged Arsenal, Driver, and Synapse implementation. The Driver PR is opened first; the Synapse participant is intentionally omitted until the second phase.

## Joint CI seamless switch validation
This commit validates that shared tests run once in Arsenal while their per-test checks remain visible from both participant PRs.

\n