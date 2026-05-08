#!/usr/bin/env python3
"""
Smoke test: verifies Storyboard CID integration end-to-end via HTTP API.

Run:  python3 scripts/smoke_storyboard_cinematic_intelligence_contract.py
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse

BASE = os.environ.get("API_BASE", "http://127.0.0.1:8010")
PASS = 0
FAIL = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"  PASS: {name}")
    else:
        FAIL += 1
        print(f"  FAIL: {name}  -- {detail}")


def api(method: str, path: str, token: str = "", body: dict | None = None) -> tuple[int, dict | str]:
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            text = resp.read().decode()
            status = resp.status
            if text.strip():
                return status, json.loads(text)
            return status, ""
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        try:
            return e.code, json.loads(body_text)
        except (json.JSONDecodeError, ValueError):
            return e.code, body_text


def main() -> int:
    global PASS, FAIL

    print("===== SMOKE: Storyboard Cinematic Intelligence (HTTP) =====")

    # 1. Register or login
    stamp = int(time.time())
    register_body = {
        "email": f"smoke.cid.e2e.{stamp}@gmail.com",
        "password": "Smoke1234!",
        "username": f"smoke_cid_e2e_{stamp}",
        "name": "Smoke CID E2E",
        "full_name": "Smoke CID E2E",
    }
    status, data = api("POST", "/api/auth/register/cid", body=register_body)
    user_id = data.get("user_id", "") if isinstance(data, dict) else ""
    if status != 200 and status != 201:
        check("Register user", False, f"status={status} data={data}")
        # try login
        status, data = api("POST", "/api/auth/login", body={"email": register_body["email"], "password": register_body["password"], "username": register_body["username"]})
        if status != 200:
            print(f"  FATAL: cannot authenticate (status={status})")
            return 1

    token = ""
    if isinstance(data, dict) and "access_token" in data:
        token = data["access_token"]
    if not token:
        status, data = api("POST", "/api/auth/login", body={"email": register_body["email"], "password": register_body["password"], "username": register_body["username"]})
        if isinstance(data, dict) and "access_token" in data:
            token = data["access_token"]
    check("Authenticated", bool(token))
    if not token:
        print("  FATAL: no token")
        return 1

    # 2. Create project
    project_body = {
        "title": "Smoke CID E2E",
        "name": "Smoke CID E2E",
        "description": "Smoke test project for CID storyboard cinematic intelligence",
        "project_type": "feature_film",
    }
    status, data = api("POST", "/api/projects", token=token, body=project_body)
    project_id = data.get("id", "") if isinstance(data, dict) else ""
    if not project_id and isinstance(data, dict):
        project_id = data.get("project_id", "")
    check("Create project", status in (200, 201) and bool(project_id), f"status={status} data={data}")
    if status not in (200, 201) or not project_id:
        print("  FATAL: cannot continue without project_id")
        return 1

    # 3. Ingest script
    script_text = """INT. SMOKE TEST ROOM - DAY

A tester sits at a terminal, running automated checks. The screen flashes green.

TESTER
All CID checks passed.

ANALYST
Let's verify the metadata.
"""
    status, _ = api("POST", f"/api/projects/{project_id}/intake/script", token=token, body={"script_text": script_text})
    check("Ingest script", status in (200, 201), f"status={status}")

    # 4. Run analysis
    status, _ = api("POST", f"/api/projects/{project_id}/analysis/run", token=token, body={})
    check("Run analysis", status == 200, f"status={status}")

    # 5. Generate storyboard with full CID
    gen_body = {
        "style": "cinematic_realistic",
        "aspect_ratio": "16:9",
        "num_shots": 2,
        "use_cinematic_intelligence": True,
        "use_montage_intelligence": True,
        "validate_prompts": True,
    }
    status, data = api("POST", f"/api/projects/{project_id}/storyboard/generate", token=token, body=gen_body)
    job_id = data.get("job_id", "") if isinstance(data, dict) else ""
    total_shots = data.get("total_shots", 0) if isinstance(data, dict) else 0
    check("Generate storyboard with CID", status == 200 and bool(job_id) and total_shots > 0, f"status={status} shots={total_shots}")

    # 6. GET /storyboard returns 200 with metadata_json
    status, data = api("GET", f"/api/projects/{project_id}/storyboard", token=token)
    storyboard_ok = status == 200
    shots_list = data.get("shots", []) if isinstance(data, dict) else []
    has_metadata = any(s.get("metadata_json") is not None for s in shots_list)
    check("GET /storyboard returns 200", storyboard_ok, f"status={status}")
    check("GET /storyboard has metadata_json", has_metadata, f"total_shots={len(shots_list)}")

    # 7. GET /shots returns 200 with metadata_json
    status, data = api("GET", f"/api/projects/{project_id}/shots", token=token)
    shots_ok = status == 200
    shots_from_shots = data if isinstance(data, list) else data.get("shots", []) if isinstance(data, dict) else []
    has_metadata_shots = any(s.get("metadata_json") is not None for s in shots_from_shots)
    check("GET /shots returns 200", shots_ok, f"status={status}")
    check("GET /shots has metadata_json", has_metadata_shots, f"total_shots={len(shots_from_shots)}")

    # 8. Validate metadata_json structure
    all_metadata = [s["metadata_json"] for s in shots_list if s.get("metadata_json") is not None]
    if all_metadata:
        meta = all_metadata[0]
        check("metadata_json is dict", isinstance(meta, dict), f"type={type(meta).__name__}")
        for key in ("directorial_intent", "montage_intent", "shot_editorial_purpose", "prompt_spec", "cinematic_intent_id", "director_lens_id", "validation", "editorial_beats"):
            present = key in meta
            check(f"metadata_json contains '{key}'", present, f"keys={list(meta.keys())}")
        check("director_lens_id is string", isinstance(meta.get("director_lens_id"), str))
        check("cinematic_intent_id is string", isinstance(meta.get("cinematic_intent_id"), str))
        dv = meta.get("validation")
        check("validation is present", dv is not None)
        if dv:
            check("validation has is_valid", "is_valid" in dv)
        sep = meta.get("shot_editorial_purpose")
        if sep:
            check("shot_editorial_purpose has cut_reason", "cut_reason" in sep)
            check("shot_editorial_purpose has purpose", "purpose" in sep)
    else:
        check("metadata_json structure", False, "no metadata found to validate")

    # 9. Forbidden style references in positive_prompt
    forbidden_terms = ["spielberg", "hitchcock", "kubrick", "almodovar", "bunuel", "in the style of"]
    shots_payload = shots_list if shots_list else shots_from_shots
    prompts_clean = True
    for s in shots_payload:
        prompt = (s.get("metadata_json") or {}).get("prompt_spec") or {}
        positive = (prompt.get("positive_prompt") or "").lower() if isinstance(prompt, dict) else ""
        if not positive:
            positive = (s.get("narrative_text") or "").lower()
        for term in forbidden_terms:
            if term in positive:
                prompts_clean = False
                check(f"Forbidden term '{term}' in prompt", False, f"shot={s.get('id','')}")
    if prompts_clean:
        check("No forbidden style references in prompts", True)

    # 10. Invalid director_lens_id returns 400
    bad_lens_body = {
        "style": "cinematic_realistic",
        "aspect_ratio": "16:9",
        "num_shots": 1,
        "use_cinematic_intelligence": True,
        "director_lens_id": "non_existent_lens_xyz",
    }
    status, data = api("POST", f"/api/projects/{project_id}/storyboard/generate", token=token, body=bad_lens_body)
    detail = data.get("detail", "") if isinstance(data, dict) else ""
    check("Invalid director_lens_id returns 400", status == 400, f"status={status} detail={detail}")
    check("Invalid lens error message is clear", "Unknown director lens profile" in str(detail), f"detail={detail}")

    # 11. Invalid montage_profile_id returns 400
    bad_profile_body = {
        "style": "cinematic_realistic",
        "aspect_ratio": "16:9",
        "num_shots": 1,
        "use_cinematic_intelligence": True,
        "use_montage_intelligence": True,
        "montage_profile_id": "non_existent_profile_xyz",
    }
    status, data = api("POST", f"/api/projects/{project_id}/storyboard/generate", token=token, body=bad_profile_body)
    detail = data.get("detail", "") if isinstance(data, dict) else ""
    check("Invalid montage_profile_id returns 400", status == 400, f"status={status} detail={detail}")
    check("Invalid profile error message is clear", "Unknown montage profile" in str(detail), f"detail={detail}")

    # 12. Validate GET /storyboard with no CID (baseline still works)
    gen_baseline_body = {
        "style": "cinematic_realistic",
        "aspect_ratio": "16:9",
        "num_shots": 1,
    }
    status, data = api("POST", f"/api/projects/{project_id}/storyboard/generate", token=token, body=gen_baseline_body)
    check("Baseline (no CID) still works", status == 200, f"status={status}")

    # 13. Validate null lens with CID defaults without error
    null_lens_body = {
        "style": "cinematic_realistic",
        "aspect_ratio": "16:9",
        "num_shots": 1,
        "use_cinematic_intelligence": True,
    }
    status, data = api("POST", f"/api/projects/{project_id}/storyboard/generate", token=token, body=null_lens_body)
    check("Null lens with CID defaults", status == 200, f"status={status}")

    # Summary
    total = PASS + FAIL
    print(f"\n===== RESULTS: {PASS}/{total} passed, {FAIL}/{total} failed =====")
    return 0 if FAIL == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
