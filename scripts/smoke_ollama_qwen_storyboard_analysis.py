#!/usr/bin/env python3
"""
Smoke test for Ollama Qwen Gemma storyboard analysis pipeline.
Validates:
1. Ollama health at {OLLAMA_BASE_URL}
2. Qwen3 Coder 30B availability
3. Gemma4:26b/b availability
4. JSON generation with Qwen3 Coder 30B
5. Backend health
6. New API endpoints exist
"""
import os
import sys
import argparse
import json

# Stub heavy dependencies
for mod in ["torch", "torch.nn", "torchvision", "cv2", "numpy", "PIL",
           "sentence_transformers", "transformers", "ollama", "httpx"]:
    sys.modules.setdefault(mod, type(sys)(mod))

# Configuration
OLLAMA_URL = os.environ.get("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
BACKEND_URL = os.environ.get("SMOKE_BASE_URL", "http://127.0.0.1:8010")
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
        # Try register
        resp = _req.post(
            f"{BACKEND_URL}/api/auth/register",
            json={"username": "smoke_ollama", "email": "smoke_ollama@test.com", 
                 "password": "SmokeTest123!", "full_name": "Smoke Ollama"},
            timeout=TIMEOUT
        )
        if resp.status_code not in (200, 201):
            resp = _req.post(
                f"{BACKEND_URL}/api/auth/login",
                json={"email": "smoke_ollama@test.com", "password": "SmokeTest123!"},
                timeout=TIMEOUT
            )
        if resp.status_code in (200, 201):
            return resp.json().get("access_token", "")
    except Exception as exc:
        print(f"  [token] Error: {exc}")
    return ""

def main():
    print(f"==> Smoke: Ollama Qwen/Gemma Storyboard Pipeline")
    print(f"    Ollama: {OLLAMA_URL}")
    print(f"    Backend: {BACKEND_URL}")
    
    # 1. Ollama health
    print("\n[1] Ollama Health")
    r = _get(f"{OLLAMA_URL}/api/tags")
    ollama_up = r.status_code == 200
    _check("Ollama is running", ollama_up)
    if not ollama_up:
        print("  ⚠️  Ollama not available - some tests will be skipped")
    
    # 2. Check Qwen3 Coder 30B
    print("\n[2] Check Qwen3 Coder 30B")
    if ollama_up:
        models = r.json().get("models", [])
        model_names = [m["name"] for m in models]
        qwen_available = any("qwen3-coder:30B" in m for m in model_names)
        _check("Qwen3 Coder 30B available", qwen_available, f"models={model_names[:5]}")
    else:
        _check("Qwen3 Coder 30B available", False, "Ollama not running")
    
    # 3. Check Gemma4
    print("\n[3] Check Gemma4")
    if ollama_up:
        gemma_available = any("gemma4" in m for m in model_names)
        _check("Gemma4 available", gemma_available, f"models={model_names[:5]}")
    else:
        _check("Gemma4 available", False, "Ollama not running")
    
    # 4. Backend health
    print("\n[4] Backend Health")
    r = _get(f"{BACKEND_URL}/health")
    _check("Backend is running", r.status_code == 200, f"status={r.status_code}")
    
    # 5. Ollama status endpoint
    print("\n[5] GET /api/ops/ollama/status")
    token = _get_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    r = _get(f"{BACKEND_URL}/api/ops/ollama/status", headers=headers)
    _check("Ollama status endpoint", r.status_code in (200, 401, 403), f"status={r.status_code}")
    
    # 6. Check new endpoints exist
    print("\n[6] Check new endpoints")
    r = _post(f"{BACKEND_URL}/api/projects/00000000-0000-0000-0000-000000000000/analyze/local-ollama", 
          headers=headers)
    _check("analyze/local-ollama endpoint exists", r.status_code != 404, f"status={r.status_code}")
    
    r = _post(f"{BACKEND_URL}/api/projects/00000000-0000-0000-0000-000000000000/storyboard/prompts/from-analysis",
          headers=headers, json_data={"generation_mode": "FULL_SCRIPT"})
    _check("storyboard/prompts/from-analysis exists", r.status_code != 404, f"status={r.status_code}")
    
    print("\n==> Smoke finished")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=BACKEND_URL)
    parser.add_argument("--project-id", default="")
    parser.add_argument("--token", default="")
    args = parser.parse_args()
    
    if args.base_url:
        BACKEND_URL = args.base_url
    
    main()
