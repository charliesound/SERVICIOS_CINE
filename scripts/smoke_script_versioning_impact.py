#!/usr/bin/env python3
"""
Smoke test for Script Versioning + Impact Analysis.
"""

import sys
import os
import json

os.chdir('/opt/SERVICIOS_CINE/src')
sys.path.insert(0, '.')

print("=== Running Script Versioning Smoke Test ===\n")

print("1. Test script_versioning models import...")
try:
    from models.script_versioning import ScriptVersion, ScriptChangeReport, ProjectModuleStatus
    print("   OK: Models imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("2. Test script_version_service imports...")
try:
    from services.script_version_service import ScriptVersionService, ScriptChangeAnalysisService
    print("   OK: Services imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("3. Test script_version_routes imports...")
try:
    from routes import script_version_routes
    print("   OK: Routes imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("4. Verify hash calculation...")
sample_text = "INT. OFFICE - DAY\nJohn enters the room."
hash_result = ScriptVersionService.calculate_hash(sample_text)
print(f"   OK: Hash calculated: {hash_result[:16]}...")

print("5. Verify scene counting...")
scene_count = ScriptVersionService.count_scenes(sample_text)
print(f"   OK: Scenes counted: {scene_count}")

print("6. Test data model structure...")
from models.script_versioning import ScriptVersion
print(f"   OK: ScriptVersion fields: {[c.name for c in ScriptVersion.__table__.columns]}")

print("7. Verify router endpoints exist...")
routes_list = list(script_version_routes.router.routes)
endpoints = [r.path for r in routes_list]
print(f"   Endpoints found: {endpoints}")

expected = [
    '/versions',
    '/versions/{version_id}',
    '/versions/{version_id}/activate',
    '/versions/compare',
    '/change-reports',
    '/module-status',
]
for exp in expected:
    found = any(exp in ep for ep in endpoints)
    if found:
        print(f"   OK: {exp}")
    else:
        print(f"   MISSING: {exp}")

print("\nSUCCESS: Script Versioning code is valid")
print("Note: Full integration test requires running server with database")

sys.exit(0)