# Directiva - CID Core Modular Enforcement Sprint 1

## Objetivo

Aplicar enforcement modular quirúrgico en rutas claramente asociadas a módulos vendibles, sin bloquear superficies públicas, compartidas o todavía ambiguas.

## Contexto

- El catálogo modular y el helper `require_module_access()` ya existen.
- El frontend ya consume disponibilidad por módulo.
- Este sprint activa el primer bloqueo real por plan en backend.

## Archivos afectados

- `src/routes/producer_pitch_routes.py`
- `src/routes/budget_routes.py`
- `src/routes/funding_routes.py`
- `src/routes/project_funding_routes.py`
- `src/routes/matcher_routes.py`
- `src/routes/storyboard_routes.py`
- `src/routes/comfyui_storyboard_routes.py`
- `src/routes/ollama_storyboard_routes.py`
- `src/routes/distribution_pack_routes.py`
- `src/routes/sales_targets_routes.py`
- `src/routes/crm_routes.py`
- tests y documentación del sprint

## Entradas

- `src/config/modules.yml`
- `src/config/plans.yml`
- `src/dependencies/module_access.py`
- roadmap y documentación modular de Sprint 1

## Salidas

- Enforced routers privados por módulo
- Tests de bloqueo/permiso mínimo
- Documentación de rutas protegidas y no protegidas

## Flujo de trabajo

1. Identificar routers completamente privados y asociados a un módulo.
2. Añadir `Depends(require_module_access("module_key"))` al router o endpoint.
3. Mantener auth/tenant/permisos previos.
4. Dejar fuera rutas públicas o superficies compartidas.

## Validaciones

- `source .venv/bin/activate && python -m pytest tests/unit/ -q`
- `source .venv/bin/activate && python -m pytest tests/integration/ -q`
- `python -m compileall src`
- `alembic heads`
- `git status --short`
- `git diff --stat`

## Casos borde

- plan sin feature -> `403 MODULE_ACCESS_BLOCKED`
- dependencia comercial bloqueada -> `403 dependency_locked:*`
- módulo inexistente en helper -> `404`
- catálogo modular debe seguir accesible
- `admin` / `global_admin` -> bypass deliberado en este sprint para no bloquear operaciones internas

## Restricciones conocidas

- no tocar frontend
- no tocar Docker
- no crear migraciones
- no bloquear health/auth/plans/modules/catálogo público de funding
- no romper tests históricos

## Errores aprendidos

- no proteger `delivery_routes.py` mientras siga sirviendo deliverables cross-módulo
- no proteger `presentation_routes.py` hasta cerrar ownership de pitch vs presentación técnica
- no hacer enforcement global antes de separar superficies mixtas

## Comandos seguros

- `source .venv/bin/activate && python -m pytest tests/unit/ -q`
- `source .venv/bin/activate && python -m pytest tests/integration/ -q`
- `python -m compileall src`
- `alembic heads`
- `git status --short`
- `git diff --stat`
