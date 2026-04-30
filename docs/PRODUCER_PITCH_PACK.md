# Producer Pitch Pack - Technical Specification

## Overview

Producer Pitch Pack generates a dossier for presenting projects to producers. It aggregates data from existing modules: script, budget, funding, and storyboard.

**Status**: IMPLEMENTED

---

## Models

### `src/models/producer_pitch.py`

| Model | Table | Purpose |
|-------|-------|--------|
| `ProducerPitchPack` | `producer_pitch_packs` | Main pitch pack entity |
| `ProducerPitchSection` | `producer_pitch_sections` | Individual sections |

---

## Routes

### `src/routes/producer_pitch_routes.py`

| Method | Endpoint | Purpose |
|--------|---------|---------|
| GET | `/api/projects/{project_id}/producer-pitch` | List all packs |
| GET | `/api/projects/{project_id}/producer-pitch/active` | Get active pack |
| POST | `/api/projects/{project_id}/producer-pitch/generate` | Generate new pack |
| GET | `/api/projects/{project_id}/producer-pitch/{pack_id}` | Get pack detail |
| PATCH | `/api/projects/{project_id}/producer-pitch/{pack_id}` | Update pack |
| POST | `/api/projects/{project_id}/producer-pitch/{pack_id}/approve` | Approve pack |
| POST | `/api/projects/{project_id}/producer-pitch/{pack_id}/archive` | Archive pack |
| GET | `/api/projects/{project_id}/producer-pitch/{pack_id}/export/json` | Export JSON |
| GET | `/api/projects/{project_id}/producer-pitch/{pack_id}/export/markdown` | Export Markdown |
| GET | `/api/projects/{project_id}/producer-pitch/{pack_id}/export/zip` | Export ZIP |

---

## Service Functions

### `src/services/producer_pitch_service.py`

- `generate_pitch_pack()` - Generate pack from project data
- `get_pitch_pack()` - Get pack by ID
- `get_active_pitch_pack()` - Get active pack for project
- `list_pitch_packs()` - List all packs for project
- `update_pitch_pack()` - Update pack fields
- `approve_pitch_pack()` - Approve pack
- `archive_pitch_pack()` - Archive pack
- `export_pitch_json()` - Export as JSON
- `export_pitch_markdown()` - Export as Markdown
- `export_pitch_zip()` - Export as ZIP

---

## Dashboard Integration

Module status:
```
"producer_pack": {
    "status": "ready" | "missing",
    "summary": "{count} dossier" | "Generar dossier productor",
}
```

Recommended action when missing:
```
{
    "label": "Generar dossier productor",
    "route": "/projects/{project_id}/producer-pitch",
    "priority": "medium",
    "permission": "producer_pack.generate",
}
```

---

## Permissions

| Permission | Roles | Description |
|------------|-------|-------------|
| `producer_pack.view` | All roles | View pitch pack |
| `producer_pack.generate` | Producer, Admin | Generate/approve pack |

---

## Data Sources

The pitch pack aggregates from:
1. **Script** - logline, synopsis, intention_note, genre, format, tone
2. **Budget** - total_estimated, currency, budget_level
3. **Funding** - active opportunities count
4. **Storyboard** - selected shots

---

## Exports

### JSON
```json
{
  "id": "...",
  "project_id": "...",
  "title": "...",
  "logline": "...",
  "short_synopsis": "...",
  "budget_summary": {...},
  "funding_summary": {...}
}
```

### Markdown
Includes all sections formatted for readability.

### ZIP
Contains `pitch_pack.json` and `pitch_pack.md`.

---

## Frontend

### Page
`src_frontend/src/pages/ProducerPitchPackPage.tsx`

### API
`src_frontend/src/api/producerPitch.ts`

### Route
`/projects/:projectId/producer-pitch`

---

## Smoke Tests

- `smoke_producer_pitch_pack.py` - Core functionality
- `smoke_project_dashboard.py` - Dashboard integration
- `smoke_budget_estimator.py` - Budget dependency

---

**Last Updated**: 2026-04-28
**Status**: PRODUCER PITCH PACK — IMPLEMENTED