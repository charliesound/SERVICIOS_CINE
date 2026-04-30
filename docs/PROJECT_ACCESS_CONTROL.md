# Project Access Control: Productor Delega Permisos

## Overview

CID supports **delegated permission management** within projects. The primary authority (owner/productor) can delegate permission management to production directors and other team members.

## Key Concepts

### ProjectMember Model

Each project member has:
- `professional_role`: The role on the production (owner, producer, director, editor, etc.)
- `can_manage_permissions`: Boolean flag - can delegate/revoke permissions
- `can_manage_members`: Boolean flag - can add/remove members
- `permissions_json`: Optional custom permissions list

### Primary Authority

- **Owner**: Full control (cannot be removed)
- **Productor**: Has permission delegation by default

### Delegation Model

Only the owner or producer with `can_manage_permissions=true` can:
- Grant `can_manage_permissions` to other members
- Grant `can_manage_members` to other members

## Professional Roles

| Role | Default Permissions |
|------|----------------|
| owner | All permissions |
| producer | Full project access + delegation |
| executive_producer | View + delegation (limited) |
| production_manager | Breakdown, budget, media |
| director | Script, storyboard, editorial |
| editor | Editorial, DaVinci export |
| viewer | View only |

## API Endpoints

### List Members

```
GET /api/projects/{project_id}/members
```

### Get My Member Info

```
GET /api/projects/{project_id}/members/me
Returns: { member, permissions, can_manage_members, can_delegate, is_owner }
```

### Add Member

```
POST /api/projects/{project_id}/members
Body: { user_id, professional_role, can_manage_permissions, can_manage_members }
```

### Update Member

```
PATCH /api/projects/{project_id}/members/{user_id}
Body: { professional_role?, can_manage_permissions?, can_manage_members? }
```

### Remove Member

```
DELETE /api/projects/{project_id}/members/{user_id}
```

### Delegate Permissions

```
POST /api/projects/{project_id}/members/delegate
Body: { target_user_id, can_manage_permissions }
```

### Get Member Permissions

```
GET /api/projects/{project_id}/members/{user_id}/permissions
```

## Security Rules

1. Owner cannot be removed
2. Only owner/producer can delegate permissions
3. Permission check on all endpoints
4. Role-based permission matrix in `ROLE_DEFAULT_PERMISSIONS`

## Files Created

- `/src/models/project_member.py` - Model + constants
- `/src/services/project_access_service.py` - Service methods
- `/src/routes/project_member_routes.py` - API endpoints
- `/src_frontend/src/api/projectMembers.ts` - Frontend API
- `/src_frontend/src/pages/ProjectMembersPage.tsx` - UI page