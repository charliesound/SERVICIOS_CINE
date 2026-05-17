# Directiva - CID Mixed Module Enforcement Sprint 1

## Objetivo

Aplicar enforcement modular a las superficies mixtas identificadas en la auditoría de ownership, cerrando el enforcement inicial de los módulos vendibles del roadmap comercial.

## Contexto

- Sprint 3 aplicó `require_module_access()` a 11 route files de 5 módulos.
- Sprint 4 auditó ownership de 3 routers mixtos y produjo plan para Commit 5.
- Sprint 5 (este) implementa el enforcement aprobado.

## Archivos afectados

### Modificados
- `src/routes/presentation_routes.py` — añadido `require_module_access("pitch_deck")` a nivel de router
- `src/routes/cid_script_to_prompt_routes.py` — añadido `require_module_access("pipeline_builder")` al endpoint `/analyze-full`
- `src/config/modules.yml` — añadido `/api/cid/script-to-prompt` a route_prefixes de pipeline_builder
- `tests/unit/test_module_access_dependency.py` — +7 tests nuevos

### NO tocados (por diseño)
- `src/routes/delivery_routes.py` — NO-GO confirmado
- frontend, Docker, migraciones, AGENTS.md

## Entradas

- `docs/product/CID_MIXED_MODULE_OWNERSHIP_AUDIT.md`
- `directivas/cid_mixed_module_ownership_audit.md`
- `docs/product/CID_CORE_MODULAR_ENFORCEMENT_SPRINT1.md`
- `src/dependencies/module_access.py`
- `src/config/modules.yml`

## Salidas

- Router `presentation_routes.py` protegido como pitch_deck
- Endpoint `/analyze-full` protegido como pipeline_builder
- 7 tests de enforcement (10 total en el archivo)
- `docs/product/CID_MIXED_MODULE_ENFORCEMENT_SPRINT1.md`
- `directivas/cid_mixed_module_enforcement_sprint1.md`

## Flujo de trabajo

1. Leer auditoría y plan de Commit 5.
2. Añadir `require_module_access("pitch_deck")` router-level a presentation_routes.py.
3. Añadir `require_module_access("pipeline_builder")` endpoint-level a `/analyze-full`.
4. Añadir `/api/cid/script-to-prompt` a route_prefixes de pipeline_builder.
5. Extender tests con casos bloque/permitido/bypass para pitch_deck y pipeline_builder.
6. Verificar que stateless endpoints de cid_script_to_prompt siguen accesibles.
7. Validar.

## Validaciones

- `python -m pytest tests/unit/ -q` — deben pasar todos
- `python -m pytest tests/integration/ -q` — sin regresiones
- `python -m compileall src` — sin errores
- `alembic heads` — 1 head, sin migraciones nuevas
- `git status --short` — solo archivos esperados
- `git diff --stat` — diff mínimo

## Casos borde

- `delivery_routes.py` NO se enforce — mismo motivo que Sprint 3 (cross-module)
- presentation_routes usa `delivery_service` — enforcement no bloquea delivery porque la llamada es interna al endpoint protegido
- 13 endpoints stateless de cid_script_to_prompt no tienen auth ni DB — enforcement innecesario

## Restricciones conocidas

- No tocar frontend, Docker, migraciones ni AGENTS.md
- No cambiar contratos de API ni payloads
- No eliminar validaciones existentes (tenant, permisos, etc.)
- No romper tests legacy — admin/global_admin bypass se mantiene

## Errores aprendidos

- No hacer enforcement hasta tener auditoría de ownership clara
- No proteger routers cross-module sin modelo granular
- Los endpoints stateless sin auth no necesitan enforcement — son transformaciones de datos

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
