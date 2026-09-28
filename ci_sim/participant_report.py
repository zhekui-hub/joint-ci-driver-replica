"""Build an exact-head replica report and optionally dispatch it to Arsenal."""
import json
import os
from pathlib import Path
import sys
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen

TARGET = "zhekui-hub/joint-ci-arsenal-replica"
STATE_ISSUE = os.environ.get("JOINT_STATE_ISSUE_NUMBER", "1")


def read_joint_state(token, joint_id):
    endpoint = f"https://api.github.com/repos/{TARGET}/issues/{STATE_ISSUE}/comments?per_page=100"
    request = Request(
        endpoint,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "joint-ci-participant-replica",
        },
    )
    with urlopen(request, timeout=30) as response:
        comments = json.loads(response.read().decode("utf-8"))
    marker = f"<!-- joint-ci-state:{joint_id} -->"
    for comment in comments:
        body = comment.get("body", "")
        if not body.startswith(marker):
            continue
        try:
            return json.loads(body.split("\n", 1)[1])
        except (IndexError, json.JSONDecodeError):
            return None
    return None


def wait_for_joint_ready(token, joint_id):
    timeout = max(1, int(os.environ.get("JOINT_WAIT_TIMEOUT_SECONDS", "150")))
    interval = max(1, int(os.environ.get("JOINT_WAIT_INTERVAL_SECONDS", "5")))
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            state = read_joint_state(token, joint_id)
        except HTTPError as exc:
            print(f"JOINT_STATE_HTTP_STATUS={exc.code}", file=sys.stderr, flush=True)
            state = None
        if state:
            status = state.get("status", "unknown")
            print(f"JOINT_STATE_STATUS={status}", flush=True)
            if status == "ready":
                return 0
            if status in {"failed", "error"}:
                return 1
        time.sleep(interval)
    print("JOINT_STATE_TIMEOUT: required participants did not reach ready", file=sys.stderr, flush=True)
    return 1


def main():
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    event = json.loads(Path(event_path).read_text()) if event_path else {}
    pr = event.get("pull_request", {})
    head = pr.get("head", {})
    branch = head.get("ref") or os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME", "")
    sha = head.get("sha") or os.environ.get("GITHUB_SHA", "")
    report = {
        "schema_version": 1,
        "joint_id": os.environ.get("JOINT_CI_ID", "replica-manual"),
        "repo": os.environ.get("REPLICA_REPOSITORY", "unknown"),
        "branch": branch, "head_sha": sha,
        "pr_number": str(event.get("number", 0)),
        "ci_mode": "joint", "is_draft": bool(pr.get("draft", False)),
        "deps": json.loads(os.environ.get("JOINT_DEPS_JSON", "{}")),
        "required_members": json.loads(os.environ.get("JOINT_MEMBERS_JSON", '["driver","synapse","sim"]')),
        "source_run_id": int(os.environ.get("GITHUB_RUN_ID", "0")),
        "source_run_attempt": int(os.environ.get("GITHUB_RUN_ATTEMPT", "1")),
        "private_result": "unknown",
        "remote_tests": [{"id": "public.smoke", "params": {"profile": "default"}}],
    }
    if not branch or len(sha) != 40:
        raise ValueError("report requires a branch and a full commit SHA")
    Path("joint-report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, sort_keys=True), flush=True)
    if os.environ.get("JOINT_REPORT_ONLY", "false").lower() == "true":
        print("REPORT_ONLY: no cross-repository dispatch attempted")
        return 0
    token = os.environ.get("JOINT_DISPATCH_TOKEN", "").strip()
    if not token:
        print("DISPATCH_BLOCKED: JOINT_DISPATCH_TOKEN missing", file=sys.stderr)
        return 1
    if os.environ.get("JOINT_TARGET_REPO", TARGET) != TARGET:
        raise ValueError("dispatch target must be the private Arsenal replica")
    payload = {"event_type": "joint_ci_report", "client_payload": {"report": report}}
    request = Request(f"https://api.github.com/repos/{TARGET}/dispatches",
                      data=json.dumps(payload).encode(), method="POST",
                      headers={"Authorization": f"Bearer {token}",
                               "Content-Type": "application/json", "Accept": "application/vnd.github+json"})
    try:
        with urlopen(request, timeout=30) as response:
            print(f"DISPATCH_HTTP_STATUS={response.status}")
            if response.status != 204:
                return 1
            if os.environ.get("JOINT_WAIT", "true").lower() != "true":
                return 0
            return wait_for_joint_ready(token, report["joint_id"])
    except HTTPError as exc:
        print(f"DISPATCH_HTTP_STATUS={exc.code}; report retained as artifact", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
