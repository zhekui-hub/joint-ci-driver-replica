# Production CI replica environment

- Source repository: `ChipLTech/DLC-Kernel-Driver`
- Source main SHA: `aa84e677db3e14cd9b704534e421e0290dee7b99`
- Replica mode: `dry-run`
- Runner label: `grok-box`
- Heavy production commands are replaced by `python ci_sim/runner.py`.
- Required checks are documented in `replica-gate-policy.json`; GitHub branch protection is intentionally not changed.
- The Grok Bot cloud runner must be registered for this repository with labels `self-hosted` and `grok-box` before dispatch.
- Suggested dispatch: `gh workflow run <workflow.yml> --repo zhekui-hub/joint-ci-driver-replica --ref zhekui/chore-production-ci-replica-20260928`
