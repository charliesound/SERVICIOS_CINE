# CID Backend Gating Contract v1

## Resumen ejecutivo

- AUDIT.7 veredicto: **GO** (`/tmp/cid_backend_gating_closure_audit_7.md`).
- P0: **0** (todos cerrados en fases 3A-3O).
- P1: **0** (todos cerrados en fases 3A-3O).
- P2: **8** manual review aceptados.
- Estado de HEAD: `a704563` con tag `cid-dev-stable-backend-gating-storyboard-presentation-routes-3o-20260604`.

Este documento consolida el contrato canónico de gating backend de CID tras la fase de cierre, y actúa como referencia única para nuevas rutas y revisiones de auditoría futuras.

## Contrato canónico

Las dependencias de gating se importan exclusivamente desde `src/dependencies/tenant_context.py` y `src/dependencies/module_access.py`. El import legacy `from routes.auth_routes import get_tenant_context` se considera deprecado y solo se mantiene por compatibilidad funcional (los tests de contract gating verifican explícitamente `from dependencies.tenant_context import`).

### Dependencias base

| Dependencia | Fuente | Propósito |
|---|---|---|
| `get_tenant_context` | `dependencies.tenant_context` | Resuelve `TenantContext` desde JWT o internal API key. Garantiza `organization_id`, `user_id`, `plan`, `role`. Devuelve 401 si no hay token. |
| `require_organization` | `dependencies.tenant_context` | Encadena sobre `get_tenant_context` y verifica que el tenant tenga `organization_id` (403 si no). |
| `validate_project_access` | `dependencies.tenant_context` | Resuelve el `Project` por path `project_id` y verifica que pertenece a la organización del tenant. 404 si no se encuentra. |
| `require_write_permission` | `dependencies.tenant_context` | Encadena sobre `require_organization` y aplica `can_write_project(tenant)`. 403 si el rol/plan no permite escritura. |
| `require_module_access(module_key)` | `dependencies.module_access` | Verifica que el plan del tenant habilita el módulo (`storyboard_ai`, `script_analysis`, `pipeline_builder`, `delivery_distribution`, `breakdown`, etc.). 403 si el módulo no está habilitado. |

### Import canónico

```python
from dependencies.tenant_context import (
    TenantContext,
    get_tenant_context,
    require_write_permission,
    validate_project_access,
)
from dependencies.module_access import require_module_access
```

## Patrones por tipo de router

CID distingue los siguientes patrones de gating. Cada nueva ruta debe declarar explícitamente a qué categoría pertenece.

### 1. Project-scoped por path (default seguro)

`project_id` viene en el path de la URL (`/api/projects/{project_id}/...`). Caso más común: storyboard, presupuesto, análisis, exports.

```python
@router.post("/{project_id}/storyboard/generate")
async def generate_storyboard(
    project_id: str,
    payload: StoryboardGenerateRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(require_write_permission),
    _project: Project = Depends(validate_project_access),
) -> StoryboardJobResponse:
    ...
```

Reglas:
- `validate_project_access` siempre como `Depends`.
- Mutating endpoints: `tenant` vía `require_write_permission`.
- Read-only endpoints: `tenant` vía `get_tenant_context`.
- Llamadas al servicio deben pasar `validated_project_id = str(project.id)` y nunca el `project_id` crudo del path.

### 2. Tenant-scoped (sin project_id)

Endpoint que solo necesita el contexto del tenant (lista de proyectos, usage, billing).

```python
@router.get("")
async def list_projects(
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    user_org_id = str(tenant.organization_id)
    result = await db.execute(
        select(Project).where(Project.organization_id == user_org_id)
    )
    ...
```

### 3. Admin-scoped

Endpoint restringido a `is_admin` o `is_global_admin`. Verificación manual dentro del handler además del tenant context.

```python
async def _is_admin_tenant(tenant: TenantContext) -> bool:
    return bool(
        getattr(tenant, "is_global_admin", False)
        or getattr(tenant, "role", None) == "admin"
    )
```

### 4. Project id en body o query

`project_id` viene dentro del payload o como query param. No se puede usar `validate_project_access` como `Depends` (el path no lo contiene). Solución: helper local que use `select(Project).where(... Project.organization_id == tenant.organization_id ...)`.

```python
async def _validate_*_project_access(
    db: AsyncSession,
    project_id: str,
    tenant: TenantContext,
) -> Project:
    query = select(Project).where(Project.id == project_id)
    if not _is_admin_tenant(tenant):
        query = query.where(Project.organization_id == tenant.organization_id)
    result = await db.execute(query)
    project = result.scalar_one_or_none()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found or access denied")
    return project
```

Ejemplo canónico: `cid_script_to_prompt_routes.py::_validate_script_to_prompt_project_access`.

### 5. Bridge / proxy externo

Endpoint que reenvía a otro backend (dubbing bridge, n8n, google drive). El ownership del proyecto se delega a `validate_project_access`, el `tenant.user_id` y `tenant.organization_id` se usan para construir la llamada externa.

```python
@router.post("/projects/{project_id}/jobs")
async def create_dubbing_job(
    project_id: str,
    data: BridgeJobCreate,
    tenant: TenantContext = Depends(get_tenant_context),
    project: Project = Depends(validate_project_access),
    _write: None = Depends(require_write_permission),
):
    del tenant
    del _write
    validated_project_id = str(project.id)
    ...
```

### 6. Ops / status

Endpoint de health/availability de un subsistema (comfyui, ollama, queue). No es project-scoped.

```python
@router.get("/ops/comfyui/storyboard/status")
async def get_comfyui_storyboard_status(
    tenant: TenantContext = Depends(get_tenant_context),
) -> dict[str, Any]:
    return await comfyui_storyboard_render_service.healthcheck()
```

No requiere `require_write_permission` (es read-only operacional). Solo `get_tenant_context` para autenticar.

### 7. Read-only downloads

Sirve un artefacto ya generado en disco para un proyecto autenticado. No muta estado.

```python
@router.get("/{project_id}/storyboard/sheet/artifacts/{filename:path}")
async def download_storyboard_sheet_artifact(
    project_id: str,
    filename: str,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
):
    await _ensure_project_access(db, project_id, tenant)
    ...
```

No requiere `require_write_permission`. El ownership se valida vía helper local o `validate_project_access`.

### 8. Mutantes / export / render / execute

Genera artefactos, ejecuta renders, dispara análisis. Requiere el contrato completo.

```python
@router.post("/{project_id}/storyboard/sheet")
async def generate_storyboard_sheet(
    project_id: str,
    payload: StoryboardSheetRequest,
    db: AsyncSession = Depends(get_db),
    tenant: TenantContext = Depends(get_tenant_context),
    _write: None = Depends(require_write_permission),
) -> StoryboardSheetResponse:
    ...
```

Checklist obligatorio:
- `get_tenant_context` o `require_write_permission` para `tenant`.
- `validate_project_access` o helper local para ownership.
- `require_module_access` (vía router-level dependency o endpoint-level) si el módulo no es universal.
- Nunca delegar ownership a `select(Project)` dentro del handler sin filtro por `organization_id`.

## Registro P2 / manual review

Routers con patrones aceptados como deuda manual. No bloquean GO pero requieren revisión antes de cualquier hardening futuro.

| Router | Patrón | Justificación |
|---|---|---|
| `cid_visual_reference_routes.py` | Placeholder / profile | Endpoints stateless de análisis visual y alineación; sin project_id en scope. Aceptado como superficie de utilidad, no expone datos tenant. |
| `script_intelligence_routes.py` | Service-level org scoping | `/analyze-full` confía en `analyze_project(..., organization_id=...)` del servicio en lugar de `validate_project_access` como `Depends`. Tenant + module_access sí presentes. |
| `render_routes.py` | User-owned job pattern | Submit/retry de jobs pertenece al usuario (`tenant.user_id`), no al proyecto. Ownership por `user_id` en lugar de por `project_id`. Aceptado. |
| `integration_routes.py` | n8n webhook surface | n8n status / test event. Auth vía `get_tenant_context`, no project-scoped. |
| `workflow_routes.py` | Utility / preset surface | Plan / build / validate workflow + preset CRUD. No project-scoped; patrones internos aceptados. |
| `app_registry_routes.py` | Operational catalog | Listado y refresh del registro de apps. Catálogo operacional, no expone datos tenant. |
| `events_routes.py` | SSE broadcaster | `GET /subscribe/{user_id}` y `POST /job-status` usan patrón SSE / internal broadcaster fuera del modelo HTTP estándar. |
| `demo_routes.py` | Demo / admin mutators | Rutas de seeding y demo. Patrón interno de demo aceptado. |

Cualquier nueva ruta que aparezca en esta lista debe justificar el patrón y obtener aprobación explícita.

## Routers cerrados en fases 3K-3O

Las siguientes 5 rutas estaban marcadas con P0/P1 en AUDIT.6 y han sido cerradas en fases posteriores. Se incluyen como referencia de fases ya completas.

| Fase | Router | Cierre |
|---|---|---|
| 3K | `dubbing_bridge_routes.py` | `P0=2, P1=1` → `0,0`. Helper local para project-scoped; `require_write_permission` en mutantes. |
| 3L | `ollama_storyboard_routes.py` | `P0=2` → `0`. `validate_project_access` + `require_write_permission` + `require_module_access`. |
| 3M | `cid_script_to_prompt_routes.py` | `P0=1` → `0`. Helper `_validate_script_to_prompt_project_access` para `/analyze-full`. |
| 3N | `comfyui_storyboard_routes.py` | `P1=1` → `0`. `require_write_permission` en render POST + tenant context en status GET. |
| 3O | `storyboard_presentation_routes.py` | `P1=1` → `0`. `_ensure_project_access` + `require_write_permission` en sheet POST. Artifact download read-only se mantiene sin write gate. |

Cada cierre tiene un test contract en `tests/unit/test_<router>_gating_contract.py` que verifica estáticamente que el router cumple el contrato.

## Validaciones finales

Las siguientes validaciones se ejecutan en cada cambio de routing o cierre de fase.

### Tests contract gating

```bash
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m pytest tests/unit/test_*_gating_contract.py -q
```

Estado actual: 239 tests contract gating en 22 archivos, todos en verde.

### Guard de seguridad

```bash
git diff --check
bash scripts/dev/guard_wsl_repo.sh
```

Verifica:
- Sin errores de whitespace en el diff.
- WSL pwd correcto (`/opt/SERVICIOS_CINE`).
- Sin rutas Windows en pwd.
- Sin copia anidada (`/opt/SERVICIOS_CINE/opt` no existe).
- Sin `.env`, `*.db`, ni artefactos sensibles staged.
- Sin secretos en diff staged.

### Estado de repo

```bash
git status --short --untracked-files=all
```

Esperado: vacío tras el cierre o solo el nuevo archivo `backend_gating_contract_v1.md` durante la fase 1.

## Hardening opcional futuro

Recomendaciones de seguimiento, no bloqueantes para el cierre:

1. **Normalizar import legacy** `from routes.auth_routes import get_tenant_context` → `from dependencies.tenant_context import get_tenant_context` en los routers ya cerrados que aún usan la ruta legacy (`google_drive_routes.py`, `integration_routes.py`, `render_routes.py`, `sales_targets_routes.py`, `shot_routes.py`). Funcional hoy; consistencia de import path.
2. **Migrar service-level org scoping** en `script_intelligence_routes.py` a `validate_project_access` cuando el endpoint evolucione a recibir `project_id` por path en lugar de body.
3. **Considerar `validate_project_access`** en `events_routes.py` si el broadcaster SSE evoluciona a project-scoped.
4. **Re-evaluar P2** en cada nueva fase de routing y reducirlo a `P2=0` solo si los patrones desaparecen.

## Referencias

- `/tmp/cid_backend_gating_closure_audit_6.md` — baseline pre-3K.
- `/tmp/cid_backend_gating_closure_audit_7.md` — baseline GO.
- `docs/architecture/cid_backend_gating_policy_v1.md` — política general.
- `docs/product/cid_project_access_model_v1.md` — modelo de acceso por proyecto.
- `src/dependencies/tenant_context.py` — implementación de dependencias.
- `src/dependencies/module_access.py` — gating por módulo/plan.
- `tests/unit/test_*_gating_contract.py` — tests contract por router.
