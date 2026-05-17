# Directiva: Auditoría de CID Script Analysis Pro

## Objetivo

Auditar el estado real del módulo `script_analysis` para determinar qué falta para convertirlo en el primer módulo comercial vendible del ecosistema CID.

## Contexto

CID Script Analysis Pro es el módulo de análisis de guion cinematográfico. Tiene backend completo (intake, análisis, sinopsis, versionado, diff) y frontend embebido en ProjectDetailPage. Pero carece de enforcement por plan, pantalla propia, export directo y demo guiada.

El roadmap comercial (CID_MODULAR_COMMERCIAL_ROADMAP.md) lo identifica como el mejor candidato para Sprint 2.

## Archivos afectados

### Backend
- `src/routes/intake_routes.py` — 5 endpoints (intake/idea, intake/script, analysis/run, analysis/summary, breakdown/scenes, breakdown/departments)
- `src/routes/project_routes.py` — PUT script, POST analyze, POST storyboard
- `src/routes/script_version_routes.py` — 7 endpoints (CRUD versiones, compare, change-reports, module-status)
- `src/routes/ollama_storyboard_routes.py` — POST analyze/local-ollama
- `src/services/script_intake_service.py` — ScriptIntakeService, AnalysisService
- `src/services/script_version_service.py` — ScriptVersionService, ScriptChangeAnalysisService
- `src/services/script_synopsis_service.py` — ScriptSynopsisService
- `src/services/local_script_analysis_service.py` — análisis vía Ollama/Qwen
- `src/dependencies/module_access.py` — require_module_access (ya existe, usado por otros módulos)
- `src/config/modules.yml` — definición del módulo
- `src/config/plans.yml` — feature flags por plan

### Frontend
- `src_frontend/src/pages/ProjectDetailPage.tsx` — workspace actual (2020 líneas)
- `src_frontend/src/pages/ProjectsPage.tsx` — badge de guion
- `src_frontend/src/pages/ModulesCatalogPage.tsx` — CTA del módulo

### Tests
- `tests/integration/test_project_script_analysis_flow.py`

## Entradas

- Código fuente del backend y frontend
- Configuración de módulos y planes
- Test de integración existente
- Roadmap comercial

## Salidas

- `docs/product/CID_SCRIPT_ANALYSIS_PRO_AUDIT.md` — documento de auditoría
- `directivas/cid_script_analysis_pro_audit.md` — esta directiva

## Flujo de trabajo

1. Leer todos los archivos backend del módulo (routes, services, models, schemas)
2. Leer frontend donde se usa Script Analysis
3. Leer configuración de módulos y planes
4. Leer tests existentes
5. Identificar endpoints sin enforcement
6. Identificar gaps de UX y export
7. Escribir documento de auditoría
8. Escribir directiva
9. Validar con compileall + tests + npm build + git status

## Validaciones

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m py_compile src/routes/intake_routes.py
python -m py_compile src/routes/project_routes.py
python -m py_compile src/routes/script_version_routes.py
python -m pytest tests/integration/test_project_script_analysis_flow.py -q -x
cd src_frontend && npm run build
./scripts/smoke_cid_dev.sh
./scripts/validate_cid_dev.sh
```

## Casos borde

- `intake_routes.py` comparte endpoints de breakdown (módulo separado) — no añadir enforcement de script_analysis a breakdown sin coordinación
- `ollama_storyboard_routes.py` tiene `/analyze/local-ollama` sin enforcement pero `/storyboard/prompts/from-analysis` ya enforce como storyboard_ai — consistencia requiere ambos con script_analysis o ambos con storyboard_ai
- `cid_script_to_prompt_routes.py` tiene `/analyze-full` con enforce de `pipeline_builder` — es un análisis completo que debería requerir `script_analysis` también

## Restricciones conocidas

- NO modificar código funcional durante la auditoría
- NO tocar frontend a menos que sea estrictamente necesario
- NO commitear archivos sensibles
- NO ejecutar renders reales ni llamar a ComfyUI /prompt

## Errores aprendidos

- El enforcement no estaba en el sprint inicial de modularización (Sprint 1 core) porque se priorizó Core primero
- La auditoría anterior (CID_MODULAR_COMMERCIAL_ROADMAP.md) identificó Script Analysis como candidato pero no detalló los gaps específicos — esta directiva los documenta

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m pytest tests/integration/test_project_script_analysis_flow.py -q -x
cd src_frontend && npm run build 2>&1 | tail -5
git status --short
```
