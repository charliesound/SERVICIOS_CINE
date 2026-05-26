# STORYBOARD.CINEMA.2A — CinematicShotGrammarEngine base

Fecha: 2026-05-26

## Archivos creados

| Archivo | Tipo | Líneas |
|---|---|---|
| `src/schemas/cinematic_grammar_schema.py` | Schemas/enums | 225 |
| `src/services/cinematic_shot_grammar_engine.py` | Servicio | 560 |
| `tests/unit/test_cinematic_grammar_schema.py` | Tests schema | 120 |
| `tests/unit/test_cinematic_shot_grammar_engine.py` | Tests engine | 310 |

> **HOTFIX-2** (2026-05-26): Añadidos 11 campos de raccord visual a `CinematicShotSpec`, método `_apply_visual_raccord` en el motor, y 11 tests de validación.

## Enums implementados

| Enum | Valores |
|---|---|
| `CinematicShotType` | 17 tipos (ELS, LS, MLS, MS, MCU, CU, ECU, POV, OTS, INSERT, TWO_SHOT, LA, HA, DA, AERIAL, MACRO, REVERSE) |
| `CoveragePattern` | 11 patrones (classic, threat, suspense, exploration, action, dialogue, confrontation, discovery, transition, emotional, sound_focus) |
| `ContinuityRule` | 12 reglas (eyeline_match, match_on_action, cross_cutting, jump_cut, continuity_cut, montage, axis_of_action, screen_direction, sound_bridge, match_cut, cutaway, insert_cut) |
| `EditorialRole` | 12 roles (establishing, master, coverage, insert, reaction, pov, transition, closing, bridge, sound_detail, threat_indicator, action_beat) |
| `ShotPriority` | 5 niveles (must_have, high, medium, low, optional) |
| `CinematicFunction` | 13 funciones (establish_context, exposition, build_tension, reveal_threat, action_beat, dialogue, reaction, atmosphere, sound_focus, transition_device, discovery, climax, resolution) |
| `SceneType` | 12 tipos detectables |
| `ReferenceMode` | 3 modos (filmic, literary, mixed) |
| `BeatType` | 7 tipos (action, dialogue, description, atmosphere, reaction, transition, sound, reveal) |

## Modelos implementados

- `CinematicShotSpec` — especificación individual de plano (33 campos tras HOTFIX-2)
- `OrderedShotPlan` — plan ordenado de planos para una escena
- `CinematicGrammarRequest` — request de entrada (scene_text, scene_type_hint, character_names, beats, reference_mode)
- `CinematicGrammarResult` — resultado completo con plan + metadatos

## Reglas implementadas en el motor

### Detección de tipo de escena (`detect_scene_type`)
- Keyword matching por escena (12 tipos, ~100 keywords)
- Scoring: el tipo con más keywords coincidentes gana
- Fallback a `SUSPENSE` si no hay matches

### Selección de patrón de cobertura (`select_coverage_pattern`)
- Mapa directo scene_type → coverage_pattern
- 11 patrones de cobertura predefinidos con 3-8 planos cada uno

### Construcción de plan (`build_ordered_shot_plan`)
- Mapeo de shot_key (WS, MS, CU, etc.) → `CinematicShotType`
- Detección de beats desde el texto (acción, diálogo, sonido, atmósfera, revelación)
- Asignación de cámara y lente según tipo de plano y función dramática

### Notas de continuidad (`apply_continuity_notes`)
- Notas contextuales por rol (POV, reacción, establishing, threat_indicator, etc.)
- Notas de raccord tras POV (mantener dirección de mirada)
- Notas de raccord tras primer plano (reubicación espacial)
- Notas de eyeline para planos POV
- Sugerencias de montaje (match on action, corte por sonido, disolver)

### Prioridades (`assign_priorities`)
- Asignadas por defecto según patrón (implementación extensible)

### Metadata de raccord visual (`_apply_visual_raccord`) — HOTFIX-2
- Detecta personajes desde el texto (palabras capitalizadas no gramaticales)
- Extrae props, localización, iluminación y atmósfera del texto de escena
- Pobla 11 campos de continuidad visual en cada plano del plan
- `character_continuity_note`, `character_reference_id`, `wardrobe_continuity_note`
- `prop_continuity_note`, `set_continuity_note`, `location_reference_id`
- `lighting_continuity_note`, `atmosphere_continuity_note`
- `axis_continuity_note`, `movement_direction_note`, `visual_raccord_note`
- Todos los campos son `None` por defecto; se propagan coherentemente a todos los planos
- Diseñado para que CINEMA.2B/2C consuman esta metadata en prompt generation / Visual Bible / ComfyUI

## Ejemplo Marta — resultado (post-hotfix)

Texto:
> Marta entra con una linterna. La casa está en silencio. El suelo cruje. Marta pregunta si hay alguien. Una sombra cruza al fondo del pasillo. Marta se queda quieta.

Escena detectada: `suspense` (8 keywords: 'silencio', 'cruje', 'sombra', 'quieta', 'pregunta', 'fondo', 'linterna', 'entra')
Patrón seleccionado: `suspense_coverage`

**8 planos generados:**

| # | Shot type | Rol | Función | Prioridad | Prompt intent |
|---|---|---|---|---|---|
| 1 | LONG_SHOT | establishing | establish_context | must_have | — |
| 2 | MEDIUM_SHOT | action_beat | action_beat | must_have | — |
| 3 | INSERT | sound_detail | sound_focus | high | "Detalle del sonido — el suelo cruje bajo los pies" |
| 4 | MEDIUM_CLOSE_UP | coverage | dialogue | must_have | "Personaje se detiene y pregunta — tensión contenida" |
| 5 | POV | pov | reveal_threat | must_have | "Punto de vista de Marta — haz de linterna explorando la oscuridad" |
| 6 | MEDIUM_LONG_SHOT | threat_indicator | build_tension | must_have | "Sombra que cruza al fondo del pasillo — amenaza difusa" |
| 7 | CLOSE_UP | reaction | reaction | must_have | "Reacción de Marta — se queda quieta, tensión creciente" |
| 8 | LONG_SHOT | closing | resolution | high | — |

Reglas de continuidad: eyeline_match, continuity_cut, screen_direction

Notas generadas:
- Shot 2 (action_beat): "Empalmar por movimiento — match on action"
- Shot 3 (sound_detail): "Sincronizar sonido con imagen — corte por sonido"
- Shot 4 (dialogue): "Plano general de contexto — corte directo"
- Shot 5 (POV): "Punto de vista del personaje — mismo eje que plano anterior" + eyeline
- Shot 6 (threat_indicator): "Indicador de amenaza — valor de aislamiento; Vuelta a plano objetivo tras POV" + raccord
- Shot 7 (reaction): "Reacción a estímulo previo"
- Shot 8 (closing): "Plano de cierre — disolver o corte directo" + raccord

## Tests

| Archivo | Tests | Resultado |
|---|---|---|
| `test_cinematic_grammar_schema.py` | 14 | ✅ 14 passed |
| `test_cinematic_shot_grammar_engine.py` | 39 | ✅ 39 passed |
| `test_storyboard_*.py` (regresión) | 190 | ✅ 190 passed (sin cambios) |

Validaciones Marta (post-hotfix):
- ✅ Mínimo **8 planos** generados (especificación obligatoria)
- ✅ **Dialogue shot**: MEDIUM_CLOSE_UP con función DIALOGUE y prioridad MUST_HAVE
- ✅ **Threat shot**: THREAT_INDICATOR con prioridad MUST_HAVE
- ✅ Al menos un INSERT
- ✅ Al menos un POV
- ✅ Al menos un threat_indicator
- ✅ Al menos un REACTION
- ✅ Prioridades MUST_HAVE presentes (5/8 planos)
- ✅ continuity_note en reaction shot
- ✅ eyeline_note en POV shot
- ✅ raccord_note tras POV
- ✅ cinematic_grammar_version = "v0.1"
- ✅ prompt_intent personalizado por contexto detectado

Validaciones Marta raccord visual (HOTFIX-2):
- ✅ character_continuity_note presente en todos los planos (con ref a Marta)
- ✅ character_reference_id = "Marta"
- ✅ wardrobe_continuity_note presente
- ✅ prop_continuity_note con "flashlight"
- ✅ set_continuity_note con "abandoned house hallway"
- ✅ location_reference_id presente
- ✅ lighting_continuity_note con "flashlight"
- ✅ atmosphere_continuity_note con "silent"
- ✅ visual_raccord_note con "preserve"
- ✅ axis_continuity_note en establishing shot
- ✅ Todos los planos comparten metadata visual coherente (mismos valores)

## Lo que queda sin integrar

- `storyboard_shot_planner_service.py` — no modificado (será STORYBOARD.CINEMA.2B)
- `storyboard_service.py` — no modificado (será STORYBOARD.CINEMA.2B)
- Prompt generation — no modificado
- Frontend — no modificado
- Export Storyboard Sheet — no modificado
- Trazabilidad existente — schemas nuevos no afectan a los existentes
- `CinematicGrammarVersion` como tabla dedicada — pospuesto a fase posterior (se usa metadata_json)
- Tests de integración con DB — el motor es stateless, no requiere DB

## Riesgos

- Keyword matching es frágil: textos cortos o ambiguos pueden dar falsos positivos. Mejorable con NLP en fase posterior.
- Los patrones de cobertura son fijos por tipo de escena. En 2B se podrán parametrizar por personajes, tono, etc.
- Algunas notas de continuidad son genéricas. En 2C se mejorarán con contexto específico del plano.
- El mapeo `detect_scene_type` favorece el primer tipo en caso de empate por orden de diccionario. Mejorable con scoring ponderado.
- Metadata de raccord visual se genera con heurísticas simples (keyword → props/luz/atmósfera); CINEMA.2B/2C recibirá datos estructurados desde el script breakdown.

## GO/NO-GO para STORYBOARD.CINEMA.2B

**GO.** Motor base completo, tests pasando, sin regresiones, sin integración con generación real.
