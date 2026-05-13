# Fase 2.0 — Security Audit CID / AILinkCinema

## Alcance

Auditoría de seguridad completa del backend CID antes de implementar
la capa Enterprise Security (Fase 2).

## Hallazgos

### 1. Sistema de autenticación dual

Existen dos sistemas de configuración que pueden divergir:
- **Nuevo**: Pydantic `core.config.Settings` (lectura de `.env`)
- **Legado**: YAML `config.py` → `config` dict singleton

Las rutas de auth (`routes/auth_routes.py`) leen desde el dict legacy
`config["auth"]`, no desde Settings. Si las env vars actualizan Settings
pero no el dict legacy, pueden divergir.

**Riesgo**: Medio. El dict legacy se sincroniza durante startup.

### 2. JWT — Carencias Enterprise

| Aspecto | Estado actual | Requerido |
|---------|--------------|-----------|
| `exp` | ✅ Implementado | Obligatorio |
| `iat` | ❌ No incluido | Obligatorio |
| `nbf` | ❌ No incluido | Obligatorio |
| `iss` | ❌ No incluido | Obligatorio |
| `aud` | ❌ No incluido | Obligatorio |
| Validación issuer | ❌ No se valida | Obligatorio |
| Validación audience | ❌ No se valida | Obligatorio |
| Algoritmo explícito | ✅ HS256 | Obligatorio |

### 3. Endpoints ComfyUI sin autenticación

Los 5 endpoints de `/api/v1/comfyui/*` exponen:
- URLs internas de 5 instancias ComfyUI
- Puertos y health status
- Mapeo task_type → instancia

**Riesgo**: Alto. Cualquier persona con acceso a la red puede obtener
el mapa completo de infraestructura ComfyUI.

### 4. Secrets y credenciales

| Hallazgo | Riesgo |
|----------|--------|
| `.env` contiene `GOOGLE_DRIVE_CLIENT_ID` y `GOOGLE_DRIVE_CLIENT_SECRET` reales | Alto |
| `certs/server.key` en el repo | Alto |
| `JWT_SECRET` no está definido en `.env` (solo `AUTH_SECRET_KEY`) | Medio |

### 5. Rate Limiting

- **In-memory**: Los límites se pierden al reiniciar el servidor
- **Sin Redis**: No escalable a múltiples workers/instancias
- Límite de auth: 10 req/60s basado en IP

### 6. Security Headers

El `Caddyfile.deploy` ya configura algunos headers a nivel proxy:
```
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

Pero la app FastAPI no los establece por sí misma, lo que significa
que en entornos sin Caddy (dev local, test) estos headers no están
presentes.

### 7. CORS

- `cors_allowed_methods: ["*"]` y `cors_allowed_headers: ["*"]`
- En production se valida que origins no contengan `*`
- En development se permite `*` con warning

### 8. Roles y permisos

Existe un sistema de roles (owner, admin, producer, etc.) en
`role_permission_service.py` para el frontend, pero no hay
scopes ni enforcement a nivel de API backend.

### 9. Tasa de login

- Hardcoded en rate limiter middleware como 10 req/60s para `/api/auth/*`
- No configurable desde env var

### 10. Sin Internal API Key

No existe mecanismo para integraciones internas (service-to-service).

## Prioridades

| Prioridad | Acción | Fase |
|-----------|--------|------|
| 🔴 Crítica | Proteger endpoints ComfyUI | 2.3 |
| 🔴 Crítica | Añadir iss/aud/iat/nbf a JWT | 2.1 |
| 🟡 Alta | Security Headers en app | 2.5 |
| 🟡 Alta | Dependencias require_scope/require_role | 2.2 |
| 🟡 Alta | Internal API Key | 2.4 |
| 🟢 Media | Redis-ready rate limit | 2.6 |
| 🟢 Media | Security audit logging | 2.7 |

## Recomendaciones adicionales

1. Rotar `GOOGLE_DRIVE_CLIENT_SECRET` y eliminar del `.env`
2. Eliminar `certs/server.key` del repositorio o añadir a `.gitignore`
3. Unificar sistema de configuración (eliminar legacy `config.py` a futuro)
4. Añadir `JWT_SECRET` al `.env` real
