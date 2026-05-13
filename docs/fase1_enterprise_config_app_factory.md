# Fase 1 — Config Enterprise / App Factory / Health / Error Handling

## Resumen Ejecutivo

Se refactorizó el arranque de la aplicación para usar un patrón **App Factory**
con **Pydantic Settings** como fuente de configuración canónica, **health checks**
separados (live/ready/startup), **error handling** global con formato JSON
uniforme, y **Request ID** obligatorio en toda petición.

## Archivos Creados

| Archivo | Propósito |
|---|---|
| `src/core/__init__.py` | Package init |
| `src/core/config.py` | Pydantic `BaseSettings` con validación por entorno |
| `src/core/errors.py` | Manejadores globales HTTPException / 422 / 500 |
| `src/core/lifespan.py` | Lifespan async con startup/shutdown |
| `src/core/app_factory.py` | `create_app()` — factoría principal |
| `src/middleware/request_id.py` | Middleware X-Request-ID |
| `src/routes/health.py` | Endpoints `/health/live`, `/health/ready`, `/health/startup` |

## Archivos Modificados

| Archivo | Cambio |
|---|---|
| `src/app.py` | Ahora solo es `app = create_app()` |
| `src/config.py` | Mantiene compatibilidad hacia atrás; delega en `core.config` |

## Variables de Entorno Nuevas

| Variable | Default | Obligatoria (prod) | Descripción |
|---|---|---|---|
| `APP_NAME` | `AILinkCinema` | No | Nombre del servicio |
| `APP_ENV` | `development` | Sí | Entorno: development/staging/production/test |
| `APP_VERSION` | `1.0.0` | No | Versión semver |
| `JWT_SECRET` | `""` | **Sí** (min 32 chars) | Secreto JWT |
| `JWT_ALGORITHM` | `HS256` | No | Algoritmo JWT |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:3000,...` | **Sí** (`*` prohibido) | Orígenes CORS |
| `LOG_LEVEL` | `INFO` | No | Nivel de log |
| `REQUEST_ID_HEADER` | `X-Request-ID` | No | Header de correlación |
| `HEALTHCHECK_DB_ENABLED` | `true` | No | Incluir DB en health check |
| `HEALTHCHECK_REDIS_ENABLED` | `false` | No | Incluir Redis en health check |
| `REDIS_URL` | `""` | No | URL de Redis |
| `API_PREFIX` | `/api` | No | Prefijo global de API |

## Endpoints Health

| Endpoint | Código | Función |
|---|---|---|
| `GET /health/live` | 200 | Liveness — proceso vivo |
| `GET /health/ready` | 200 | Readiness — dependencias ok/degraded |
| `GET /health/startup` | 200 | Startup — estado de inicialización |
| `GET /health` | 200 | Alias legacy (compatibilidad) |
| `GET /ready` | 200/503 | Alias legacy (compatibilidad) |

### Formato Respuesta Uniforme

```json
{
  "status": "ok",
  "service": "AILinkCinema",
  "env": "development",
  "checks": {
    "database": {"status": "ok"},
    "redis": {"status": "skipped"}
  },
  "request_id": "abc123..."
}
```

## Formato Error Global

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": {"fields": [...]},
    "request_id": "abc123..."
  }
}
```

## Validación de Config

- **Producción**: `JWT_SECRET` obligatorio (≥32 chars), `DATABASE_URL` obligatorio,
  `CORS_ALLOWED_ORIGINS` no puede contener `*`.
- Si falta algo crítico, el proceso falla en startup (no en runtime).
- Development acepta defaults seguros y emite warnings.

## CORS Enterprise

- Development puede permitir localhost y `*` (con warning).
- Production exige lista explícita de orígenes.
- `allow_credentials` controlado por `CORS_ALLOW_CREDENTIALS`.

## Request ID / Correlation ID

- Middleware en `RequestIDMiddleware`.
- Lee header `X-Request-ID` si existe.
- Genera UUID4 automático si no.
- Almacena en `request.state.request_id`.
- Incluido en toda respuesta y en todo error JSON.

## Riesgos Resueltos (P0)

| ID | Riesgo | Archivo | Estado |
|---|---|---|---|
| R01 | Config raw os.getenv sin Pydantic | `config.py` | ✅ Resuelto |
| R02 | Ruta /templates duplicada | — | ✅ No existe en este repo |
| R09 | Sin request_id/correlation_id | — | ✅ Resuelto (middleware) |
| R10 | Errores HTTP sin formato JSON unificado | — | ✅ Resuelto (global handlers) |
| R11 | CORS default * en producción | — | ✅ Resuelto (Settings valida) |
| R14 | Sin health checks separados live/ready/startup | — | ✅ Resuelto |

## Cómo Validar Localmente

```bash
# Compilar
python -m compileall src/

# Tests nuevos
cd /opt/SERVICIOS_CINE
PYTHONPATH=src python -m pytest tests/unit/test_config.py -v
PYTHONPATH=src python -m pytest tests/unit/test_health.py -v
PYTHONPATH=src python -m pytest tests/unit/test_error_handler.py -v
PYTHONPATH=src python -m pytest tests/unit/test_request_id.py -v

# Tests existentes
python -m pytest tests/unit/ -v
python -m pytest tests/integration/ -v

# Arrancar y probar
cd src
python -m uvicorn app:app --port 8010 &
curl http://127.0.0.1:8010/health/live
curl http://127.0.0.1:8010/health/ready
curl http://127.0.0.1:8010/health/startup
curl http://127.0.0.1:8010/ruta-inexistente
```

## Riesgos Pendientes para Fase 2

| ID | Riesgo |
|---|---|
| R03 | Sync SQLAlchemy engine en async FastAPI |
| R04 | Multi-tenancy no enforceada |
| R05 | JWT sin issuer/audience validation |
| R06 | Rate limit en memoria, no Redis |
| R12 | Auth token parcialmente logueado |
