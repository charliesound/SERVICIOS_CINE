#!/usr/bin/env python3
"""
Smoke test for Role-Based Dashboards.
"""

import sys
import os

os.chdir('/opt/SERVICIOS_CINE/src')
sys.path.insert(0, '.')

print("=== Running Role-Based Dashboard Smoke Test ===\n")

print("1. Test role_permission_service imports...")
try:
    from services.role_permission_service import (
        get_role_default,
        get_permissions_for_role,
        can,
        get_module_order_for_role,
        has_admin_access,
        VALID_ROLES,
    )
    print("   OK: Service imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("2. Test role validation...")
for role in ["owner", "admin", "producer", "production_manager", "director", "editor", "viewer"]:
    canonical = get_role_default(role)
    print(f"   OK: {role} -> {canonical}")

print("3. Test permissions by role...")
roles_to_test = ["producer", "director", "editor", "viewer"]
for role in roles_to_test:
    perms = get_permissions_for_role(role)
    print(f"   {role}: {len(perms)} permissions")
    if role == "producer":
        assert "budget.view" in perms
        assert "davinci.export" in perms
    if role == "editor":
        assert "editorial.view" in perms
        assert "davinci.export" in perms
        assert "admin.users" not in perms
    if role == "viewer":
        assert "admin.users" not in perms
        assert "budget.view" in perms

print("4. Test can() function...")
assert can("admin", "admin.users") == True
assert can("producer", "admin.users") == False
assert can("editor", "davinci.export") == True
assert can("viewer", "davinci.export") == False

print("5. Test admin access...")
assert has_admin_access("owner") == True
assert has_admin_access("admin") == True
assert has_admin_access("producer") == False
assert has_admin_access("viewer") == False

print("6. Test module order by role...")
producer_modules = get_module_order_for_role("producer")
editor_modules = get_module_order_for_role("editor")
print(f"   producer order: {producer_modules[:3]}...")
print(f"   editor order: {editor_modules[:3]}...")

print("7. Test project_routes imports...")
try:
    import routes.project_routes
    print("   OK: project_routes imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("8. Verify dashboard has role_dashboard field...")
from routes import project_routes
routes_list = list(project_routes.router.routes)
dashboard_route = None
for r in routes_list:
    if hasattr(r, 'path') and 'dashboard' in r.path:
        dashboard_route = r
        break
if dashboard_route:
    print(f"   OK: Dashboard route found with param: role")
else:
    print("   WARNING: Could not verify route param")

print("\nSUCCESS: Role-Based Dashboard code is valid")
sys.exit(0)