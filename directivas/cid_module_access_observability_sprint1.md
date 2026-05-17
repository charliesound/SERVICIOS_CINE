# Directiva - CID Module Access Observability Sprint 1

## Objetivo

Añadir logging estructurado y seguro al helper `require_module_access()` para observabilidad de bloqueos modulares, sin cambiar contratos de API ni aplicar nuevo enforcement.

## Contexto

- CID ya tiene enforcement modular en 7 módulos vendibles.
- Cuando un usuario recibe 403 MODULE_ACCESS_BLOCKED, el cliente ve el detalle pero el servidor no registra nada.
- Este sprint añade logging estructurado para soporte, ventas y diagnóstico.

## Archivos afectados

### Modificados
- `src/dependencies/module_access.py` — añadida función `_log_module_event()` y llamadas en cada punto de salida
- `tests/unit/test_module_access_dependency.py` — +5 tests de logging con caplog

### NO tocados
- Rutas, servicios, frontend, Docker, migraciones, AGENTS.md

## Entradas

- `docs/product/CID_CORE_MODULAR_ENFORCEMENT_SPRINT1.md`
- `docs/product/CID_MIXED_MODULE_ENFORCEMENT_SPRINT1.md`
- `src/dependencies/module_access.py`
- `src/services/logging_service.py`
- `src/middleware/request_id.py`

## Salidas

- `require_module_access()` emite eventos estructurados: MODULE_ACCESS_BLOCKED, MODULE_ACCESS_GRANTED_BY_ADMIN, MODULE_ACCESS_ERROR
- 5 tests de logging con caplog
- `docs/product/CID_MODULE_ACCESS_OBSERVABILITY_SPRINT1.md`
- `directivas/cid_module_access_observability_sprint1.md`

## Eventos emitidos

| Evento | Nivel | Cuándo |
|---|---|---|
| MODULE_ACCESS_BLOCKED | WARNING | Plan sin feature o dependencia bloqueada |
| MODULE_ACCESS_GRANTED_BY_ADMIN | INFO | Admin/global_admin atraviesa bypass |
| MODULE_ACCESS_ERROR | WARNING | Module_key no existe o error de catálogo |

## Campos de seguridad

- No loggear tokens, payloads, documentos, emails, API keys, secrets.
- Usar `user_id` como identificador de usuario.
- `request_id` opcional solo si middleware presente.

## Flujo de trabajo

1. Leer código actual de `require_module_access()`.
2. Añadir inyección de `Request` para obtener path/method/request_id.
3. Añadir `_log_module_event()` con formato key=value.
4. Llamar a `_log_module_event()` en cada punto de salida (blocked, admin bypass, error).
5. Añadir tests caplog para cada evento.
6. Validar.

## Validaciones

- `python -m pytest tests/unit/ -q` — 331 passed
- `python -m pytest tests/integration/ -q` — 83 passed
- `python -m compileall src` — sin errores
- `alembic heads` — 1 head
- `git status --short` — solo archivos esperados

## Casos borde

- request_id ausente en tests → `getattr(request.state, "request_id", None)` lo maneja
- Request no disponible (test sin Request) → `request: Request = None` permite el bypass
- admin bypass → se loggea GRANTED_BY_ADMIN pero NO BLOCKED
- module_key inválido → se loggea MODULE_ACCESS_ERROR con 404

## Restricciones conocidas

- No cambiar response payload 403
- No aplicar nuevo enforcement
- No cambiar rutas
- No tocar frontend, Docker, migraciones, AGENTS.md

## Errores aprendidos

- No usar `Request | None` como type hint en dependencia FastAPI → usar `Request = None` sin Union
- request.state.request_id solo existe si request_id_middleware está instalado → acceder con getattr seguro

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"

python -m pytest tests/unit/test_module_access_dependency.py -v
python -m pytest tests/unit/ -q
python -m pytest tests/integration/ -q
python -m compileall src
alembic heads
git status --short
git diff --stat
```
