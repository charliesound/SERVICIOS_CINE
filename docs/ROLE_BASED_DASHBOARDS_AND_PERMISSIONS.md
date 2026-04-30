# Role-Based Dashboards + Permissions

## Overview

CID now supports role-based dashboards and permissions. Each user sees relevant modules and actions based on their professional role.

## Roles Defined

| Role | Description | Dashboard Priority |
|------|-------------|---------------------|
| owner | Project owner / admin | All modules, full control |
| admin | Admin user | All modules, most actions |
| producer | Producer | Budget, funding, producer pack, distribution, CRM |
| production_manager | Production manager | Breakdown, reports, media, documents |
| director | Director | Script, storyboard, notes |
| editor | Editor / montador | Media, reports, editorial, DaVinci export |
| viewer | Read-only access | View only, no actions |

## Permissions by Role

### Owner/Admin
- All project permissions
- Manage users
- Admin settings

### Producer
- View script, budget, funding, producer pack, distribution, CRM
- Generate budgets
- Export to DaVinci
- No admin permissions

### Production Manager
- View/Edit breakdown
- Ingest documents
- Scan media
- View reports

### Director
- View/Edit script
- Generate storyboard
- View budget
- No admin/critical actions

### Editor
- View all modules
- Reconcile, score, assemble
- Export to DaVinci
- No funding/CRM management

### Viewer
- View only
- No critical actions
- No management permissions

## API Endpoints

Dashboard accepts optional `role` parameter:

```
GET /api/projects/{project_id}/dashboard
GET /api/projects/{project_id}/dashboard?role=producer
```

Response includes:

```json
{
  "project_id": "...",
  "title": "...",
  "overall_progress": 45,
  "modules": {...},
  "recommended_next_actions": [...],
  "role_dashboard": {
    "active_role": "producer",
    "available_roles": ["producer", "admin"],
    "permissions": [...],
    "user_role": "producer"
  }
}
```

## Frontend

- Shows current role in dashboard header
- Actions marked as "Sin permiso" if locked
- Permissions badge shows permission count

## Impact Analysis

When role changes:
- Module order reprioritized for role
- Actions filtered by permissions
- Recommended actions show locked/unlocked state

## What's NOT Done

- Full backend permission enforcement on all endpoints (future sprint)
- User role management UI
- Organization-level role overrides