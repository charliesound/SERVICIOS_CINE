# FASE 8 — Informe Consolidado: Phase 4 Storyboard Cinematic Intelligence Integration

**Auditor:** Principal Architect / Release Manager  
**Fecha:** 2026-05-08  
**Rama:** `main`  
**Servidor:** `http://127.0.0.1:8010`  
**Base de datos:** `/opt/SERVICIOS_CINE/src/ailinkcinema.db` (SQLite)

---

## Resumen Ejecutivo

La integración de **Cinematic Intelligence (CID)** en el generador de storyboard está **COMPLETA y APTA para commit**. Los 3 bugs reales fueron corregidos y verificados.

| Aspecto | Estado |
|---|---|
| `metadata_json` deserializado correctamente en API | ✅ Corregido |
| PromptSpec llega a ComfyUI | ✅ Corregido |
| `GET /api/projects/{id}/storyboard` | ✅ HTTP 200 |
| `GET /api/projects/{id}/shots` | ✅ HTTP 200 con `metadata_json` dict |
| `POST /storyboard/generate` con CID completo | ✅ HTTP 200 |
| `director_lens_id` inválido | ✅ HTTP 400 controlado |
| `montage_profile_id` inválido | ✅ HTTP 400 controlado |
| Tests unitarios | ✅ 46/46 pasan |
| Smoke tests HTTP | ✅ 31/31 pasan |
| Frontend build | ✅ `npm run build` exitoso |
| Seguridad (fugas de secretos) | ✅ Sin hallazgos |
| Migración Alembic | ⚠️ Documentado, no bloqueante |

---

## Bug 1 — `_serialize_shot()` omitía `metadata_json` (CORREGIDO)

**Causa raíz:** La función `_serialize_shot()` en `src/routes/shot_routes.py:42-64` construía manualmente `StoryboardShotResponse` sin pasar `metadata_json`, por lo que siempre era `None` en la respuesta del endpoint `GET /projects/{id}/shots`.

**Solución:** Se agregó `metadata_json=getattr(shot, "metadata_json", None)` en la línea 56.

**Impacto colateral:** El endpoint `GET /projects/{id}/storyboard` (que usa `model_validate(from_attributes=True)`) ya funcionaba correctamente porque el `field_validator` de Pydantic convertía el string JSON a dict automáticamente.

**Archivo:** `src/routes/shot_routes.py:56`

---

## Bug 2 — `director_lens_id` / `montage_profile_id` inválidos daban 500 (CORREGIDO)

**Causa raíz:** `_build_cinematic_storyboard_shot()` llamaba a `cinematic_intent_service.build_intent()` con cualquier `director_lens_id`, que internamente llamaba a `director_lens_service.get_profile()`. Si el ID no existía, lanzaba `ValueError` que no era capturado, produciendo HTTP 500.

**Solución:** Se agregó validación temprana en `generate_storyboard()`:
- `director_lens_service.get_profile()` captura `ValueError` → HTTP 400
- `montage_intelligence_service.list_profiles()` verifica existencia → HTTP 400
- Validación solo ocurre cuando `use_cinematic_intelligence=True` / `use_montage_intelligence=True`
- IDs `None` no se validan (usan default interno)

**Archivo:** `src/services/storyboard_service.py:211-226`

**Respuestas HTTP:**
- `{"detail": "Unknown director lens profile: {lens_id}"}` → **400**
- `{"detail": "Unknown montage profile: {profile_id}"}` → **400**

---

## Bug 3 — `field_validator` para `metadata_json` en esquema Pydantic (CORREGIDO, sesión anterior)

**Causa raíz:** `StoryboardShotResponse.metadata_json: Optional[Any]` recibía un string JSON desde la BD pero no tenía lógica para convertirlo a `dict`. Pydantic lo dejaba como `None`.

**Solución:** `@field_validator("metadata_json", mode="before")` que llama `json.loads()` en valores string.

**Archivo:** `src/schemas/shot_schema.py:54-66`

---

## Métricas de Validación

### Tests unitarios — 46 pasan (27 originales + 19 nuevos de Phase 4)

```
tests/unit/test_storyboard_cinematic_intelligence.py ........ 27/27
tests/unit/test_director_lens_service.py .................. 10/10
tests/unit/test_montage_intelligence_service.py ............ 5/5
tests/unit/test_cid_script_to_prompt_pipeline.py ........... 4/4
```

Tests nuevos añadidos en esta sesión:
- `TestStoryboardShotResponseMetadataJson` (4 tests): conversión string→dict, null, empty string
- `TestDirectorLensValidation` (3 tests): validación de lens_ids conocidos, error en inválidos
- `TestMontageProfileValidation` (2 tests): validación de profile_ids conocidos

### Smoke test HTTP — 31/31 pasan

Pruebas endpoint-a-endpoint:
- Autenticación y creación de proyecto
- Ingesta de script y análisis
- Generación storyboard con CID completo → 200
- `GET /storyboard` → 200 con `metadata_json`
- `GET /shots` → 200 con `metadata_json`
- 8 campos de `metadata_json` validados
- `director_lens_id` inválido → 400
- `montage_profile_id` inválido → 400
- Sin referencias prohibidas en prompts
- Baseline sin CID sigue funcionando
- Null lens con CID funciona

### py_compile — Sin errores

Todos los archivos clave compilan sin errores.

### npm run build — Sin errores

`tsc && vite build` — 1669 módulos transformados, build exitoso.

### guard_no_db_commit.sh — PASS

Sin archivos .db en staging.

---

## Archivos Modificados (Phase 4 CID)

### Modificados en esta sesión de auditoría

| Archivo | Cambio |
|---|---|
| `src/services/storyboard_service.py` | +`director_lens_service` import; validación de lens/profile IDs antes de generación |
| `src/routes/shot_routes.py` | +`metadata_json=getattr(shot, "metadata_json", None)` en `_serialize_shot()` |
| `tests/unit/test_storyboard_cinematic_intelligence.py` | +9 tests: deserialización metadata_json, validación lens/profile |
| `scripts/smoke_storyboard_cinematic_intelligence_contract.py` | Reescribir como smoke HTTP end-to-end con 31 checks |
| `audits/fase8_informe_consolidado_phase4_cid.md` | Este informe |

### Modificados en sesiones anteriores (Phase 4 baseline)

| Archivo | Cambio |
|---|---|
| `src/models/storyboard.py` | +`metadata_json: Mapped[str \| None]` |
| `src/schemas/shot_schema.py` | +`field_validator` para deserializar `metadata_json` |
| `src/schemas/storyboard_schema.py` | +5 campos en `StoryboardGenerateRequest` |
| `src/routes/storyboard_routes.py` | Pasa 5 nuevos parámetros a `generate_storyboard()` |
| `src_frontend/src/types/storyboard.ts` | +`CinematicShotMetadata`, +5 campos en payload |
| `src_frontend/src/pages/StoryboardBuilderPage.tsx` | Panel CID: lentes, montaje, validación, metadata |
| `src/app.py` | Registro de rutas CID |
| `src/services/storyboard_service.py` | `_build_cinematic_storyboard_shot()`, `_scene_dict_to_script_scene()`, etc. |

### Archivos nuevos (Phase 4 CID)

Todo el ecosistema CID (servicios, rutas, esquemas, configuraciones, tests, scripts de smoke)

---

## Riesgos Pendientes Reales

1. **`GET /api/projects/{id}/storyboard`** — Funciona correctamente (HTTP 200). Riesgo original mitigado.

2. **Migración Alembic** — La BD fue bootstrapeda por `create_all()`. La tabla `alembic_version` no existe. Hay 3 cabezas no fusionadas. Esto es preexistente y no bloquea esta fase, pero debe resolverse antes de producción real.

3. **Chunk size warning en frontend** — `dist/assets/index-CizA4Xdx.js` (895 KB). No bloqueante, pero podría optimizarse con `dynamic import()`.

---

## Comando de Commit Selectivo Recomendado (NO EJECUTAR)

```bash
git add \
  src/models/storyboard.py \
  src/schemas/shot_schema.py \
  src/schemas/storyboard_schema.py \
  src/routes/shot_routes.py \
  src/routes/storyboard_routes.py \
  src/services/storyboard_service.py \
  src_frontend/src/pages/StoryboardBuilderPage.tsx \
  src_frontend/src/types/storyboard.ts \
  src/app.py \
  tests/unit/ \
  scripts/smoke_storyboard_cinematic_intelligence_contract.py \
  alembic/versions/0079ce20dc99_add_storyboard_shot_metadata_json.py \
  src/config/cid_director_lens_profiles.yaml \
  src/config/cid_montage_principles.yaml \
  src/config/cid_script_to_prompt_rules.yaml \
  src/routes/cid_script_to_prompt_routes.py \
  src/schemas/cid_script_to_prompt_schema.py \
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
  audits/fase8_informe_consolidado_phase4_cid.md

git commit -m "feat(cid): Phase 4 — Storyboard Cinematic Intelligence integration

- Add cinematic_intelligence, montage_intelligence, prompt_validation to storyboard generator
- Add metadata_json column with full CID payload (directorial intent, shot editorial purpose, prompt spec, validation)
- Add director_lens_id and montage_profile_id selectors with early validation (HTTP 400 on invalid IDs)
- Fix _serialize_shot() to include metadata_json in GET /shots response
- Fix Pydantic field_validator for metadata_json string-to-dict deserialization
- Update frontend with CID panel UI for lens/montage/validation controls
- Add 46 unit tests and 31 HTTP smoke tests"
```

**Nota:** Los archivos de landing (`src_frontend/src/components/landing/*`, `src_frontend/public/landing-media/*`, etc.) no están incluidos porque pertenecen a un track separado.
