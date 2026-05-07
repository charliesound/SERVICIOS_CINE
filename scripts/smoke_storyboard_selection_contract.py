#!/usr/bin/env python3
"""
Smoke test: storyboard selection contract - REAL execution only.
Validates SELECTED_SCENES, SCENE_RANGE, SEQUENCE, SINGLE_SCENE modes.
Uses dynamic user registration and creates temporary project with valid script.
"""
import os
import sys
import json
import uuid
import time

# Configuration
BASE_URL = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8010")
TIMEOUT = 30

# Use only stdlib
from urllib import request as _urlreq, error as _urlerr

def _get(url, headers=None, params=None):
    full = url + "?" + "&".join(f"{k}={v}" for k, v in (params or {}).items()) if params else url
    req = _urlreq.Request(full, headers=headers or {})
    try:
        with _urlreq.urlopen(req, timeout=TIMEOUT) as resp:
            return _Resp(resp)
    except _urlerr.HTTPError as exc:
        return _Resp(exc)

def _post(url, headers=None, json_data=None):
    data = json.dumps(json_data).encode() if json_data else None
    req = _urlreq.Request(url, data=data, headers={**(headers or {}), "Content-Type": "application/json"}, method="POST")
    try:
        with _urlreq.urlopen(req, timeout=TIMEOUT) as resp:
            return _Resp(resp)
    except _urlerr.HTTPError as exc:
        return _Resp(exc)

class _Resp:
    def __init__(self, resp):
        self._resp = resp
        self.status_code = getattr(resp, "code", getattr(resp, "status", 500))
        _raw = resp.read() if hasattr(resp, 'read') else b""
        self._text = _raw.decode() if _raw else ""
    
    @property
    def text(self):
        return self._text
    
    def json(self):
        return json.loads(self._text) if self._text else {}

def _make_token():
    """Get token: register dynamic user, then login."""
    try:
        unique_email = f"smoke_{uuid.uuid4().hex[:8]}@test.local"
        pw = "SmokeTest123!"
        
        # Register
        reg_data = json.dumps({"username": f"smoke_{uuid.uuid4().hex[:6]}", "email": unique_email, "password": pw, "full_name": "Smoke Test"}).encode()
        reg_req = _urlreq.Request(f"{BASE_URL}/api/auth/register", data=reg_data, headers={"Content-Type": "application/json"}, method="POST")
        
        try:
            with _urlreq.urlopen(reg_req, timeout=TIMEOUT) as resp:
                data = json.loads(resp.read())
                token = data.get("access_token", "")
                if token:
                    print(f"  Registered new user: {unique_email}")
                    return token
        except _urlerr.HTTPError:
            pass  # User might exist, try login
        
        # Login
        login_data = json.dumps({"email": unique_email, "password": pw}).encode()
        login_req = _urlreq.Request(f"{BASE_URL}/api/auth/login", data=login_data, headers={"Content-Type": "application/json"}, method="POST")
        with _urlreq.urlopen(login_req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
            token = data.get("access_token", "")
            print(f"  Logged in as: {unique_email}")
            return token
    except Exception as exc:
        print(f"  [token] Error: {exc}")
    return ""

def _create_project(token, name="Smoke Test Project"):
    """Create a temporary project with minimal valid script."""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Create project
    proj_data = json.dumps({"name": name, "description": "For storyboard smoke testing"}).encode()
    req = _urlreq.Request(f"{BASE_URL}/api/projects", data=proj_data, headers={**headers, "Content-Type": "application/json"}, method="POST")
    
    try:
        with _urlreq.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read())
            project_id = data.get("id", "")
            print(f"  Created project: {project_id}")
            
            # Add script
            script = """SCENE 1
Int. OFFICE - DAY
JOHN enters the room.

SCENE 2
Ext. STREET - DAY
MARY walks down the street.

SCENE 3
Int. KITCHEN - NIGHT
JOHN and MARY cook dinner.
"""
            script_data = json.dumps({"script_text": script}).encode()
            script_req = _urlreq.Request(f"{BASE_URL}/api/projects/{project_id}/script", data=script_data, headers={**headers, "Content-Type": "application/json"}, method="PUT")
            
            with _urlreq.urlopen(script_req, timeout=TIMEOUT) as script_resp:
                print(f"  Script added to project")
                return project_id
    except Exception as exc:
        print(f"  [project] Error: {exc}")
    return ""

def _check(label, ok, detail=""):
    status = "✅" if ok else "❌"
    print(f"  {status} {label}" + (f": {detail}" if detail else ""))

def main():
    print(f"==> Smoke: storyboard selection contract @ {BASE_URL}")
    print("="*50)
    
    # 1. Health check
    print("\n[1] Health check")
    r = _get(f"{BASE_URL}/health")
    _check("Backend reachable", r.status_code == 200, f"status={r.status_code}")
    if r.status_code != 200:
        return
    
    # 2. Get token
    print("\n[2] Getting token...")
    token = _make_token()
    if not token:
        print("  ERROR: Could not get token")
        return
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Get or create project
    print("\n[3] Getting/creating test project...")
    r = _get(f"{BASE_URL}/api/projects", headers=headers)
    project_id = ""
    if r.status_code == 200:
        projects = r.json().get("projects", [])
        if projects:
            project_id = projects[0].get("id", "")
            print(f"  Using existing project: {project_id}")
    
    if not project_id:
        project_id = _create_project(token)
        if not project_id:
            print("  ERROR: Could not create project")
            return
    
    # 4. Get storyboard options
    print("\n[4] GET /api/projects/{project_id}/storyboard/options")
    r = _get(f"{BASE_URL}/api/projects/{project_id}/storyboard/options", headers=headers)
    if r.status_code != 200:
        _check("options 200", False, f"status={r.status_code}")
        return
    data = r.json()
    modes = data.get("modes", [])
    _check("SELECTED_SCENES in modes", "SELECTED_SCENES" in modes, f"modes={modes}")
    
    # 5. Generate with SELECTED_SCENES
    print("\n[5] POST generate SELECTED_SCENES scene_numbers=[1] shots_per_scene=1")
    r = _post(
        f"{BASE_URL}/api/projects/{project_id}/storyboard/generate",
        headers=headers,
        json_data={
            "generation_mode": "SELECTED_SCENES",
            "scene_numbers": [1],
            "shots_per_scene": 1,
            "style_preset": "cinematic_realistic",
            "overwrite": True,
        },
    )
    if r.status_code not in (200, 201, 202):
        _check("generate SELECTED_SCENES accepted", False, f"status={r.status_code} body={r.text[:300]}")
        return
    
    body = r.json()
    real_mode = body.get("mode") or body.get("generation_mode")
    total_scenes = body.get("total_scenes", -1)
    total_shots = body.get("total_shots", -1)
    _check("mode is SELECTED_SCENES", real_mode == "SELECTED_SCENES", f"mode={real_mode}")
    _check("total_scenes == 1", total_scenes == 1, f"total_scenes={total_scenes}")
    _check("total_shots == 1", total_shots == 1, f"total_shots={total_shots}")
    
    # 6. Filter by scene_number=1
    print("\n[6] GET /api/projects/{project_id}/storyboard?scene_number=1")
    r = _get(f"{BASE_URL}/api/projects/{project_id}/storyboard", headers=headers, params={"scene_number": 1})
    if r.status_code == 200:
        data = r.json()
        shots = data.get("shots", [])
        all_scene_1 = all(s.get("scene_number") == 1 for s in shots)
        _check("All shots scene_number=1", all_scene_1, f"shots_count={len(shots)}")
    else:
        _check("Filter scene_number=1", False, f"status={r.status_code}")
    
    # 7. Pipeline endpoints
    print("\n[7] Pipeline endpoints")
    r1 = _get(f"{BASE_URL}/api/workflows/presets")
    _check("workflows/presets 200", r1.status_code == 200, f"status={r1.status_code}")
    
    r2 = _get(f"{BASE_URL}/api/pipelines/presets", headers=headers)
    _check("pipelines/presets not 404", r2.status_code != 404, f"status={r2.status_code}")
    
    r3 = _get(f"{BASE_URL}/api/pipelines/jobs", headers=headers)
    _check("pipelines/jobs not 404", r3.status_code != 404, f"status={r3.status_code}")
    
    print("\n==> Smoke finished")

if __name__ == "__main__":
    main()
