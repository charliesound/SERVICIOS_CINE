# STORYBOARD.DIRECTOR.NOTES.1 — Arquitectura de notas del director para storyboard

Fecha: 2026-05-26

## 1. Diagnóstico

El guion no siempre contiene todos los detalles visuales, de personajes, entorno, mobiliario, props, atmósfera, blocking e intención dramática que el director quiere incorporar. La capa Director Notes debe ser una capa de **override creativo**:

- No modifica el guion original.
- No sustituye el análisis del guion.
- Añade intención, raccord, props, entorno, personaje y puesta en escena.

## 2. Arquitectura jerárquica

| Entidad | Ámbito |
|---|---|
| `ProjectDirectorNotes` | Notas globales del proyecto |
| `SequenceDirectorNotes` | Notas por secuencia |
| `ShotDirectorNotes` | Notas por plano individual |
| `CharacterDirectorNotes` | Notas por personaje |
| `LocationDirectorNotes` | Notas por localización / entorno |
| `PropDirectorNotes` | Notas por mobiliario / props |

## 3. Prioridad de aplicación

De mayor a menor:

1. Override manual del director.
2. Notas de secuencia / plano.
3. Visual Bible.
4. Análisis del guion.
5. Heurística automática.

## 4. Campos para personajes

- `character_id`
- `character_name`
- `age_range`
- `face_description`
- `hair`
- `wardrobe`
- `body_language`
- `emotional_state`
- `continuity_constraints`
- `forbidden_changes`
- `visual_references`

## 5. Campos para localización / entorno

- `location_id`
- `location_name`
- `period`
- `architecture_style`
- `atmosphere`
- `lighting`
- `color_palette`
- `textures`
- `spatial_layout`
- `recurring_elements`
- `forbidden_elements`
- `continuity_constraints`

## 6. Campos para mobiliario / props

- `prop_id`
- `prop_name`
- `description`
- `placement`
- `dramatic_importance`
- `continuity_rule`
- `must_appear`
- `forbidden_changes`

## 7. Campos para puesta en escena / blocking

- `blocking_notes`
- `entrance_direction`
- `exit_direction`
- `eyeline_target`
- `movement_path`
- `actor_position`
- `camera_relation`
- `axis_rule`

## 8. Campos para intención dramática

- `tone`
- `emotional_goal`
- `suspense_level`
- `rhythm`
- `visual_metaphor`
- `director_intent`
- `montage_intent`

## 9. Integración con CinematicShotGrammarEngine

Un futuro `DirectorNotesResolver` debe ejecutarse **antes** del `CinematicShotGrammarEngine` y puede influir en:

- `coverage_pattern`
- `reference_mode`
- `shot_type`
- `priority`
- `visual_raccord_note`
- `character_continuity_note`
- `set_continuity_note`
- `prop_continuity_note`
- `lighting_continuity_note`

## 10. Integración con Visual Bible / Character Bible / Set Bible

Las notas del director alimentan:

- Biblia visual del proyecto.
- Biblia de personajes.
- Biblia de localizaciones / decorados.
- Props recurrentes.
- Continuidad visual entre planos.

## 11. Integración con prompt generation

| Bloque | Propósito |
|---|---|
| `prompt_positive_additions` | Elementos que deben aparecer |
| `prompt_negative_constraints` | Elementos prohibidos |
| `continuity_prompt_block` | Raccord entre planos |
| `character_lock_block` | Fijar apariencia de personaje |
| `location_lock_block` | Fijar localización |
| `prop_lock_block` | Fijar props |

## 12. Integración con trazabilidad

Cada plano debe poder mostrar:

- Qué notas del director afectaron al plano.
- Qué reglas fueron override.
- Qué campos vinieron del guion.
- Qué campos vinieron de Visual Bible.
- Qué campos vinieron de Director Notes.
- `director_note_refs` en `metadata_json`.

## 13. Propuesta UX

En Storyboard Builder, crear sección **"Dirección / Notas creativas"** con pestañas:

- Proyecto
- Personajes
- Secuencias
- Localizaciones
- Props / Mobiliario
- Plano seleccionado
- Reglas de continuidad

Botones:

- Guardar notas
- Aplicar al storyboard
- Regenerar prompts con notas
- Ver impacto en trazabilidad

## 14. Roadmap MVP incremental

| Fase | Alcance |
|---|---|
| **STORYBOARD.DIRECTOR.NOTES.2A** | Schemas + `DirectorNotesResolver` backend-only, sin tocar frontend. |
| **STORYBOARD.DIRECTOR.NOTES.2B** | Integración con `CinematicShotGrammarEngine`: notas influyen en `coverage_pattern`, `reference_mode`, `shot_type`, `priority` y visual raccord. |
| **STORYBOARD.DIRECTOR.NOTES.2C** | Integración con prompt generation, Visual Bible, Character Bible y Set Bible. |
| **STORYBOARD.DIRECTOR.NOTES.2D** | UI mínima en Storyboard Builder: pestaña "Dirección / Notas creativas". |
| **STORYBOARD.DIRECTOR.NOTES.2E** | Trazabilidad de notas aplicadas en `ShotTracePanel`. |

## 15. Persistencia MVP

Para MVP **no es obligatorio crear tablas nuevas**. Puede empezar usando:

- Estructura JSON persistida.
- `metadata_json` controlada.

Tablas dedicadas quedan para fase posterior.

## 16. Riesgos

- Exceso de metadata que dificulte el mantenimiento.
- Conflicto entre notas del director y análisis automático del guion.
- Notas contradictorias entre secuencias y planos.
- Pérdida de trazabilidad de qué nota afectó a qué decisión.
- Desalineación con Visual Bible si no se sincronizan.
- Prompts demasiado largos por acumulación de bloques.
- Sobrecontrol creativo que elimine la flexibilidad del motor.

## 17. GO / NO-GO

**GO** para implementación MVP incremental.

**NO-GO** si se intenta implementar todo de golpe o si se requieren tablas nuevas antes de validar el MVP.
