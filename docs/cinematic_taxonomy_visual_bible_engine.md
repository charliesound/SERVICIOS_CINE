# Cinematic Taxonomy & Visual Bible Engine

## Propósito

Proveer una taxonomía cinematográfica estructurada y reutilizable para el
enriquecimiento de prompts de storyboard en CID. Permite a usuarios y pipelines
seleccionar combinaciones coherentes de tipo de plano, composición, movimiento
de cámara, estilo visual, cámara, stock de película, iluminación, color grading
y estilo narrativo — todo agrupado en *presets cinematográficos* listos para
usar.

## Arquitectura actual (FASE 1)

```
┌──────────────────────────────────────────────────┐
│  src/config/cinematic_taxonomy.yml               │
│  (YAML — fuente de verdad de la taxonomía)       │
└──────────────────┬───────────────────────────────┘
                   │ load (singleton, lazy)
┌──────────────────▼───────────────────────────────┐
│  CinematicTaxonomyService                        │
│  - get_full_taxonomy()                           │
│  - get_category(name)                            │
│  - get_presets() / get_preset(id)                │
│  - enrich_prompt(base, preset_id, tags)          │
└──────────────────┬───────────────────────────────┘
                   │
┌──────────────────▼───────────────────────────────┐
│  /api/cinematic-taxonomy/*                       │
│  5 endpoints read-only + 1 enrich                │
└──────────────────────────────────────────────────┘
```

**Principios:**
- Sin base de datos. La taxonomía vive en YAML (fácil de editar, versionar).
- Servicio singleton, carga lazy.
- Sin dependencia de autenticación en FASE 1.
- Sin conexión a storyboard_service.py ni ComfyUI.

## Archivos creados (FASE 1)

| Archivo | Rol |
|---------|-----|
| `src/config/cinematic_taxonomy.yml` | Taxonomía completa en YAML (11 secciones, 60+ elementos, 8 presets) |
| `src/schemas/cinematic_taxonomy_schema.py` | Schemas Pydantic v2 |
| `src/services/cinematic_taxonomy_service.py` | Lógica de negocio (singleton) |
| `src/routes/cinematic_taxonomy_routes.py` | Endpoints FastAPI |
| `tests/unit/test_cinematic_taxonomy_service.py` | Tests unitarios del servicio (14 tests) |
| `tests/unit/test_cinematic_taxonomy_routes.py` | Tests de integración de rutas (11 tests) |
| `src/core/app_factory.py` | Registro del router (modificado, +2 líneas) |

## Endpoints disponibles

| Método | Path | Response |
|--------|------|----------|
| `GET` | `/api/cinematic-taxonomy` | `CinematicTaxonomyResponse` — taxonomía completa agrupada por categoría |
| `GET` | `/api/cinematic-taxonomy/{category}` | `list[TaxonomyElement]` — elementos de una categoría |
| `GET` | `/api/cinematic-taxonomy/presets` | `list[CinematicPreset]` — todos los presets |
| `GET` | `/api/cinematic-taxonomy/presets/{preset_id}` | `CinematicPreset` — un preset por ID |
| `POST` | `/api/cinematic-taxonomy/enrich-prompt` | `EnrichPromptResponse` — prompt enriquecido |

## Estructura del YAML (`src/config/cinematic_taxonomy.yml`)

### Categorías (10)

Cada categoría contiene una lista de elementos. Cada elemento tiene:

```yaml
- id: ecu                      # Identificador único
  name: Extreme Close-Up       # Nombre legible
  category: shot_types         # Categoría (redundante, útil para filtros)
  description: ...             # Descripción cinematográfica
  prompt_tags: [...]           # Tags para prompt positivo
  negative_prompt_tags: [...]  # Tags para prompt negativo
  use_cases: [...]             # Casos de uso narrativo
```

Categorías disponibles:

| Categoría | Elementos | Ejemplos |
|-----------|-----------|----------|
| `shot_types` | 11 | ECU, CU, MS, WS, OTS, POV, Dutch Angle, Aerial |
| `composition` | 7 | Rule of Thirds, Center Framing, Leading Lines, Symmetry, Frame-in-Frame, Shallow/Deep Focus |
| `camera_movements` | 9 | Pan, Tilt, Dolly, Tracking, Crane, Steadicam, Handheld, Whip Pan, Zoom |
| `visual_styles` | 6 | Hand-Drawn, Rough Pencil, Ink, Charcoal, Graphic Novel, Cinematic Realistic |
| `modern_cameras` | 4 | ARRI ALEXA 35, RED V-RAPTOR, SONY VENICE 2, Panavision DXL2 |
| `analog_cameras` | 4 | ARRIFLEX 416, Panavision Millennium XL2, ARRIFLEX 235, Bolex H16 |
| `film_stocks` | 4 | Kodak Vision3 50D/250D/500T, Ektachrome 100D |
| `lighting_styles` | 6 | Naturalistic, High Key, Low Key, Chiaroscuro, Practical, Golden Hour |
| `color_grading` | 5 | Teal & Orange, Desaturated, Vibrant, Sepia, Bleach Bypass |
| `narrative_styles` | 4 | Classical, Nonlinear, Episodic, Documentary |

### Presets cinematográficos (8)

Cada preset combina elementos de todas las categorías para crear un
look coherente:

| ID | Nombre | Perfil |
|----|--------|--------|
| `noir_classic` | Classic Film Noir | Low key, dutch angles, desaturated, 500T |
| `epic_blockbuster` | Epic Blockbuster | Wide shots, crane, teal-orange, ALEXA 35 |
| `indie_intimate` | Indie Intimate | Handheld, shallow DOF, natural light, VENICE 2 |
| `retro_70s_vibrant` | Retro 70s Vibrant | Zoom, center framing, Ektachrome, saturated |
| `horror_tense` | Horror / Tension | Dutch angles, POV, low key, bleach bypass |
| `documentary_realism` | Documentary Realism | Handheld, deep focus, vérité, desaturated |
| `music_video_vibrant` | Music Video / Fashion | High energy, vibrant, RED V-RAPTOR, Ektachrome |
| `period_drama` | Period Drama | Classical composition, warm palette, sepia |

## Servicio: CinematicTaxonomyService

### Patrón

Singleton (mismo patrón que `ModuleCatalogService`).

```python
class CinematicTaxonomyService:
    _instance = None

    def __new__(cls): ...
    def __init__(self):
        # Carga lazy del YAML una sola vez
        self._load_taxonomy()
```

### Métodos

| Método | Parámetros | Retorno |
|--------|-----------|---------|
| `get_full_taxonomy()` | — | `dict[str, list[TaxonomyElement]]` |
| `get_category(name)` | `category_name: str` | `list[TaxonomyElement]` |
| `get_presets()` | — | `list[CinematicPreset]` |
| `get_preset(preset_id)` | `preset_id: str` | `CinematicPreset` |
| `enrich_prompt(...)` | `base_prompt, preset_id?, selected_tags?` | `EnrichPromptResponse` |

### Errores

- `CategoryNotFoundError` (404) — categoría no existe
- `PresetNotFoundError` (404) — preset no existe
- `TaxonomyLoadError` (422) — error de carga del YAML

## enrich_prompt — Lógica

1. Si `preset_id` está presente, carga el preset y extrae sus `prompt_tags` y
   `negative_prompt_tags`.
2. Si `selected_tags` está presente, los agrega a los tags positivos (evitando
   duplicados con los del preset).
3. Construye el `enriched_prompt` como: `base_prompt. | ` + tags unidos.
4. Construye el `negative_prompt` como lista separada por comas.
5. Verifica límites — genera warnings si se exceden.

## Límite anti-over-prompting

| Límite | Valor | Efecto |
|--------|-------|--------|
| Tags positivos máx. | 20 | Warning + prompt puede ser demasiado complejo |
| Tags negativos máx. | 10 | Warning + resultados pueden ser restrictivos |

### Diferencia recomendada: SDXL vs Flux/Wan

- **SDXL**: Tag soup funcional. Máximo 15–18 tags, separados por comas. El
  modelo entiende bien listas planas. Priorizar `prompt_tags` cortos y
  directos.
- **Flux / Wan**: Fusión semántica. Preferir 5–8 tags integrados en lenguaje
  natural. Los presets actuales están optimizados para SDXL. Para Flux/Wan se
  recomienda una segunda pasada que fusione los tags en frases coherentes.

*(Esta optimización está planificada para FASE 2.)*

## Ejemplos de uso

### Obtener taxonomía completa
```bash
curl -s "http://127.0.0.1:8010/api/cinematic-taxonomy" | jq '.categories | keys'
```

### Obtener tipos de plano
```bash
curl -s "http://127.0.0.1:8010/api/cinematic-taxonomy/shot_types" | jq '.[].name'
```

### Enriquecer prompt con preset
```bash
curl -s -X POST "http://127.0.0.1:8010/api/cinematic-taxonomy/enrich-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "base_prompt": "A detective walking down a rainy street",
    "preset_id": "noir_classic"
  }' | jq '.enriched_prompt'
```

### Enriquecer con tags personalizados
```bash
curl -s -X POST "http://127.0.0.1:8010/api/cinematic-taxonomy/enrich-prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "base_prompt": "A couple dancing at sunset",
    "selected_tags": ["golden hour lighting", "shallow depth of field"]
  }' | jq '{enriched: .enriched_prompt, negative: .negative_prompt}'
```

### Categoría inexistente (404 esperado)
```bash
curl -s -o /dev/null -w "%{http_code}" \
  "http://127.0.0.1:8010/api/cinematic-taxonomy/nonexistent"
# → 404
```

## Riesgos actuales (FASE 1)

1. **Sin DB** — La taxonomía es YAML-only. FASE 2 deberá migrar a DB para
   permitir presets personalizados por usuario/organización.
2. **Sin autenticación** — Los endpoints son públicos. FASE 2 debe agregar
   `Depends(get_current_user_optional)` donde corresponda.
3. **Sin integración ComfyUI** — `enrich_prompt` no está conectado a
   `comfyui_storyboard_render_service.py`.
4. **Sin integración storyboard** — No hay llamado desde el pipeline de
   storyboard.
5. **Sin frontend** — No hay UI para seleccionar presets o tags.
6. **Presets fijos** — No hay endpoints CRUD para presets personalizados.
7. **Over-prompting guard es básico** — Solo cuenta tags, no analiza
   conflictos semánticos entre tags.

## Contrato técnico para FASE 2

```
FASE 2 debe:
├── Mantener compatibilidad con FASE 1 (no romper endpoints existentes)
├── Agregar autenticación a endpoints (Depends)
├── Agregar DB persistence (SQLAlchemy model + migración Alembic)
├── Agregar CRUD de presets personalizados (POST/PUT/DELETE)
├── Integrar enrich_prompt en storyboard_service.py
├── Integrar enrich_prompt en comfyui_storyboard_render_service.py
├── Agregar UI para selección de presets en StoryboardBuilderPage
├── Optimizar para Flux/Wan (fusión semántica de tags)
└── No eliminar YAML (se mantiene como seed data + documentación viva)
```
