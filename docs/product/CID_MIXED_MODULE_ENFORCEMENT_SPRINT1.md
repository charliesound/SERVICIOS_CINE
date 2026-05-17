# CID Mixed Module Enforcement Sprint 1

## Resumen ejecutivo

Commit 5 aplica enforcement modular a las superficies mixtas aprobadas por la auditoría de ownership:

- `presentation_routes.py` → protegido como `pitch_deck` (router-level)
- `cid_script_to_prompt_routes.py` → protegido como `pipeline_builder` (endpoint-level solo en `/analyze-full`)
- `delivery_routes.py` → **NO-GO**, se mantiene sin enforcement nuevo

Este commit cierra el enforcement de los 7 módulos vendibles identificados en el roadmap comercial.

## Módulos protegidos (acumulado)

| Módulo | Sprint 3 | Sprint 5 (este) |
|---|---|---|
| `pitch_deck` | `producer_pitch_routes.py` | + `presentation_routes.py` |
| `budget_lite` | `budget_routes.py` | — |
| `funding_grants` | `funding_routes.py` (privado), `project_funding_routes.py`, `matcher_routes.py` | — |
| `storyboard_ai` | `storyboard_routes.py`, `comfyui_storyboard_routes.py`, `ollama_storyboard_routes.py` | — |
| `delivery_distribution` | `distribution_pack_routes.py`, `sales_targets_routes.py`, `crm_routes.py` | — |
| `pipeline_builder` | — | `cid_script_to_prompt_routes.py` (solo `/analyze-full`) |

## Rutas protegidas en este commit

### pitch_deck

- `src/routes/presentation_routes.py` — router completo con `Depends(require_module_access("pitch_deck"))`
  - `GET /api/projects/{project_id}/presentation/filmstrip`
  - `GET /api/projects/{project_id}/presentation/filmstrip.html`
  - `GET /api/projects/{project_id}/presentation/export/pdf`
  - `POST /api/projects/{project_id}/presentation/export/pdf/persist`
  - `GET /api/projects/{project_id}/presentation/assets/{asset_id}/preview`
  - `GET /api/projects/{project_id}/presentation/assets/{asset_id}/thumbnail`
  - `POST /api/projects/{project_id}/presentation/export-pdf`

### pipeline_builder

- `src/routes/cid_script_to_prompt_routes.py` endpoint único con `Depends(require_module_access("pipeline_builder"))`
  - `POST /api/cid/script-to-prompt/analyze-full`

## Rutas deliberadamente no protegidas

### NO-GO confirmado

- `src/routes/delivery_routes.py` — cross-module, sirve deliverables creados por pitch_deck, funding_grants y postproduction. Requiere modelo granular futuro por deliverable.

### Stateless / sin auth

- 13 endpoints de `cid_script_to_prompt_routes.py` se mantienen sin enforcement por ser funciones de transformación puras sin acceso a datos de proyecto/organización:
  - `POST /run`, `/parse`, `/intent`, `/prompt`, `/validate`
  - `GET /director-lenses`, `/director-lenses/{lens_id}`
  - `POST /director-lenses/choose`, `/directorial-intent`
  - `GET /montage-profiles`
  - `POST /montage-intent`, `/editorial-beats`, `/shot-editorial-purpose`

## Comportamiento 403 esperado

Misma semántica que Sprint 3: el helper `require_module_access()` devuelve `403` con:

```json
{
  "code": "MODULE_ACCESS_BLOCKED",
  "module": "pitch_deck|pipeline_builder",
  "plan": "<plan_name>",
  "reason": "plan_feature_missing | dependency_locked:<module>"
}
```

Bypass para `admin` y `global_admin` se mantiene.

## Relación con auditoría previa

- La auditoría (`CID_MIXED_MODULE_OWNERSHIP_AUDIT.md`) documentó ownership real por endpoint.
- Este commit implementa exactamente lo recomendado en la sección "Plan exacto para Commit 5".

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `src/routes/presentation_routes.py` | + import `require_module_access`, + router-level `Depends("pitch_deck")` |
| `src/routes/cid_script_to_prompt_routes.py` | + imports `select`, `require_module_access`, + endpoint-level `Depends("pipeline_builder")` en `/analyze-full` |
| `src/config/modules.yml` | + `/api/cid/script-to-prompt` en route_prefixes de pipeline_builder |
| `tests/unit/test_module_access_dependency.py` | + 7 tests (pitch_deck × 3, pipeline_builder × 3, stateless × 1) |

## Límites conocidos

- `delivery_routes.py` sigue sin enforcement — los deliverables son accesibles globalmente (control por organización existente).
- `cid_script_to_prompt` tiene 13 endpoints stateless sin auth — son funciones de transformación que no acceden a DB.
- `presentation_routes.py` usa `delivery_service.create_project_file_deliverable` — el enforcement de pitch_deck no bloquea la creación de deliverables (llamada interna dentro del endpoint protegido).
- Dos patrones de tenant context coexisten (`routes.auth_routes.get_tenant_context` y `dependencies.tenant_context.get_tenant_context`) — el helper modular usa el segundo, presentation usa el primero. Ambos funcionan en paralelo.

## Siguiente commit recomendado

1. Añadir observabilidad explícita de bloqueos modulares: loggear cada 403 MODULE_ACCESS_BLOCKED con tenant/module/plan para soporte comercial.
2. Diseñar modelo granular de enforcement para `delivery_routes.py` (por deliverable.format_type o source_review_id).
3. Unificar los dos patrones de tenant context.
