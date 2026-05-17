# Directiva - CID Core Modular Backend Sprint 1

## Objetivo

Introducir una base backend central para catalogar modulos vendibles de CID sin romper rutas existentes ni aplicar enforcement masivo todavia.

## Contexto

- CID ya tiene varios modulos tecnicamente avanzados.
- El roadmap comercial exige separar Core, modulos, planes y futura narrativa de suite vendible.
- En este sprint se necesita solo lectura, catalogacion y preparacion de enforcement.

## Archivos afectados

- `src/config/modules.yml`
- `src/config/plans.yml`
- `src/services/module_catalog_service.py`
- `src/schemas/module_catalog_schema.py`
- `src/routes/module_catalog_routes.py`
- `src/dependencies/module_access.py`
- `src/core/app_factory.py`
- `tests/unit/test_module_catalog_service.py`
- `tests/unit/test_module_catalog_routes.py`
- `docs/product/CID_CORE_MODULAR_BACKEND_SPRINT1.md`

## Entradas

- `docs/product/CID_MODULAR_COMMERCIAL_ROADMAP.md`
- `src/config/plans.yml`
- `src/core/app_factory.py`
- `src/routes/project_routes.py`
- servicios y dependencias existentes de planes, tenant y permisos

## Salidas

- Catalogo central de modulos
- Endpoints backend de catalogo modular
- Helper de acceso modular reutilizable
- Tests unitarios minimos
- Documentacion de sprint

## Flujo de trabajo

1. Cargar catalogo YAML.
2. Validar keys unicas y dependencias existentes.
3. Resolver acceso modular a partir del plan efectivo y las features `module_*`.
4. Exponer endpoints publicos de catalogo y endpoint contextual `/me`.
5. Mantener enforcement existente sin alteraciones.

## Validaciones

- `python -m pytest tests/unit/ -q`
- `python -m pytest tests/integration/ -q`
- `python -m compileall src`
- `alembic heads`
- `git status --short`
- `git diff --stat`

## Casos borde

- plan inexistente
- modulo inexistente
- feature faltante en `plans.yml`
- dependencia de modulo bloqueada por plan
- usuario sin plan resoluble -> fallback `free`

## Restricciones conocidas

- no tocar frontend
- no tocar Docker
- no crear migraciones
- no cambiar comportamiento de endpoints existentes salvo anadir lectura de catalogo
- no tocar `AGENTS.md`

## Errores aprendidos

- no mezclar enforcement fuerte con catalogacion en el mismo commit
- no asumir que `all_lower_features` ya expande modulos automaticamente
- no introducir dependencias de modulo que obliguen cambios de base de datos en Sprint 1

## Comandos seguros

- `python -m pytest tests/unit/ -q`
- `python -m pytest tests/integration/ -q`
- `python -m compileall src`
- `alembic heads`
- `git status --short`
- `git diff --stat`
