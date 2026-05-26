# STORYBOARD.TRACE.2D — Hotfix rutas trace ausentes en OpenAPI Docker

Fecha: 2026-05-26

## Problema confirmado

> `curl http://127.0.0.1/openapi.json | jq ... | grep storyboard.*/trace` → `NO_TRACE_ROUTES`
>
> Aunque el test local `app.openapi()` mostraba las 3 rutas, el Docker real no las exponía.

## Causa raíz

**No era un bug de registro de rutas en FastAPI.**

El backend registraba correctamente las 3 rutas trace en el router `storyboard_routes.py`
(prefix `/api/projects`). La app local verificaba `app.openapi()` y encontraba:

```
/api/projects/{project_id}/storyboard/trace
/api/projects/{project_id}/storyboard/shots/{shot_id}/trace
/api/projects/{project_id}/storyboard/assets/{asset_id}/trace
```

**El problema estaba en el reverse-proxy.** El `Caddyfile.deploy` (línea 53-55) bloqueaba
explícitamente `/openapi.json` con `respond 404`:

```caddy
handle /openapi.json {
    respond 404
}
```

Toda petición a `http://127.0.0.1/openapi.json` era interceptada por Caddy antes de llegar
al backend. Las rutas reales (`/api/projects/.../trace`) funcionaban correctamente porque
están bajo el matcher `/api/*` que sí se reenvía al backend.

También se bloqueaban `/docs`, `/redoc`, `/auth`, `/n8n`, `/qdrant`.

## Fix aplicado

**Archivo:** `Caddyfile.deploy` (línea 53-55)

Cambio:

```diff
-    handle /openapi.json {
-        respond 404
-    }
+    handle /openapi.json {
+        reverse_proxy backend:8000
+    }
```

El Caddyfile está montado como volumen (`./Caddyfile.deploy:/etc/caddy/Caddyfile:ro`),
por lo que el cambio es efectivo al reiniciar el contenedor:

```bash
docker compose -f compose.base.yml -f compose.home.yml restart reverse-proxy
```

No fue necesario reconstruir el backend: las rutas trace ya estaban en el commit `8f1750e`.

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `Caddyfile.deploy` | Permitir `/openapi.json` → backend:8000 (no bloquear) |
| `tests/unit/test_storyboard_trace_openapi_routes.py` | **Nuevo** — 7 tests de validación OpenAPI |

## Tests unitarios nuevos

`tests/unit/test_storyboard_trace_openapi_routes.py` (7 tests):

- `test_openapi_contains_all_storyboard_trace_routes` — usa la app real (`from app import app`),
  genera el schema completo y verifica que las 3 rutas trace están presentes
- `test_openapi_shot_trace_path_has_get_method` — verifica GET + path parameters
- `test_openapi_project_trace_path_has_get_method` — verifica GET
- `test_openapi_asset_trace_path_has_get_method` — verifica GET
- `test_all_trace_paths_in_openapi` (parametrize ×3) — cada ruta individual

## Validación local

```bash
# Compile check
python -m py_compile src/routes/storyboard_routes.py
python -m py_compile src/core/app_factory.py
python -m py_compile src/services/storyboard_trace_service.py
python -m py_compile src/schemas/storyboard_trace_schema.py
```
Resultado: PASS.

```bash
# OpenAPI route tests
PYTHONPATH=src python -m pytest tests/unit/test_storyboard_trace_openapi_routes.py -v
```
Resultado: **7 passed** en 13.15s.

```bash
# Existing trace route tests
PYTHONPATH=src python -m pytest tests/unit/test_storyboard_trace_routes.py -v
```
Resultado: **3 passed** en 9.36s.

```bash
# Full storyboard suite
PYTHONPATH=src python -m pytest tests/unit/test_storyboard_*.py -q
```
Resultado: **190 passed** en 20.61s (183 anteriores + 7 nuevos).

## Validación Docker real

```bash
docker compose -f compose.base.yml -f compose.home.yml restart reverse-proxy
sleep 3
curl -sS http://127.0.0.1/openapi.json | jq -r '.paths | keys[]' | grep -E "storyboard.*/trace"
```

Resultado:

```
/api/projects/{project_id}/storyboard/assets/{asset_id}/trace
/api/projects/{project_id}/storyboard/shots/{shot_id}/trace
/api/projects/{project_id}/storyboard/trace
```

**PASS: 3/3 rutas trace visibles en OpenAPI Docker.**

## Riesgos pendientes

- `/docs`, `/redoc`, `/auth`, `/n8n`, `/qdrant` siguen bloqueados en Caddy (decisión de
  seguridad explícita en el deploy). Si se necesitan en desarrollo, habrá que desbloquearlos
  individualmente.
- El `curl` usa `127.0.0.1:80` (Caddy). En entornos VPS el dominio público puede tener reglas
  adicionales. La verificación en local es suficiente para este hotfix.
- No se modificó ningún contrato de respuesta trace.

## Resultado

**GO técnico.** La causa raíz era el Caddyfile bloqueando `/openapi.json`, no el registro
de rutas en FastAPI. Se corrigió el bloqueo, se añadió test de regresión OpenAPI y se
verificó en el Docker real.

No se hizo commit.
