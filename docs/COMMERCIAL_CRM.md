# Commercial CRM - Technical Specification

## Overview

Commercial CRM provides basic opportunity tracking and contact management for commercial follow-up.

**Status**: IMPLEMENTED

---

## Models

### `src/models/crm.py`

| Model | Table | Purpose |
|-------|-------|--------|
| `CRMContact` | `crm_contacts` | Contact/company management |
| `CRMOpportunity` | `crm_opportunities` | Project opportunities |
| `CRMCommunication` | `crm_communications` | Communication history |
| `CRMTask` | `crm_tasks` | Follow-up tasks |

---

## Routes

### `src/routes/crm_routes.py`

| Method | Endpoint | Purpose |
|--------|---------|---------|
| GET | `/api/crm/contacts` | List contacts |
| POST | `/api/crm/contacts` | Create contact |
| GET | `/api/crm/contacts/{id}` | Get contact |
| PATCH | `/api/crm/contacts/{id}` | Update contact |
| POST | `/api/crm/contacts/{id}/archive` | Archive contact |
| GET | `/api/projects/{id}/crm/summary` | CRM summary |
| GET | `/api/projects/{id}/crm/opportunities` | List opportunities |
| POST | `/api/projects/{id}/crm/opportunities` | Create opportunity |
| GET | `/api/projects/{id}/crm/opportunities/{id}` | Get opportunity |
| PATCH | `/api/projects/{id}/crm/opportunities/{id}` | Update opportunity |
| POST | `/api/projects/{id}/crm/opportunities/{id}/status` | Update status |
| GET | `/api/projects/{id}/crm/communications` | List communications |
| POST | `/api/projects/{id}/crm/communications` | Add communication |
| GET | `/api/projects/{id}/crm/tasks` | List tasks |
| POST | `/api/projects/{id}/crm/tasks` | Create task |
| POST | `/api/projects/{id}/crm/tasks/{id}/complete` | Complete task |
| POST | `/api/projects/{id}/crm/tasks/{id}/cancel` | Cancel task |

---

## Service Functions

### `src/services/crm_service.py`

- `create_contact()` - Create contact
- `list_contacts()` - List contacts with filters
- `get_contact()` - Get contact by ID
- `update_contact()` - Update contact
- `archive_contact()` - Archive contact
- `create_opportunity()` - Create opportunity
- `list_project_opportunities()` - List opportunities
- `update_opportunity()` - Update opportunity
- `add_communication()` - Add communication
- `list_communications()` - List communications
- `create_task()` - Create task
- `list_tasks()` - List tasks
- `complete_task()` - Complete task
- `cancel_task()` - Cancel task
- `get_crm_summary()` - Get summary with counts

---

## Dashboard Integration

Module status:
```
"crm": {
    "status": "ready" | "missing",
    "summary": "{count} oportunidad" | "Sin oportunidades comerciales",
}
```

Recommended action when missing:
```
{
    "label": "Crear oportunidad comercial",
    "route": "/projects/{project_id}/crm",
    "priority": "medium",
    "permission": "crm.manage",
}
```

---

## Permissions

| Permission | Roles | Description |
|------------|-------|-------------|
| `crm.view` | All roles | View CRM |
| `crm.manage` | Producer, Admin | Full CRM access |

---

## Opportunity Status

| Status | Description |
|--------|-------------|
| `new` | New opportunity |
| `prepared` | Pack prepared |
| `contacted` | Initial contact made |
| `follow_up` | Awaiting follow-up |
| `interested` | Contact interested |
| `meeting_scheduled` | Meeting scheduled |
| `negotiating` | In negotiation |
| `accepted` | Deal accepted |
| `rejected` | Deal rejected |
| `closed` | Opportunity closed |

---

## Contact Types

| Type | Purpose |
|------|---------|
| `producer` | Production company |
| `distributor` | Film distributor |
| `sales_agent` | Sales agent |
| `cinema` | Cinema/exhibitor |
| `platform` | Streaming platform |
| `festival` | Film festival |
| `investor` | Investor/financier |
| `institution` | Institutional contact |
| `other` | Other |

---

## Important Notes

1. **No email integration**: This CRM does NOT send emails automatically.
2. **Manual communications**: All communications are logged manually.
3. **No external integration**: Does not integrate with Gmail, Salesforce, etc.
4. **Tracking only**: Purpose is to track opportunity status, not full sales automation.

---

## Frontend

### Page
`src_frontend/src/pages/CommercialCrmPage.tsx`

### API
`src_frontend/src/api/crm.ts`

### Route
`/projects/:projectId/crm`

---

## Smoke Tests

- `smoke_commercial_crm.py` - Core functionality
- `smoke_distribution_pack.py` - Distribution pack dependency
- `smoke_project_dashboard.py` - Dashboard integration

---

**Last Updated**: 2026-04-28
**Status**: COMMERCIAL CRM — IMPLEMENTED