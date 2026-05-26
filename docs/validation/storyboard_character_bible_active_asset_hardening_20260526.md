# CHARACTER.BIBLE.2E.1 — Active asset validation + concurrency documentation

**Fecha:** 2026-05-26
**Rama/commit base:** `cid-dev-stable-character-bible-persistence-assets-20260526` (994a31f)
**Auditoría posterior:** Post-CHARACTER.BIBLE.2E

---

## Objetivo

Microfase de hardening que aborda dos hallazgos de la auditoría:
1. **Active asset validation** — `add_reference` no verificaba que el `MediaAsset` estuviera activo.
2. **Concurrency documentation** — `asyncio.Lock` es correcto para single-worker pero no es seguro en multi-worker.

---

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `src/routes/character_bible_routes.py` | +13/−1: `MediaAsset.status == MediaAssetStatus.INDEXED` en WHERE, segunda query para diagnosticar asset inactivo vs inexistente |
| `tests/unit/test_character_bible_routes.py` | +20/−3: `_FakeMediaAsset.status`, `media_asset_active` en `_FakeDb`, override `override_db_with_inactive_media`, test `test_add_reference_inactive_media_asset` |
| `docs/validation/storyboard_character_bible_active_asset_hardening_20260526.md` | Reporte consolidado de validación y concurrencia |

---

## Comportamiento añadido

### `POST /api/projects/{project_id}/character-bible/{character_id}/references`

#### Consulta SQL actualizada

```python
# Antes (2E):
select(MediaAsset).where(
    MediaAsset.id == payload.asset_id,
    MediaAsset.project_id == project_id,
    MediaAsset.organization_id == str(tenant.organization_id),
)

# Después (2E.1):
select(MediaAsset).where(
    MediaAsset.id == payload.asset_id,
    MediaAsset.project_id == project_id,
    MediaAsset.organization_id == str(tenant.organization_id),
    MediaAsset.status == MediaAssetStatus.INDEXED,          # <-- nueva condición
)
```

#### Mensajes de error

| Escenario | Código | detail |
|-----------|--------|--------|
| `asset_id` no existe en ningún `MediaAsset` del proyecto | 400 | `asset_id does not match any media asset in this project` |
| `MediaAsset` existe pero su `status != MediaAssetStatus.INDEXED` | 400 | `media asset exists but is not active (status != indexed) in this project` |

#### Flujo de validación completo

1. `asset_id` vacío → 400
2. `asset_id` contiene path traversal → 400
3. `MediaAsset` no existe con mismo `project_id` + `organization_id` + `MediaAssetStatus.INDEXED`:
   - Si existe pero con status distinto → 400 (inactivo)
   - Si no existe → 400 (no match)
4. `MediaAsset` activo encontrado → auto-popula `asset_api_url` + `asset_file_name`
5. Servicio guarda referencia

---

## Concurrency y single-worker

### Estado actual: `asyncio.Lock()` (válido para single-worker)

```python
async def _save(self, project_id: str) -> None:
    async with self._lock:
        # atomic write: .tmp → rename
```

- `asyncio.Lock()` es seguro dentro de un mismo proceso (event loop).
- Previene escrituras concurrentes al mismo archivo JSON.
- Garantiza atomicidad de la operación `.tmp` → `.json`.

### No usar en multi-worker sin migrar

| Problema | Consecuencia |
|----------|--------------|
| Cada worker tiene su propia copia en memoria (`_store`) | Inconsistencia entre workers |
| `asyncio.Lock` no sincroniza entre procesos | Race condition en escritura de archivos |
| Dos workers escriben el mismo `project_id.json` | Pérdida de datos |

### Alternativas para multi-worker (ordenadas por recomendación)

1. **Migrar a tabla SQL** (recomendada) — `asyncio.Lock()` se reemplaza por transacciones DB. Cada worker lee/escribe la misma tabla. Es la solución correcta a largo plazo.

2. **Redis Lock** — Usar `aioredis` + `redis.lock` para coordinar workers. Más rápido que file-lock pero añade dependencia.

3. **File lock (`fcntl.flock`)** — Usar bloqueo a nivel de sistema de archivos. Funciona en Linux pero no en todos los filesystems. Requiere manejo cuidadoso de timeouts.

### Riesgo aceptado para entorno actual

El despliegue actual es **single-worker** (un solo proceso Uvicorn). En este escenario:
- `asyncio.Lock()` es correcto y suficiente.
- No hay riesgo de race conditions.
- La escritura atómica protege contra corrupción por fallo en medio de write.

**Cuando se escale a multi-worker, la migración a DB es obligatoria antes de activar el segundo worker.**

---

## Tests

### Nuevo test: `test_add_reference_inactive_media_asset`

```python
def test_add_reference_inactive_media_asset(self, client):
    # Arrange: fake DB returns asset with status="deleted"
    app.dependency_overrides[get_db] = override_db_with_inactive_media
    client.put(...)  # create character entry

    # Act: try to link inactive asset
    response = client.post(.../references, ...)

    # Assert: 400 with "inactive" in detail message
    assert response.status_code == 400
    assert "inactive" in data["detail"].lower() or "not active" in data["detail"].lower()
```

### Tests existentes que siguen funcionando

| Test | Escenario | Status |
|------|-----------|--------|
| `test_add_reference` | Asset activo, mismo proyecto → 200 | ✅ |
| `test_add_reference_invalid_media_asset` | Asset no existe → 400 | ✅ |
| `test_add_reference_inactive_media_asset` | Asset inactivo → 400 | ✅ nuevo |
| `test_add_reference_empty_asset_id` | asset_id vacío → 400 | ✅ |
| `test_add_reference_invalid_path_in_asset_id` | Path traversal → 400 | ✅ |

### Suite completa

```
Validación ejecutada en esta fase:
- test_character_bible_routes.py — 19 passed
- test_character_bible_service.py — 29 passed
- test_character_bible_persistence.py — 12 passed
- test_character_bible_openapi_routes.py — 13 passed

Total validado en Character Bible hardening: 73 passed, 0 failures.
```

---

## Limitaciones

1. **Mock de test no ejecuta SQL real** — `_FakeDb.execute()` usa string matching para determinar qué devolver. La nueva lógica con dos queries distingue entre asset activo, inactivo e inexistente. Si SQLAlchemy cambia la forma de serializar el WHERE, el mock podría necesitar ajuste.
2. **`MediaAssetStatus` solo define `MediaAssetStatus.INDEXED`** — Si en el futuro se añaden más status activos (ej. `"processed"`, `"ready"`), habrá que actualizar el filtro.
3. **Cobertura multi-worker solo documentada** — No hay tests de integración multi-worker porque el entorno no lo soporta.

---

## GO/NO-GO para commit

| Criterio | Estado |
|----------|--------|
| Active asset validation implementado | ✅ `MediaAsset.status == MediaAssetStatus.INDEXED` |
| Mensaje de error específico para inactivo | ✅ Dos queries: diagnóstico claro |
| Tests: activo, inactivo, inexistente | ✅ 3 escenarios cubiertos |
| Sin romper API existente | ✅ 73 tests específicos Character Bible hardening, 0 failures |
| Concurrency documentado | ✅ Riesgo documentado, alternativas listadas |
| Sin tocar frontend/ComfyUI/storyboard | ✅ Solo 2 archivos backend + 1 doc |
| Sin exponer rutas físicas | ✅ No se modificó lógica de sanitización |

### Decisión: **GO** ✅
