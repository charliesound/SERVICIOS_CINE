# Validación FASE 1.1 — Cinematic Taxonomy & Visual Bible Engine

## Metadata

| Campo | Valor |
|-------|-------|
| **Commit** | `f3dd00a` feat: add cinematic taxonomy visual bible engine phase 1 |
| **Tag** | `cid-dev-stable-cinematic-taxonomy-phase1-20260519` |
| **Fecha** | 2026-05-19 |
| **Entorno** | Local / WSL2 Ubuntu |
| **Backend** | `uvicorn core.app_factory:create_app --factory --host 0.0.0.0 --port 8010` |
| **Python** | 3.12 |
| **PYTHONPATH** | `src` |

## 1. Validación de orden de rutas

**Archivo auditado:** `src/routes/cinematic_taxonomy_routes.py`

**Orden confirmado (correcto):**

| Orden | Decorador | Path | Método |
|-------|-----------|------|--------|
| 1 | `@router.get("")` | `/api/cinematic-taxonomy` | GET |
| 2 | `@router.get("/presets")` | `/api/cinematic-taxonomy/presets` | GET |
| 3 | `@router.get("/presets/{preset_id}")` | `/api/cinematic-taxonomy/presets/{preset_id}` | GET |
| 4 | `@router.get("/{category}")` | `/api/cinematic-taxonomy/{category}` | GET |
| 5 | `@router.post("/enrich-prompt")` | `/api/cinematic-taxonomy/enrich-prompt` | POST |

Las rutas fijas `/presets` y `/presets/{preset_id}` aparecen **antes** que la
ruta dinámica `/{category}`. `/enrich-prompt` es POST, sin conflicto con
las rutas GET.

**Veredicto: ✓ Correcto. No requiere cambios.**

## 2. py_compile

```bash
python -m py_compile src/schemas/cinematic_taxonomy_schema.py   → OK (sin errores)
python -m py_compile src/services/cinematic_taxonomy_service.py → OK (sin errores)
python -m py_compile src/routes/cinematic_taxonomy_routes.py    → OK (sin errores)
```

## 3. Tests unitarios

```bash
PYTHONPATH=src python -m pytest tests/unit/test_cinematic_taxonomy_service.py -q
→ 14 passed

PYTHONPATH=src python -m pytest tests/unit/test_cinematic_taxonomy_routes.py -q
→ 11 passed
```

**Total: 25/25 passed.**

## 4. OpenAPI Schema Validation

```python
from core.app_factory import create_app
app = create_app()
paths = app.openapi()["paths"]
for p in sorted(paths):
    if "cinematic-taxonomy" in p:
        print(p)
```

**Rutas registradas en OpenAPI:**

| Path | Estado |
|------|--------|
| `/api/cinematic-taxonomy` | ✓ |
| `/api/cinematic-taxonomy/enrich-prompt` | ✓ |
| `/api/cinematic-taxonomy/presets` | ✓ |
| `/api/cinematic-taxonomy/presets/{preset_id}` | ✓ |
| `/api/cinematic-taxonomy/{category}` | ✓ |

**Total: 5/5 rutas visibles.**

## 5. Smoke Tests Reales (HTTP contra :8010)

### 5.1 GET /api/cinematic-taxonomy

```bash
curl -i "http://127.0.0.1:8010/api/cinematic-taxonomy"
```

**Esperado:** HTTP 200, JSON con `categories` y `total_elements`
**Obtenido:** HTTP 200, 10 categorías, total_elements > 50
**Veredicto:** ✓

### 5.2 GET /api/cinematic-taxonomy/shot_types

```bash
curl -i "http://127.0.0.1:8010/api/cinematic-taxonomy/shot_types"
```

**Esperado:** HTTP 200, JSON array con elementos de shot_types
**Obtenido:** HTTP 200, 11 elementos (ECU, CU, MCU, MS, MWS, WS, EWS, OTS, POV, Dutch Angle, Aerial)
**Veredicto:** ✓

### 5.3 GET /api/cinematic-taxonomy/presets

```bash
curl -i "http://127.0.0.1:8010/api/cinematic-taxonomy/presets"
```

**Esperado:** HTTP 200, JSON array con 8 presets
**Obtenido:** HTTP 200, 8 presets (noir_classic, epic_blockbuster, indie_intimate, retro_70s_vibrant, horror_tense, documentary_realism, music_video_vibrant, period_drama)
**Veredicto:** ✓

### 5.4 GET /api/cinematic-taxonomy/presets/noir_classic

```bash
curl -i "http://127.0.0.1:8010/api/cinematic-taxonomy/presets/noir_classic"
```

**Esperado:** HTTP 200, preset noir_classic
**Obtenido:** HTTP 200, id=noir_classic, name="Classic Film Noir", shot_types contiene "cu", "mcu", "dutch"
**Veredicto:** ✓

### 5.5 POST /api/cinematic-taxonomy/enrich-prompt (con preset)

**Request:**
```json
{
  "base_prompt": "A detective walking down a rainy street",
  "preset_id": "noir_classic"
}
```

**Esperado:** HTTP 200, enriched_prompt comienza con base_prompt, applied_preset.id = noir_classic
**Obtenido:** HTTP 200, enriched_prompt = "A detective walking down a rainy street. film noir aesthetic | classic noir | ...", negative_prompt contiene tags negativos, warnings = []
**Veredicto:** ✓

### 5.6 GET /api/cinematic-taxonomy/categoria_falsa_999

```bash
curl -i "http://127.0.0.1:8010/api/cinematic-taxonomy/categoria_falsa_999"
```

**Esperado:** HTTP 404
**Obtenido:** HTTP 404 con detail explicativo
**Veredicto:** ✓

### 5.7 POST /api/cinematic-taxonomy/enrich-prompt (preset inexistente)

**Request:**
```json
{
  "base_prompt": "Test",
  "preset_id": "no_existe"
}
```

**Esperado:** HTTP 404
**Obtenido:** HTTP 404
**Veredicto:** ✓

### 5.8 POST /api/cinematic-taxonomy/enrich-prompt (sin preset ni tags)

**Request:**
```json
{
  "base_prompt": "A simple scene"
}
```

**Esperado:** HTTP 200, enriched_prompt = base_prompt, applied_tags = [], warnings = []
**Obtenido:** HTTP 200, enriched_prompt = "A simple scene", applied_preset = null, warnings = []
**Veredicto:** ✓

## 6. Resumen de resultados

| Prueba | Resultado |
|--------|-----------|
| Orden de rutas | ✓ Correcto |
| py_compile (3 archivos) | ✓ 3/3 OK |
| pytest servicio (14 tests) | ✓ 14/14 passed |
| pytest rutas (11 tests) | ✓ 11/11 passed |
| OpenAPI schema (5 rutas) | ✓ 5/5 visibles |
| GET /api/cinematic-taxonomy | ✓ HTTP 200 |
| GET /shot_types | ✓ HTTP 200 |
| GET /presets | ✓ HTTP 200 |
| GET /presets/noir_classic | ✓ HTTP 200 |
| POST /enrich-prompt (con preset) | ✓ HTTP 200 |
| GET /categoria_falsa_999 | ✓ HTTP 404 |
| POST /enrich-prompt (preset inexistente) | ✓ HTTP 404 |
| POST /enrich-prompt (base only) | ✓ HTTP 200 |

## 7. Veredicto Final

**GO ✓** — FASE 1.1 validada. Smoke tests OK. Documentación creada. Sin bugs
detectados. Sin cambios funcionales necesarios.

**Precaución:** Los 89 fallos de la suite global de tests son preexistentes
(infraestructura async / pytest-asyncio). Fuera de alcance de FASE 1.1.

## 8. Comando para levantar backend (referencia)

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
PYTHONPATH=src uvicorn core.app_factory:create_app --factory \
  --host 0.0.0.0 --port 8010 --reload
```
