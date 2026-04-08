from __future__ import annotations

import argparse
import json
import time
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="HTTP smoke checks for backend endpoints")
    parser.add_argument("--base-url", default="http://127.0.0.1:3000", help="Backend base URL")
    parser.add_argument("--wait-seconds", type=float, default=8.0, help="Max wait for render job terminal state")
    return parser.parse_args()


def request_json(method: str, url: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    data = None
    headers: Dict[str, str] = {}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = Request(url, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body) if body else {}
    except HTTPError as error:
        body = error.read().decode("utf-8")
        raise RuntimeError(f"HTTP {error.code} for {url}: {body}") from error
    except URLError as error:
        raise RuntimeError(f"Request failed for {url}: {error}") from error


def main() -> int:
    args = parse_args()
    base_url = args.base_url.rstrip("/")

    health = request_json("GET", f"{base_url}/api/health")
    if health.get("ok") is not True:
        raise RuntimeError("/api/health did not return ok=true")

    ops = request_json("GET", f"{base_url}/api/ops/status")
    if ops.get("ok") is not True:
        raise RuntimeError("/api/ops/status did not return ok=true")

    create = request_json(
        "POST",
        f"{base_url}/api/render/jobs",
        payload={"request_payload": {"prompt": {"1": {"class_type": "KSampler", "inputs": {}}}}},
    )
    if create.get("ok") is not True:
        raise RuntimeError("POST /api/render/jobs did not return ok=true")

    job = create.get("job") or {}
    job_id = job.get("job_id")
    if not isinstance(job_id, str) or not job_id.strip():
        raise RuntimeError("Created render job did not include job_id")

    deadline = time.monotonic() + max(args.wait_seconds, 1.0)
    terminal = None

    while time.monotonic() < deadline:
        get_job = request_json("GET", f"{base_url}/api/render/jobs/{job_id}")
        current = (get_job.get("job") or {}).get("status")
        if current in {"succeeded", "failed", "timeout"}:
            terminal = get_job
            break
        time.sleep(0.5)

    if terminal is None:
        raise RuntimeError(f"Render job {job_id} did not reach terminal state within {args.wait_seconds}s")

    final_job = terminal.get("job") or {}
    final_status = final_job.get("status")
    if final_status not in {"succeeded", "failed", "timeout"}:
        raise RuntimeError(f"Unexpected final status: {final_status}")

    if final_status == "succeeded" and not isinstance(final_job.get("result"), dict):
        raise RuntimeError("Succeeded job missing result object")

    if final_status in {"failed", "timeout"} and not isinstance(final_job.get("error"), dict):
        raise RuntimeError("Failed/timeout job missing error object")

    listed = request_json("GET", f"{base_url}/api/render/jobs?limit=20")
    jobs = listed.get("jobs") if isinstance(listed.get("jobs"), list) else []
    if not any(isinstance(item, dict) and item.get("job_id") == job_id for item in jobs):
        raise RuntimeError("Created render job not found in list endpoint")

    print("HTTP_SMOKE_OK")
    print(f"HTTP_SMOKE_INFO final_status={final_status} job_id={job_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
