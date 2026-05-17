# Directiva: CID Breakdown Enforcement (Sprint 3)

## Objetivo

Aplicar enforcement backend del modulo `breakdown` de forma quirurgica usando `require_module_access("breakdown")` solo en endpoints de ownership claro.

## Contexto

La auditoria de Breakdown confirmo que los endpoints de lectura de escenas y departamentos existian sin gate comercial por plan.

Este sprint corrige ese gap sin tocar contratos de API, frontend, Docker, modelos ni migraciones.

## Archivos afectados

- `src/routes/intake_routes.py`
- `tests/integration/test_script_analysis_enforcement.py`
- `docs/product/CID_BREAKDOWN_ENFORCEMENT.md`
- `directivas/cid_breakdown_enforcement.md`

## Entradas

- `docs/product/CID_BREAKDOWN_AUDIT.md`
- `directivas/cid_breakdown_audit.md`
- `src/dependencies/module_access.py`
- `src/config/modules.yml`
- `src/config/plans.yml`

## Salidas

- Endpoints Breakdown protegidos con `require_module_access("breakdown")`.
- Tests de integracion ajustados para 403/allow/admin-bypass.
- Documentacion tecnica y de release de enforcement.

## Flujo de trabajo

1. Confirmar ownership de endpoints Breakdown en auditoria.
2. Aplicar dependencia a nivel endpoint en router mixto.
3. Verificar no regresion de Script Analysis y rutas compartidas.
4. Ajustar tests minimos de enforcement.
5. Ejecutar validaciones backend obligatorias.
6. Documentar decisiones y riesgos.

## Endpoints protegidos

- `GET /api/projects/{project_id}/breakdown/scenes`
- `GET /api/projects/{project_id}/breakdown/departments`

## Endpoints no protegidos deliberadamente

- Script Analysis Pro (`module_script_analysis`)
- Budget Lite (`module_budget_lite`)
- Project Core y endpoints compartidos sin ownership breakdown claro

## Validaciones

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m pytest tests/unit/ -q
python -m pytest tests/integration/test_script_analysis_enforcement.py -q
python -m pytest tests/integration/test_project_script_analysis_flow.py -q
python -m pytest tests/integration/test_script_analysis_export.py -q
python -m pytest tests/integration/ -q
python -m compileall src
alembic heads
git status --short
git diff --stat
```

## Casos borde

- Router mixto: evitar router-level dependency para no bloquear endpoints no-breakdown.
- Usuarios admin/global admin deben mantener bypass por disenio.
- Planes sin `module_breakdown` deben recibir `MODULE_ACCESS_BLOCKED` 403.

## Restricciones conocidas

- No cambiar payloads/responses ni status codes existentes fuera de gate de acceso.
- No tocar frontend, Docker, migraciones, AGENTS.md.
- No aplicar enforcement a endpoints compartidos con ownership ambiguo.

## Errores aprendidos

- Tratar rutas por prefijo sin validar ownership real genera sobre-enforcement.
- En routers mixtos, endpoint-level dependency reduce riesgo de regresion.

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m pytest tests/integration/test_script_analysis_enforcement.py -q
python -m pytest tests/integration/test_project_script_analysis_flow.py -q
python -m pytest tests/integration/test_script_analysis_export.py -q
python -m compileall src
git status --short
```
