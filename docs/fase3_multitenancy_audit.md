# Fase 3.0 — Multi-tenant Audit CID / AILinkCinema

## Modelos con organization_id

| Modelo | Columna | Nullable | Notas |
|--------|---------|----------|-------|
| `Organization` | N/A (es el tenant) | — | Entidad raíz del tenant |
| `User` | `organization_id` | NO | FK al tenant |
| `Project` | `organization_id` | NO | FK al tenant |
| `ProjectJob` | `organization_id` | NO (indexed) | FK al tenant |
| `ProjectMember` | `organization_id` | — (en otro archivo) | Miembros del proyecto |

## Modelos sin organization_id que podrían necesitarlo

Ninguno identificado como crítico. Los modelos sin org_id son tablas
de sistema o utilidad (Metrics, Events, etc.) que no requieren
aislamiento multi-tenant.

## Rutas con project_id

| Archivo | Endpoints | Auth actual | Riesgo |
|---------|-----------|-------------|--------|
| `project_document_routes.py` | 8 endpoints | ✅ TenantContext + org check | Bajo |
| `funding_routes.py` | 10+ endpoints | ✅ TenantContext (except 3 públicos) | Bajo |
| `matcher_routes.py` | 3 endpoints | ❌ Sin auth, usa org_id query param | **ALTO** |
| `project_routes.py` (analyze) | 1 endpoint | ⚠️ get_current_user_optional | Medio |
| `funding_catalog_routes.py` | — | No revisado | Medio |
| `budget_routes.py` | — | No revisado | Medio |

## Patrones de acceso actuales

1. **Recomendado — TenantContext**: Usa `get_tenant_context` → compara
   `project.organization_id` con `tenant.organization_id`. Usado en
   `project_document_routes.py` y `funding_routes.py`.

2. **Vulnerable — query param**: Acepta `organization_id` como query
   param sin verificar JWT. Usado en `matcher_routes.py`.

3. **Manual — fetch user**: Obtiene user desde DB, obtiene org, compara.
   Usado en `project_routes.py` analyze endpoint.

## Hallazgos críticos

### 1. JWT no incluye organization_id
`create_access_token` en auth_routes.py solo incluye `sub` y `email`.
El `TokenData` en security.py espera `organization_id` del payload
pero nunca se incluye en la creación del token.

### 2. matcher_routes.py sin autenticación
Los endpoints `/trigger`, `/status`, `/jobs` aceptan `organization_id`
como query param y NO validan que el caller pertenezca a esa org.
Cualquier cliente con acceso a la red puede ejecutar jobs de matcher
para cualquier proyecto/organización.

### 3. Dual auth sin coordinación
- `dependencies/auth.py` / `auth_routes.py`: usa `get_tenant_context`
  con `TenantContext`
- `dependencies/security.py`: usa `TokenData` con `require_scope`
- Cada sistema tiene su propia convención de claims en el token

### 4. UserResponse sin organization_id
El schema de respuesta de usuario (auth_schema.py) no expone
`organization_id`, haciéndolo invisible para el frontend.

## Prioridades

| Prioridad | Acción | Fase |
|-----------|--------|------|
| 🔴 Crítica | Fix JWT para incluir organization_id | 3.1 |
| 🔴 Crítica | Añadir auth a matcher_routes.py | 3.2 |
| 🟡 Alta | Crear tenant_access_service.py | 3.3 |
| 🟡 Alta | Tests anti data leakage | 3.4 |
| 🟢 Media | Cross-tenant checks en endpoints restantes | 3.5+ |
