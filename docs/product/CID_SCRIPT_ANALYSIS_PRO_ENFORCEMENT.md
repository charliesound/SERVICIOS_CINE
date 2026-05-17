# CID Script Analysis Pro — Enforcement Backend por Plan

## Resumen ejecutivo

Commit quirúrgico de enforcement para el módulo `script_analysis`.
Se añadió `require_module_access("script_analysis")` a todos los endpoints privados de ownership claro del módulo.
No se modificaron contratos de API, payloads, responses, migraciones ni frontend.

**Estado anterior**: Sin control de acceso por plan — cualquier usuario autenticado podía usar análisis de guion.
**Estado actual**: Todos los endpoints de Script Analysis exigen `module_script_analysis` en el plan del usuario.
**Usuarios admin/global_admin**: Bypass automático (comportamiento existente de `require_module_access`).

---

## Endpoints protegidos

| Archivo | Endpoint | Método | Estrategia |
|---|---|---|---|
| `intake_routes.py` | `/api/projects/{id}/intake/script` | POST | endpoint-level |
| `intake_routes.py` | `/api/projects/{id}/analysis/run` | POST | endpoint-level |
| `intake_routes.py` | `/api/projects/{id}/analysis/summary` | GET | endpoint-level |
| `project_routes.py` | `/api/projects/{id}/script` | PUT | endpoint-level |
| `project_routes.py` | `/api/projects/{id}/analyze` | POST | endpoint-level |
| `script_version_routes.py` | `/api/projects/{id}/script/versions` | GET | router-level |
| `script_version_routes.py` | `/api/projects/{id}/script/versions` | POST | router-level |
| `script_version_routes.py` | `/api/projects/{id}/script/versions/{vid}` | GET | router-level |
| `script_version_routes.py` | `/api/projects/{id}/script/versions/{vid}/activate` | POST | router-level |
| `script_version_routes.py` | `/api/projects/{id}/script/versions/compare` | POST | router-level |
| `script_version_routes.py` | `/api/projects/{id}/script/change-reports` | GET | router-level |
| `script_version_routes.py` | `/api/projects/{id}/module-status` | GET | router-level |
| `ollama_storyboard_routes.py` | `/api/projects/{id}/analyze/local-ollama` | POST | endpoint-level |

**Total**: 13 endpoints protegidos en 4 archivos de rutas.

---

## Endpoints NO protegidos deliberadamente

| Endpoint | Archivo | Motivo |
|---|---|---|
| `POST /api/projects/intake/idea` | `intake_routes.py` | **Core** — crear proyecto no requiere análisis. Es la puerta de entrada gratuita. |
| `GET /api/projects/{id}/breakdown/scenes` | `intake_routes.py` | **Breakdown** — módulo separado con su propio `feature_flag_key: module_breakdown`. Ownership compartido entre Script Analysis y Breakdown. Pendiente de auditoría de Breakdown. |
| `GET /api/projects/{id}/breakdown/departments` | `intake_routes.py` | **Breakdown** — mismo motivo. |
| `POST /api/projects/{id}/storyboard` | `project_routes.py` | **Storyboard AI** — módulo separado (`storyboard_ai`). Recibirá su propio enforcement en Sprint correspondiente. |
| `GET /api/ops/ollama/status` | `ollama_storyboard_routes.py` | **Público** — health check sin auth. No contiene datos sensibles. |
| `POST /api/projects/{id}/storyboard/prompts/from-analysis` | `ollama_storyboard_routes.py` | **Storyboard AI** — ya tiene `require_module_access("storyboard_ai")`. Correcto. |
| `POST /api/cid/script-to-prompt/analyze-full` | `cid_script_to_prompt_routes.py` | **Pipeline Builder** — ya tiene `require_module_access("pipeline_builder")`. Pendiente de decisión si debe requerir también `script_analysis`. |
| Todos los endpoints de `report_routes.py` | `report_routes.py` | **Reportes de producción** (camera/sound/script/director notes). Pertenecen a producción, no a Script Analysis. |
| Todos los endpoints de `document_routes.py` | `document_routes.py` | **Documentos** — sistema genérico de gestión documental. No es ownership de Script Analysis. |

---

## Estrategia de enforcement

### Router-level (cuando todo el router es ownership claro)
`script_version_routes.py` — los 7 endpoints pertenecen 100% a versionado de guion, que es parte de Script Analysis Pro.

### Endpoint-level (cuando el router mezcla módulos)
- `intake_routes.py` mezcla: core (`/intake/idea`), script_analysis (`/intake/script`, `/analysis/run`, `/analysis/summary`), breakdown (`/breakdown/scenes`, `/breakdown/departments`)
- `project_routes.py` mezcla: core (CRUD proyecto), script_analysis (`/script`, `/analyze`), storyboard_ai (`/storyboard`)
- `ollama_storyboard_routes.py` mezcla: público (`/ops/ollama/status`), script_analysis (`/analyze/local-ollama`), storyboard_ai (`/storyboard/prompts/from-analysis`)

---

## Comportamiento esperado

### 403: MODULE_ACCESS_BLOCKED
Cuando un usuario no-admin con un plan que NO incluye `module_script_analysis` intenta acceder a un endpoint protegido:

```json
{
  "error": {
    "code": "forbidden",
    "message": "Forbidden",
    "details": {
      "code": "MODULE_ACCESS_BLOCKED",
      "module": "script_analysis",
      "plan": "<plan_name>",
      "reason": "plan_feature_missing"
    }
  }
}
```

### Nota sobre plans.yml
Actualmente **todos los planes** (demo, free, creator, producer, studio, enterprise) incluyen `module_script_analysis` en sus features. Esto significa que el enforcement está arquitectónicamente instalado pero no bloquea a nadie con un plan válido. El bloqueo real ocurrirá cuando:
- Se cree un plan sin `module_script_analysis`
- Se modifique un plan existente para quitarlo

---

## Relación con plans.yml y modules.yml

- `modules.yml`: `script_analysis.feature_flag_key: module_script_analysis`
- `plans.yml`: `features: [..., module_script_analysis, ...]` en todos los planes

La dependencia `require_module_access("script_analysis")` verifica que el feature flag `module_script_analysis` esté en las features efectivas del plan del usuario. Si no está, devuelve 403.

---

## Tests añadidos

Archivo: `tests/integration/test_script_analysis_enforcement.py`

| Test | Escenario | Resultado esperado |
|---|---|---|
| `test_intake_script_with_valid_plan_returns_200` | Usuario admin con plan demo → endpoint protegido | 200 |
| `test_analysis_summary_with_valid_plan_returns_200` | Usuario admin con plan demo → endpoint protegido GET | 200 |
| `test_put_script_with_valid_plan_returns_200` | Usuario admin → PUT script | 200 |
| `test_protected_endpoint_without_module_access_returns_403` | Usuario no-admin + mock de módulo deshabilitado → endpoint protegido | 403 |
| `test_intake_idea_unprotected_returns_200` | Usuario admin → endpoint core sin enforcement | 200 |
| `test_ollama_status_unprotected_returns_200` | Sin auth → endpoint público | 200 |

**Resultado**: 6/6 passed.

Tests legados no afectados:
- `tests/integration/test_project_script_analysis_flow.py` → 1 passed
- `tests/unit/` → 331 passed
- `tests/integration/` completo → 89 passed

---

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `src/routes/intake_routes.py` | +3 `require_module_access("script_analysis")` a intake/script, analysis/run, analysis/summary |
| `src/routes/project_routes.py` | +1 import, +2 `require_module_access("script_analysis")` a PUT script, POST analyze |
| `src/routes/script_version_routes.py` | +1 import, router-level dependency en APIRouter |
| `src/routes/ollama_storyboard_routes.py` | +1 `require_module_access("script_analysis")` a /analyze/local-ollama |

## Archivos creados

| Archivo | Propósito |
|---|---|
| `tests/integration/test_script_analysis_enforcement.py` | Tests de enforcement del módulo |
| `docs/product/CID_SCRIPT_ANALYSIS_PRO_ENFORCEMENT.md` | Esta documentación |
| `directivas/cid_script_analysis_pro_enforcement.md` | Directiva técnica |

---

## Riesgos conocidos

1. **Todos los planes incluyen `module_script_analysis`**: El enforcement está instalado pero no bloquea a nadie con un plan válido. Esto es intencional — permite hacer rollout sin romper acceso existente.
2. **Breakdown comparte endpoints con Script Analysis**: Los endpoints `/breakdown/scenes` y `/breakdown/departments` en `intake_routes.py` usan `analysis_service` internamente pero pertenecen al módulo `breakdown`. No se protegieron con `script_analysis` para no bloquear Breakdown antes de que tenga su propio enforcement.
3. **`/analyze/local-ollama` sin enforcement anterior**: Este endpoint ahora requiere `script_analysis`. Antes era accesible a cualquier usuario autenticado. Es un cambio de comportamiento legítimo pero debe comunicarse.
4. **`/analyze-full` en pipeline_builder**: Ya tiene `require_module_access("pipeline_builder")` pero es un análisis completo de guion. Posible doble enforcement en el futuro.

---

## Siguiente commit recomendado

**Commit 2 — Export directo de Script Analysis Pro**

Crear endpoint `GET /projects/{id}/analysis/export?format=json|md` que serialice:
- Análisis completo (escenas, personajes, localizaciones)
- Sinopsis, logline, género, tono, estructura
- Breakdown técnico
- Reportes de cambio entre versiones

Esto permite al usuario descargar su análisis como artefacto portable y compartible.
