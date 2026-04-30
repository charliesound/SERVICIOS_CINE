#!/usr/bin/env python3
"""
Smoke test for Project Access Control (ProjectMember delegation).
"""

import sys
import os

os.chdir('/opt/SERVICIOS_CINE/src')
sys.path.insert(0, '.')

print("=== Running Project Access Control Smoke Test ===\n")

print("1. Test ProjectMember model imports...")
try:
    from models.project_member import (
        ProjectMember,
        PROFESSIONAL_ROLES,
        PROJECT_PERMISSIONS,
        ROLE_DEFAULT_PERMISSIONS,
    )
    print("   OK: ProjectMember model imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("2. Test professional roles...")
expected_roles = ["owner", "producer", "director", "editor", "viewer"]
for role in expected_roles:
    assert role in PROFESSIONAL_ROLES, f"Missing role: {role}"
print(f"   OK: {len(PROFESSIONAL_ROLES)} roles defined")

print("3. Test permission constants...")
assert len(PROJECT_PERMISSIONS) > 20, "Should have many permissions"
assert "project.permissions.delegate" in PROJECT_PERMISSIONS
assert "project.permissions.manage" in PROJECT_PERMISSIONS
print(f"   OK: {len(PROJECT_PERMISSIONS)} permissions")

print("4. Test role default permissions...")
assert "owner" in ROLE_DEFAULT_PERMISSIONS
assert "producer" in ROLE_DEFAULT_PERMISSIONS
producer_perms = ROLE_DEFAULT_PERMISSIONS["producer"]
assert "project.permissions.delegate" in producer_perms
assert "project.permissions.manage" in producer_perms
print(f"   producer has {len(producer_perms)} permissions")

viewer_perms = ROLE_DEFAULT_PERMISSIONS["viewer"]
assert "project.permissions.delegate" not in viewer_perms
print(f"   viewer has {len(viewer_perms)} permissions (no delegation)")

print("5. Test project_access_service imports...")
try:
    from services.project_access_service import (
        get_project_member,
        get_project_members,
        add_project_member,
        delegate_permissions,
        get_effective_permissions,
        check_permission,
        can_manage_project_members,
        can_delegate_permissions,
        is_project_owner,
    )
    print("   OK: Service imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("6. Test project_member_routes imports...")
try:
    import routes.project_member_routes
    print("   OK: Routes imported")
except Exception as e:
    print(f"   FAIL: {e}")
    sys.exit(1)

print("7. Test app includes project members router...")
from app import app
route_paths = [r.path for r in app.routes if hasattr(r, 'path')]
member_routes = [p for p in route_paths if '/members' in p]
assert len(member_routes) > 0, "No member routes found"
print(f"   OK: Found {len(member_routes)} member route(s)")
print(f"      Example: {member_routes[0]}")

print("\nSUCCESS: Project Access Control code is valid")
sys.exit(0)