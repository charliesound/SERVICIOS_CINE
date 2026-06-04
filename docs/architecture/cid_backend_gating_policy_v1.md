# CID Backend Gating Policy v1

## Objective
Establish the requirements for backend gating (permissions/authorization)
in CID. Frontend-only gating (`PlanRoute.tsx`) is insufficient — all
critical endpoints must validate access server-side before serving data.

## Current state (verified)

### Frontend gating (exists)
- `PlanRoute.tsx`: checks `canAccessProgram(user, program)`
- Hierarchy: `demo < creator < producer < studio < enterprise`
- `canAccessCID(user)`: verifies signup_type, account_status, cid_enabled
- Applied in `App.tsx` on `/cid/{program}` routes

### Backend gating (DOES NOT EXIST)
- `billing_plan` exists in `User` and `OrganizationMember` models
- `program` exists in `User` model
- `PROFESSIONAL_ROLES` defined in `models/project_member.py`
- `plan_routes.py` has plan management endpoints
- `plan_limits_service.py` has limit checking
- **No endpoint validates billing_plan, program, or role**
- No middleware applies authorization by plan or role
- `admin_routes.py` uses billing_plan only for filters

## Policy

### 1. All critical endpoints MUST validate backend ownership/access
Every endpoint must verify at minimum:
- `organization_id` — user belongs to the org
- `project_id` — project belongs to the org
- `user_id` — user is a member of the project

### 2. Plan gating
Endpoints serving plan-dependent features MUST validate:
- `billing_plan` — user/org has the required plan
- `program` — user has the required program level
- Module access per plan configuration (`plans.yml` / `modules.yml`)

### 3. Role gating
Endpoints for role-specific actions MUST validate:
- `professional_role` — from `ProjectMember.PROFESSIONAL_ROLES`
- Permissions per role: read/create/update/delete per module/phase
- Access model defined in `docs/product/cid_project_access_model_v1.md`

### 4. Implementation pattern (future phase)
```python
# Proposed reusable dependency
from dependencies.gating import require_plan, require_role, require_project_access

@router.get("/projects/{project_id}/budget")
async def get_budget(
    project: Project = Depends(require_project_access),
    user: User = Depends(require_plan("producer")),
    role: str = Depends(require_role("producer", "owner")),
):
    ...
```

### 5. Plans and their limits

| Plan | Access scope | Key modules |
|---|---|---|
| Demo | Read-only, limited projects | Dashboard, script analysis (preview) |
| Creator (9.99€) | Rama 2 basic | Script, breakdown, storyboard (limited) |
| Producer (19.99€) | Rama 1 + 2 | Full prepro, budget, funding |
| Studio (29.99€) | Rama 1 + 2 + 3 partial | + Rodaje, editorial, distribution |
| Enterprise (99.99€) | All | Full access, custom roles |

*Note: These are current code plans. Commercial target differs (see
`cid_pricing_canonicalization_needed_v1.md`).*

### 6. What NOT to do yet
- Do NOT implement the gating dependency now
- Do NOT modify any endpoint signatures
- Do NOT remove `PlanRoute.tsx` or frontend gating
- Do NOT change `billing_plan` defaults in models

## References
- `src_frontend/src/components/PlanRoute.tsx` — frontend-only gating
- `src/models/core.py` — User.billing_plan, User.program
- `src/models/project_member.py` — ProjectMember, PROFESSIONAL_ROLES
- `src/config/plans.yml` — plan definitions
- `src/routes/plan_routes.py` — plan management endpoints
- `docs/product/cid_project_access_model_v1.md` — access model v1
- `CID.BASELINE.SAFETY.CANONICALIZATION.1` section 8
