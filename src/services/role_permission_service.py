"""
Role permission service for CID.
Defines permissions and role-based access control.
"""

from typing import Optional


VALID_ROLES = [
    "owner",
    "admin",
    "producer",
    "production_manager",
    "director",
    "editor",
    "viewer",
]

PERMISSIONS_BY_ROLE = {
    "owner": [
        "project.view",
        "project.edit",
        "project.delete",
        "script.view",
        "script.edit",
        "script.version.create",
        "script.version.activate",
        "storyboard.view",
        "storyboard.generate",
        "breakdown.view",
        "breakdown.edit",
        "budget.view",
        "budget.generate",
        "budget.edit",
        "funding.view",
        "funding.manage",
        "producer_pack.view",
        "producer_pack.generate",
        "distribution.view",
        "distribution.manage",
        "crm.view",
        "crm.manage",
        "media.scan",
        "media.view",
        "documents.ingest",
        "documents.approve",
        "reports.view",
        "reports.edit",
        "editorial.view",
        "editorial.reconcile",
        "editorial.score",
        "editorial.assembly",
        "davinci.export",
        "admin.users",
        "admin.settings",
    ],
    "admin": [
        "project.view",
        "project.edit",
        "script.view",
        "script.edit",
        "script.version.create",
        "script.version.activate",
        "storyboard.view",
        "storyboard.generate",
        "breakdown.view",
        "breakdown.edit",
        "budget.view",
        "budget.generate",
        "budget.edit",
        "funding.view",
        "funding.manage",
        "producer_pack.view",
        "producer_pack.generate",
        "distribution.view",
        "distribution.manage",
        "crm.view",
        "crm.manage",
        "media.scan",
        "media.view",
        "documents.ingest",
        "documents.approve",
        "reports.view",
        "reports.edit",
        "editorial.view",
        "editorial.reconcile",
        "editorial.score",
        "editorial.assembly",
        "davinci.export",
        "admin.users",
        "admin.settings",
    ],
    "producer": [
        "project.view",
        "script.view",
        "script.version.create",
        "storyboard.view",
        "breakdown.view",
        "budget.view",
        "budget.generate",
        "funding.view",
        "funding.manage",
        "producer_pack.view",
        "producer_pack.generate",
        "distribution.view",
        "crm.view",
        "crm.manage",
        "media.view",
        "documents.ingest",
        "reports.view",
        "editorial.view",
        "davinci.export",
    ],
    "production_manager": [
        "project.view",
        "script.view",
        "storyboard.view",
        "breakdown.view",
        "breakdown.edit",
        "budget.view",
        "funding.view",
        "producer_pack.view",
        "distribution.view",
        "media.scan",
        "media.view",
        "documents.ingest",
        "documents.approve",
        "reports.view",
        "reports.edit",
        "editorial.view",
    ],
    "director": [
        "project.view",
        "script.view",
        "script.edit",
        "script.version.create",
        "script.version.activate",
        "storyboard.view",
        "storyboard.generate",
        "breakdown.view",
        "budget.view",
        "funding.view",
        "producer_pack.view",
        "media.view",
        "document.view",
        "reports.view",
        "editorial.view",
    ],
    "editor": [
        "project.view",
        "script.view",
        "storyboard.view",
        "breakdown.view",
        "budget.view",
        "funding.view",
        "producer_pack.view",
        "media.view",
        "documents.ingest",
        "reports.view",
        "editorial.view",
        "editorial.reconcile",
        "editorial.score",
        "editorial.assembly",
        "davinci.export",
    ],
    "viewer": [
        "project.view",
        "script.view",
        "storyboard.view",
        "breakdown.view",
        "budget.view",
        "funding.view",
        "producer_pack.view",
        "media.view",
        "reports.view",
        "editorial.view",
    ],
}

PERMISSION_GROUPS = {
    "script": [
        "script.view",
        "script.edit",
        "script.version.create",
        "script.version.activate",
    ],
    "storyboard": [
        "storyboard.view",
        "storyboard.generate",
    ],
    "budget": [
        "budget.view",
        "budget.generate",
        "budget.edit",
    ],
    "funding": [
        "funding.view",
        "funding.manage",
    ],
    "producer_pack": [
        "producer_pack.view",
        "producer_pack.generate",
    ],
    "distribution": [
        "distribution.view",
        "distribution.manage",
    ],
    "crm": [
        "crm.view",
        "crm.manage",
    ],
    "media": [
        "media.scan",
        "media.view",
    ],
    "documents": [
        "documents.ingest",
        "documents.approve",
    ],
    "reports": [
        "reports.view",
        "reports.edit",
    ],
    "editorial": [
        "editorial.view",
        "editorial.reconcile",
        "editorial.score",
        "editorial.assembly",
    ],
    "davinci": [
        "davinci.export",
    ],
    "admin": [
        "admin.users",
        "admin.settings",
    ],
}

CRITICAL_ACTIONS = [
    "script.version.activate",
    "budget.generate",
    "producer_pack.generate",
    "distribution.manage",
    "crm.manage",
    "davinci.export",
    "admin.users",
    "admin.settings",
]

DASHBOARD_MODULE_ORDER = {
    "producer": [
        "script",
        "budget",
        "funding",
        "producer_pack",
        "distribution",
        "crm",
        "editorial",
        "storyboard",
        "media",
        "reports",
        "breakdown",
    ],
    "production_manager": [
        "breakdown",
        "budget",
        "reports",
        "media",
        "documents",
        "script",
        "storyboard",
        "editorial",
    ],
    "director": [
        "script",
        "storyboard",
        "breakdown",
        "budget",
        "producer_pack",
        "media",
        "reports",
    ],
    "editor": [
        "media",
        "reports",
        "editorial",
        "script",
        "storyboard",
        "breakdown",
        "budget",
    ],
    "admin": [
        "script",
        "storyboard",
        "breakdown",
        "budget",
        "funding",
        "producer_pack",
        "distribution",
        "crm",
        "media",
        "documents",
        "reports",
        "editorial",
    ],
    "viewer": [
        "script",
        "storyboard",
        "breakdown",
        "budget",
        "producer_pack",
        "media",
        "reports",
        "editorial",
    ],
}

DEFAULT_ROLE = "viewer"


def get_role_default(user_role: Optional[str]) -> str:
    """Get the canonical role from user role field."""
    if not user_role:
        return DEFAULT_ROLE
    
    if user_role in VALID_ROLES:
        return user_role
    
    role_map = {
        "admin": "admin",
        "owner": "owner",
        "producer": "producer",
        "manager": "production_manager",
        "director": "director",
        "editor": "editor",
        "user": "viewer",
        "viewer": "viewer",
    }
    
    return role_map.get(user_role, DEFAULT_ROLE)


def get_permissions_for_role(role: str) -> list[str]:
    """Get list of permissions for a role."""
    canonical_role = get_role_default(role)
    return PERMISSIONS_BY_ROLE.get(canonical_role, [])


def can(role: str, permission: str) -> bool:
    """Check if role has specific permission."""
    permissions = get_permissions_for_role(role)
    return permission in permissions


def filter_actions_by_permissions(actions: list[dict], role: str) -> list[dict]:
    """Filter actions based on role permissions."""
    permissions = get_permissions_for_role(role)
    
    filtered = []
    for action in actions:
        perm = action.get("permission")
        if not perm or perm in permissions:
            filtered.append(action)
        else:
            filtered.append({
                **action,
                "locked": True,
                "reason": "permission_denied",
            })
    
    return filtered


def get_module_order_for_role(role: str) -> list[str]:
    """Get module display order for a role."""
    canonical_role = get_role_default(role)
    return DASHBOARD_MODULE_ORDER.get(canonical_role, [])


def is_critical_permission(permission: str) -> bool:
    """Check if permission is critical/sensitive."""
    return permission in CRITICAL_ACTIONS


def get_user_dashboard_roles(user_role: Optional[str], available_dashboards: list[str] = None) -> list[str]:
    """Get available dashboard roles for a user."""
    canonical_role = get_role_default(user_role)
    
    if canonical_role in ["owner", "admin"]:
        if available_dashboards:
            return [r for r in available_dashboards if r in VALID_ROLES]
        return VALID_ROLES
    
    return [canonical_role]


def has_admin_access(role: str) -> bool:
    """Check if role has admin access."""
    return role in ["owner", "admin"]