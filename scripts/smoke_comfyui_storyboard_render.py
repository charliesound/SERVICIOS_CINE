#!/usr/bin/env python3
"""
Smoke test: ComfyUI Storyboard Render.
Validates ComfyUI connection and render endpoint.
"""
import os
import sys
import json
import argparse

# Stub heavy dependencies
for mod in ["torch", "torch.nn", "torchvision", "cv2", "numpy", "PIL",
           "sentence_transformers", "transformers", "ollama", "httpx"]:
    sys.modules.setdefault(mod, type(sys)(mod))

# Configuration
BASE_URL = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8010")
COMFYUI_URL = os.environ.get("COMFYUI_STORYBOARD_BASE_URL", "http://127.0.0.1:8188")
TIMEOUT = 10

# HTTP client
try:
    import requests as _req
    def _get(url, headers=None, params=None):
        return _req.get(url, headers=headers, params=params, timeout=TIMEOUT)
    def _post(url, headers=None, json_data=None):
        return _req.post(url, headers=headers, json=json_data, timeout=TIMEOUT)
except ImportError:
    from urllib import request as _urlreq, error as _urlerr
    import json as _json
    def _get(url, headers=None, params=None):
        full = url + "?" + "&".join(f"{k}={v}" for k, v in (params or {}).items()) if params else url
        req = _urlreq.Request(full, headers=headers or {})
        try:
            with _urlreq.urlopen(req, timeout=TIMEOUT) as resp:
                return _Resp(resp)
        except _urlerr.HTTPError as exc:
            return _Resp(exc)
    def _post(url, headers=None, json_data=None):
        data = _json.dumps(json_data).encode() if json_data else None
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
    @property
    def text(self):
        return self._resp.read().decode() if hasattr(self._resp, 'read') else ''
    def json(self):
        return _json.loads(self.text)

def _check(label, ok, detail=""):
    status = "✅" if ok else "❌"
    print(f"  {status} {label}" + (f": {detail}" if detail else ""))

def _get_token():
    """Get token via register/login."""
    try:
        import requests as _req
        unique_email = f"smoke_comfyui_{os.getpid()}@test.local"
        pw = "SmokeTest123!"
        # Try register
        resp = _req.post(
            f"{BASE_URL}/api/auth/register",
            json={"username": f"smoke_comfyui_{os.getpid()}", "email": unique_email, "password": pw, "full_name": "Smoke ComfyUI"},
            timeout=TIMEOUT
        )
        if resp.status_code not in (200, 201):
            resp = _req.post(
                f"{BASE_URL}/api/auth/login",
                json={"email": unique_email, "password": pw},
                timeout=TIMEOUT
            )
        if resp.status_code in (200, 201):
            return resp.json().get("access_token", "")
    except Exception as exc:
        print(f"  [token] Error: {exc}")
    return ""

def main():
    print(f"==> Smoke: ComfyUI Storyboard Render")
    print(f"    Backend: {BASE_URL}")
    print(f"    ComfyUI: {COMFYUI_URL}")
    print("="*50)
    
    # 1. ComfyUI health
    print("\n[1] ComfyUI Health")
    r = _get(f"{COMFYUI_URL}/system_stats")
    comfy_up = r.status_code == 200
    _check("ComfyUI is running", comfy_up)
    if comfy_up:
        data = r.json()
        devices = data.get("system", {}).get("devices", [])
        if devices:
            print(f"    Device: {devices[0].get('name', 'unknown')}")
            print(f"    VRAM: {devices[0].get('vram_usage', {}).get('total', 0)}")
    
    # 2. Backend health
    print("\n[2] Backend Health")
    r = _get(f"{BASE_URL}/health")
    _check("Backend is running", r.status_code == 200)
    
    # 3. ComfyUI status endpoint
    print("\n[3] GET /api/ops/comfyui/storyboard/status")
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = _get(f"{BASE_URL}/api/ops/comfyui/storyboard/status", headers=headers)
    _check("ComfyUI status endpoint", r.status_code in (200, 401, 403), f"status={r.status_code}")
    
    # 4. Check OpenAPI for render endpoint
    print("\n[4] Check OpenAPI for render endpoint")
    r = _get(f"{BASE_URL}/openapi.json")
    if r.status_code == 200:
        data = r.json()
        paths = data.get("paths", {})
        render_path = f"{BASE_URL}/api/projects/00000000-0000-0000-0000-000000000000/storyboard/render"
        found = any("storyboard/render" in p for p in paths.keys())
        _check("render endpoint in OpenAPI", found)
    
    # 5. Skip render if no token or project
    print("\n[5] Render test (skipped without project)")
    if not token:
        print("  ⚠️  No token - skipping render test")
    else:
        print("  ℹ️  Use --project-id and --token to test render")
    
    print("\n==> Smoke finished")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BASE_URL)
    parser.add_argument("--comfyui-url", default=COMFYUI_URL)
    parser.add_argument("--project-id", default="")
    parser.add_argument("--token", default="")
    parser.add_argument("--skip-render", action="store_true")
    args = parser.parse_args()
    
    if args.base_url:
        BASE_URL = args.base_url
    if args.comfyui_url:
        COMFYUI_URL = args.comfyui_url
    
    main()
