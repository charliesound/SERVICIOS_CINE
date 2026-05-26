# CHARACTER.BIBLE.2B — CharacterBibleResolver

Fecha: 2026-05-26

## Archivos

| Archivo | Acción | Líneas |
|---|---|---|
| `src/services/character_bible_resolver_service.py` | **CREADO** | ~250 |
| `src/schemas/character_bible_schema.py` | **MODIFICADO** (añadido `trace_metadata` a `CharacterBibleResolveResult`) | +1 |
| `tests/unit/test_character_bible_resolver_service.py` | **CREADO** | ~600 |
| `docs/validation/storyboard_character_bible_resolver_base_20260526.md` | **CREADO** | — |

## API pública

### `CharacterBibleResolver`

| Método | Entrada | Salida |
|---|---|---|
| `resolve_character_references_for_shot(...)` | `bible_entries`, `shot_number`, `sequence_id?`, `character_ids_in_shot?`, `director_notes_result?` | `list[CharacterBibleResolveResult]` |
| `resolve_character_references_for_sequence(...)` | `bible_entries`, `sequence_id`, `character_ids_in_sequence?` | `list[CharacterBibleResolveResult]` |
| `select_look_variant(entry, request)` | `CharacterBibleEntry`, `CharacterBibleResolveRequest` | `CharacterLookVariant \| None` |
| `select_approved_reference(entry, look)` | `CharacterBibleEntry`, `CharacterLookVariant?` | `(ApprovedReferenceAsset?, list[ApprovedReferenceAsset])` |
| `build_character_lock_block(entry, look, primary, secondary)` | — | `str \| None` |
| `build_negative_constraints(entry, look)` | — | `str \| None` |
| `build_trace_metadata(entry, look, primary, secondary, ...)` | — | `dict[str, Any]` |

## Output del resolver

Cada `CharacterBibleResolveResult` contiene:

| Campo | Descripción |
|---|---|
| `character_id` | ID del personaje |
| `character_name` | Nombre |
| `resolved_look` | Look variant aplicado (o None) |
| `primary_reference` | ApprovedReferenceAsset principal |
| `secondary_references` | Referencias secundarias |
| `prompt_lock_block` | Bloque de texto para prompt (rostro, ropa, pelo, props) |
| `prompt_negative_block` | Restricciones negativas para prompt |
| `continuity_block` | Reglas de continuidad |
| `applied_reference_ids` | Lista de IDs de referencias aplicadas |
| `unresolved_props` | Props sin resolver |
| `trace_metadata` | Metadatos de trazabilidad |

## Reglas implementadas

### Selección de look variant (orden de precedencia)
1. `look_id` explícito en request
2. `narrative_phase` coincide
3. `scene_id` está en `scene_ids` del variant
4. `default_look_id` del entry
5. Primer variant disponible
6. None si no hay variants

### Selección de referencia aprobada
1. Las del look variant tienen prioridad sobre las del entry
2. Si hay `is_primary=True`, esa es la referencia principal
3. Sin primary flag, se ordena por `sort_order` y se toma la primera
4. Si no hay references, primary=None

### Director Notes override
- Si `director_notes_result` tiene `character_lock_block`, se usa ese en lugar del del Bible
- Si tiene `prompt_negative_constraints`, se concatenan con los del Bible
- Si tiene `continuity_prompt_block`, se usa ese en lugar del del Bible
- `trace_metadata` registra `director_notes_override_applied=True` y lista de campos overrideados

### Personaje sin referencia
- `entry` no encontrado → `unresolved_result` con confidence=0.0, trace.unresolved=True

## Seguridad

- `asset_api_url` siempre formato `/api/...` — nunca rutas absolutas
- Ningún bloque de texto contiene `/opt/`, `/mnt/`, `C:`, `storage_path`, `canonical_path`
- Todo test de paths absolutos pasa

## Tests: 46 tests, 0 fallos

| Categoría | Tests |
|---|---|
| `TestResolveApprovedReference` | 3 |
| `TestSelectLookVariant` | 5 |
| `TestFallbackToBaseLook` | 2 |
| `TestUnresolvedCharacter` | 2 |
| `TestCharacterLockBlock` | 3 |
| `TestNegativeConstraints` | 3 |
| `TestContinuityBlock` | 1 |
| `TestTraceMetadata` | 6 |
| `TestResolveForShot` | 3 |
| `TestResolveForSequence` | 2 |
| `TestResolutionResultFields` | 4 |
| `TestSelectApprovedReference` | 3 |
| `TestDirectorNotesOverride` | 4 |
| `TestNoAbsolutePaths` | 5 |

Validaciones clave:
- ✅ Resuelve referencia aprobada principal
- ✅ Resuelve look_variant exacto
- ✅ Fallback a look base (default_look_id > primer variant)
- ✅ Personaje sin bible → unresolved
- ✅ character_lock_block incluye rostro/ropa/pelo/props
- ✅ negative_constraints se propagan desde look + entry + scene_ids
- ✅ continuity_block incluye reglas + vestuario + pelo
- ✅ trace_metadata incluye approved_reference_asset_ids
- ✅ trace_metadata incluye character_reference_ids_used
- ✅ trace_metadata incluye look_variant_applied
- ✅ trace_metadata incluye bible_version
- ✅ trace_metadata incluye confidence
- ✅ No expone /opt, /mnt, C:, storage_path, canonical_path
- ✅ Director Notes override registrado en trace_metadata
- ✅ Director Notes character_lock_block reemplaza Bible
- ✅ Director Notes negatives se concatenan
- ✅ Múltiples personajes en un shot
- ✅ Sin bible_entries pero con character_ids → unresolved

## Regresiones

- 42 tests de CHARACTER.BIBLE.2A → 42 passed
- 46 tests de CHARACTER.BIBLE.2B → 46 passed
- 32 tests de DIRECTOR.NOTES.2A schema → 32 passed
- 28 tests de DIRECTOR.NOTES.2A resolver → 28 passed
- 39 tests de engine → 39 passed
- 30 tests de DN integration → 30 passed
- **Total: 217 tests, 0 fallos, 0 regresiones**

## Lo que queda pendiente

- **CHARACTER.BIBLE.2C**: Integración con CinematicShotGrammarEngine (llamar al resolver desde `_apply_director_notes` o nuevo hook), integración con prompt generation, Visual Bible, Set Bible.
- **CHARACTER.BIBLE.2D**: API REST + subida de assets aprobados.
- **CHARACTER.BIBLE.2E**: UI en Storyboard Builder (pestaña "Biblia de personajes") + trazabilidad en ShotTracePanel.
- **CHARACTER.BIBLE.2F**: Persistencia en DB con tablas dedicadas.

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Múltiples look variants válidas para un shot | Orden de precedencia explícito (look_id > narrative_phase > scene_id > default > first) |
| Director Notes y Character Bible contradictorios | Director Notes siempre gana, trace registra override |
| Props en `key_props` sin `prop_reference` asociado | `unresolved_props` enumera explícitamente los no resueltos |
| `confidence=0` para personajes sin bible | El planificador debe decidir si genera shot aún sin referencia |
| Scene_id matching impreciso (una escena puede abarcar múltiples fases) | scene_id tiene menor prioridad que narrative_phase; el usuario puede matchear explícitamente |

## GO / NO-GO

**GO** para CHARACTER.BIBLE.2C (integración con CinematicShotGrammarEngine + prompt generation).

Resolver completo, 46 tests, 0 regresiones sobre 217 tests existentes. Sin frontend, sin DB, sin tocar ComfyUI. Arquitectura segura (sin rutas absolutas). Override de Director Notes contemplado y testeado.
