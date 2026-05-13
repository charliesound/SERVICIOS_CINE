# Fase 2 — Security Enterprise CID / AILinkCinema

## Objetivo

Elevar la seguridad del backend CID a nivel enterprise, añadiendo
JWT con claims estándar, protección de endpoints por scope/role,
security headers, internal API key, rate limit Redis-ready,
y auditoría de seguridad.

## Variables de entorno nuevas

```
# JWT Enterprise
JWT_ISSUER=ailinkcinema
JWT_AUDIENCE=cid-api
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
AUTH_DISABLED=false

# Internal API Key (opcional)
INTERNAL_API_KEY_ENABLED=false
INTERNAL_API_KEYS=

# Rate Limit
RATE_LIMIT_BACKEND=memory
LOGIN_RATE_LIMIT_PER_MINUTE=10

# Redis (necesario si RATE_LIMIT_BACKEND=redis)
REDIS_URL=
```

## JWT Claims obligatorios

| Claim | Descripción | Validación |
|-------|-------------|------------|
| `sub` | Identificador del usuario | Obligatorio |
| `exp` | Expiración (epoch) | Rechazar si expirado |
| `iat` | Emisión (epoch) | Rechazar si ausente o futuro. Margen clock skew: 30s |
| `nbf` | No válido antes de (epoch) | Rechazar si futuro |
| `iss` | Emisor: `ailinkcinema` | Rechazar si no coincide |
| `aud` | Audiencia: `cid-api` | Rechazar si no coincide |
| `roles` | Lista de roles del usuario | Para `require_role()` |
| `scopes` | Lista de scopes del usuario | Para `require_scope()` |

## Roles

| Role | Descripción |
|------|-------------|
| `admin` | Acceso completo a todo |
| `producer` | Gestión de proyectos y recursos |
| `operator` | Operación de instancias ComfyUI |
| `viewer` | Solo lectura |

## Scopes

| Scope | Descripción | Endpoints |
|-------|-------------|-----------|
| `projects:read` | Leer proyectos | Proyectos (read) |
| `projects:write` | Crear/editar proyectos | Proyectos (write) |
| `comfyui:read` | Leer instancias ComfyUI | `GET /api/v1/comfyui/instances`, `resolve` |
| `comfyui:health` | Health check ComfyUI | `GET /api/v1/comfyui/instances/*/health`, `/api/v1/comfyui/health` |
| `admin:read` | Leer config de admin | Admin (read) |
| `admin:write` | Modificar config de admin | Admin (write) |

## Endpoints públicos

```
GET /health/live
GET /health/ready
GET /health/startup
```

## Endpoints protegidos (con scope)

| Ruta | Scope | Método |
|------|-------|--------|
| `/api/v1/comfyui/instances` | `comfyui:read` | GET |
| `/api/v1/comfyui/instances/{key}` | `comfyui:read` | GET |
| `/api/v1/comfyui/instances/{key}/health` | `comfyui:health` | GET |
| `/api/v1/comfyui/health` | `comfyui:health` | GET |
| `/api/v1/comfyui/resolve/{task_type}` | `comfyui:read` | GET |

## Cómo generar token de prueba

```python
from routes.auth_routes import create_access_token

token = create_access_token({
    "sub": "test-user",
    "roles": ["admin"],
    "scopes": ["comfyui:read", "comfyui:health"],
    "organization_id": "test-org",
})
print(f"Bearer {token}")
```

O usando curl + login real:

```bash
curl -s -X POST http://127.0.0.1:8010/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@test.com","password":"test123"}' | jq -r '.access_token'
```

## Cómo validar con curl

### Sin token (debe fallar con AUTH_DISABLED=false):

```bash
curl -i http://127.0.0.1:8010/api/v1/comfyui/instances
# → 401 Unauthorized
```

### Con token válido:

```bash
TOKEN=$(python3 -c "
from routes.auth_routes import create_access_token
print(create_access_token({'sub':'test','roles':['admin'],'scopes':['comfyui:read','comfyui:health'],'organization_id':'org'}))
")
curl -i -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8010/api/v1/comfyui/instances
# → 200 OK
```

### Health público (siempre accesible):

```bash
curl -i http://127.0.0.1:8010/health/live
# → 200 OK (sin auth)
```

### Security headers:

```bash
curl -i http://127.0.0.1:8010/health/live
# Verificar:
# X-Content-Type-Options: nosniff
# X-Frame-Options: DENY
# Referrer-Policy: no-referrer
# Permissions-Policy: camera=(), microphone=(), geolocation=()
```

## Modo AUTH_DISABLED en development

Para desarrollo local sin necesidad de tokens:

```bash
AUTH_DISABLED=true python -m uvicorn app:app
```

En este modo:
- Todos los endpoints protegidos son accesibles sin token
- Se genera un `TokenData` de bypass con rol `admin` y todos los scopes
- Se registra un log `auth_disabled_dev_bypass` por cada request
- **NUNCA** usar en production (validado en startup con error)

## Riesgos pendientes

1. Las rutas antiguas (`/api/auth/me`, `/api/users/*`, etc.) NO están
   protegidas con scopes en esta fase (se refactorizarán en Fase 3+).
   Usan su propio sistema de autenticación basado en la dependencia
   `get_current_user` de `dependencies/auth.py`.

2. El rate limit Redis no está implementado como backend real.
   La configuración `RATE_LIMIT_BACKEND=redis` existe pero el driver
   Redis no está conectado. Es preparación para integración futura.

3. No hay multi-tenancy real implementado. El campo `organization_id`
   está presente en el token pero no se valida contra la organización
   del usuario en cada request.

## Próxima fase recomendada

Fase 3 — Multi-tenancy real:
- Validar `organization_id` del token contra el recurso solicitado
- Aislar datos por organización
- Scopes por organización
- Rate limit con Redis real
- Refactorizar auth legacy a scopes
- Refresh token rotation
- Password complexity policy
- Account lockout after N failed attempts
