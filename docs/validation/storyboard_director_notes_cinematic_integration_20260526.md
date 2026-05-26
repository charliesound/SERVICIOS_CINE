# STORYBOARD.DIRECTOR.NOTES.2B — Integración DirectorNotesResolver + CinematicShotGrammarEngine

Fecha: 2026-05-26

## Archivos modificados/creados

| Archivo | Cambio |
|---|---|
| `src/schemas/cinematic_grammar_schema.py` | Modificado — añadidos campos `director_notes_result`, `director_notes_bundle` a `CinematicGrammarRequest` |
| `src/services/cinematic_shot_grammar_engine.py` | Modificado — añadido `_apply_director_notes`, modificados `build_ordered_shot_plan` y `plan_scene_coverage` |
| `tests/unit/test_cinematic_shot_grammar_director_notes_integration.py` | Creado — 30 tests de integración |
| `docs/validation/storyboard_director_notes_cinematic_integration_20260526.md` | Creado — este reporte |

## Cómo se integran Director Notes con CinematicShotGrammarEngine

### Entrada
`CinematicGrammarRequest` ahora acepta dos campos opcionales:
- `director_notes_result: DirectorNotesResolveResult | None = None` — resultado resuelto del resolver
- `director_notes_bundle: DirectorNotesBundle | None = None` — bundle original con notas estructuradas

Ambos campos tienen default `None`, por lo que **ningún test existente se rompe**.

### Flujo de ejecución

```
plan_scene_coverage(request)
  ├── detect_scene_type()
  ├── select_coverage_pattern(scene_type)
  ├── [OVERRIDE] coverage_pattern desde cinematic_grammar_overrides si existe
  ├── build_ordered_shot_plan(text, pattern, character_names, director_notes...)
  │     ├── _detect_beats()
  │     ├── _apply_prompt_intents()
  │     ├── apply_continuity_notes()
  │     ├── _apply_visual_raccord()
  │     ├── _apply_director_notes()      ← NUEVO
  │     └── assign_priorities()
  └── CinematicGrammarResult
```

### Método nuevo: `_apply_director_notes(shots, director_notes_result, bundle)`

Aplica notas del director como **override post-heurística**. Recibe la lista de planos ya construida y devuelve una versión modificada respetando la prioridad declarada.

## Reglas implementadas

| # | Regla | Mecanismo |
|---|---|---|
| 1 | **Character continuity** | Si bundle tiene `CharacterDirectorNotes`, propaga `character_continuity_note` y `wardrobe_continuity_note` a todos los planos |
| 2 | **Location/set continuity** | Si bundle tiene `LocationDirectorNotes`, propaga `set_continuity_note` y `location_reference_id` a todos los planos |
| 3 | **Lighting/atmosphere continuity** | Si bundle tiene `LocationDirectorNotes` con `lighting`/`atmosphere`, propaga `lighting_continuity_note` y `atmosphere_continuity_note` |
| 4 | **Prop must_appear** | Si `prop.must_appear` y no existe INSERT, lo añade como MUST_HAVE. Si ya existe, lo eleva a MUST_HAVE |
| 5 | **Extreme close-up request** | Si `shot.shot_type_override == "extreme_close_up"` y no existe ECU, lo añade como MUST_HAVE REACTION |
| 6 | **Coverage pattern override** | Si `cinematic_grammar_overrides["coverage_pattern"]` existe, sobreescribe el patrón ANTES de construir planos |
| 7 | **Reference mode override** | Si `cinematic_grammar_overrides["reference_mode"]` existe, propaga a todos los planos |
| 8 | **Visual raccord block** | Si `prompt_blocks.visual_raccord_block` existe, propaga `visual_raccord_note` |
| 9 | **Prioridad estricta** | Override manual > secuencia/plano > Visual Bible > análisis > heurística. Wardrobe de override manual gana a heurística |
| 10 | **Voice draft sin revisión** | No afecta al plan (`voice_drafts_pending_review` se reporta pero no se aplica) |
| 11 | **Voice draft revisado** | Si se convierte en `PropDirectorNotes` o similar con `reviewed_by_user=True`, sí afecta |

## Ejemplo Marta con Director Notes

Con bundle que incluye:
- `CharacterDirectorNotes`: Marta — chaqueta oscura, vaqueros, botas
- `LocationDirectorNotes`: Casa abandonada — oscuridad, linterna como luz motriz, atmósfera polvorienta
- `PropDirectorNotes`: Linterna — must_appear=True

Resultado:
- ✅ Mínimo 8 planos
- ✅ `character_continuity_note` = "Marta must remain visually consistent across all shots per Director Notes."
- ✅ `wardrobe_continuity_note` = "Per Director Notes: Chaqueta oscura, vaqueros, botas."
- ✅ `set_continuity_note` = "Per Director Notes: Casa abandonada."
- ✅ `location_reference_id` = "casa_abandonada"
- ✅ `lighting_continuity_note` = "Per Director Notes: Oscuridad total, solo linterna como luz motriz."
- ✅ `atmosphere_continuity_note` = "Per Director Notes: silencioso, polvoriento, opresivo."
- ✅ INSERT elevado a MUST_HAVE (por must_appear)
- ✅ THREAT conservado como MUST_HAVE
- ✅ DIALOGUE conservado
- ✅ POV conservado
- ✅ REACTION conservado

## Tests

| Suite | Tests | Resultado |
|---|---|---|
| `test_director_notes_schema.py` | 32 | ✅ 32 passed |
| `test_director_notes_resolver_service.py` | 28 | ✅ 28 passed |
| `test_cinematic_shot_grammar_director_notes_integration.py` | 30 | ✅ 30 passed |
| `test_cinematic_grammar_schema.py` | 14 | ✅ 14 passed |
| `test_cinematic_shot_grammar_engine.py` | 39 | ✅ 39 passed |
| `test_storyboard_*.py` (regresión) | 190 | ✅ 190 passed (sin cambios) |

**Total: 333 tests, 0 fallos, 0 regresiones.**

## Lo que queda pendiente

- Integración con prompt generation real (DIRECTOR.NOTES.2C)
- Integración con Visual Bible / Character Bible / Set Bible (DIRECTOR.NOTES.2C)
- UI en Storyboard Builder (DIRECTOR.NOTES.2D)
- Trazabilidad en ShotTracePanel (DIRECTOR.NOTES.2E)
- Persistencia con tablas dedicadas (fase posterior)
- Grabación y transcripción de voz real (fase posterior)

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Director Notes sobreescribe heurísticas útiles | Prioridad estricta: solo override manual gana a todo |
| Prop must_appear duplica inserts | Se eleva el existente en lugar de añadir duplicado |
| ECU siempre se añade aunque no tenga sentido dramático | Se añade solo si `shot_type_override` lo pide explícitamente |
| Voice drafts sin revisión se cuelan en el plan | `reviewed_by_user=False` bloquea aplicación |
| Bundle vacío o None rompe el motor | Guard condition temprano: si no hay DN, `return shots` sin cambios |
| Tests existentes se rompen por nuevo campo en Request | Campo opcional con default None; 53 tests existentes pasan sin cambios |

## GO / NO-GO

**GO** para STORYBOARD.DIRECTOR.NOTES.2C (prompt generation + Visual/Character/Set Bible).

Integración completa, stateless, testable, sin tocar frontend, sin modificar comportamiento actual del storyboard. 333 tests pasan sin regresiones.
