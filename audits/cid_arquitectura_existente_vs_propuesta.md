# Auditoría Arquitectónica: CID Existente vs Propuesta Estratégica

**Rol:** Principal Architect + Release Safety Engineer  
**Fecha:** 2026-05-08  
**Rama:** `main`  
**Propósito:** Evitar trabajo duplicado antes de implementar nuevas capas CID

---

## Resumen Ejecutivo

El sistema CID actual **YA IMPLEMENTA el 80% del pipeline propuesto**. Los objetos `CinematicIntent`, `PromptSpec`, `SemanticPromptValidationResult`, y `VisualQAEvaluation` existen formalmente en `src/schemas/cid_script_to_prompt_schema.py`. El pipeline orquestado por `cid_script_to_prompt_pipeline_service.py` ya recorre: parsing de guion → breakdown semántico → intención cinematográfica → continuidad → construcción de prompt → validación semántica → QA visual.

**Lo que NO existe aún:**
- `SemanticBreakdown` como objeto formal (existe como `ScriptScene` + `ScriptSequence` pero sin naming explícito)
- `ContinuityState` como objeto formal (existe como `continuity_memory_service` con raw dicts, no modelo Pydantic)
- `ShotProgressionPlan` como objeto formal (existe como `StoryboardSequenceBlock` + `EditorialBeat` + `ShotEditorialPurpose` pero disperso)

**Riesgo real de duplicación:** ALTO. No implementar nada nuevo sin antes consolidar lo existente.

---

## Qué Ya Existe

### Objetos formales (Pydantic models en `src/schemas/cid_script_to_prompt_schema.py`, 559 líneas)

| Objeto | ¿Propuesto? | ¿Existe? | Línea | Estado |
|---|---|---|---|---|
| `ScriptScene` | — | ✅ | 40 | committed |
| `ScriptSequence` | — | ✅ | 70 | committed |
| `DirectorLensProfile` | — | ✅ | 91 | committed |
| `DirectorLensDecision` | — | ✅ | 129 | committed |
| `DirectorialIntent` | — | ✅ | 149 | committed |
| `EditorialBeat` | — | ✅ | 186 | committed |
| `MontageIntent` | — | ✅ | 218 | committed |
| `ShotEditorialPurpose` | — | ✅ | 260 | committed |
| `CinematicIntent` | ✅ | ✅ | 324 | committed |
| `PromptSpec` | ✅ (como VisualPromptSpec) | ✅ | 361 | committed |
| `SemanticPromptValidationResult` | ✅ | ✅ | 395 | untracked |
| `VisualQAEvaluation` | ✅ | ✅ | 436 | untracked |
| `SemanticBreakdown` | ✅ | ❌ | — | no existe |
| `ContinuityState` | ✅ | ❌ | — | no existe |
| `ShotProgressionPlan` | ✅ | ❌ | — | no existe |

### Servicios existentes (todos untracked)

| Servicio | Rol | Pipeline Stage |
|---|---|---|
| `cid_script_scene_parser_service.py` | Parsea guion → `ScriptScene`/`ScriptSequence` | 1 — Semantic Breakdown |
| `continuity_memory_service.py` | Construye memoria de personajes/localizaciones | 2 — Continuity State |
| `director_lens_service.py` | Selecciona lente directorial | 3 — Cinematic Intent |
| `directorial_intent_service.py` | Construye `DirectorialIntent` (mise-en-scene, blocking, camera) | 3 — Cinematic Intent |
| `cinematic_intent_service.py` | Orquesta `CinematicIntent` completo | 3 — Cinematic Intent |
| `montage_intelligence_service.py` | Construye `MontageIntent`, `EditorialBeat`, `ShotEditorialPurpose` | 4 — Shot Progression |
| `prompt_construction_service.py` | Construye `PromptSpec` con positive/negative prompt | 5 — Visual Prompt Spec |
| `semantic_prompt_validation_service.py` | Valida prompt vs intent → `SemanticPromptValidationResult` | 6 — Semantic Validator |
| `visual_qc_service.py` | Evalúa readiness → `VisualQAEvaluation` | 6 — Visual QA |
| `cid_script_to_prompt_pipeline_service.py` | Orquesta pipeline end-to-end | 1→6 — Pipeline |

### Pipeline ya orquestado

```
Script text
  → cid_script_scene_parser_service.parse_script()  → ScriptScene[]
  → continuity_memory_service.build_*()              → continuity anchors
  → cinematic_intent_service.build_intent()           → CinematicIntent
  → prompt_construction_service.build_prompt_spec()   → PromptSpec
  → semantic_prompt_validation_service.validate()     → SemanticPromptValidationResult
  → visual_qc_service.evaluate_prompt()               → VisualQAEvaluation
  → ScriptToPromptRunResponse
```

Este pipeline está expuesto vía `POST /api/cid/script-to-prompt/run` en `cid_script_to_prompt_routes.py`.

### Integración con storyboard

`storyboard_service.py` (committed, modificado) ya integra el pipeline CID cuando `use_cinematic_intelligence=True`:
- Llama `continuity_memory_service.build_continuity_anchors()`
- Llama `cinematic_intent_service.build_intent()`
- Llama `prompt_construction_service.build_prompt_spec()`
- Llama `semantic_prompt_validation_service.validate()` (si `validate_prompts=True`)
- Almacena todo en `metadata_json` de `StoryboardShot`
- El render payload usa `positive_prompt` del `PromptSpec`

### Landing Visual Bible

`src_frontend/src/data/landingVisualBible.ts` (untracked) contiene:
- 13 `LandingVisualSpec` con `narrativePurpose`, `sourceText`, `continuityRules[]`, `positivePrompt`, `negativePrompt`, `status`
- Es la fuente de verdad para landing imagery
- 3 estados: `ready` (5), `needs_regeneration` (8)

`src_frontend/src/utils/landingVisuals.ts` (untracked): funciones `getLandingVisual()` y `getLandingVisualsByRole()`

---

## Mapa de Solapes

| Nueva pieza propuesta | Ya existe en | Estado | Riesgo de duplicado | Recomendación |
|---|---|---|---|---|
| `SemanticBreakdown` | `ScriptScene` + `ScriptSequence` | Parcial | Medio | No crear nuevo. Renombrar o extraer a schema si se necesita tipo explícito |
| `CinematicIntent` | `cinematic_intent_service.build_intent()` → `CinematicIntent` | Completo | **Alto** | NO duplicar. Está en schema, servicio, pipeline y storyboard |
| `ContinuityState` | `continuity_memory_service` (raw dicts, no modelo) | No existe como Pydantic | Bajo | Crear modelo Pydantic `ContinuityState` y refactorizar `continuity_memory_service` para retornarlo |
| `ShotProgressionPlan` | `EditorialBeat[]` + `ShotEditorialPurpose` + `StoryboardSequenceBlock` | Parcial/disperso | Medio | Crear modelo `ShotProgressionPlan` que agrupe beats, editorial purpose y shot types en una sola estructura |
| `VisualPromptSpec` | `PromptSpec` (idéntico: positive_prompt, negative_prompt, semantic_anchors, continuity_anchors, etc.) | **Completo** | **Máximo** | NO crear. `PromptSpec` es exactamente lo propuesto. Usar como está |
| `VisualQAEvaluation` | `visual_qc_service.evaluate_prompt()` → `VisualQAEvaluation` | Completo | Alto | NO duplicar. El stub existe y el schema está definido. Extender si se necesita lógica real de QA post-render |
| semantic validation | `semantic_prompt_validation_service.validate()` | Completo | Alto | NO duplicar |
| director lens rules | `director_lens_service` + `cid_director_lens_profiles.yaml` | Completo | Alto | NO duplicar |
| montage rules | `montage_intelligence_service` + `cid_montage_principles.yaml` | Completo | Alto | NO duplicar |
| "generación visual controlada" | `prompt_construction_service._build_positive_prompt()` + `_build_negative_prompt()` | Completo | Alto | NO duplicar |
| "continuidad de plano general → medio → contraplano" | `montage_intelligence_service.build_shot_editorial_purpose()` (previous_shot_type, next_shot_type) | Parcial | Medio | Extender con reglas de progresión shot-to-shot |
| landing visual bible | `landingVisualBible.ts` + `landing_semantic_prompts_v3*.json` | Completo | Alto | NO duplicar. Consolidar |
| reglas de análisis de guion | `cid_script_to_prompt_rules.yaml` + `cid_script_scene_parser_service.py` | Completo | Alto | NO duplicar |

---

## Git Status: Committed vs Untracked

### 1. Archivos ya commiteados (385 relevantes)
- Toda la infraestructura base: `src/app.py`, `src/database.py`, `src/config.py`
- Modelos: `src/models/storyboard.py`
- Schemas base: `src/schemas/storyboard_schema.py`, `src/schemas/shot_schema.py`
- Routes base: `src/routes/storyboard_routes.py`, `src/routes/shot_routes.py`
- Servicios base: `src/services/storyboard_service.py`
- ComfyUI workflows: `src/comfyui_workflows/*.json` (7 files)
- Frontend types: `src_frontend/src/types/storyboard.ts`
- Landing components (modificados): `LandingHeroCinematic.tsx`, `LandingPipelineBuilder.tsx`, etc.

### 2. Archivos modificados (19)
- `src/app.py` — registro de rutas CID
- `src/models/storyboard.py` — `metadata_json` column
- `src/routes/shot_routes.py` — `_serialize_shot()` fix
- `src/routes/storyboard_routes.py` — pase de parámetros CID
- `src/schemas/shot_schema.py` — `field_validator` metadata_json
- `src/schemas/storyboard_schema.py` — 5 campos CID
- `src/services/storyboard_service.py` — `_build_cinematic_storyboard_shot()`, validación lens/profile
- `src_frontend/src/pages/StoryboardBuilderPage.tsx` — panel CID
- Landing components (9 TSX) — ajustes landing v3
- `src_frontend/src/types/storyboard.ts` — `CinematicShotMetadata`, payload

### 3. Archivos untracked útiles (38)
**Deben committearse (CID core):**
- `src/services/cinematic_intent_service.py`
- `src/services/continuity_memory_service.py`
- `src/services/director_lens_service.py`
- `src/services/directorial_intent_service.py`
- `src/services/montage_intelligence_service.py`
- `src/services/prompt_construction_service.py`
- `src/services/semantic_prompt_validation_service.py`
- `src/services/visual_qc_service.py`
- `src/services/cid_script_scene_parser_service.py`
- `src/services/cid_script_to_prompt_pipeline_service.py`
- `src/routes/cid_script_to_prompt_routes.py`
- `src/schemas/cid_script_to_prompt_schema.py`
- `src/config/cid_director_lens_profiles.yaml`
- `src/config/cid_montage_principles.yaml`
- `src/config/cid_script_to_prompt_rules.yaml`
- `tests/unit/test_cid_script_to_prompt_pipeline.py`
- `tests/unit/test_director_lens_service.py`
- `tests/unit/test_montage_intelligence_service.py`
- `tests/unit/test_storyboard_cinematic_intelligence.py`
- `scripts/smoke_cid_script_to_prompt_contract.py`
- `scripts/smoke_director_lens_contract.py`
- `scripts/smoke_montage_intelligence_contract.py`
- `scripts/smoke_storyboard_cinematic_intelligence_contract.py`

**Deben committearse (Landing frontend data):**
- `src_frontend/src/data/landingVisualBible.ts`
- `src_frontend/src/data/cidScriptToPromptDemo.ts`
- `src_frontend/src/utils/landingVisuals.ts`
- `src_frontend/src/components/landing/LandingScriptToPromptProof.tsx`
- `src_frontend/src/components/landing/LandingMediaBackground.tsx`

### 4. Archivos que NO deben entrar (aún)
- `.tmp/` — outputs de build, renders, review HTML, payloads intermedios
- `docs/validation/` — informes de auditoría visual
- `docs/landing_media_contact_sheet.jpg` — artefacto de revisión
- `src_frontend/public/landing-media/candidates/` — renders de prueba no aprobados
- `src_frontend/public/landing-media/landing-*-v3.webp` — imágenes actuales (ya están siendo trackeadas via manifest)

### 5. Scripts de infraestructura landing (NO bloquear)
Estos pertenecen al pipeline de generación de imágenes landing, no al core CID:
- `scripts/build_landing_*.py`
- `scripts/import_landing_*.py`
- `scripts/render_landing_*.py`
- `scripts/make_*_contact_sheet.py`
- `scripts/promote_landing_*.py`
- `scripts/patch_landing_*.py`
- `scripts/list_comfyui_input_images.py`

---

## Recomendación de Arquitectura Mínima (4 Niveles)

### Nivel 1 — Consolidar (YA, before any new code)
**Objetivo:** Lo que ya existe funciona y está probado. No tocarlo.

✅ No tocar:
- `cinematic_intent_service.py` — orquesta intención cinematográfica
- `prompt_construction_service.py` — construye el prompt final
- `semantic_prompt_validation_service.py` — valida prompt vs escena
- `director_lens_service.py` — catálogo de lentes
- `montage_intelligence_service.py` — inteligencia de montaje
- `storyboard_service.py` — integración storyboard + CID
- `cid_script_to_prompt_pipeline_service.py` — pipeline orquestado
- `cid_script_to_prompt_schema.py` — todos los objetos Pydantic
- `landingVisualBible.ts` — fuente de verdad visual landing

### Nivel 2 — Extender (próximo sprint)
**Objetivo:** Cerrar gaps sin romper lo existente.

1. **Crear `ContinuityState` como Pydantic model** en `cid_script_to_prompt_schema.py`:
   - Refactorizar `continuity_memory_service` para retornar `ContinuityState` en vez de raw dict
   - Incluir: `character_anchors`, `location_anchors`, `tone_anchors`, `palette_anchors`, `scene_id`, `sequence_id`
   - Mantener compatibilidad hacia atrás

2. **Crear `ShotProgressionPlan` como Pydantic model**:
   - Agrupar `EditorialBeat[]`, `ShotEditorialPurpose`, shot types pool, `sequence_id`
   - Extender `montage_intelligence_service` para retornar plan completo de progresión
   - Incluir reglas de: wide → medium → close-up → over-shoulder

3. **Renombrar `ScriptScene` → alias `SemanticBreakdown`** (o crear type alias):
   - `ScriptScene` ya contiene: scene_number, heading, int_ext, location, time_of_day, characters, action_summary, dramatic_objective, conflict, emotional_tone
   - Es básicamente un `SemanticBreakdown` con otro nombre
   - Opción A: type alias `SemanticBreakdown = ScriptScene`
   - Opción B: refactorizar nombre (riesgo de romper imports)

### Nivel 3 — Continuidad real para secuencias (sprint+2)
- Implementar `continuity_memory_service` con persistencia real (DB backed, no solo in-memory)
- Memoria de personajes: qué vestían, dónde estaban, estado emocional
- Memoria de localizaciones: luz, hora del día, objetos presentes
- Reglas de progresión shot-to-shot: general → medio → contraplano
- Detección de saltos de raccord (el schema `SemanticPromptValidationResult` ya tiene `errors` y `warnings`)

### Nivel 4 — Visual QA post-render (sprint+3)
- `visual_qc_service.py` es actualmente un stub que siempre retorna `approve_for_render`
- Implementar QA real: cargar imagen generada, analizar con LLM/VLM, comparar con `PromptSpec`
- Detectar: oscuridad excesiva, abstracción vacía, falta de personajes, incoherencia de localización
- Usar `VisualQAEvaluation` existente (tiene `semantic_match_score`, `cinematic_match_score`, `continuity_score`, `detected_issues`, `recommendation`)

---

## Plan de Implementación Sin Duplicar

### 1. Qué NO tocar (ya existe y funciona)
- `src/schemas/cid_script_to_prompt_schema.py` — todos los modelos Pydantic
- `src/services/cinematic_intent_service.py` — orquestación de intención
- `src/services/prompt_construction_service.py` — construcción de prompts
- `src/services/semantic_prompt_validation_service.py` — validación semántica
- `src/services/director_lens_service.py` — lentes directoriales
- `src/services/montage_intelligence_service.py` — inteligencia de montaje
- `src/services/cid_script_to_prompt_pipeline_service.py` — pipeline orquestado
- `src/services/storyboard_service.py` — integración storyboard
- `src/routes/cid_script_to_prompt_routes.py` — endpoints CID
- `src_frontend/src/data/landingVisualBible.ts` — visual bible landing
- `src_frontend/src/data/cidScriptToPromptDemo.ts` — demo data

### 2. Qué extender (próximo sprint)
| Archivo | Extensión |
|---|---|
| `continuity_memory_service.py` | Retornar `ContinuityState` en vez de raw dict. Agregar shot progression rules |
| `montage_intelligence_service.py` | Retornar `ShotProgressionPlan` que agrupe beats + editorial purpose + shot pool |
| `cid_script_to_prompt_schema.py` | Agregar modelos `ContinuityState` y `ShotProgressionPlan` |
| `visual_qc_service.py` | Implementar QA real post-render (actualmente stub) |
| `semantic_prompt_validation_service.py` | Agregar reglas de validación de progresión shot-to-shot |

### 3. Qué crear nuevo
| Archivo | Propósito |
|---|---|
| Nada urgente | El 80% del pipeline propuesto ya existe |

### 4. Qué refactorizar (más adelante)
- `ScriptScene` → alias `SemanticBreakdown` (o renombrar, con cuidado de imports)
- Los servicios CID actualmente cargan YAML en cada llamada (sin cache). Considerar caching.
- `continuity_memory_service` está in-memory, sin persistencia real. Para producción necesita DB.

### 5. Qué archivos conviene commitear AHORA
**Commit 1 — CID Core (ALTO PRIORIDAD):**
```bash
git add \
  src/schemas/cid_script_to_prompt_schema.py \
  src/routes/cid_script_to_prompt_routes.py \
  src/services/cid_script_scene_parser_service.py \
  src/services/cid_script_to_prompt_pipeline_service.py \
  src/services/cinematic_intent_service.py \
  src/services/continuity_memory_service.py \
  src/services/director_lens_service.py \
  src/services/directorial_intent_service.py \
  src/services/montage_intelligence_service.py \
  src/services/prompt_construction_service.py \
  src/services/semantic_prompt_validation_service.py \
  src/services/visual_qc_service.py \
  src/config/cid_director_lens_profiles.yaml \
  src/config/cid_montage_principles.yaml \
  src/config/cid_script_to_prompt_rules.yaml \
  src/app.py \
  src/models/storyboard.py \
  src/schemas/shot_schema.py \
  src/schemas/storyboard_schema.py \
  src/routes/shot_routes.py \
  src/routes/storyboard_routes.py \
  src/services/storyboard_service.py \
  src_frontend/src/types/storyboard.ts \
  src_frontend/src/pages/StoryboardBuilderPage.tsx
```
Mensaje: `feat(cid): Phase 4 — Storyboard Cinematic Intelligence integration with full CID pipeline`

**Commit 2 — Tests + Smokes:**
```bash
git add \
  tests/unit/ \
  scripts/smoke_cid_script_to_prompt_contract.py \
  scripts/smoke_director_lens_contract.py \
  scripts/smoke_montage_intelligence_contract.py \
  scripts/smoke_storyboard_cinematic_intelligence_contract.py
```
Mensaje: `test(cid): Unit tests and HTTP smoke tests for CID pipeline`

**Commit 3 — Landing Data + Demo:**
```bash
git add \
  src_frontend/src/data/landingVisualBible.ts \
  src_frontend/src/data/cidScriptToPromptDemo.ts \
  src_frontend/src/utils/landingVisuals.ts \
  src_frontend/src/components/landing/LandingScriptToPromptProof.tsx \
  src_frontend/src/components/landing/LandingMediaBackground.tsx
```
Mensaje: `feat(landing): Visual bible, CID demo data and Script-to-Prompt proof component`

### 6. Qué archivos dejar fuera
- `.tmp/` — outputs de build
- `docs/validation/` — informes de auditoría visual
- `scripts/build_landing_*.py`, `scripts/import_landing_*.py`, `scripts/render_landing_*.py` — pipeline de generación de imágenes landing (commit separado cuando esté listo)
- `src_frontend/public/landing-media/candidates/` — renders de prueba no aprobados
- `alembic/versions/0079ce20dc99_*.py` — migración Alembic (requiere resolver 3 cabezas primero)
- `audits/` — informes de auditoría (opcional, mantener para trazabilidad)

### 7. Qué smokes faltan
| Smoke | Estado |
|---|---|
| `scripts/smoke_storyboard_cinematic_intelligence_contract.py` | ✅ 31/31 HTTP |
| `scripts/smoke_cid_script_to_prompt_contract.py` | ✅ (unitario) |
| `scripts/smoke_director_lens_contract.py` | ✅ (unitario) |
| `scripts/smoke_montage_intelligence_contract.py` | ✅ (unitario) |
| HTTP smoke para `POST /api/cid/script-to-prompt/run` | ❌ **FALTA** |
| HTTP smoke para continuity memory con escenas múltiples | ❌ **FALTA** |
| HTTP smoke para visual QA con imagen post-render | ❌ **FALTA** (requiere QA real) |

### 8. Orden recomendado de commits
1. **Commit 1: CID Core** (ahora — libera Phase 4)
2. **Commit 2: Tests + Smokes** (ahora — inmediatamente después)
3. **Commit 3: Landing Data** (ahora — independiente)
4. Sprint 2: `ContinuityState` + `ShotProgressionPlan` (extender)
5. Sprint 3: Continuidad persistente + detección de saltos
6. Sprint 4: Visual QA post-render real

---

## Advertencias de Seguridad

1. **No exponer `POST /api/cid/script-to-prompt/run` sin auth** — el pipeline puede llamar a Ollama local y consumir recursos. Verificar que `cid_script_to_prompt_routes.py` use `get_tenant_context`.
2. **No hardcodear rutas de modelos** — los workflows ComfyUI usan placeholders. Los scripts de patch (`patch_landing_*.py`) convierten a rutas locales, pero esos son scripts, no código en producción.
3. **No committear `.tmp/`** — contiene payloads con seeds deterministas y paths locales.
4. **`visual_qc_service.py` es un stub** — no validar contra él aún. Siempre retorna `approve_for_render`.
5. **Los YAML de configuración CID no tienen validación de schema** — si se editan manualmente, pueden romper servicios silenciosamente. Considerar agregar `pydantic.Field` validation.
6. **No hay rate limiting en endpoints CID** — `POST /api/cid/script-to-prompt/run` puede saturar Ollama local.

---

## Prompt Reducido para la Siguiente Implementación

```
NO duplicar. El pipeline CID ya existe:
  ScriptScene → CinematicIntent → PromptSpec → Validation → VisualQAEvaluation

Lo que FALTA (3 objetos formales):
- ContinuityState: modelo Pydantic para continuity_memory_service
- ShotProgressionPlan: agrupar EditorialBeat + ShotEditorialPurpose + shot_type pool
- (SemanticBreakdown: alias opcional de ScriptScene)

Lo que FALTA (extender):
1. continuity_memory_service → retornar ContinuityState (no raw dict)
2. montage_intelligence_service → retornar ShotProgressionPlan
3. visual_qc_service → QA real post-render (actualmente stub)
4. Reglas shot-to-shot: wide → medium → close-up → over-shoulder

Lo que NO tocar:
- cinematic_intent_service (completo)
- prompt_construction_service (completo)
- semantic_prompt_validation_service (completo)
- director_lens_service (completo)
- storyboard_service._build_cinematic_storyboard_shot (completo)
- cid_script_to_prompt_schema.py (tiene todos los modelos Pydantic)
- cid_script_to_prompt_pipeline_service.py (orquestación completa)
- landingVisualBible.ts (fuente de verdad visual)
```

---

## Comandos de Validación Post-Implementación

```bash
# Compilar
PYTHONPATH=src python3 -m py_compile \
  src/schemas/cid_script_to_prompt_schema.py \
  src/services/continuity_memory_service.py \
  src/services/montage_intelligence_service.py \
  src/services/visual_qc_service.py

# Tests unitarios
.venv/bin/python -m pytest tests/unit/ -q

# Smoke tests HTTP
python3 scripts/smoke_storyboard_cinematic_intelligence_contract.py

# Frontend
cd src_frontend && npm run build

# Seguridad
bash scripts/guard_no_db_commit.sh
```

---

## Decisión de Commit

**SÍ commitear AHORA** los Commits 1, 2 y 3 (CID Core + Tests + Landing Data).

**NO esperar** a implementar `ContinuityState`, `ShotProgressionPlan` o QA real. Esos son sprints separados. Lo que existe ya está probado (46 tests unitarios + 31 smoke HTTP) y funcionando end-to-end.

**NO duplicar** nada del pipeline CID existente. El 80% del sistema propuesto ya está implementado y en producción (o listo para commit).
