# CHARACTER.BIBLE.2C — Integración CharacterBibleResolver con CinematicShotGrammarEngine

Fecha: 2026-05-26

## Archivos

| Archivo | Acción |
|---|---|
| `src/schemas/cinematic_grammar_schema.py` | **MODIFICADO** — import `CharacterBibleResolveResult`, 4 campos nuevos en `CinematicShotSpec`, 1 campo en `CinematicGrammarRequest`, 1 campo en `CinematicGrammarResult` |
| `src/services/cinematic_shot_grammar_engine.py` | **MODIFICADO** — nuevo método `_apply_character_bible`, pipeline reordenado, `build_ordered_shot_plan` y `plan_scene_coverage` extendidos |
| `tests/unit/test_cinematic_shot_grammar_character_bible_integration.py` | **CREADO** — 30 tests |
| `docs/validation/storyboard_character_bible_cinematic_integration_20260526.md` | **CREADO** — reporte |

## Nuevos campos en schema

### `CinematicShotSpec`
| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `approved_reference_asset_ids` | `list[str]` | `[]` | Asset IDs de referencias aprobadas |
| `look_variant_applied` | `str \| None` | `None` | ID del look variant aplicado |
| `character_lock_applied` | `str \| None` | `None` | `"character_bible"` o `"director_notes"` |
| `character_negative_constraints` | `str \| None` | `None` | Restricciones negativas compiladas |

### `CinematicGrammarRequest`
| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `character_bible_results` | `list[CharacterBibleResolveResult] \| None` | `None` | Resultados del CharacterBibleResolver |

### `CinematicGrammarResult`
| Campo | Tipo | Default | Descripción |
|---|---|---|---|
| `character_bible_metadata` | `dict[str, Any]` | `{}` | Metadatos de resolución (resolved/unresolved, look variants) |

## Pipeline (orden de aplicación)

1. `_apply_prompt_intents` → intenciones narrativas por tipo de plano
2. `apply_continuity_notes` → reglas de continuidad base
3. `_apply_visual_raccord` → raccord visual heurístico (casa abandonada, linterna)
4. **`_apply_character_bible`** → **NUEVO**: referencias aprobadas de personaje/look
5. `_apply_director_notes` → override creativo (gana sobre Character Bible)
6. `assign_priorities` → prioridades finales

## Reglas implementadas

### `_apply_character_bible`
- Solo procesa resultados con `primary_reference` (resolved)
- Propaga a todos los planos: `approved_reference_asset_ids`, `look_variant_applied`, `character_lock_applied`
- Construye `character_continuity_note` combinado con `prompt_lock_block`
- Propaga `character_negative_constraints` y `unresolved_props`
- Personajes unresolved → se ignoran, no rompen el plan

### Director Notes override
- `_apply_director_notes` corre DESPUÉS de `_apply_character_bible`
- Si DN tiene character data (`char_note` o `wardrobe`), marca `character_lock_applied = "director_notes"`
- CB llena gaps que DN no cubre (approved_reference_asset_ids, look_variant_applied)

### Plan-level metadata (`CinematicGrammarResult.character_bible_metadata`)
```json
{
  "character_count": 1,
  "resolved_characters": ["char_marta"],
  "unresolved_characters": [],
  "look_variants_applied": ["look_night_entrance"],
  "character_bible_active": true
}
```

## Tests: 30 tests, 0 fallos

| Categoría | Tests |
|---|---|
| `TestCharacterBibleIntegration` | 14 |
| `TestCharacterBibleAndDirectorNotesInteraction` | 3 |
| `TestNoAbsolutePaths` | 3 |
| `TestMultipleCharacters` | 3 |
| `TestCharacterBibleWithPriority` | 2 |
| `TestEdgeCases` | 2 |

Validaciones clave:
- ✅ Referencia aprobada se propaga a todos los planos del personaje
- ✅ `look_variant_applied` aparece en metadata de planos
- ✅ `character_lock_applied` = `"character_bible"` cuando CB resuelve
- ✅ `approved_reference_asset_ids` aparece en cada plano
- ✅ Negative constraints se propagan a `character_negative_constraints`
- ✅ Unresolved characters no rompen el plan; se registran en metadata
- ✅ Director Notes gana sobre CB: `character_lock_applied = "director_notes"`, wardrobe overridea
- ✅ CB llena gaps que DN no cubre (approved_reference_asset_ids)
- ✅ Marta + CB genera mínimo 8 planos, conserva threat/dialogue/POV/insert/reaction
- ✅ `character_bible_metadata` incluye resolved/unresolved/look_variants
- ✅ Empty `character_bible_results` no rompe nada
- ✅ `character_bible_results=None` no rompe nada
- ✅ Múltiples personajes resueltos
- ✅ Mixto resolved + unresolved
- ✅ No se exponen `/opt/`, `/mnt/`, `C:`, `storage_path`, `canonical_path`

## Regresiones

| Suite | Tests | Resultado |
|---|---|---|
| CHARACTER.BIBLE.2A schema | 42 | ✅ 0 fallos |
| CHARACTER.BIBLE.2B resolver | 46 | ✅ 0 fallos |
| CHARACTER.BIBLE.2C integración | 30 | ✅ 0 fallos |
| DIRECTOR.NOTES.2A schema | 32 | ✅ 0 fallos |
| DIRECTOR.NOTES.2A resolver | 28 | ✅ 0 fallos |
| CinematicShotGrammarEngine base | 39 | ✅ 0 fallos |
| DIRECTOR.NOTES.2B integración | 30 | ✅ 0 fallos |
| **Total** | **247** | **✅ 0 fallos, 0 regresiones** |

## Ejemplo Marta con Character Bible

Dado:
- `CharacterBibleEntry` con look_variant `look_night_entrance`, approved_ref `asset_marta_face_v2`, wardrobe_notes "Jeans oscuros, camiseta negra, chaqueta vaquera"
- Escena de suspense con linterna, silencio, crujido, sombra

Resultado:
- `Shot[0].approved_reference_asset_ids` = `["asset_marta_face_v2", "asset_marta_full_body", "asset_marta_wardrobe_night"]`
- `Shot[0].look_variant_applied` = `"look_night_entrance"`
- `Shot[0].character_lock_applied` = `"character_bible"`
- `Shot[0].character_continuity_note` incluye "Personaje: Marta | referencia_principal: /api/assets/marta_face_v2.png | vestuario: Jeans oscuros..."
- `Shot[0].character_negative_constraints` incluye "Personaje Marta: evitar No cambiar a ropa clara"
- `CinematicGrammarResult.character_bible_metadata.resolved_characters` = `["char_marta"]`
- 8 planos generados con POV, INSERT/SOUND_DETAIL, REACTION, THREAT_INDICATOR, ESTABLISHING, CLOSING

## Riesgos

| Riesgo | Mitigación |
|---|---|
| CB llena campos que DN podría querer dejar vacíos | CB corre antes que DN; DN decide si sobrescribe |
| `character_lock_applied` no se actualiza si DN no tiene character data | Solo se marca "director_notes" si DN aporta char_note o wardrobe |
| Múltiples personajes en un shot → nota combinada larga | La nota combina todos los personajes con ";"; la heurística visual_raccord sigue usando el primer character |
| `approved_reference_asset_ids` puede ser `[]` si no hay asset_ids en trace_metadata | Validado en test: empty list no rompe serialización |

## GO / NO-GO

**GO** para CHARACTER.BIBLE.2D (API REST + subida de assets aprobados).

Integración completa de Character Bible con CinematicShotGrammarEngine. Pipeline reordenado correctamente (prompt → continuity → raccord → **CB** → **DN**). 30 tests de integración, 0 regresiones sobre 247 tests. Sin frontend, sin DB, sin ComfyUI. Relación CB/DN documentada y testeada.
