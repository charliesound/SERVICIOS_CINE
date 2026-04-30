# Funding & Grants Assistant - Technical Contract

## Overview

Funding & Grants module is fully integrated in AILinkCinema. The module uses existing infrastructure and canonical models from `src/models/production.py`.

**Status**: CONSOLIDATED

---

## Canonical Models

The following models are the canonical funding models used throughout the application:

### `src/models/production.py`

| Model | Table | Purpose |
|-------|-------|--------|
| `FundingSource` | `funding_sources` | Funding agency/organization (ICAA, CCAA, Europa Creative, etc.) |
| `FundingCall` | `funding_calls` | Specific funding call/opportunity |
| `PrivateFundingSource` | `private_funding_sources` | Private investors/financing |
| `ProjectFundingSource` | `project_funding_sources` | Project-specific funding tracking |

### `src/models/producer.py` (Legacy)

| Model | Table | Purpose |
|-------|-------|--------|
| `FundingOpportunity` | `funding_opportunities` | **DEPRECATED** - Legacy demo opportunities |
| `SavedOpportunity` | `saved_opportunities` | **DEPRECATED** - Project saved opportunities |

---

## Legacy / Deprecated Models

### `src/models/producer.py`

- `FundingOpportunity` - Used only by `producer_routes.py` for demo catalog
- `SavedOpportunity` - Used only by `producer_routes.py` for legacy saved functionality
- **Status**: DEPRECATED but still imported to avoid breaking routes

### `src/models/funding.py`

- **DELETED** - Was duplicate of canonical models, no longer exists

---

## Canonical Routes

The following routes are the canonical funding routes:

### Main Routes

| Route | File | Purpose |
|-------|------|---------|
| `/api/funding/opportunities` | `funding_catalog_routes.py` | List funding opportunities |
| `/api/funding/opportunities/{id}` | `funding_catalog_routes.py` | Get opportunity detail |
| `/api/funding/calls` | `funding_routes.py` | Full funding calls API |
| `/api/projects/{id}/funding/private-sources` | `project_funding_routes.py` | Project private funding |
| `/api/projects/{id}/funding/matches` | `project_funding_routes.py` | Funding matches |

### Admin Routes

| Route | File | Purpose |
|-------|------|---------|
| `/api/admin/funding/sync` | `admin_funding_routes.py` | Sync funding catalog |
| `/api/admin/funding/ingest` | `admin_funding_routes.py` | Ingest from sources |

### Legacy Routes (Deprecated)

| Route | File | Purpose |
|-------|------|---------|
| `/api/producer/funding/opportunities` | `producer_routes.py` | Demo opportunities |
| `/api/producer/saved-opportunities` | `producer_routes.py` | Legacy saved |

---

## Canonical Services

| Service | File | Purpose |
|---------|------|---------|
| `funding_ingestion_service.py` | Ingest funding from external sources |
| `funding_matcher_service.py` | Match projects to funding |
| `funding_alert_service.py` | Deadline alerts |
| `project_funding_service.py` | Project funding tracking |
| `funding_dossier_service.py` | Funding dossier generation |

---

## Frontend

| Page | File | Purpose |
|------|------|---------|
| Project Funding | `src_frontend/src/pages/ProjectFundingPage.tsx` | Main funding assistant UI |

### Dashboard Integration

The dashboard shows funding status in the module card:

```
modules["funding"] = {
    "status": "ready" | "missing",
    "summary": "{count} oportunidades" | "Ver oportunidades de ayudas",
}
```

---

## Permissions

| Permission | Role | Description |
|------------|------|------------|
| `funding.view` | All roles | View funding opportunities |
| `funding.manage` | Producer, Admin | Manage project funding |

---

## Database Schema

### Active Tables

- `funding_sources` - Funding agencies
- `funding_calls` - Funding calls/opportunities
- `funding_requirements` - Per-call requirements
- `project_funding_sources` - Project-specific funding
- `private_funding_sources` - Private investors
- `project_funding_matches` - Project-call matching

### Legacy Tables (Deprecated)

- `funding_opportunities` - Demo catalog (not actively used)
- `saved_opportunities` - Legacy saved links

---

## No-Duplicate Contract

1. **DO NOT** create new models for funding in separate files
2. **DO NOT** add to `models/funding.py` - file was deleted
3. **DO** use `models.production.FundingCall` and `FundingSource`
4. **DO** extend existing services for new features
5. **DO NOT** create parallel funding catalogs

---

## Smoke Tests

- `smoke_project_dashboard.py` - Dashboard funding integration
- `smoke_role_based_dashboard.py` - Role permissions for funding
- `check_funding_no_duplicate_models.py` - No duplicate model check

---

**Last Updated**: 2026-04-28
**Status**: FUNDING CONSOLIDATION — CLOSED