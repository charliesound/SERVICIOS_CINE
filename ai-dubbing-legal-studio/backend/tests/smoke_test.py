#!/usr/bin/env python
"""Smoke test rápido del sistema"""

import requests
import json

BASE = "http://localhost:8000"
email = "smoke@test.com"
password = "test123"

def log(label, result):
    status = "✅" if result else "❌"
    print(f"{status} {label}")

# 1. Health
r = requests.get(f"{BASE}/health")
log("Health check", r.status_code == 200 and r.json().get("status") == "ok")

# 2. Register
r = requests.post(f"{BASE}/api/auth/register", json={
    "email": email, "password": password, "name": "Smoke Test", "role": "admin"
})
log("Register user", r.status_code == 200)
token = None
if r.status_code == 200:
    # Login
    r = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": password})
    log("Login", r.status_code == 200)
    token = r.json().get("access_token")
else:
    r = requests.post(f"{BASE}/api/auth/login", json={"email": email, "password": password})
    token = r.json().get("access_token")

headers = {"Authorization": f"Bearer {token}"}

# 3. Create project
r = requests.post(f"{BASE}/api/projects", json={"name": "Test Proyecto"}, headers=headers)
log("Create project", r.status_code == 200)
project_id = r.json().get("id")

# 4. List projects
r = requests.get(f"{BASE}/api/projects", headers=headers)
log("List projects", r.status_code == 200 and len(r.json()) > 0)

# 5. Create actor
r = requests.post(f"{BASE}/api/actors", json={"name": "Test Actor", "voice_language": "es"}, headers=headers)
log("Create actor", r.status_code == 200)
actor_id = r.json().get("id")

# 6. Create contract
r = requests.post(f"{BASE}/api/contracts", json={
    "actor_id": actor_id,
    "contract_ref": "SMOKE-001",
    "signed_date": "2026-01-01T00:00:00Z",
    "expiry_date": "2027-01-01T00:00:00Z",
    "ia_consent": True,
    "allowed_languages": ["es", "en"],
    "allowed_territories": ["ES", "MX"],
    "allowed_usage_types": ["dubbing"],
}, headers=headers)
log("Create contract", r.status_code == 200)
contract_id = r.json().get("id")

# 7. Validate contract (should pass)
r = requests.post(f"{BASE}/api/contracts/{contract_id}/validate", json={
    "mode": "voz_original_ia_autorizada", "language": "es", "territory": "ES", "usage_type": "dubbing"
}, headers=headers)
log("Validate contract (pass)", r.status_code == 200 and r.json().get("blocked") == False)

# 8. Create dubbing job
r = requests.post(f"{BASE}/api/dubbing-jobs/project/{project_id}", json={
    "mode": "voz_original_ia_autorizada",
    "source_language": "es",
    "target_language": "en",
    "contract_id": contract_id,
    "actor_id": actor_id,
}, headers=headers)
log("Create dubbing job", r.status_code == 200)
job_id = r.json().get("id")

# 9. Start job
r = requests.post(f"{BASE}/api/dubbing-jobs/{job_id}/start", headers=headers)
log("Start dubbing job", r.status_code == 200)

# 10. Check audit
r = requests.get(f"{BASE}/api/audit/job/{job_id}", headers=headers)
log("Audit log exists", r.status_code == 200 and len(r.json()) > 0)

print(f"\nProject ID: {project_id}")
print(f"Contract ID: {contract_id}")
print(f"Job ID: {job_id}")
print("\nSmoke test completado.")
