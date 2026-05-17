# Directiva - CID Mixed Module Ownership Audit

## Objetivo

Auditar ownership de las tres superficies de ruta mixta que quedaron sin enforcement en Sprint 3, documentar la matriz endpoint → módulo y producir el plan para Commit 5.

## Contexto

- Sprint 3 protegió 11 route files de 5 módulos vendibles.
- Tres routers quedaron fuera por ser superficies compartidas:
  - `src/routes/presentation_routes.py`
  - `src/routes/delivery_routes.py`
  - `src/routes/cid_script_to_prompt_routes.py`
- Este sprint (4) audita ownership SIN tocar código funcional.

## Archivos afectados

### Auditados (solo lectura)
- `src/routes/presentation_routes.py`
- `src/routes/delivery_routes.py`
- `src/routes/cid_script_to_prompt_routes.py`

### Creados en este sprint
- `docs/product/CID_MIXED_MODULE_OWNERSHIP_AUDIT.md`
- `directivas/cid_mixed_module_ownership_audit.md`

### Se tocarán en Commit 5
- `src/routes/presentation_routes.py` — añadir `require_module_access("pitch_deck")`
- `src/routes/cid_script_to_prompt_routes.py` — añadir `require_module_access("pipeline_builder")` en `/analyze-full`
- `src/config/modules.yml` — añadir `/api/cid/script-to-prompt` a route_prefixes de pipeline_builder

## Entradas

- `src/config/modules.yml` — definiciones de módulo y route_prefixes
- `src/dependencies/module_access.py` — helper de enforcement
- `docs/product/CID_CORE_MODULAR_ENFORCEMENT_SPRINT1.md` — doc de Sprint 3
- `directivas/cid_core_modular_enforcement_sprint1.md`

## Salidas

- `docs/product/CID_MIXED_MODULE_OWNERSHIP_AUDIT.md` — auditoría completa con matriz endpoint→módulo
- `directivas/cid_mixed_module_ownership_audit.md` — esta directiva

## Flujo de trabajo

1. Leer los 3 route files objetivo.
2. Leer servicios que importan para entender dependencias cruzadas.
3. Buscar callers cross-module (grep `create_project_file_deliverable`).
4. Mapear cada endpoint a módulo propietario.
5. Documentar GO/NO-GO por superficie.
6. Redactar plan para Commit 5.
7. Validar con compileall + pytest.

## Validaciones

- `python -m compileall src`
- `python -m pytest tests/unit/ -q` (si no es excesivo)
- `python -m pytest tests/integration/ -q` (si no es excesivo)
- `git status --short`
- `git diff --stat`

## Casos borde

- delivery_routes.py NO se enforce porque bloquea acceso a deliverables creados por otros módulos
- cid_script_to_prompt endpoints stateless sin auth NO requieren enforcement (son transformaciones puras)
- presentation_routes comparte delivery_service pero solo como output → no es conflicto de ownership
- Admin/global_admin bypass aplica en Commit 5 igual que en Sprint 3

## Restricciones conocidas

- No tocar código funcional en este sprint
- No modificar rutas, servicios ni frontend
- No tocar Docker
- No tocar AGENTS.md
- No aplicar `require_module_access()` en este commit
- No romper tests legacy

## Errores aprendidos

- No asumir que un prefijo en modules.yml implica ownership exclusivo — delivery_routes tiene el prefijo `/api/delivery` declarado pero sirve a múltiples módulos
- Los endpoints sin auth en cid_script_to_prompt no deben recibir enforcement forzado — son funciones de transformación que no acceden a datos de organización
- presentation_routes NO es un router separado de pitch_deck — es su capa de presentación visual, ya correctamente declarada en modules.yml

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m compileall src
python -m pytest tests/unit/test_module_access_dependency.py -q -x
python -m pytest tests/unit/test_module_catalog_service.py -q -x
python -m pytest tests/unit/test_module_catalog_routes.py -q -x
git status --short
git diff --stat
```
