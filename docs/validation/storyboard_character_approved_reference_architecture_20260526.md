# CHARACTER.APPROVED.REFERENCE.1 — Character Bible / Approved Reference Assets

Fecha: 2026-05-26

## Diagnóstico

Cada personaje del storyboard debe tener una o varias imágenes aprobadas como referencia visual oficial. El sistema actual solo soporta referencias textuales (`visual_references: list[str]` en `CharacterDirectorNotes`). No hay trazabilidad por shot de qué asset visual se usó, ni soporte para variantes por look narrativo, ni bloqueo de prompt hacia ComfyUI que garantice consistencia.

## Propuesta técnica

### Arquitectura en 3 capas

```
┌─────────────────────────────────────────────────────────┐
│  Capa 1: Character Bible (schemas + assets)             │
│  - ApproveReferenceAsset                               │
│  - CharacterLookVariant (por fase narrativa)            │
│  - CharacterBibleEntry (personaje completo)             │
├─────────────────────────────────────────────────────────┤
│  Capa 2: Resolver (CharacterBibleResolver)              │
│  - Resuelve qué look aplicar por shot/scene             │
│  - Genera prompt_lock_block para ComfyUI                │
│  - Genera continuity_block para shot metadata           │
├─────────────────────────────────────────────────────────┤
│  Capa 3: Integración                                    │
│  - DirectorNotes → selecciona look_variant              │
│  - CinematicShotGrammarEngine → recibe applied_refs     │
│  - Prompt generation → character_lock_block con assets  │
│  - ShotTracePanel → muestra qué reference se usó        │
└─────────────────────────────────────────────────────────┘
```

## Schemas (CHARACTER.BIBLE.2A)

Archivo: `src/schemas/character_bible_schema.py` — 7 modelos, 1 enum, implementado y testeado.

| Modelo | Campos clave |
|---|---|
| `ApprovedAssetType` | `face_sheet`, `wardrobe_sheet`, `full_body`, `hair_makeup`, `prop_reference`, `expression_sheet`, `pose_sheet`, `action_still`, `mood_board`, `concept_art` |
| `ApprovedReferenceAsset` | `asset_id`, `asset_type`, `asset_api_url`, `asset_file_name`, `reference_id`, `description`, `is_primary`, `sort_order`, `approved_by_user_id`, `approved_at` |
| `CharacterLookVariant` | `look_id`, `look_name`, `narrative_phase`, `approved_references`, `wardrobe_notes`, `hair_makeup_notes`, `key_props`, `continuity_rules`, `negative_constraints`, `scene_ids` |
| `CharacterBibleEntry` | `character_id`, `project_id`, `character_name`, `approved_reference_asset_id`, `secondary_reference_asset_ids`, `look_variants`, `default_look_id`, `wardrobe_notes`, `hair_makeup_notes`, `key_props`, `continuity_rules`, `negative_constraints`, `notes`, `version` |
| `ShotCharacterReference` | `project_id`, `shot_number`, `sequence_id`, `character_id`, `applied_look_id`, `applied_reference_asset_ids`, `wardrobe_confirmed`, `hair_makeup_confirmed`, `props_confirmed`, `continuity_verified`, `tracking_note` |
| `CharacterBibleResolveRequest` | `project_id`, `character_id`, `look_id`, `narrative_phase`, `scene_id` |
| `CharacterBibleResolveResult` | `project_id`, `character_id`, `character_name`, `resolved_look`, `primary_reference`, `secondary_references`, `prompt_lock_block`, `prompt_negative_block`, `continuity_block`, `applied_reference_ids`, `unresolved_props` |

### Seguridad: No expone rutas absolutas

- `asset_api_url` usa formato `/api/...` — nunca rutas de filesystem
- `asset_file_name` es solo nombre lógico para display
- `reference_id` es identificador externo (ej. `ref_marta_001`)
- `approved_by_user_id` es ID de usuario, no nombre
- `asset_id` es el identificador interno para todas las operaciones

## Resolver

Archivo a crear: `src/services/character_bible_resolver_service.py`

| Método | Propósito |
|---|---|
| `resolve_for_scene(project_id, character_id, scene_id)` | Elige el look por fase narrativa de la escena |
| `resolve_for_shot(project_id, character_id, scene_id, shot_number)` | Elige el look y devuelve assets concretos |
| `build_character_lock_block(entry, look)` | Genera bloque de prompt para ComfyUI con assets |
| `build_continuity_block(entry, look, previous_shot_ref)` | Verifica continuidad entre shots |
| `verify_shot_continuity(shot_refs)` | Valida que todos los shots usen el mismo look |

### Lógica de resolución de look

```
1. Si shot_number tiene CharacterDirectorNotes con shot_type_override → usar look asociado
2. Si scene_id está en look_variant.scene_ids → usar ese look
3. Si narrative_phase coincide → usar ese look
4. Si hay default_look_id → usar default
5. Sino → primer look_variant disponible
```

## Integración con Director Notes

`CharacterDirectorNotes` actual ya tiene:
- `visual_references: list[str]` — IDs de referencia (se mantiene)

En futura fase se añadirá:
- `bible_look_id: str | None` — look activo de Character Bible
- `approved_asset_ids: list[str]` — assets aprobados que sobreescriben la biblia

Prioridad:
1. Override manual en `ShotDirectorNotes`
2. `CharacterDirectorNotes.approved_asset_ids`
3. `CharacterBibleEntry` → look resuelto

## Integración con CinematicShotGrammarEngine

Añadir a `CinematicShotSpec` en futura fase:

```python
approved_reference_asset_ids: list[str] = Field(default_factory=list)
character_look_id: str | None = None
character_bible_version: int | None = None
```

El engine recibirá `character_bible_result: CharacterBibleResolveResult | None` y propagará:
- `approved_reference_asset_ids` a cada shot
- `character_look_id` desde el look resuelto
- `prompt_intent` con el bloque de continuidad

## Integración con prompt generation

Cada bloque de prompt actual (`character_lock_block`) se enriquece con:

```
Character lock: Marta
  Face reference: assets/marta_face_v2.png
  Wardrobe reference: assets/marta_wardrobe_night.png
  Hair: castaño largo recogido (asset: marta_hair_v2.png)
  Key props: linterna metálica negra (asset: linterna_ref.png)
  Continuity: same look across shots 1-8
  Negative: no cambiar peinado, no cambiar chaqueta
```

## Persistencia MVP (CHARACTER.BIBLE.2A)

**No se crean tablas nuevas.** El MVP de CHARACTER.BIBLE.2A es puramente schemas + tests:

- `CharacterBibleEntry`, `ShotCharacterReference`, `CharacterBibleResolveResult` se almacenan como JSON dentro de `metadata_json` del proyecto o shot según corresponda.
- Tablas dedicadas (`character_bible_entries`, `character_look_variants`, `approved_reference_assets`) quedan para fase posterior (CHARACTER.BIBLE.2D+).
- El resolver (`CharacterBibleResolver` en 2B/C) trabajará sobre estructuras en memoria obtenidas desde `metadata_json`.

### Campos de trazabilidad por shot

Cada `ShotCharacterReference` almacena en `metadata_json` del shot:

```json
{
  "character_reference_ids_used": ["asset_marta_face_v2", "asset_marta_wardrobe_night"],
  "approved_reference_asset_ids": ["asset_marta_face_v2", "asset_marta_wardrobe_night"],
  "look_variant_applied": "look_night_entrance",
  "character_id": "char_marta",
  "wardrobe_confirmed": true,
  "continuity_verified": true
}
```

Estos campos son consumidos por:
- `ShotTracePanel` → muestra qué references se usaron por shot
- Prompt generation → construye `character_lock_block`
- ComfyUI → carga los assets correctos

## Integración con Visual Bible / Set Bible

La Character Bible es hermana de la Visual Bible y Set Bible:

| Biblia | Contenido | Uso |
|---|---|---|
| Character Bible | Assets por personaje/look | `character_lock_block` |
| Visual Bible | Estilo visual global, paleta, luz | `visual_raccord_block` |
| Set Bible | Decorados, props de atrezo | `location_lock_block`, `prop_lock_block` |

Todas comparten el mismo patrón: schema → resolver → bloque de prompt → trazabilidad por shot.

## Metadata por shot

Cada `ShotCharacterReference` se almacena en `metadata_json` del shot:

```json
{
  "character_references": [
    {
      "character_id": "char_marta",
      "applied_look_id": "look_night_entrance",
      "applied_reference_asset_ids": [
        "asset_marta_face_v2",
        "asset_marta_wardrobe_night",
        "asset_linterna_ref"
      ],
      "wardrobe_confirmed": true,
      "hair_makeup_confirmed": true,
      "props_confirmed": true,
      "continuity_verified": true
    }
  ]
}
```

Esta metadata es consumida por:
- `ShotTracePanel` → muestra qué references se usaron
- Prompt generation → construye `character_lock_block`
- ComfyUI → carga los assets correctos

## Endpoints necesarios

Futura API REST:

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/api/character-bible/entry` | Crear/actualizar entrada de personaje |
| GET | `/api/character-bible/entry/{character_id}` | Obtener entrada + looks |
| POST | `/api/character-bible/look` | Añadir variante de look |
| PUT | `/api/character-bible/look/{look_id}` | Actualizar look |
| POST | `/api/character-bible/asset` | Subir/subir reference asset |
| DELETE | `/api/character-bible/asset/{asset_id}` | Eliminar asset |
| POST | `/api/character-bible/resolve` | Resolver look para shot/scene |
| GET | `/api/projects/{project_id}/characters/{char_id}/references` | References por shot del proyecto |

## Archivos a crear/modificar

| Archivo | Acción |
|---|---|
| `src/schemas/character_bible_schema.py` | Crear (ya creado) |
| `src/services/character_bible_resolver_service.py` | Crear en DIRECTOR.NOTES.2C |
| `src/schemas/cinematic_grammar_schema.py` | Modificar: añadir `approved_reference_asset_ids`, `character_look_id` a `CinematicShotSpec` |
| `src/services/cinematic_shot_grammar_engine.py` | Modificar: integrar `CharacterBibleResolveResult` |
| `src/routes/character_bible_routes.py` | Crear (cuando se implemente API) |
| `tests/unit/test_character_bible_schema.py` | Crear |
| `tests/unit/test_character_bible_resolver_service.py` | Crear |

## Roadmap de integración

| Fase | Alcance |
|---|---|
| **CHARACTER.BIBLE.2A** | Schemas + resolver backend-only (este documento + schema ya creado) |
| **CHARACTER.BIBLE.2B** | Integración con CinematicShotGrammarEngine + Director Notes |
| **CHARACTER.BIBLE.2C** | Integración con prompt generation + Visual Bible |
| **CHARACTER.BIBLE.2D** | API REST + subida de assets |
| **CHARACTER.BIBLE.2E** | UI en Storyboard Builder + ShotTracePanel |

Se integra de forma natural en el roadmap DIRECTOR.NOTES:
- DIRECTOR.NOTES.2C incluye CHARACTER.BIBLE.2B + Visual Bible + Set Bible

## Tests propuestos

| Test | Validación |
|---|---|
| `test_resolve_look_by_narrative_phase` | Elige look correcto según fase narrativa |
| `test_resolve_look_by_scene_id` | Elige look por scene_id explícito |
| `test_resolve_default_look` | Usa default_look_id si no hay match |
| `test_primary_reference_asset` | asset is_primary=True se devuelve como primary |
| `test_character_lock_block_generated` | prompt_lock_block contiene assets + wardrobe |
| `test_negative_block_generated` | prompt_negative_block con forbidden_changes |
| `test_continuity_block_generated` | continuity_block con continuity_rules |
| `test_multiple_looks_per_character` | Varios looks, cada uno con sus assets |
| `test_roundtrip_serialize_bible_entry` | CharacterBibleEntry serializa/deserializa |
| `test_shot_reference_tracks_applied_assets` | ShotCharacterReference registra qué assets se usaron |
| `test_unresolved_props_reported` | Props sin asset reference aparecen en unresolved_props |
| `test_look_variant_assigns_scenes` | scene_ids asigna look a escenas concretas |

## GO / NO-GO

**GO** para CHARACTER.BIBLE.2A (schemas + resolver).

El diseño está completo: 7 modelos, 7 endpoints propuestos, integración clara con Director Notes, CinematicShotGrammarEngine, prompt generation y ShotTracePanel. No toca frontend, no modifica funcionamiento actual, no requiere tablas nuevas para MVP (JSON/metadata_json).

**NO-GO** si se intenta implementar subida de assets real, generación de prompts ComfyUI, o persistencia con tablas dedicadas antes de validar el MVP del resolver.
