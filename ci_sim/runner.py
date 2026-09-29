"""Run a lightweight replica job while preserving dependency semantics."""
import hashlib
import json
import os
import sys


def main():
    repo = os.environ.get("REPLICA_REPOSITORY", "unknown")
    workflow = os.environ.get("REPLICA_SOURCE_WORKFLOW", "unknown")
    job = os.environ.get("REPLICA_SOURCE_JOB", "unknown")
    matrix = os.environ.get("MATRIX_JSON", "{}")
    failure = os.environ.get("SIMULATE_FAILURE", "")
    needs = json.loads(os.environ.get("NEEDS_JSON", "{}"))
    allow_skipped = os.environ.get("REPLICA_ALLOW_SKIPPED_NEEDS", "").lower() == "true"
    failed_needs = {
        key: value.get("result")
        for key, value in needs.items()
        if value.get("result") != "success"
        and not (allow_skipped and value.get("result") == "skipped")
    }
    result = "failure" if failed_needs or failure in (repo, workflow, job, "all") else "success"
    identity = f"{repo}:{workflow}:{job}:{matrix}"
    print(
        json.dumps(
            {
                "repo": repo,
                "workflow": workflow,
                "job": job,
                "scope": os.environ.get("REPLICA_SCOPE", "private"),
                "execution_owner": os.environ.get("REPLICA_EXECUTION_OWNER", "participant"),
                "matrix": matrix,
                "result": result,
                "failed_needs": failed_needs,
                "test_key": "replica-" + hashlib.sha256(identity.encode()).hexdigest()[:16],
            },
            sort_keys=True,
        )
    )
    return 0 if result == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
