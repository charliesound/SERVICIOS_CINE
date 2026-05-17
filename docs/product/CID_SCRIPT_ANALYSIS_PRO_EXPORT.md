# CID Script Analysis Pro — Export Directo

## Resumen ejecutivo

Commit 2 del Sprint 2. Se añadió el endpoint `GET /api/projects/{project_id}/analysis/export?format=json|md` que serializa el análisis completo de guion (scenes, breakdowns, departments, synopsis, logline, characters, locations) en formato JSON o Markdown descargable.

**Estado anterior**: No existía exportación del análisis — el usuario solo podía verlo dentro de la app.
**Estado actual**: Endpoint de export con formato JSON (application/json) y Markdown (text/markdown), ambos con `Content-Disposition: attachment`.

---

## Endpoint

| Método | Ruta | Formato | Auth |
|--------|------|---------|------|
| GET | `/api/projects/{project_id}/analysis/export` | `?format=json` o `?format=md` | `require_module_access("script_analysis")` |

### Responses

| Código | Condición |
|--------|-----------|
| 200 | Export exitoso (JSON o MD según formato) |
| 422 | `format` no es `json` ni `md` |
| 404 | Proyecto no encontrado |

### Formato del filename

- JSON: `CID_script_analysis_{project_id}.json`
- Markdown: `CID_script_analysis_{project_id}.md`

### Payload JSON (resumen de campos)

```json
{
  "export_version": "1.0",
  "source": "cid_script_analysis_pro",
  "project_id": "...",
  "project_name": "...",
  "generated_at": "2026-05-17T...",
  "has_analysis": true,
  "has_script": true,
  "warnings": [],
  "logline": "...",
  "synopsis_short": "...",
  "synopsis_extended": "...",
  "premise": "...",
  "theme": "...",
  "genre": "...",
  "tone": "...",
  "dramatic_structure": "...",
  "characters": ["..."],
  "locations": ["..."],
  "scenes": [...],
  "sequences": [...],
  "breakdowns": [...],
  "department_breakdown": {...},
  "analysis_engine": "...",
  "analysis_summary": {...},
  "production_notes": [...],
  "storyboard_suggestions": [...]
}
```

Comportamiento con análisis vacío:
- Si no hay `ProductionBreakdown` con `status == "completed"`, `has_analysis: false` con `warnings: ["no_analysis_found"]`
- Si no hay `project.script_text`, `has_script: false` con `warnings: ["no_script_text"]`
- Sinopsis, logline, género, tono y estructura se regeneran desde `ScriptSynopsisService.analyze_script()` si hay `script_text`
- Si no hay script_text, el payload omite los campos de sinopsis

---

## Arquitectura

### Servicio de export

`src/services/script_analysis_export_service.py` — `ScriptAnalysisExportService`

- `build_export_payload(db, project_id)` → `dict | None`
  - Lee `Project` y `ProductionBreakdown` de DB
  - Parsea `breakdown_json` para scenes, breakdowns, departments, metadata
  - Llama a `ScriptSynopsisService.analyze_script()` para logline/sinopsis/género/tono (regeneración síncrona desde `project.script_text`)
  - Normaliza characters/locations desde sinopsis o desde scenes como fallback
  - Recolecta warnings (no_analysis_found, no_script_text, warnings de sinopsis)
- `to_markdown(payload)` → `str`
  - Genera Markdown legible con secciones condicionales (solo incluye lo que existe en el payload)

### Endpoint

`src/routes/intake_routes.py` — `GET /{project_id}/analysis/export`

- Dependencia: `require_module_access("script_analysis")`
- Valida formato: solo `json` o `md` (422 si no)
- Busca proyecto: 404 si no existe
- `Content-Disposition: attachment` con filename según formato

---

## Fuentes de datos

| Dato | Fuente | Persistencia |
|------|--------|-------------|
| Scenes, breakdowns, departments, sequences, metadata | `ProductionBreakdown.breakdown_json` (columna `Text`) | DB |
| Logline, synopsis, premise, theme, genre, tone, dramatic_structure | `ScriptSynopsisService.analyze_script()` | Regeneración síncrona desde `project.script_text` |
| Characters, locations | Sinopsis + fallback desde scenes | Híbrido |
| Project name, script_text | `Project` | DB |

No se crearon tablas nuevas ni se modificaron modelos existentes.

---

## Archivos creados

| Archivo | Propósito |
|---------|-----------|
| `src/services/script_analysis_export_service.py` | `ScriptAnalysisExportService` con `build_export_payload()` y `to_markdown()` |
| `tests/integration/test_script_analysis_export.py` | 7 tests de export |
| `docs/product/CID_SCRIPT_ANALYSIS_PRO_EXPORT.md` | Esta documentación |
| `directivas/cid_script_analysis_pro_export.md` | Directiva técnica |

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `src/routes/intake_routes.py` | +1 import de export service, + endpoint GET `/analysis/export` con `require_module_access("script_analysis")` |

---

## Tests

Archivo: `tests/integration/test_script_analysis_export.py`

| Test | Escenario | Resultado |
|------|-----------|-----------|
| `test_export_json_returns_200_with_structure` | JSON con proyecto con análisis | 200, estructura esperada |
| `test_export_json_includes_synopsis_fields` | JSON con sinopsis fields | logline, synopsis, genre, tone presentes |
| `test_export_json_includes_analysis_data` | JSON con breakdown data | scenes, characters, breakdowns válidos |
| `test_export_md_returns_200_with_content` | Markdown con proyecto con análisis | 200, secciones esperadas |
| `test_export_invalid_format_returns_422` | Formato inválido | 422 |
| `test_export_nonexistent_project_returns_404` | Proyecto inexistente | 404 |
| `test_export_json_no_analysis_still_returns_synopsis` | Sin análisis pero con script | 200 con warnings |

**Resultado**: 7/7 passed.

Tests legados no afectados:
- `tests/integration/test_project_script_analysis_flow.py` → 1 passed
- `tests/integration/test_script_analysis_enforcement.py` → 6 passed
- `tests/unit/` → 331 passed
- `tests/integration/` completo → 89 passed (incluyendo los nuevos)

---

## Validaciones realizadas

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"

python -m compileall src/                                          # sin errores
python -m pytest tests/unit/ -q                                     # 331 passed
python -m pytest tests/integration/ -q                              # 89 passed
python -m pytest tests/integration/test_project_script_analysis_flow.py -q  # 1 passed
python -m pytest tests/integration/test_script_analysis_enforcement.py -q   # 6 passed
python -m pytest tests/integration/test_script_analysis_export.py -q        # 7 passed
alembic heads                                                        # ec2e3eaf1271 (sin cambios)
git status --short                                                   # solo archivos esperados
```

---

## Riesgos conocidos

1. **`ScriptSynopsisService.analyze_script()` es síncrono**: Se llama desde un endpoint async; aunque funciona sin problemas hoy, podría bloquear el event loop si el análisis se vuelve pesado. Migrar a `run_in_executor` si hay quejas de performance.
2. **Characters/locations tienen dos fuentes**: La sinopsis provee datos estructurados; si no hay sinopsis (no hay script_text), se extraen de scenes como fallback. Esto puede dar resultados incompletos.
3. **El Markdown generado es texto plano**: No hay formato enriquecido, tablas complejas, ni gráficos. Suficiente para compartir, no para presentación comercial.
4. **Dependencia de `ScriptSynopsisService`**: Si el servicio de sinopsis cambia su interfaz, el export service debe actualizarse. Hay tests que protegen contra esto.

---

## Siguiente commit recomendado

**Commit 3 — Pantalla propia de Script Analysis Pro**

Crear `ScriptAnalysisProPage.tsx` con workspace dedicado, resumen del análisis, sinopsis, personajes, localizaciones, estructura dramática y botón de export. Esto da al módulo una identidad visual propia y permite demo guiada.
