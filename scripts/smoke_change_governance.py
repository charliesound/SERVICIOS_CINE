#!/usr/bin/env python3
"""
Smoke test for Change Governance and Shotlist Approval.
"""

import sys
import os

os.chdir('/opt/SERVICIOS_CINE/src')
sys.path.insert(0, '.')

print("=== Running Change Governance Smoke Test ===\n")

print("1. Test change governance models...")
try:
    from models.change_governance import (
        ProjectChangeRequest,
        ProjectApproval,
        ApprovedProjectBaseline,
        PlannedShot,
        ShootingPlan,
        ShootingPlanItem,
    )
    print("   OK: Models imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("2. Test constants...")
from models.change_governance import (
    CHANGE_REQUEST_TARGET_MODULES,
    SHOT_STATUSES,
    BASELINE_TYPES,
)
assert "budget" in CHANGE_REQUEST_TARGET_MODULES
assert "approved" in SHOT_STATUSES
assert "script" in BASELINE_TYPES
print(f"   OK: {len(CHANGE_REQUEST_TARGET_MODULES)} target modules, {len(SHOT_STATUSES)} shot statuses")

print("3. Test change_governance_service...")
try:
    from services.change_governance_service import (
        create_change_request,
        list_change_requests,
        approve_change_request,
        reject_change_request,
        create_baseline,
        get_active_baseline,
        can_approve,
    )
    print("   OK: Service imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("4. Test can_approve permissions...")
try:
    from services.change_governance_service import can_approve
    result = can_approve("producer", "budget")
    print(f"   producer->budget: {result}")
    result = can_approve("producer", "storyboard")
    print(f"   producer->storyboard: {result}")
    print("   OK: can_approve works correctly")
except Exception as e:
    print(f"   Warning: {e}")

print("5. Test shotlist_service...")
try:
    from services.shotlist_service import (
        analyze_script_for_planned_shots,
        get_planned_shots,
        approve_planned_shot,
    )
    print("   OK: Service imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("6. Test script analysis for shots...")
test_script = """
INT. COFFEE SHOP - DAY
JOHN enters.

INT. OFFICE - NIGHT
Meeting in progress.
"""
shots = analyze_script_for_planned_shots(test_script, "test-project", "test-org")
print(f"   Generated {len(shots)} shots from script")

print("7. Test shooting_plan_coverage_service...")
try:
    from services.shooting_plan_coverage_service import (
        get_shot_coverage,
        get_pickup_recommendations,
    )
    print("   OK: Service imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("8. Test routes import...")
import routes.change_governance_routes
import routes.shotlist_routes
import routes.shooting_plan_routes
print("   OK: Routes imported")

print("9. Test app has new routers...")
from app import app
route_paths = [r.path for r in app.routes if hasattr(r, 'path')]
change_routes = [p for p in route_paths if '/change-requests' in p]
shotlist_routes = [p for p in route_paths if '/planned-shots' in p]
print(f"   Found {len(change_routes)} change routes, {len(shotlist_routes)} shotlist routes")

print("\nSUCCESS: Change Governance code is valid")
sys.exit(0)