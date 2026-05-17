# Directiva: CID Script Analysis Pro — Export Directo

## Objetivo

Añadir endpoint de exportación del análisis completo de guion en formato JSON y Markdown para permitir al usuario descargar el análisis como artefacto portable y compartible.

## Contexto

Commit 2 del Sprint 2 del roadmap modular. La auditoría (CID_SCRIPT_ANALYSIS_PRO_AUDIT.md) identificó que el módulo carecía de export directo (gap #3). El commit 1 (enforcement) ya está completado. Este commit no toca frontend, Docker, migraciones, AGENTS.md ni contratos de API existentes.

## Archivos afectados

### Creados
- `src/services/script_analysis_export_service.py` — `ScriptAnalysisExportService` con `build_export_payload()` y `to_markdown()`
- `tests/integration/test_script_analysis_export.py` — 7 tests de export
- `docs/product/CID_SCRIPT_ANALYSIS_PRO_EXPORT.md` — documentación
- `directivas/cid_script_analysis_pro_export.md` — esta directiva

### Modificados
- `src/routes/intake_routes.py` — +1 import de export service, + endpoint GET `/analysis/export` con `require_module_access("script_analysis")`

## Entradas

- `ProductionBreakdown.breakdown_json` — JSON blob con scenes, characters, locations, departments, sequences, metadata
- `Project.script_text` — texto del guion (para regenerar sinopsis)
- `ScriptSynopsisService.analyze_script()` — genera logline, sinopsis, premise, theme, genre, tone, dramatic_structure (síncrono)
- `AnalysisService.get_summary()` / `get_scenes()` — patrones reutilizables de lectura de breakdown

## Salidas

- Endpoint `GET /api/projects/{project_id}/analysis/export?format=json|md`
- Export service que combina datos de breakdown + sinopsis
- Tests que verifican: JSON 200 con estructura, MD 200, formato inválido 422, proyecto inexistente 404, export sin análisis con warnings

## Flujo de trabajo

1. Crear `ScriptAnalysisExportService` con:
   - `_parse_breakdown()` — parseo seguro de `breakdown_json`
   - `build_export_payload()` — payload unificado desde DB + sinopsis
   - `to_markdown()` — Markdown legible con secciones condicionales
2. Añadir endpoint en `intake_routes.py`:
   - Validar formato: solo `json` o `md` (si no, 422)
   - Buscar proyecto (si no, 404)
   - Llamar a `build_export_payload()`
   - Si `None` (proyecto no encontrado pero ya validado), devolver 404
   - Responder con `Content-Disposition: attachment` + filename
   - Proteger con `require_module_access("script_analysis")`
3. Añadir tests de integración
4. Validar: compileall, tests unitarios, tests integración, alembic, git

## Validaciones

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"

python -m compileall src/
python -m pytest tests/unit/ -q
python -m pytest tests/integration/test_project_script_analysis_flow.py -q
python -m pytest tests/integration/test_script_analysis_enforcement.py -q
python -m pytest tests/integration/test_script_analysis_export.py -q
python -m pytest tests/integration/ -q
alembic heads
git status --short
git diff --stat
```

## Casos borde

- `format` no es `json` ni `md` → 422 controlado (FastAPI validation)
- Proyecto no existe → 404
- Proyecto existe pero no tiene `ProductionBreakdown` → 200 con `has_analysis: false`, warnings
- Proyecto existe pero no tiene `script_text` → 200 sin campos de sinopsis, warning
- `breakdown_json` es `NULL` o inválido → `_parse_breakdown()` devuelve `{}`
- `ScriptSynopsisService.analyze_script()` devuelve `None` → el export service lo maneja como sinopsis ausente
- Characters/locations vacíos → se omiten del payload (no se incluyen como arrays vacíos en MD)

## Restricciones conocidas

- NO tocar frontend, Docker, migraciones, AGENTS.md, contratos de API existentes
- NO añadir PDF todavía — requiere infraestructura adicional
- NO crear tablas nuevas ni modificar modelos existentes
- `ScriptSynopsisService.analyze_script()` es síncrono — llamado desde endpoint async sin `run_in_executor`

## Errores aprendidos

- El contenido de `ProductionBreakdown.breakdown_json` no tiene schema fijo — siempre parsear con try/except y usar helpers `_dict_or_empty`, `_list_or_empty`
- `ScriptSynopsisService.analyze_script()` requiere `script_text` no vacío — el export service verifica `project.script_text` antes de llamarlo
- Las respuestas del export service son siempre 200 con análisis vacío — no 404 ni 204

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m pytest tests/integration/test_script_analysis_export.py -q -x
python -m pytest tests/integration/test_project_script_analysis_flow.py -q -x
python -m pytest tests/integration/test_script_analysis_enforcement.py -q -x
python -m compileall src/
git diff --stat
```
