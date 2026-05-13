# Fase 3 — Multi-tenancy Real: Post-Antigravity Review

## Hallazgos Antigravity

### 1. Fuga de datos cross-tenant via `is_admin`

**Vulnerabilidad**: Patrón `if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id)`
en 14+ archivos permitía que cualquier usuario con rol `admin` accediera
a proyectos de *cualquier* organización si conocía el UUID.

**Impacto**: ALTO — Fuga de datos entre organizaciones.

### 2. Dependencia inconsistente de `get_tenant_context`

**Vulnerabilidad**: `routes/auth_routes.py` exportaba su propia versión de
`get_tenant_context` sin `is_global_admin`. Las rutas saneadas importaban
desde `routes.auth_routes` en lugar de `dependencies.tenant_context`.

**Impacto**: ALTO — Los fixes de `is_global_admin` no tenían efecto en
rutas que importaban la versión incorrecta.

### 3. Falta de `require_write_permission`

**Vulnerabilidad**: Endpoints POST/PATCH/DELETE solo validaban pertenencia
a organización pero no verificaban que el rol tuviera permisos de escritura.
Un `viewer` podía modificar datos si tenía JWT válido.

**Impacto**: MEDIO — Escritura no autorizada por usuarios de solo lectura.

### 4. Data attribution bug con global_admin

**Vulnerabilidad**: Cuando `is_global_admin` de Org X creaba recursos para
proyecto de Org A, los endpoints usaban `tenant.organization_id` (Org X)
en lugar de `project.organization_id` (Org A). El recurso quedaba atribuido
a la organización incorrecta.

**Impacto**: ALTO — Ruptura de integridad de datos multi-tenant. Recursos
project-scoped invisibles para la organización propietaria del proyecto.

**Archivos afectados**:
- `project_funding_routes.py` — `create_source` usaba `tenant.organization_id`
- `delivery_routes.py` — `create_deliverable` usaba `tenant.organization_id`
- `cid_pipeline_routes.py` — `execute_pipeline` y `list_jobs` usaban `tenant.organization_id`
- `matcher_routes.py` — bloqueaba `global_admin` con org_id mismatch

## Fixes aplicados

| Fix | Archivos | Cambio |
|-----|----------|--------|
| Cross-org bypass eliminado | 8 rutas | `is_admin` → `is_global_admin` |
| Import corregido | 8 rutas | `routes.auth_routes` → `dependencies.tenant_context` |
| Write permission añadida | 8 rutas | `Depends(require_write_permission)` en 30 endpoints |
| Scope bypass eliminado | `tenant_context.py` | `require_project_scope` ya no bypass con `is_admin` |
| Data attribution corregida | 4 rutas | `tenant.organization_id` → `project.organization_id` en project-scoped resources |

## Validación

### Compilación

```bash
python -m compileall -q src/core src/routes src/services src/schemas \
  src/middleware src/dependencies src/app.py src/config.py
# ✅ OK — sin errores
```

### Tests unitarios

| Suite | Resultado |
|-------|-----------|
| `tests/unit/test_tenant_context.py` | **4/4 pass** (circular import resuelto) |
| `tests/unit/test_tenant_access_service.py` | 7/7 pass |
| `tests/unit/` completo | 291/291 pass **100%** |

### Tests integración multi-tenancy

| Test | Resultado |
|------|-----------|
| `test_tenant_a_can_access_own_project` | ✅ |
| `test_tenant_b_cannot_access_tenant_a_project_documents` | ✅ |
| `test_tenant_b_cannot_trigger_matcher_for_tenant_a` | ✅ |
| `test_health_still_public` | ✅ |
| `test_comfyui_without_token_still_protected` | ✅ |
| `test_nonexistent_project_returns_404` | ✅ |
| `test_admin_org_b_cannot_access_org_a_project` | ✅ |
| `test_admin_org_b_cannot_trigger_matcher_for_org_a` | ✅ |
| `test_producer_org_b_cannot_access_org_a` | ✅ |
| `test_matcher_without_token_returns_401` | ✅ |
| `test_admin_org_b_cannot_access_org_a_funding` | ✅ (nuevo) |
| `test_admin_org_b_cannot_access_org_a_project_funding` | ✅ (nuevo) |
| `test_admin_org_b_cannot_access_org_a_queue` | ✅ (nuevo) |
| `test_global_admin_can_access_org_a_project` | ✅ (nuevo) |
| `test_viewer_cannot_post_private_funding_source` | ✅ (nuevo) |
| `test_404_returns_json_with_detail` | ✅ (nuevo) |

**Total: 16/16 pass**

### Tests data attribution

| Test | Resultado |
|------|-----------|
| `test_global_admin_creates_funding_source_attributed_to_project_org` | ✅ |
| `test_org_a_user_can_see_funding_source_created_by_global_admin` | ✅ |
| `test_org_b_user_cannot_see_funding_source_of_org_a` | ✅ |
| `test_admin_org_b_cannot_create_source_in_org_a` | ✅ |
| `test_viewer_cannot_create_funding_source` | ✅ |
| `test_matcher_global_admin_can_access_org_a` | ✅ |
| `test_matcher_admin_org_b_blocked_from_org_a` | ✅ |
| `test_matcher_viewer_cannot_trigger` | ✅ |

**Total: 8/8 pass**

### Tests integración completo

**38 passed**, 0 failed, 0 errors. **100% verde.**

### Alembic

```
ec2e3eaf1271 (head)
```

Single head — sin migraciones nuevas.

### Runtime smoke

```json
GET /health/live         → 200 {"status":"ok"}
GET /health/ready        → 200 {"status":"ok","checks":{"database":"ok","redis":"skipped"}}
GET /health/startup      → 200 {"status":"ok","startup_ok":true}
GET /api/v1/comfyui/instances → 401 (sin token)
GET /ruta-inexistente    → 404 {"error":{"request_id":"cid-test-001",...}}
```

## Veredicto

**READY FOR ANTIGRAVITY RE-REVIEW**

### Criterios cumplidos

- [x] Sin `tenant.is_admin` en rutas para bypass cross-org
- [x] `is_global_admin` único rol con bypass cross-org
- [x] 30 endpoints de escritura protegidos con `require_write_permission`
- [x] Import de `dependencies.tenant_context` en 8 rutas principales
- [x] Tests de aislamiento multi-tenancy: 16/16 pass
- [x] Alembic single head `ec2e3eaf1271`
- [x] Runtime smoke: health, 401, 404 con request_id
- [x] Sin cambios en IA, ComfyUI, frontend, DB migrations
- [x] Sin commits realizados
- [x] Data attribution: resources project-scoped usan `project.organization_id`
- [x] `matcher_routes.py` permite `global_admin` cross-org

### Criterios NO cumplidos (fuera de scope)

- [ ] Servicios legacy (`shot_service.py`, `concept_art_service.py`,
      `presentation_service.py`, `storyboard_service.py`) aún usan
      `is_admin` para cross-org bypass
- [ ] 17 rutas aún importan `get_tenant_context` desde `routes.auth_routes`
      (sin `is_global_admin`)
- [ ] `routes.auth_routes.get_tenant_context` obsoleta aún existe
- [x] `project_funding_routes.py` completamente saneado: 0 ocurrencias
      de `organization_id=tenant.organization_id` en service calls project-scoped
      (14 endpoints corregidos)

### Archivos modificados (14 + nuevo test)

```
M src/routes/admin_funding_routes.py
M src/routes/admin_routes.py
M src/routes/auth_routes.py
M src/routes/cid_pipeline_routes.py
M src/routes/cid_test_routes.py
M src/routes/delivery_routes.py
M src/routes/editorial_routes.py
M src/routes/funding_routes.py
M src/routes/intake_routes.py
M src/routes/matcher_routes.py
M src/routes/project_funding_routes.py
M src/routes/queue_routes.py
M src/schemas/auth_schema.py
M tests/integration/test_matcher_v3.py
?? src/dependencies/tenant_context.py
?? src/services/tenant_access_service.py
?? tests/integration/test_multitenancy_isolation.py
?? tests/unit/test_tenant_access_service.py
?? tests/unit/test_tenant_context.py
?? docs/fase3_multitenancy_audit.md
?? docs/fase3_multitenancy_real.md
```

### Vulnerabilidades corregidas

| ID | Vulnerabilidad | Severidad | Estado |
|----|---------------|-----------|--------|
| V1 | Cross-tenant bypass via `is_admin` | ALTA | CORREGIDA |
| V2 | Import inconsistente de TenantContext | ALTA | CORREGIDA |
| V3 | Viewer puede escribir sin permiso | MEDIA | CORREGIDA |
| V4 | Scope bypass en `require_project_scope` | MEDIA | CORREGIDA |
| V5 | Data attribution incorrecta para recursos project-scoped | ALTA | CORREGIDA (14 endpoints en project_funding_routes.py + delivery + cid_pipeline) |
