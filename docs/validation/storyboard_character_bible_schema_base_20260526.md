# CHARACTER.BIBLE.2A — Character Bible schemas base

Fecha: 2026-05-26

## Archivos

| Archivo | Tipo | Líneas |
|---|---|---|
| `src/schemas/character_bible_schema.py` | Schemas | 115 |
| `tests/unit/test_character_bible_schema.py` | Tests | 310 |
| `docs/validation/storyboard_character_approved_reference_architecture_20260526.md` | Arquitectura actualizada | — |
| `docs/validation/storyboard_character_bible_schema_base_20260526.md` | Reporte de validación | — |

## Schemas implementados (7 modelos + 1 enum)

### Enum
`ApprovedAssetType`: face_sheet, wardrobe_sheet, full_body, hair_makeup, prop_reference, expression_sheet, pose_sheet, action_still, mood_board, concept_art

### Modelos
| Modelo | Propósito |
|---|---|
| `ApprovedReferenceAsset` | Asset individual aprobado (face, wardrobe, prop, etc.) con `asset_api_url`, `reference_id`, `approved_by_user_id` — sin rutas absolutas |
| `CharacterLookVariant` | Variante de look por fase narrativa con referencias, vestuario, props, reglas de continuidad y restricciones negativas |
| `CharacterBibleEntry` | Entrada completa de personaje con múltiples looks, referencias primarias/secundarias, versión |
| `ShotCharacterReference` | Trazabilidad por shot: qué look y qué assets se aplicaron, confirmaciones de continuidad |
| `CharacterBibleResolveRequest` | Request para resolver qué look aplicar |
| `CharacterBibleResolveResult` | Resultado resuelto con look, referencias, bloques de prompt, props no resueltos |

### Seguridad
- `asset_api_url` siempre en formato `/api/...` — nunca rutas absolutas de filesystem
- `approved_by_user_id` usa ID de usuario, no nombres
- `reference_id` es identificador externo lógico
- `asset_file_name` es solo nombre para display

## Tests: 42 tests, 0 fallos

| Categoría | Tests |
|---|---|
| `TestApprovedAssetType` | 6 |
| `TestApprovedReferenceAsset` | 7 |
| `TestCharacterLookVariant` | 7 |
| `TestCharacterBibleEntry` | 7 |
| `TestShotCharacterReference` | 6 |
| `TestCharacterBibleResolveRequest` | 2 |
| `TestCharacterBibleResolveResult` | 5 |
| `TestNoAbsolutePaths` | 3 |

Validaciones clave:
- ✅ Serialización roundtrip de todos los modelos
- ✅ Múltiples look variants por personaje
- ✅ ApprovedReferenceAsset con is_primary y secundarias
- ✅ CharacterBibleEntry con referencias aprobadas
- ✅ ShotCharacterReference con applied_reference_asset_ids
- ✅ negative_constraints y continuity_rules
- ✅ No expone rutas absolutas (asset_api_url, no file path)
- ✅ scene_ids asigna look a escenas concretas
- ✅ Unresolved props reportados en resolve result
- ✅ project_id en todos los modelos que lo requieren

## Lo que queda pendiente

- `CharacterBibleResolver` service (CHARACTER.BIBLE.2B)
- Integración con CinematicShotGrammarEngine (CHARACTER.BIBLE.2B)
- Integración con Director Notes (CHARACTER.BIBLE.2B)
- Integración con prompt generation + Visual Bible (CHARACTER.BIBLE.2C)
- API REST + subida de assets (CHARACTER.BIBLE.2D)
- UI en Storyboard Builder + ShotTracePanel (CHARACTER.BIBLE.2E)
- Tablas dedicadas (fase posterior; MVP usa JSON/metadata_json)

## Riesgos

| Riesgo | Mitigación |
|---|---|
| Assets sin API real apuntan a URL ficticia | `asset_api_url` es opcional; MVP valida solo el schema |
| Múltiples looks por personaje pueden confundir | `default_look_id` + `scene_ids` mantienen resolución predecible |
| approved_references duplicadas entre look variants | Cada variant tiene su propia lista; la resolución elige una sola |
| Progresión sin resolver lleva a props no trazados | `unresolved_props` se reporta explícitamente |

## GO / NO-GO

**GO** para CHARACTER.BIBLE.2B (resolver + integración con CinematicShotGrammarEngine y Director Notes).

Schemas completos, testeables, seguros (sin rutas absolutas), sin tablas nuevas, sin frontend. 42 tests pasan. Arquitectura documentada con trazabilidad por shot y roadmap de integración claro.
