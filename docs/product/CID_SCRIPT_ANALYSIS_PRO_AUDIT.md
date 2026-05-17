# CID Script Analysis Pro — Auditoría de Estado Comercial

## Resumen ejecutivo

CID Script Analysis Pro es el **módulo con mayor madurez funcional** del ecosistema CID después de Core.
Sus componentes backend (intake, análisis, sinopsis, versionado, diff) están completos y probados.
Sin embargo, **no es vendible como SKU independiente** hoy porque carece de enforcement por plan, pantalla propia, export directo y demo guiada.

**Estado actual**: PARCIAL AVANZADO (técnico) / PARCIAL AVANZADO (comercial)
**Esfuerzo estimado para cerrar**: 3-5 commits quirúrgicos

---

## Endpoints auditados

| Endpoint | Método | Módulo | Auth | Persiste | Enforce plan | Gap |
|---|---|---|---|---|---|---|
| `/api/projects/{id}/script` | PUT | core | sí | sí | NO | Sin `require_module_access("script_analysis")` |
| `/api/projects/{id}/intake/script` | POST | script_analysis | sí | sí | NO | Sin `require_module_access` |
| `/api/projects/{id}/analysis/run` | POST | script_analysis | sí | sí | NO | Sin `require_module_access` |
| `/api/projects/{id}/analysis/summary` | GET | script_analysis | sí | lee | NO | Sin `require_module_access` |
| `/api/projects/{id}/breakdown/scenes` | GET | breakdown | sí | lee | NO | Sin `require_module_access` |
| `/api/projects/{id}/breakdown/departments` | GET | breakdown | sí | lee | NO | Sin `require_module_access` |
| `/api/projects/{id}/analyze` (project_routes) | POST | script_analysis | sí | sí | analyses limit | Sin `require_module_access("script_analysis")` |
| `/api/projects/{id}/script/versions` | GET | script_analysis | sí | lee | NO | Sin `require_module_access` |
| `/api/projects/{id}/script/versions` | POST | script_analysis | sí | sí | NO | Sin `require_module_access` |
| `/api/projects/{id}/script/versions/{vid}` | GET | script_analysis | sí | lee | NO | Sin `require_module_access` |
| `/api/projects/{id}/script/versions/{vid}/activate` | POST | script_analysis | sí | sí | NO | Sin `require_module_access` |
| `/api/projects/{id}/script/versions/compare` | POST | script_analysis | sí | sí | NO | Sin `require_module_access` |
| `/api/projects/{id}/script/change-reports` | GET | script_analysis | sí | lee | NO | Sin `require_module_access` |
| `/api/projects/{id}/module-status` | GET | script_analysis | sí | lee | NO | Sin `require_module_access` |
| `/api/projects/{id}/analyze/local-ollama` | POST | script_analysis | sí | sí | NO | Sin `require_module_access` |
| `/api/cid/script-to-prompt/analyze-full` | POST | pipeline_builder | sí | no | SÍ (pipeline_builder) | Enforce correcto pero módulo incorrecto |
| `/api/projects/{id}/storyboard` | POST | storyboard_ai | sí | sí | storyboards limit | Sin `require_module_access("storyboard_ai")` |
| `/api/intake/idea` | POST | core | sí | sí | NO | Sin enforcement |

### Hallazgo crítico

**NINGÚN endpoint del módulo `script_analysis` tiene `require_module_access("script_analysis")`**.
Esto significa que cualquier usuario con token válido puede usar el análisis de guion completo sin importar su plan.

---

## Pantallas auditadas (Frontend)

| Pantalla | Archivo | Módulo | Responsive | Gap |
|---|---|---|---|---|
| Detalle de proyecto (tabs) | `ProjectDetailPage.tsx` (~2020 líneas) | core | sí | **Script Analysis no tiene pantalla propia**. Vive dentro de ProjectDetail como tabs (Script, Analysis, Storyboard, History). |
| Listado de proyectos | `ProjectsPage.tsx` | core | sí | Badge "✓ Guion / Sin guion" visible. Correcto. |
| Catálogo de módulos | `ModulesCatalogPage.tsx` | core | sí | CTA de `script_analysis` apunta a `/projects` — "Selecciona un proyecto para abrir el flujo real". Correcto pero no hay landing propio del módulo. |

### Hallazgo frontend

Script Analysis **no existe como página/ruta propia**. Todo su UX está embebido en `ProjectDetailPage.tsx`. Esto es funcionalmente correcto (el análisis pertenece a un proyecto) pero comercialmente débil: no hay workspace dedicado, no hay onboarding propio, no hay demo guiada del módulo.

---

## Servicios auditados

| Servicio | Archivo | Líneas | Propósito | Completitud |
|---|---|---|---|---|
| `ScriptIntakeService` + `AnalysisService` | `script_intake_service.py` | 550 | Parseo de guion + análisis con LLM | COMPLETO. Produce escenas, personajes, localizaciones, departamentos, presupuesto. |
| `ScriptVersionService` + `ScriptChangeAnalysisService` | `script_version_service.py` | 496 | Versionado + diff entre versiones | COMPLETO. Impacto en producción, presupuesto, storyboard, funding, dossier, distribución. |
| `ScriptSynopsisService` | `script_synopsis_service.py` | 313 | Sinopsis, logline, género, tono, estructura | COMPLETO. Base del producto vendible. |
| `LocalScriptAnalysisService` | `local_script_analysis_service.py` | 172 | Análisis vía Ollama/Qwen | COMPLETO. Prompt maestro en español. |
| `OllamaClientService` | `ollama_client_service.py` | 228 | Cliente Ollama con resolución por tarea | COMPLETO. |
| `module_catalog_service` | `module_catalog_service.py` | — | Catálogo de módulos + acceso por plan | COMPLETO. Ya usado por otros módulos. |

---

## Modelos auditados

| Modelo | Archivo | Propósito |
|---|---|---|
| `ScriptVersion` | `script_versioning.py` | Versiones de guion |
| `ScriptChangeReport` | `script_versioning.py` | Reportes de cambio entre versiones |
| `ProjectModuleStatus` | `script_versioning.py` | Estado de módulos por proyecto |
| `Character` | `narrative.py` | Personajes |
| `Scene` | `narrative.py` | Escenas |
| `Sequence` | `narrative.py` | Secuencias |
| `ProductionBreakdown` | `production.py` | Desglose técnico |
| `DepartmentLineItem` | `production.py` | Partidas por departamento |
| `BudgetScenario` | `production.py` | Escenarios de presupuesto |

---

## Estado comercial actual

### Lo que existe hoy (funcionalidad real)

- Subida de guion (texto plano) por proyecto
- Análisis completo: escenas, personajes, localizaciones, departamentos, presupuesto estimado
- Sinopsis, logline, premisa, tema, género, tono, estructura dramática
- Notas de producción y recomendaciones de storyboard
- Versionado de guion con diff entre versiones
- Reportes de cambio con impacto en producción, presupuesto, storyboard, funding, dossier, distribución
- Análisis vía LLM remoto o local (Ollama/Qwen)
- Resumen de análisis persistido por proyecto

### Lo que NO existe (gaps para venta)

| # | Requisito | Existe hoy | Archivo afectado | Gap | Prioridad | Esfuerzo |
|---|---|---|---|---|---|---|
| 1 | Enforcement por plan en endpoints | NO | `intake_routes.py`, `project_routes.py`, `script_version_routes.py`, `ollama_storyboard_routes.py` | Añadir `require_module_access("script_analysis")` | **ALTA** | 1 commit |
| 2 | Pantalla propia de Script Analysis | NO | `src_frontend/src/pages/` | Crear `ScriptAnalysisProPage.tsx` con workspace dedicado | **ALTA** | 1 commit |
| 3 | Export directo (PDF/JSON/MD) | NO | `src/routes/` o `src/services/` | Endpoint de exportación del análisis completo | **ALTA** | 1 commit |
| 4 | Landing/demo guiada del módulo | NO | Frontend | Página de demostración con datos semilla | MEDIA | 1 commit |
| 5 | Copy comercial en catálogo | PARCIAL | `modules.yml` | Texto comercial mejorado con beneficios y límites | MEDIA | 1 commit |
| 6 | Test de enforcement | NO | `tests/integration/` | Test que verifica bloqueo sin plan | MEDIA | 1 commit |
| 7 | CTA específica desde catálogo | NO | `ModulesCatalogPage.tsx` | Enlace a demo guiada o proyecto semilla | BAJA | 1 commit |
| 8 | Onboarding del módulo | NO | Frontend | Tutorial/pasos para primer análisis | BAJA | 1 commit |

---

## Definición de "CID Script Analysis Pro vendible"

Un análisis de guion vendible debe entregar como mínimo:

1. **Logline** — una línea que captura la esencia
2. **Sinopsis** — resumen narrativo de 1-3 párrafos
3. **Premisa** — qué pregunta plantea la historia
4. **Tema** — el "de qué trata realmente"
5. **Género(s)** — clasificación con porcentajes
6. **Tono** — atmósfera emocional dominante
7. **Personajes** — lista con rol, arco, conflicto
8. **Localizaciones** — lugares donde transcurre la acción
9. **Estructura narrativa** — actos, puntos de giro, ritmo
10. **Riesgos** — problemas potenciales detectados
11. **Informe exportable** — PDF/JSON/MD para compartir

**Estado actual**: 9/11 existen en `ScriptSynopsisService`. Faltan: riesgos y exportación.

---

## Dependencias del módulo

```
core (base obligatoria)
  └── script_analysis (este módulo)
        ├── breakdown
        ├── budget_lite
        ├── pitch_deck
        ├── storyboard_ai
        └── funding_grants
```

Script Analysis es **la fuente primaria** de 5 módulos downstream. Cerrarlo bien es requisito para vender Breakdown, Budget, Pitch, Storyboard y Funding.

---

## Propuesta de implementación (por commits)

### Commit 1: Enforcement por plan en endpoints de Script Analysis

```bash
# Archivos:
src/routes/intake_routes.py        # + require_module_access
src/routes/project_routes.py       # + require_module_access en PUT script + POST analyze
src/routes/script_version_routes.py # + require_module_access en todos los endpoints
src/routes/ollama_storyboard_routes.py # + require_module_access en /analyze/local-ollama
```

Añadir `require_module_access("script_analysis")` como dependencia en todos los endpoints del módulo.

### Commit 2: Endpoint de export directo

```bash
# Archivo nuevo o existente:
src/routes/script_analysis_routes.py  # nuevo router con endpoint de export
# o añadir a intake_routes.py:
#   GET /projects/{id}/analysis/export?format=json|pdf|md
```

Servicio de exportación que serializa el análisis completo + sinopsis + breakdown en formato portable.

### Commit 3: Pantalla propia de Script Analysis Pro

```bash
# Archivos nuevos:
src_frontend/src/pages/ScriptAnalysisProPage.tsx  # workspace dedicado
src_frontend/src/App.tsx                          # ruta /projects/:id/script-analysis
src_frontend/src/api/scriptAnalysisApi.ts         # API client específico
```

La pantalla debe incluir: resumen del análisis, sinopsis, personajes, localizaciones, estructura, export button.

### Commit 4: Tests de enforcement

```bash
tests/integration/test_script_analysis_enforcement.py
```

Test que verifica: endpoint sin plan → 403, endpoint con plan → 200.

---

## Validaciones previstas

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"

# Compile check
python -m py_compile src/routes/intake_routes.py
python -m py_compile src/routes/project_routes.py
python -m py_compile src/routes/script_version_routes.py

# Tests existentes
python -m pytest tests/integration/test_project_script_analysis_flow.py -q -x

# Frontend
cd src_frontend && npm run build

# Smoke
./scripts/smoke_cid_dev.sh
./scripts/validate_cid_dev.sh
```

---

## GO / NO-GO

**¿Script Analysis es vendible hoy?** → **NO**

**¿Puede ser vendible en 4 commits?** → **SÍ**

| Criterio | Estado actual | Estado objetivo |
|---|---|---|
| Pantalla propia | NO | SÍ (Commit 3) |
| Endpoint funcional | SÍ | SÍ |
| Persistencia real | SÍ | SÍ |
| Control por plan | NO | SÍ (Commit 1) |
| Export útil | NO | SÍ (Commit 2) |
| Demo reproducible | NO (solo con proyecto real) | SÍ (Commit 3) |
| Tests mínimos | PARCIAL (1 test de integración) | SÍ (+1 test enforcement) |
| Copy comercial | PARCIAL | SÍ (mejorar modules.yml) |

**Veredicto**: Proceder con Sprint 2. Script Analysis Pro es el mejor candidato para ser el primer módulo comercial después de CID Core.

---

## Archivos inspeccionados

- `src/routes/intake_routes.py` — endpoints de intake + análisis + breakdown
- `src/routes/project_routes.py` — PUT script + POST analyze + POST storyboard
- `src/routes/script_version_routes.py` — CRUD versiones + change reports + module status
- `src/routes/ollama_storyboard_routes.py` — análisis local Ollama + prompts
- `src/routes/cid_script_to_prompt_routes.py` — endpoint analyze-full (ya enforce)
- `src/services/script_intake_service.py` — parseo + análisis
- `src/services/script_version_service.py` — versionado + diff
- `src/services/script_synopsis_service.py` — sinopsis/logline/género/tono/estructura
- `src/services/local_script_analysis_service.py` — análisis vía Ollama/Qwen
- `src/services/ollama_client_service.py` — cliente Ollama
- `src/dependencies/module_access.py` — enforcement mechanism
- `src/config/modules.yml` — definición de script_analysis
- `src/config/plans.yml` — feature module_script_analysis en planes
- `src_frontend/src/pages/ProjectDetailPage.tsx` — workspace actual de análisis
- `src_frontend/src/pages/ProjectsPage.tsx` — listado con badge de guion
- `src_frontend/src/pages/ModulesCatalogPage.tsx` — CTA del módulo
- `tests/integration/test_project_script_analysis_flow.py` — test de integración
- `docs/product/CID_MODULAR_COMMERCIAL_ROADMAP.md` — roadmap comercial
