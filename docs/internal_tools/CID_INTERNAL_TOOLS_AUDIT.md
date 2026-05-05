# CID INTERNAL TOOLS — FASE 1 AUDIT

## 1. Resumen ejecutivo

AILinkCinema/CID cuenta con una arquitectura multi-tenant basada en Organization, con planes definidos en `plans.yml` y un sistema de autenticación JWT funcional. Existen endpoints administrativos básicos, pero **no hay una consola interna unificada** para gestión operativa, comercial y de soporte. El sistema de permisos se basa en `access_level == "admin"` y `cid_enabled`, sin RBAC granular. Se requiere construir "CID Internal Tools" como capa segura de administración interna.

## 2. Estado actual del sistema

| Componente | Estado | Notas |
|---|---|---|
| Multi-tenant (Organization) | ✅ Operativo | User → Organization → billing_plan |
| Auth JWT | ✅ Operativo | `get_tenant_context()` resuelve plan efectivo |
| Plan limits | ✅ Operativo | `plans.yml` + `plan_limits_service.py` |
| Admin routes básicos | ⚠️ Limitados | Solo system overview, listar proyectos/jobs/orgs |
| Plan change API | ✅ Operativo | `POST /api/plans/change` (solo propio) |
| CID Pipeline Builder | ⚠️ Feature flag | `CID_PIPELINE_BUILDER_ENABLED` |
| User management | ❌ Faltante | No hay CRUD de usuarios para admins |
| Demo requests workflow | ❌ Faltante | No hay aprobación/rechazo programático |
| Partner interests workflow | ❌ Faltante | No hay gestión de leads comerciales |
| Audit log | ❌ Faltante | No hay trazabilidad de cambios administrativos |
| RBAC granular | ❌ Faltante | Solo `access_level == "admin"` |
| Frontend admin UI | ❌ Faltante | No existe layout ni páginas de administración |

## 3. Capacidades ya existentes

### Backend reusable
- **`src/routes/admin_routes.py`**: `/system/overview`, `/scheduler/status`, `/projects`, `/jobs`, `/organizations`
- **`src/routes/plan_routes.py`**: `/catalog`, `/me`, `/change`, `/{plan_name}`, `/{plan_name}/can-run/{task_type}`
- **`src/services/account_service.py`**: `apply_internal_plan_change()`, `get_user_by_email()`, `resolve_effective_plan()`
- **`src/models/core.py`**: Modelos `User`, `Organization`, `Project`, `ProjectJob` con campos necesarios
- **`src/config/plans.yml`**: 6 planes (demo, free, creator, producer, studio, enterprise)

### Frontend reusable
- **`src_frontend/src/store/auth.ts`**: `canAccessCID()`, `canAccessProgram()`, `getAccessLevel()`, `getPrimaryCIDTarget()`
- **`src_frontend/src/types/auth.ts`**: Tipos `CIDProgram`, `AccessLevel`, `AccountStatus`, `UserProfile`
- **`src_frontend/src/api/client.ts`**: Cliente Axios con interceptor de auth

## 4. Carencias detectadas

1. **Sin CRUD de usuarios para admins**: No hay endpoints para listar/buscar/modificar usuarios por terceros
2. **Sin gestión de demo requests**: Los usuarios con `signup_type="demo_request"` no tienen flujo de aprobación
3. **Sin gestión de partner interests**: Los `signup_type="partner_interest"` no tienen flujo comercial
4. **Sin audit log**: Los cambios de plan, CID enable, account_status no se registran con motivo/actor
5. **Sin RBAC granular**: Solo `is_admin = (access_level == "admin")`, no hay roles como operator/sales/support
6. **Sin feature flags dinámicos**: `CID_PIPELINE_BUILDER_ENABLED` es env var, no hay gestión por org
7. **Sin gestión de organizaciones**: No hay endpoint para cambiar plan de org o desactivarla
8. **Sin dashboard interno**: No hay consola unificada para el equipo interno

## 5. Riesgos técnicos y de seguridad

| Riesgo | Severidad | Mitigación propuesta |
|---|---|---|
| Admin puede quitarse acceso a sí mismo | Alta | Validar en backend que al menos un admin quede |
| Cambios de plan sin trazabilidad | Alta | Implementar `AdminAuditLog` obligatorio |
| Emails de testers expuestos en frontend | Media | Nunca enviar lista de testers al frontend |
| Feature flags controlados por env | Media | Migrar a DB o configuración centralizada |
| `access_level` string sin validación | Media | Usar enum o validación estricta en Pydantic |
| Plan override sin expiración | Baja | Agregar TTL o logs de reactivación |
| No hay rate limiting específico para admin | Media | Aplicar límite `admin` en `rate_limiter.py` |

## 6. Arquitectura propuesta

```
┌─────────────────────────────────────────────────────┐
│           CID Internal Tools (Frontend)            │
│  /internal/dashboard                              │
│  /internal/users                                  │
│  /internal/organizations                          │
│  /internal/demo-requests                         │
│  /internal/partner-interests                      │
│  /internal/audit-log                             │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│      API Layer (Backend - Nuevos routers)        │
│  /api/internal/*  (protegido por RBAC)          │
│  - users.py                                     │
│  - organizations.py                             │
│  - demo_requests.py                             │
│  - partner_interests.py                         │
│  - audit.py                                     │
│  - feature_flags.py                             │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│      Service Layer (Lógica de negocio)           │
│  - internal_user_service.py                     │
│  - internal_org_service.py                      │
│  - demo_workflow_service.py                      │
│  - partner_workflow_service.py                   │
│  - audit_service.py                             │
└──────────────────────┬──────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────┐
│      Data Layer (Models + Audit Log)             │
│  - AdminAuditLog (nuevo modelo)                 │
│  - FeatureFlag (opcional, nuevo modelo)         │
│  - User, Organization (existentes)              │
└─────────────────────────────────────────────────┘
```

## 7. Módulos funcionales propuestos

### A. Internal Dashboard
- Resumen del sistema (reutiliza `/api/admin/system/overview`)
- Contadores: usuarios activos, organizaciones, proyectos, jobs
- Solicitudes demo pendientes
- Partner interests pendientes
- Jobs recientes con errores
- Alertas de seguridad (intentos de acceso fallidos, etc.)

### B. User Management
- `GET /api/internal/users` — listar con filtros (email, org, plan, signup_type, account_status)
- `GET /api/internal/users/{user_id}` — detalle de usuario
- `PATCH /api/internal/users/{user_id}/access` — cambiar account_status, cid_enabled, onboarding_completed, access_level
- `PATCH /api/internal/users/{user_id}/plan` — cambiar billing_plan (requiere motivo)
- `POST /api/internal/users/{user_id}/impersonate` — (futuro) login as user

### C. Organization Management
- `GET /api/internal/organizations` — listar organizaciones
- `GET /api/internal/organizations/{org_id}` — detalle + usuarios asociados
- `PATCH /api/internal/organizations/{org_id}/plan` — cambiar billing_plan
- `PATCH /api/internal/organizations/{org_id}/status` — activar/desactivar
- `GET /api/internal/organizations/{org_id}/projects` — proyectos de la org
- `GET /api/internal/organizations/{org_id}/jobs` — jobs de la org

### D. Plan & Access Control
- Reutiliza `GET /api/plans/catalog` para ver planes disponibles
- `GET /api/internal/users/{user_id}/effective-plan` — muestra plan resuelto
- `POST /api/internal/users/{user_id}/plan-override` — override temporal (con TTL)
- Registro obligatorio de motivo en audit log

### E. Demo Requests
- `GET /api/internal/demo-requests` — listar usuarios con `signup_type="demo_request"` y `account_status="pending"`
- `POST /api/internal/demo-requests/{user_id}/approve` — cambia a `account_status="active"`, `signup_type="cid_user"`, asigna plan (demo/creator/producer)
- `POST /api/internal/demo-requests/{user_id}/reject` — mantiene `account_status="pending"` o cambia a `suspended`
- Notas internas comerciales (campo en `AdminAuditLog`)

### F. Partner Interests
- `GET /api/internal/partner-interests` — listar `signup_type="partner_interest"`
- `PATCH /api/internal/partner-interests/{user_id}` — cambiar estado, notas comerciales
- Conversión a organización enterprise (crea Organization + cambia user)

### G. Feature Flags
- Propuesta: migrar de env vars a tabla `feature_flags`:
  - `flag_name` (ej: `cid_pipeline_builder`)
  - `enabled_global` (bool)
  - `enabled_for_orgs` (JSON array de org_ids)
  - `enabled_for_users` (JSON array de user_ids)
- `GET /api/internal/feature-flags` — listar flags
- `PATCH /api/internal/feature-flags/{flag_name}` — actualizar

### H. Audit Log
- Modelo `AdminAuditLog`:
  - `id`, `admin_user_id`, `target_user_id`, `target_org_id`
  - `action` (enum: plan_change, access_change, cid_toggle, etc.)
  - `previous_value`, `new_value`
  - `reason` (obligatorio para cambios sensibles)
  - `timestamp`
- `GET /api/internal/audit-log` — consulta con filtros

## 8. Endpoints propuestos

| Método | Ruta | Descripción | Auth | Permiso | Modelo/Servicio | Riesgo |
|---|---|---|---|---|---|---|
| GET | `/api/internal/dashboard` | Resumen sistema | Admin | admin | existente | Bajo |
| GET | `/api/internal/users` | Listar usuarios | Admin | admin | User | Bajo |
| GET | `/api/internal/users/{id}` | Detalle usuario | Admin | admin | User | Bajo |
| PATCH | `/api/internal/users/{id}/access` | Cambiar acceso | Admin | admin | User | Medio |
| PATCH | `/api/internal/users/{id}/plan` | Cambiar plan | Admin | admin | User+Org | Alto |
| GET | `/api/internal/organizations` | Listar orgs | Admin | admin | Organization | Bajo |
| GET | `/api/internal/organizations/{id}` | Detalle org | Admin | admin | Organization | Bajo |
| PATCH | `/api/internal/organizations/{id}/plan` | Cambiar plan org | Admin | admin | Organization | Alto |
| PATCH | `/api/internal/organizations/{id}/status` | Activar/desactivar | Admin | admin | Organization | Medio |
| GET | `/api/internal/demo-requests` | Listar demo reqs | Admin | admin/sales | User | Bajo |
| POST | `/api/internal/demo-requests/{id}/approve` | Aprobar demo | Admin | admin/sales | User | Medio |
| POST | `/api/internal/demo-requests/{id}/reject` | Rechazar demo | Admin | admin/sales | User | Medio |
| GET | `/api/internal/partner-interests` | Listar partners | Admin | admin/sales | User | Bajo |
| PATCH | `/api/internal/partner-interests/{id}` | Gestionar partner | Admin | admin/sales | User+Org | Medio |
| GET | `/api/internal/audit-log` | Consultar audit | Admin | admin | AdminAuditLog | Bajo |
| GET | `/api/internal/feature-flags` | Listar flags | Admin | admin | FeatureFlag | Bajo |
| PATCH | `/api/internal/feature-flags/{name}` | Cambiar flag | Admin | admin | FeatureFlag | Medio |

## 9. Modelos nuevos propuestos

### AdminAuditLog (Prioridad: ALTA)
```python
class AdminAuditLog(Base):
    __tablename__ = "admin_audit_logs"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    admin_user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    target_user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    target_org_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # plan_change, access_change, etc.
    previous_value: Mapped[Optional[str]] = mapped_column(String(500))
    new_value: Mapped[Optional[str]] = mapped_column(String(500))
    reason: Mapped[Optional[str]] = mapped_column(String(1000))
    metadata_json: Mapped[Optional[str]] = mapped_column(String(5000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```
- Índices: `admin_user_id`, `target_user_id`, `target_org_id`, `created_at`
- Requiere migración Alembic
- Prioridad: ALTA (para cumplimiento y seguridad)

### FeatureFlag (Prioridad: MEDIA)
```python
class FeatureFlag(Base):
    __tablename__ = "feature_flags"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    flag_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    enabled_global: Mapped[bool] = mapped_column(Boolean, default=False)
    enabled_for_orgs: Mapped[Optional[str]] = mapped_column(String(5000))  # JSON array
    enabled_for_users: Mapped[Optional[str]] = mapped_column(String(5000))  # JSON array
    description: Mapped[Optional[str]] = mapped_column(String(500))
    updated_by: Mapped[Optional[str]] = mapped_column(String(36))
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```
- Requiere migración Alembic
- Prioridad: MEDIA (puede empezar con env vars)

### InternalNote (Prioridad: BAJA)
```python
class InternalNote(Base):
    __tablename__ = "internal_notes"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: uuid.uuid4().hex)
    target_user_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    author_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    note_type: Mapped[str] = mapped_column(String(50))  # sales, support, general
    content: Mapped[str] = mapped_column(String(2000))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```
- Prioridad: BAJA (puede usar `AdminAuditLog.metadata_json` inicialmente)

## 10. RBAC y permisos internos

### Propuesta de evolución de `access_level`

Actualmente: `"none" | "limited" | "standard" | "full"` (en frontend) / `String(50)` en backend.

Propuesta para Internal Tools:

| Rol | access_level | Permisos |
|---|---|---|
| admin | `admin` | Acceso total a Internal Tools |
| operator | `operator` | Gestión de usuarios y orgs (no feature flags) |
| sales | `sales` | Demo requests, partner interests, notas comerciales |
| support | `support` | Solo lectura de usuarios y auditoría |

### Implementación inicial (MVP)
- Mantener `is_admin = (user.access_level == "admin")` para MVP
- En el futuro: crear tabla `role_assignments` o expandir `access_level` a enum validado

### Acciones que requieren motivo obligatorio
- Cambio de plan (cualquier plan change)
- Desactivación de cuenta o organización
- Desactivación de `cid_enabled`
- Cambios de `account_status` a suspended/inactive

### Protección contra autobloqueo
- En `PATCH /internal/users/{id}/access`: validar que no se quede el sistema sin admins
- Verificar: `if target_user_id == admin_user_id AND new_access_level != "admin" → 403`

## 11. Audit log y trazabilidad

### Acciones que deben ser auditadas (obligatorio)
- Plan changes (usuario y organización)
- Account status changes
- CID enabled/disabled
- Access level changes
- Demo request approval/rejection
- Partner interest status changes
- Feature flag changes

### Estructura de log recomendada
```json
{
  "admin_user_id": "user_uuid",
  "action": "plan_change",
  "target_user_id": "target_uuid",
  "previous_value": "free",
  "new_value": "enterprise",
  "reason": "Cliente upgradeado para demo comercial",
  "metadata": {"demo_type": "sales_call", "duration_days": 30},
  "timestamp": "2026-05-05T10:00:00Z"
}
```

## 12. Feature flags

### Estado actual
- `CID_PIPELINE_BUILDER_ENABLED` → variable de entorno
- `ENABLE_DEMO_ROUTES` → variable de entorno
- `ENABLE_EXPERIMENTAL_ROUTES` → variable de entorno
- `ENABLE_POSTPRODUCTION_ROUTES` → variable de entorno

### Propuesta
Por ahora (MVP): mantener variables de entorno, documentar en `config.py`.

Futuro: migrar a tabla `feature_flags` con soporte por org/usuario.

### CID Internal Test Mode (nuevo)
- `CID_INTERNAL_TEST_MODE_ENABLED` → env var
- `CID_INTERNAL_TESTER_EMAILS` → env var (lista separada por comas)
- `CID_INTERNAL_TEST_PLAN` → env var (default: enterprise)

Este mecanismo ya está implementado en la FASE 2 anterior (ver `src/services/cid_test_mode.py`).

## 13. Frontend propuesto

### Rutas protegidas
```
/internal/dashboard          → Dashboard principal
/internal/users              → Gestión de usuarios
/internal/users/:id          → Detalle de usuario
/internal/organizations      → Gestión de organizaciones
/internal/organizations/:id  → Detalle de organización
/internal/demo-requests      → Solicitudes demo
/internal/partner-interests  → Intereses partner
/internal/audit-log         → Auditoría
/internal/feature-flags      → Feature flags (futuro)
```

### Protección de rutas
```typescript
// En router, validar:
if (!user || user.access_level !== 'admin') {
  redirect('/')
}
```

### Layout sugerido
- Sidebar izquierdo con secciones (Dashboard, Users, Orgs, Demo, Partners, Audit)
- Header con info de admin y logout
- No visible en navegación pública
- No indexado por motores de búsqueda (meta robots noindex)

## 14. Plan de implementación por sprints

### Sprint Internal Tools 1 (Backend Read-only)
- Crear modelos `AdminAuditLog` + migración Alembic
- Expandir `admin_routes.py` con:
  - `GET /api/admin/users` (listar todos los usuarios)
  - `GET /api/admin/users/{user_id}` (detalle)
  - `GET /api/admin/demo-requests`
  - `GET /api/admin/partner-interests`
- Frontend: página básica `/internal/dashboard` (solo lectura)

### Sprint Internal Tools 2 (Cambios controlados)
- `PATCH /api/admin/users/{id}/access`
- `PATCH /api/admin/users/{id}/plan` (con audit log)
- `PATCH /api/admin/organizations/{id}/plan`
- `PATCH /api/admin/organizations/{id}/status`
- Frontend: formularios de edición de usuario/org

### Sprint Internal Tools 3 (Demo y Partners)
- `POST /api/admin/demo-requests/{id}/approve`
- `POST /api/admin/demo-requests/{id}/reject`
- `PATCH /api/admin/partner-interests/{id}`
- Conversión de partner a org enterprise
- Frontend: vistas de aprobación/rechazo

### Sprint Internal Tools 4 (Audit y RBAC)
- `GET /api/admin/audit-log` con filtros
- Validación de no autobloqueo
- Expansión de `access_level` a roles granulares
- Frontend: vista de auditoría

### Sprint Internal Tools 5 (Frontend completo)
- Dashboard completo con métricas
- Búsqueda y filtros en todas las vistas
- Navegación interna completa
- Móvil responsive (opcional)

## 15. Decisiones pendientes

1. **¿Usar `access_level` string o crear tabla de roles?** → Para MVP, mantener string con validación. Futuro: tabla `role_assignments`.
2. **¿Feature flags en DB o seguir con env vars?** → Para MVP, mantener env vars. Futuro: tabla `feature_flags`.
3. **¿Dónde guardar notas comerciales?** → Inicialmente en `AdminAuditLog.metadata_json`. Futuro: tabla `internal_notes`.
4. **¿El admin puede impersonar a usuarios?** → NO para MVP (riesgo de seguridad). Evaluar en el futuro.
5. **¿Integrar con sistema de pagos real?** → NO. Los cambios de plan via Internal Tools son manuales y no deben disparar cobros.

## 16. Recomendación final

Se recomienda **GO** para pasar a implementación, con las siguientes condiciones:

1. **MVP inicial**: Implementar solo Sprint 1 y 2 (read-only + cambios controlados con audit log)
2. **Seguridad**: Obligatorio implementar `AdminAuditLog` y validación de motivo en cambios de plan
3. **No modificar flujos de pagos**: Los cambios de plan son manuales y sin cobro
4. **Proteger autobloqueo**: Validar que siempre quede al menos un admin
5. **CID Internal Test Mode**: Ya implementado (ver FASE 2), usar como base para pruebas
6. **No tocar `ailinkcinema_s2.db`**: Usar migraciones Alembic para cambios en DB

El sistema actual tiene las bases sólidas (multi-tenant, planes, auth) para construir CID Internal Tools de forma segura y progresiva.

---

## 17. CID Internal Test Routes — Análisis detallado

> Fuente: `src/routes/cid_test_routes.py` · Auditado: 2026-05-05

### 17.1 Registro del router

```python
router = APIRouter(prefix="/api/internal-test", tags=["cid-internal-test"])
```

**Prefijo**: `/api/internal-test`  
**Tag**: `cid-internal-test`

### 17.2 Guard de acceso — `require_internal_tester`

```python
async def require_internal_tester(tenant: TenantContext = Depends(get_tenant_context)) -> TenantContext:
    if not tenant.is_admin:
        raise HTTPException(status_code=403)
    if not is_internal_tester(tenant.user.email):
        raise HTTPException(status_code=403, detail="Not an internal tester")
    return tenant
```

**Requisito dual**: el usuario debe ser admin **Y** estar en `CID_INTERNAL_TESTER_EMAILS`.  
No basta con ser admin — las herramientas de test están estrictamente aisladas del acceso admin estándar.

### 17.3 Endpoints existentes

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/internal-test/demo-project` | Crea proyecto demo simulado en la DB |
| `POST` | `/api/internal-test/pipeline-simulation` | Simula ejecución completa de pipeline |
| `GET` | `/api/internal-test/status` | Estado del test mode (plan efectivo, emails activos) |

### 17.4 Servicio de soporte — `cid_test_mode.py`

Ubicación: `src/services/cid_test_mode.py`

| Función | Descripción |
|---|---|
| `is_test_mode_enabled()` | Lee `CID_INTERNAL_TEST_MODE_ENABLED` (env var, default `false`) |
| `get_test_plan()` | Lee `CID_INTERNAL_TEST_PLAN` (env var, default `enterprise`) |
| `get_tester_emails()` | Lee `CID_INTERNAL_TESTER_EMAILS` (CSV, default vacío) |
| `is_internal_tester(email)` | Combina `is_test_mode_enabled()` + `get_tester_emails()` |
| `apply_test_override(original_plan, email)` | Devuelve `(effective_plan, is_override_applied)` |

**Variables de entorno requeridas**:
```bash
CID_INTERNAL_TEST_MODE_ENABLED=true
CID_INTERNAL_TESTER_EMAILS=dev@ailinkcinema.com,qa@ailinkcinema.com
CID_INTERNAL_TEST_PLAN=enterprise   # default
```

### 17.5 Notas de seguridad
- La lista de testers **nunca se expone al frontend** — reside exclusivamente en env vars del servidor.
- El override de plan solo aplica para el contexto de test, no modifica la DB.
- `apply_test_override` es idempotente: si el usuario no es tester, devuelve el plan original sin cambios.

---

## 18. CID Pipeline Builder Routes — Análisis

> Fuente: `src/routes/cid_pipeline_routes.py` · Auditado: 2026-05-05

**Prefijo**: `/api/pipelines`  
**Feature flag**: `CID_PIPELINE_BUILDER_ENABLED` (env var, `0|1|true|false|yes|on`)

### 18.1 Endpoints registrados

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/pipelines/presets` | Listar presets de pipeline disponibles |
| `POST` | `/api/pipelines/validate` | Validar configuración de pipeline |
| `POST` | `/api/pipelines/generate` | Generar pipeline a partir de prompt/parámetros |
| `POST` | `/api/pipelines/execute` | Ejecutar pipeline (crea job simulado) |
| `GET` | `/api/pipelines/jobs` | Listar jobs de pipeline del tenant |
| `GET` | `/api/pipelines/jobs/{job_id}` | Detalle de job de pipeline |

### 18.2 Servicios de soporte

- `cid_pipeline_builder_service` — Lógica principal de construcción de pipeline
- `cid_pipeline_preset_service` — Catálogo de presets
- `cid_pipeline_simulated_job_service` — Jobs simulados (sin ComfyUI real)
- `cid_pipeline_validation_service` — Validación de configuraciones

### 18.3 Isolación de tenants

La función `_get_project_or_403` verifica:
```python
if not tenant.is_admin and str(project.organization_id) != str(tenant.organization_id):
    raise HTTPException(status_code=403)
```
Los admins pueden acceder a cualquier proyecto (necesario para Internal Tools).

---

## 19. Demo Routes — Análisis

> Fuente: `src/routes/demo_routes.py` · Auditado: 2026-05-05

**Prefijo**: `/api/demo`  
**Feature flag**: `ENABLE_DEMO_ROUTES` (env var)

### 19.1 Endpoints registrados

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/demo/status` | Estado del entorno demo |
| `GET` | `/api/demo/users` | Usuarios demo disponibles |
| `POST` | `/api/demo/seed` | Semillar datos de demo en la DB |
| `POST` | `/api/demo/reset` | Resetear entorno demo |
| `GET` | `/api/demo/jobs/{user_id}` | Jobs de un usuario demo |
| `GET` | `/api/demo/projects` | Proyectos demo |
| `GET` | `/api/demo/narrative-project` | Proyecto narrativo de demo |
| `GET` | `/api/demo/narrative-html` | HTML narrativo generado |
| `POST` | `/api/demo/seed-narrative` | Semillar proyecto narrativo |
| `GET` | `/api/demo/presets` | Presets disponibles en demo |
| `POST` | `/api/demo/quick-start` | Onboarding rápido de demo |

> ⚠️ **Nota de seguridad**: Estas rutas de demo deben estar desactivadas en producción (`ENABLE_DEMO_ROUTES=false`). Verificar que el seed/reset no pueda ejecutarse sobre la DB de producción.

---

## 20. Admin Routes existentes — Inventario completo

> Fuente: `src/routes/admin_routes.py` · Auditado: 2026-05-05

**Prefijo**: `/api/admin`  
**Guard**: `_require_admin(tenant)` → `tenant.is_admin == True`

| Método | Ruta | Descripción | Limitación detectada |
|---|---|---|---|
| `GET` | `/api/admin/system/overview` | Overview: scheduler, queue, backends | Solo datos de sistema, no usuarios |
| `GET` | `/api/admin/scheduler/status` | Estado del job scheduler | — |
| `GET` | `/api/admin/projects` | Todos los proyectos (cross-tenant) | Sin filtros de búsqueda |
| `GET` | `/api/admin/jobs` | Todos los jobs (cross-tenant) | Sin filtros, no incluye org |
| `GET` | `/api/admin/organizations` | Todas las orgs con stats básicas | `job_count` es placeholder (hardcoded 0) |

**Gap crítico**: `job_count` en `/api/admin/organizations` siempre devuelve `0` (comentario en código: `"Placeholder for now"`). Requiere join con `ProjectJob` via `Project`.

---

## 21. Hallazgos de frontend — Bugs identificados en audit

### Bug: Duplicate React key en LandingPage footer

**Archivo**: `src_frontend/src/data/landingContent.ts`  
**Detectado**: Console log de browser, 2026-05-05  
**Severidad**: Baja (advertencia React, no bloquea funcionalidad)

**Causa**: Dos entradas en `footer.links` compartían el mismo `href: '/pricing'`:
```ts
// ANTES (buggy)
{ label: 'Solicitar demo', href: '/pricing' },  // ← duplicado
{ label: 'Precios', href: '/pricing' },
```

**Fix aplicado** en esta sesión:
```ts
// DESPUÉS (correcto)
{ label: 'Solicitar demo', href: '/register/demo' },  // ← href único
{ label: 'Precios', href: '/pricing' },
```

**Estado**: ✅ Corregido en `src_frontend/src/data/landingContent.ts` línea 361.

### Advertencias de React Router v6 → v7

**Archivo**: `src_frontend/src/main.tsx` (App Router)  
**Tipo**: Advertencias de migración, no errores  
**Advertencias**:
- `v7_startTransition`: Activar future flag para transiciones de estado
- `v7_relativeSplatPath`: Activar future flag para resolución de rutas relativas en Splat routes

**Acción recomendada**: Agregar `future` flags al `BrowserRouter` cuando se planifique migración a React Router v7.

```tsx
// Solución futura (no urgente)
<BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
```

**Estado**: ⚠️ Pendiente (no urgente, no bloquea funcionamiento).

---

*Audit completado: 2026-05-05 — Versión 1.1*  
*Próxima acción: Sprint Internal Tools 1 — Backend read-only + AdminAuditLog*
