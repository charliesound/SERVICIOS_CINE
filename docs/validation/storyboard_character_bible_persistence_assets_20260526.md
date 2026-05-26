# CHARACTER.BIBLE.2E — Persistencia real + asset upload controlado

**Fecha:** 2026-05-26  
**Rama:** cid-dev-stable-storyboard-character-bible-api-base-20260526  
**Commit base:** 51cb73b  
**Cobertura:** Backend exclusivamente (sin frontend, sin ComfyUI, sin storyboard)

---

## Persistencia elegida

**File-backed JSON** en `data/character_bible/{project_id}.json`.

| Opción | Decisión |
|--------|----------|
| Nueva tabla SQL | ❌ Descartado — require migración, overhead alto para MVP |
| `metadata_json` en Project | ❌ Project no tiene columna JSON |
| `metadata_json` en MediaAsset | ❌ No escala, semántica incorrecta |
| **File-backed JSON** | **✅ Elegido** |

**Razones:**
- Riesgo cero de migración (no toca esquema DB)
- Sobrevive a reinicio del servicio
- Sigue el patrón existente (`data/solutions_registry.json`)
- Fácil de inspeccionar/depurar
- Escritura atómica (`.tmp` → `.json`)
- Puede migrarse a DB en fase posterior sin romper API

**Estructura de archivo:**
```
data/character_bible/{project_id}.json
```
Contenido: `dict[character_id, CharacterBibleEntry.model_dump()]`

---

## Archivos modificados/creados

| Archivo | Acción | Cambio |
|---------|--------|--------|
| `src/services/character_bible_service.py` | Modificado | +125/-53: persistencia file-backed, métodos write pasan a async, `reset()` para tests |
| `src/routes/character_bible_routes.py` | Modificado | +30/-2: `await` en métodos async, validación `MediaAsset` en `add_reference` |
| `tests/unit/test_character_bible_service.py` | Modificado | +112/-82: tests adaptados a async + `tmp_path` para data_dir |
| `tests/unit/test_character_bible_routes.py` | Modificado | +38/-1: `_FakeDb.media_asset_exists`, `override_db_with_media`, test asset inválido |
| `tests/unit/test_character_bible_persistence.py` | **Nuevo** | 12 tests: save/reload, variants, references, version, projects, atomic write |

---

## Endpoints afectados

| Endpoint | Cambio |
|----------|--------|
| `PUT /api/projects/{id}/character-bible/{char_id}` | Ahora `await`, persiste a disco |
| `POST .../look-variants` | Ahora `await`, persiste a disco |
| `POST .../references` | **Nuevo**: valida `asset_id` contra `MediaAsset` real en DB, auto-popula `asset_api_url` y `asset_file_name` |

Endpoints GET y POST resolve/trace no cambiaron (solo lectura).

---

## Seguridad

### Validación de tenant/project
- Endpoints existentes verifican `Project.organization_id` vía `_get_project_or_404()`

### Validación de media_asset_id en `add_reference`
Consulta en DB:
```sql
SELECT * FROM media_assets
WHERE id = :asset_id
  AND project_id = :project_id
  AND organization_id = :org_id
```
Si no existe o no pertenece al proyecto: `400 Bad Request`.

### Auto-populado controlado
- Si `asset_api_url` no se provee → `/api/media-assets/{asset.id}/download`
- Si `asset_file_name` no se provee → `media_asset.file_name`
- Nunca se exponen: `canonical_path`, `storage_path`, `mount_path`, `/opt/`, `/mnt/`, `C:\`

### Sin rutas absolutas
- `_sanitize_asset_url()` en service bloquea `/opt/`, `/mnt/`, `C:`, `storage_path`, `canonical_path`
- El endpoint `/references` en routes verifica path traversal (`/`, `\\`, `..`)
- Tests `test_no_absolute_paths_in_response` y `test_add_reference_sanitizes_absolute_path`

---

## Tests

### Suite completa de Character Bible: 114 tests

| Archivo | Tests | Nuevos |
|---------|-------|--------|
| `test_character_bible_schema.py` | 42 | 0 |
| `test_character_bible_service.py` | 29 | +12 (vs 17 anteriores) |
| `test_character_bible_routes.py` | 18 | +1 (test asset inválido) |
| `test_character_bible_persistence.py` | **12** | 12 (nuevo) |
| `test_character_bible_openapi_routes.py` | 13 | 0 |

### Tests de persistencia específicos
- `test_save_and_reload_entry` — guarda, crea nuevo servicio, verifica carga
- `test_persist_look_variant` — persistencia de variantes de look
- `test_persist_reference` — persistencia de assets aprobados
- `test_persist_update_increments_version` — versionado sobrevive reload
- `test_project_isolation_across_reload` — aislamiento entre proyectos
- `test_json_file_is_written` — archivo JSON válido en disco
- `test_multiple_projects_multiple_files` — un archivo por proyecto
- `test_empty_data_dir_does_not_crash` — directorio vacío no falla
- `test_corrupt_file_does_not_crash` — archivo corrupto no impide carga
- `test_atomic_write_leaves_valid_file` — escritura atómica no deja `.tmp`
- `test_reload_with_no_writes_starts_empty` — sin escrituras = store vacío

### Validación de asset linking
- `test_add_reference_invalid_media_asset` — asset_id inexistente → 400
- `test_add_reference_empty_asset_id` → 400
- `test_add_reference_invalid_path_in_asset_id` → 400

### Resultados globales
```
1016 passed in tests/unit/ (1558 warnings, 0 failures)
```

---

## Limitaciones

1. **Sin tabla DB dedicada** — la persistencia file-backed es MVP. Si el volumen de datos crece o se requiere query compleja, migrar a tabla SQL.
2. **Sin upload binario** — el upload de archivos aprobados se delega al sistema existente de `MediaAsset`. `add_reference` solo vincula assets ya indexados en el proyecto.
3. **Sin borrado** — no hay endpoint `DELETE` para entries, look variants ni references (queda para fase posterior).
4. **Sin WebSocket / real-time** — cambios se reflejan en disco, pero no hay notificación push.
5. **Colisiones de datos** — La escritura file-backed usa `asyncio.Lock()` pero comparte el singleton con todos los workers. En deployments multi-worker, cada worker tiene su propia copia en memoria. Para multi-worker, se necesitaría DB centralizada.

---

## Pendiente para fases futuras

- CHARACTER.BIBLE.2F: Migrar a tabla SQL (`project_character_bible_entries`, `character_look_variants`, `character_approved_references`)
- CHARACTER.BIBLE.2G: Upload binario de approved reference assets con validación de formato/tamaño
- CHARACTER.BIBLE.2H: UI en Storyboard Builder (pestaña "Personajes / Character Bible")
- CHARACTER.BIBLE.2I: Endpoint DELETE para entries y sub-recursos
- Soporte multi-worker con Redis/DB compartida

---

## GO/NO-GO para commit

### Criterios GO
| Criterio | Estado |
|----------|--------|
| Persistencia real (sobrevive reinicio) | ✅ File-backed JSON |
| MediaAsset linking con validación | ✅ Consulta DB, filtro tenant/project |
| Sin rutas absolutas en respuestas | ✅ `_sanitize_asset_url`, route validation |
| Tests: save/reload, variants, references | ✅ 12 tests de persistencia |
| Tests: asset inexistente → 400 | ✅ `test_add_reference_invalid_media_asset` |
| Sin romper API actual | ✅ 1016 tests pasan |
| Sin tocar frontend/ComfyUI/storyboard | ✅ Solo backend |
| Sin commits de secretos/artefactos runtime | ✅ `data/` en .gitignore |
| OpenAPI expone todas las rutas | ✅ 13 tests OpenAPI pasan |

### Decisión: **GO** ✅

El MVP de persistencia file-backed + validación de media_asset_id cumple todos los criterios. La API es idéntica hacia fuera, los endpoints existentes no cambian su comportamiento observable salvo que ahora persisten datos.
