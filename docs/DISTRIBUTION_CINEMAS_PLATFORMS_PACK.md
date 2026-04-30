# Distribution / Cinemas / Platforms Pack - Technical Specification

## Overview

Distribution Pack generates commercial presentation materials for different sales channels. It aggregates from existing modules and provides type-specific content.

**Status**: IMPLEMENTED

---

## Models

### `src/models/distribution.py`

| Model | Table | Purpose |
|-------|-------|--------|
| `DistributionPack` | `distribution_packs` | Main distribution pack |
| `DistributionPackSection` | `distribution_pack_sections` | Individual sections |
| `SalesTarget` | `sales_targets` | Sales targets (distributors, platforms, festivals) |
| `ProjectSalesOpportunity` | `project_sales_opportunities` | Project-target opportunities |

---

## Pack Types

| Type | Purpose |
|------|---------|
| `distributor` | Pack para distribuidoras cinematográficas |
| `sales_agent` | Pack para agentes de ventas internacional |
| `festival` | Pack para festivales de cine |
| `cinema` | Pack para cines/exhibidores |
| `platform` | Pack para plataformas de streaming |
| `general_sales` | Pack de ventas general |

---

## Routes

### Distribution Pack Routes (`src/routes/distribution_pack_routes.py`)

| Method | Endpoint | Purpose |
|--------|---------|---------|
| GET | `/api/projects/{project_id}/distribution-packs` | List packs |
| POST | `/api/projects/{project_id}/distribution-packs/generate` | Generate new pack |
| GET | `/api/projects/{project_id}/distribution-packs/{pack_id}` | Get pack detail |
| PATCH | `/api/projects/{project_id}/distribution-packs/{pack_id}` | Update pack |
| POST | `/api/projects/{project_id}/distribution-packs/{pack_id}/approve` | Approve pack |
| POST | `/api/projects/{project_id}/distribution-packs/{pack_id}/archive` | Archive pack |
| GET | `/api/projects/{project_id}/distribution-packs/{pack_id}/export/json` | Export JSON |
| GET | `/api/projects/{project_id}/distribution-packs/{pack_id}/export/markdown` | Export Markdown |
| GET | `/api/projects/{project_id}/distribution-packs/{pack_id}/export/zip` | Export ZIP |

### Sales Targets Routes (`src/routes/sales_targets_routes.py`)

| Method | Endpoint | Purpose |
|--------|---------|---------|
| GET | `/api/sales-targets` | List targets |
| POST | `/api/sales-targets` | Create target |
| GET | `/api/sales-targets/{target_id}` | Get target |
| PATCH | `/api/sales-targets/{target_id}` | Update target |
| GET | `/api/projects/{project_id}/sales-opportunities` | List opportunities |
| POST | `/api/projects/{project_id}/sales-opportunities/suggest` | Suggest targets |
| POST | `/api/projects/{project_id}/sales-opportunities` | Create opportunity |
| PATCH | `/api/projects/{project_id}/sales-opportunities/{opportunity_id}` | Update opportunity |

---

## Service Functions

### `src/services/distribution_pack_service.py`

- `generate_distribution_pack()` - Generate pack from project data
- `get_distribution_pack()` - Get pack by ID
- `get_active_distribution_pack()` - Get active pack
- `list_distribution_packs()` - List all packs
- `update_distribution_pack()` - Update pack
- `approve_distribution_pack()` - Approve pack
- `archive_distribution_pack()` - Archive pack
- `export_distribution_pack_json()` - Export as JSON
- `export_distribution_pack_markdown()` - Export as Markdown

### `src/services/sales_target_service.py`

- `create_sales_target()` - Create target
- `create_sample_targets()` - Create sample targets
- `get_sales_target()` - Get target
- `list_sales_targets()` - List targets
- `suggest_sales_targets_for_project()` - Suggest targets
- `create_sales_opportunity()` - Create opportunity
- `update_sales_opportunity()` - Update opportunity
- `list_project_sales_opportunities()` - List opportunities

---

## Sample Sales Targets

The service includes 4 sample targets (all with `source_type: sample`, `status: sample`):

1. Demo Cine Independiente (distributor)
2. Demo Plataforma Documental (platform)
3. Demo Festival Ópera Prima (festival)
4. Demo Circuito Exhibición Educativa (cinema)

**Note**: These are example data, not real contacts.

---

## Dashboard Integration

Module status:
```
"distribution": {
    "status": "ready" | "missing",
    "summary": "{count} pack" | "Generar pack distribución",
}
```

Recommended action when missing:
```
{
    "label": "Generar pack distribución",
    "route": "/projects/{project_id}/distribution",
    "priority": "medium",
    "permission": "distribution.manage",
}
```

---

## Data Sources

The distribution pack aggregates from:
1. **ProducerPitchPack** - logline, synopsis, target_audience
2. **ScriptVersion** - logline, synopsis
3. **Budget** - budget summary
4. **Funding** - funding summary

Each pack_type generates different sections:
- **distributor**: commercial positioning, territory strategy, exploitation windows
- **platform**: audience, retention potential, catalog positioning
- **festival**: artistic note, director statement, festival strategy
- **cinema**: local audience, special events

---

## Exports

### JSON
```json
{
  "id": "...",
  "pack_type": "distributor",
  "logline": "...",
  "comparables": [...],
  "territory_strategy": [...],
  "available_materials": [...]
}
```

### Markdown
Complete formatted document with all sections.

### ZIP
Contains `distribution_pack.json` and `distribution_pack.md`.

---

## Frontend

### Page
`src_frontend/src/pages/DistributionPackPage.tsx`

### API
`src_frontend/src/api/distributionPack.ts`

### Route
`/projects/:projectId/distribution`

---

## Important Disclaimer

**This is a commercial preparation tool. It does NOT guarantee:**
- Acceptance by distributors
- Placement on platforms
- Selection by festivals
- Any commercial agreement

---

## Smoke Tests

- `smoke_distribution_pack.py` - Core functionality
- `smoke_producer_pitch_pack.py` - Producer pitch dependency
- `smoke_project_dashboard.py` - Dashboard integration

---

**Last Updated**: 2026-04-28
**Status**: DISTRIBUTION PACK — IMPLEMENTED