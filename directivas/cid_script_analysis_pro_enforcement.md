# Directiva: CID Script Analysis Pro — Enforcement Backend

## Objetivo

Aplicar `require_module_access("script_analysis")` a todos los endpoints privados de ownership claro del módulo `script_analysis` para controlar el acceso por plan.

## Contexto

Este commit es el primero del Sprint 2 del roadmap modular (CID_MODULAR_COMMERCIAL_ROADMAP.md). La auditoría previa (CID_SCRIPT_ANALYSIS_PRO_AUDIT.md) identificó que ningún endpoint de Script Analysis tenía enforcement por plan, siendo este el gap de mayor prioridad.

## Archivos afectados

### Modificados
- `src/routes/intake_routes.py` — +3 endpoint-level enforcement
- `src/routes/project_routes.py` — +1 import, +2 endpoint-level enforcement
- `src/routes/script_version_routes.py` — +1 import, router-level enforcement
- `src/routes/ollama_storyboard_routes.py` — +1 endpoint-level enforcement

### Creados
- `tests/integration/test_script_analysis_enforcement.py` — 6 tests de enforcement
- `docs/product/CID_SCRIPT_ANALYSIS_PRO_ENFORCEMENT.md` — documentación
- `directivas/cid_script_analysis_pro_enforcement.md` — esta directiva

## Entradas

- `docs/product/CID_SCRIPT_ANALYSIS_PRO_AUDIT.md` — auditoría con gaps identificados
- `src/dependencies/module_access.py` — mecanismo de enforcement (ya existente)
- `src/config/modules.yml` — definición del módulo con `feature_flag_key: module_script_analysis`
- `src/config/plans.yml` — features por plan (todos incluyen `module_script_analysis`)

## Salidas

- Código con enforcement en 13 endpoints
- Tests que verifican 200 con plan válido y 403 con módulo bloqueado
- Documentación de la intervención

## Flujo de trabajo

1. Identificar endpoints de ownership claro de script_analysis desde la auditoría
2. Aplicar `require_module_access("script_analysis")`:
   - Router-level si todo el router es ownership claro
   - Endpoint-level si el router mezcla módulos
3. No tocar endpoints compartidos con Breakdown, Storyboard AI, Pipeline Builder, Core
4. No tocar endpoints públicos
5. Añadir tests de enforcement
6. Validar: compileall, tests unitarios, tests integración, alembic, git

## Validaciones

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"

python -m compileall src/
python -m pytest tests/unit/ -q
python -m pytest tests/integration/test_project_script_analysis_flow.py -q
python -m pytest tests/integration/test_script_analysis_enforcement.py -q
python -m pytest tests/integration/ -q
alembic heads
git status --short
git diff --stat
```

## Casos borde

- `intake_routes.py`: `POST /intake/idea` es Core, no Script Analysis. No proteger.
- `intake_routes.py`: `GET /breakdown/scenes` y `/breakdown/departments` son Breakdown, no Script Analysis. No proteger.
- `ollama_storyboard_routes.py`: `GET /ops/ollama/status` es público (sin auth). No proteger.
- `ollama_storyboard_routes.py`: `POST /storyboard/prompts/from-analysis` ya tiene `require_module_access("storyboard_ai")`. No cambiar.
- `project_routes.py`: `POST /{id}/storyboard` es Storyboard AI. No proteger en este commit.
- Admin bypass: usuarios admin/global_admin no pasan por module check. Comportamiento heredado.

## Restricciones conocidas

- Todos los planes actuales incluyen `module_script_analysis` — el enforcement no bloquea a nadie hoy
- Los endpoints de Breakdown comparten `analysis_service` con Script Analysis pero se protegen por separado
- El endpoint `/analyze-full` de Pipeline Builder hace análisis completo pero pertenece a otro módulo

## Errores aprendidos

- No importar `ModuleAccessState` desde `dependencies.module_access` — está en `services.module_catalog_service`
- Usuario admin bypassa el module check — necesitar usuario no-admin para testear 403
- El error handler custom de FastAPI envuelve detalles en `{"error": {"details": {...}}}` en lugar de `{"detail": {...}}`

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m pytest tests/integration/test_script_analysis_enforcement.py -q -x
python -m pytest tests/integration/test_project_script_analysis_flow.py -q -x
python -m compileall src/
git diff --stat
```
