# STORYBOARD.CINEMA.1 — Auditoría de gramática cinematográfica

Fecha: 2026-05-26

## Contexto

El proyecto AILinkCinema/CID usa `shot_type`, `visual_mode`, `camera_movement`, `composition_tags` y
`lighting_tags` en los planos de storyboard. La gramática cinematográfica define qué valores son
válidos para estos campos, su semántica y las reglas de coherencia entre ellos.

## Estado actual

| Campo | Origen | Problema detectado |
|---|---|---|
| `shot_type` | `narrative_beat.shot_type` + metadata_json | Mezcla de escalas (CU, MCU, WS) con ángulos (LA, HA). Sin validación centralizada. |
| `visual_mode` | `storyboard_shots.visual_mode` | Valores libres (`hand_drawn_storyboard`, `3d_previsualization`). Sin enum formal. |
| `camera_movement` | Solo en metadata_json | Sin campo propio en tabla. Se pierde si no se guarda explícitamente. |
| `composition_tags` | metadata_json.prompt_spec | Formato libre, sin taxonomía. |
| `lighting_tags` | metadata_json.prompt_spec | Idem. |
| `cinematic_grammar_version` | No existe | No hay trazabilidad de versión de gramática usada al generar. |

## Rutas trace relacionadas

Las rutas trace reales para obtener metadatos de plano son:

```
GET /api/projects/{project_id}/storyboard/shots/{shot_id}/trace
GET /api/projects/{project_id}/storyboard/trace
GET /api/projects/{project_id}/storyboard/assets/{asset_id}/trace
```

Estas devuelven `StoryboardTraceRecord` con `prompt_trace`, `model_trace`, `asset_trace` y
`version_trace`. La gramática no tiene endpoint propio aún — los campos se leen desde
`metadata_json` de cada plano.

## Schemas involucrados

- `schemas/cinematic_taxonomy_schema.py` — taxonomía existente (phase 1)
- `schemas/storyboard_trace_schema.py` — `StoryboardTraceRecord` con sub-traces
- `schemas/cinematic_grammar_schema.py` — **pendiente** (crear en STORYBOARD.CINEMA.2A)

## Roadmap ajustado (MVP por fases)

### STORYBOARD.CINEMA.2A — Schemas/enums + CinematicShotGrammarEngine base

- Crear `schemas/cinematic_grammar_schema.py` con:
  - `ShotType(str, Enum)` — valores normalizados (CU, MCU, MS, MLS, WS, LA, HA, OTS, POV, ECU, etc.)
  - `VisualMode(str, Enum)` — `hand_drawn_storyboard`, `3d_previsualization`, `concept_art`, `motion_boarding`
  - `CameraMovement(str, Enum)` — `static`, `pan_left`, `pan_right`, `tilt_up`, `tilt_down`, `track_in`, `track_out`, `crane_up`, `crane_down`, `steadicam`, `handheld`, `dolly_zoom`
  - `CompositionTag(str, Enum)` — `rule_of_thirds`, `center_frame`, `leading_lines`, `frame_within_frame`, `symmetry`, `asymmetry`, `deep_space`, `shallow_space`, `dutch_angle`, `birds_eye`, `worms_eye`
  - `LightingTag(str, Enum)` — `natural`, `high_key`, `low_key`, `chiaroscuro`, `backlight`, `silhouette`, `practical`, `motivated`, `ambient`, `neon`, `golden_hour`, `night`
- Crear `services/cinematic_grammar_service.py` con `CinematicShotGrammarEngine`:
  - `validate_shot_grammar(shot_type, visual_mode, camera_movement, ...) → ValidationResult`
  - `get_valid_combinations(visual_mode) → list[tuple]` — qué shot_types son válidos para cada modo
  - `infer_missing_fields(narrative_text, ...) → dict` — inferencia básica desde narrativa
- No crear aún tabla `cinematic_grammar_versions`
- Usar `metadata_json.cinematic_grammar_version = "v0.1"` para marcar versión MVP

### STORYBOARD.CINEMA.2B — Integración con storyboard_shot_planner_service

- Conectar `CinematicShotGrammarEngine` en `storyboard_shot_planner_service.py`:
  - Validar shot_type antes de asignar a un beat
  - Si el shot_type no es válido para el visual_mode, corregir automáticamente (o warning)
  - Población de `camera_movement`, `composition_tags`, `lighting_tags` con defaults por shot_type
- Añadir validación en `POST /{project_id}/storyboard/shots/{shot_id}/feedback`
- Tests unitarios en `tests/unit/test_cinematic_grammar_integration.py`

### STORYBOARD.CINEMA.2C — Metadata + trazabilidad + badges UI

- Almacenar gramática en `metadata_json.cinematic_grammar` al generar/re-generar
- Incluir en respuesta trace (`GET .../shots/{shot_id}/trace`) un campo `cinematic_grammar`
  dentro del `prompt_trace` o como campo raíz opcional
- Badges visuales en frontend:
  - Badge de `shot_type` con color semántico (CU=rojo, MS=azul, WS=verde)
  - Badge de `visual_mode` con icono
  - Tooltip con `camera_movement`, `composition_tags`, `lighting_tags`
- Tests end-to-end en `tests/unit/test_storyboard_cinematic_grammar_ui.py`

### STORYBOARD.CINEMA.2D — Smoke test con ejemplo Marta

- Crear `scripts/smoke_cinematic_grammar_marta.sh`:
  - Crea proyecto con screenplay de Marta
  - Genera storyboard
  - Verifica shot_types asignados
  - Verifica consistencia con visual_mode
  - Verifica metadatos en respuesta trace
- Validar contra `docs/validation/storyboard_cinematic_grammar_marta_smoke_20260526.md`

## Tablas dedicadas (fase posterior)

`CinematicGrammarVersion` como tabla independiente en base de datos:

```sql
CREATE TABLE cinematic_grammar_versions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID NOT NULL REFERENCES projects(id),
    shot_id UUID REFERENCES storyboard_shots(id),
    grammar_version TEXT NOT NULL,
    grammar_snapshot JSONB,
    created_at TIMESTAMPTZ DEFAULT now()
);
```

Para MVP se usa exclusivamente `metadata_json.cinematic_grammar_version = "v0.1"`.

## Riesgos

- Cambiar `shot_type` a enum rompe datos existentes en DB → migración necesaria.
- `camera_movement` es nuevo campo → requiere migración o aceptar que viva solo en metadata_json.
- La inferencia desde narrativa puede ser imprecisa sin NLP real.

## GO/NO-GO para STORYBOARD.CINEMA.2A

**GO.** Los enums y el motor base no rompen nada existente. Se procede con fase 2A.
