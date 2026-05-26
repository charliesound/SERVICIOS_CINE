# STORYBOARD.DIRECTOR.NOTES.2A — Schemas + DirectorNotesResolver backend-only

Fecha: 2026-05-26

## Archivos creados

| Archivo | Tipo | Líneas |
|---|---|---|
| `src/schemas/director_notes_schema.py` | Schemas | 225 |
| `src/services/director_notes_resolver_service.py` | Servicio | 569 |
| `tests/unit/test_director_notes_schema.py` | Tests schema | 260 |
| `tests/unit/test_director_notes_resolver_service.py` | Tests resolver | 320 |

## Schemas implementados (11 modelos + 3 enums)

### Enums
- `DirectorNoteSource`: manual, voice, imported, system
- `DirectorNoteOverrideLevel`: override_manual, sequence_shot, visual_bible, script_analysis, automatic_heuristic

### Modelos de datos
- `BlockingNotes` — 8 campos (entrance, exit, eyeline, movement, position, camera_relation, axis_rule)
- `DramaticIntent` — 7 campos (tone, emotional_goal, suspense_level, rhythm, visual_metaphor, director_intent, montage_intent)
- `CharacterDirectorNotes` — 16 campos (character_id, character_name, age_range, face_description, hair, wardrobe, body_language, emotional_state, continuity_constraints, forbidden_changes, visual_references, blocking, dramatic_intent, source, override_priority, reviewed_by_user, applied_at)
- `LocationDirectorNotes` — 17 campos (location_id, location_name, period, architecture_style, atmosphere, lighting, color_palette, textures, spatial_layout, recurring_elements, forbidden_elements, continuity_constraints, source, override_priority, reviewed_by_user, applied_at)
- `PropDirectorNotes` — 13 campos (prop_id, prop_name, description, placement, dramatic_importance, continuity_rule, must_appear, forbidden_changes, source, override_priority, reviewed_by_user, applied_at)
- `SequenceDirectorNotes` — 14 campos (sequence_id, sequence_title, tone, rhythm, emotional_goal, visual_metaphor, blocking, dramatic_intent, source, override_priority, reviewed_by_user, applied_at)
- `ShotDirectorNotes` — 16 campos (shot_id, shot_number, sequence_id, notes, blocking, dramatic_intent, coverage_pattern_override, shot_type_override, priority_override, reference_mode_override, source, override_priority, reviewed_by_user, applied_at)
- `ProjectDirectorNotes` — 15 campos (project_id, project_title, global_tone, global_visual_style, global_lighting, global_atmosphere, notes, blocking, dramatic_intent, source, override_priority, reviewed_by_user, applied_at)
- `VoiceDirectorNoteDraft` — 7 campos (source=voice, transcript, transcript_confidence, extracted_entities, applied_to_level, reviewed_by_user, applied_at)
- `DirectorNoteOverride` — 5 campos (field_path, previous_value, new_value, override_source, timestamp)
- `DirectorNotesBundle` — 9 listas contenedoras (project, sequences, shots, characters, locations, props, voice_drafts, overrides, director_note_refs)
- `PromptBlocks` — 7 bloques de prompt (prompt_positive_additions, prompt_negative_constraints, continuity_prompt_block, character_lock_block, location_lock_block, prop_lock_block, visual_raccord_block)
- `DirectorNotesResolveRequest` — 5 campos de entrada
- `DirectorNotesResolveResult` — 8 campos de salida (prompt_blocks, applied_overrides, trace_metadata, voice_drafts_pending_review, director_note_refs, cinematic_grammar_overrides)

## Resolver implementado

`DirectorNotesResolver` en `src/services/director_notes_resolver_service.py`:

| Método | Propósito |
|---|---|
| `resolve_notes_for_project(project_id, bundle)` | Resuelve notas a nivel proyecto |
| `resolve_notes_for_sequence(project_id, sequence_id, bundle)` | Resuelve notas de proyecto + secuencia |
| `resolve_notes_for_shot(project_id, sequence_id, shot_number, bundle)` | Resuelve notas de proyecto + secuencia + plano |
| `merge_notes_by_priority(project, sequence, shot, character, location, prop)` | Merge con prioridad descendente |
| `build_prompt_blocks(bundle, sequence_id, shot_number)` | Construye los 7 bloques de prompt |
| `build_trace_metadata(bundle, project_id, sequence_id, shot_number)` | Trazabilidad de fuentes aplicadas |

### Reglas de prioridad (merge)

1. Override manual del director (índice 0 — gana siempre)
2. Notas de secuencia / plano (índice 1)
3. Visual Bible (índice 2)
4. Análisis del guion (índice 3)
5. Heurística automática (índice 4)

El merge ordena candidatos por prioridad descendente (0 último, 4 primero), de modo que cada nivel sobrescribe al anterior. El override manual siempre gana.

### Bloques de prompt generados

| Bloque | Contenido |
|---|---|
| `prompt_positive_additions` | Tono, estilo, iluminación, atmósfera, intención del director |
| `prompt_negative_constraints` | Elementos prohibidos por personaje/localización/prop |
| `continuity_prompt_block` | Restricciones de continuidad + blocking |
| `character_lock_block` | Descripción completa del personaje (rostro, cabello, vestuario, lenguaje corporal) |
| `location_lock_block` | Descripción completa de localización (periodo, arquitectura, atmósfera, iluminación, paleta, texturas) |
| `prop_lock_block` | Descripción de props (ubicación, importancia, regla de continuidad) |
| `visual_raccord_block` | Consistencia de vestuario, iluminación, atmósfera, paleta y props entre planos |

## Soporte Voice Draft

`VoiceDirectorNoteDraft` incluido con todos los campos necesarios para captura futura por voz:
- `transcript` — texto transcrito
- `transcript_confidence` — confianza del reconocimiento (0.0–1.0)
- `extracted_entities` — entidades extraídas (character, prop, location)
- `applied_to_level` — nivel de aplicación propuesto
- `reviewed_by_user` — **no se aplica hasta que el usuario revisa** (default False)
- `applied_at` — timestamp de aplicación

No se implementa grabación ni transcripción real — solo estructura preparada.

## Tests

| Archivo | Tests | Resultado |
|---|---|---|
| `test_director_notes_schema.py` | 32 | ✅ 32 passed |
| `test_director_notes_resolver_service.py` | 28 | ✅ 28 passed |

Validaciones clave:
- ✅ Schemas serializan/deserializan correctamente (roundtrip)
- ✅ Merge respeta prioridad (override manual gana a Visual Bible)
- ✅ Manual override gana sobre Visual Bible
- ✅ Notas de personaje generan character_lock_block
- ✅ Notas de localización generan location_lock_block
- ✅ Props generan prop_lock_block
- ✅ Visual raccord block generado con vestuario/iluminación/atmósfera
- ✅ Constraint negativos generados desde forbidden_changes
- ✅ Voice draft no se aplica sin reviewed_by_user
- ✅ Voice draft con reviewed_by_user no aparece en pending
- ✅ build_trace_metadata incluye director_note_refs
- ✅ applied_sources ordenados por prioridad (mayor primero)
- ✅ cinematic_grammar_overrides propagados desde shot_notes
- ✅ overrides trayectoria completa field_path + previous_value + new_value

## Lo que queda pendiente

- Integración con `CinematicShotGrammarEngine` (DIRECTOR.NOTES.2B)
- Integración con prompt generation real (DIRECTOR.NOTES.2C)
- Integración con Visual Bible / Character Bible / Set Bible (DIRECTOR.NOTES.2C)
- UI en Storyboard Builder (DIRECTOR.NOTES.2D)
- Trazabilidad en ShotTracePanel (DIRECTOR.NOTES.2E)
- Persistencia en DB con tablas dedicadas (fase posterior)
- Grabación y transcripción de voz real (fase posterior)

## Riesgos

- Exceso de metadata si se añaden muchos personajes/localizaciones/props por proyecto
- Conflicto entre notas del director y heurísticas automáticas del motor — mitigado por prioridad estricta
- Notas contradictorias entre secuencias y planos — mitigado por merge jerárquico
- Voice drafts sin revisión podrían aplicarse accidentalmente — mitigado por flag `reviewed_by_user`
- Prompts demasiado largos si se acumulan muchas notas — pendiente de limitación en 2C

## GO / NO-GO

**GO** para STORYBOARD.DIRECTOR.NOTES.2B (integración con CinematicShotGrammarEngine).

El resolver backend está completo: schemas validados, merge por prioridad probado, todos los bloques de prompt generados, voice draft preparado, trazabilidad implementada. No toca frontend, no modifica planificador existente, no requiere tablas nuevas.
