# Fase 1 Validation Closure

## Resumen ejecutivo

- Se cerró el problema principal de test discovery fuera de scope con `pytest.ini` en root.
- Se añadió `requirements-dev.txt` para reproducir la suite con `pytest<9` y `pytest-asyncio`, ya que el intérprete base tenía `pytest 9.0.3` sin plugin async compatible.
- `tests/unit/` pasa completo tras el cleanup (`171 passed`).
- `tests/integration/test_opportunity_tracking_checklist.py` quedó reparado y ya no falla por `ImportError`.
- Runtime HTTP ya devuelve 404 uniforme enterprise con `error.request_id` y respeta `X-Request-ID` custom.
- `tests/integration/` completo sigue en `NO-GO` por fallos preexistentes fuera de este cleanup puntual.

## Cambios realizados

### Archivos modificados

- `pytest.ini`
- `requirements-dev.txt`
- `src/core/errors.py`
- `tests/unit/test_error_handler.py`
- `tests/integration/test_opportunity_tracking_checklist.py`

### `pytest.ini`

```ini
[pytest]
testpaths = tests
norecursedirs =
    OLD
    ai-dubbing-legal-studio
    .venv
    src/.venv
    node_modules
    dist
    build
pythonpath =
    src
asyncio_mode = auto
markers =
    asyncio: mark test as async
```

### `requirements-dev.txt`

```text
-r src/requirements.txt
pytest>=8.2,<9
pytest-asyncio>=0.24,<0.27
```

## Comandos ejecutados

```bash
python -m pytest --collect-only -q
python -m pytest tests/unit/test_health.py -q
PYTHONPATH=src python - <<'PY'
from app import app
print(type(app))
print(getattr(app, 'title', None))
PY
find . -maxdepth 3 \( -name "docker-compose.yml" -o -name "compose.yml" -o -name "docker-compose*.yml" \) -print
docker compose -f deploy/docker/docker-compose.local.yml config
python -m compileall src/
git status --short
```

### Entorno de validación reproducible usado para pytest

```bash
python3 -m venv --system-site-packages /tmp/cid-phase1-venv
/tmp/cid-phase1-venv/bin/python -m pip install -r requirements-dev.txt
PATH="/tmp/cid-phase1-venv/bin:$PATH" python -m pytest --collect-only -q
PATH="/tmp/cid-phase1-venv/bin:$PATH" python -m pytest tests/unit/ -q
PATH="/tmp/cid-phase1-venv/bin:$PATH" python -m pytest tests/integration/ -q
```

Nota: el `python` global del host tenía `pytest 9.0.3` y no tenía `pytest-asyncio`; por eso la validación reproducible se ejecutó en un venv local de revisión sin tocar proyectos fuera de scope.

## Resultado de collect-only

- `OLD/sensitive_review/...` dejó de ser recolectado.
- `ai-dubbing-legal-studio/backend/tests/...` dejó de ser recolectado.
- `cid-budget/tests/...` también quedó fuera al limitar `testpaths = tests`.
- La recolección del backend activo quedó limitada a `tests/`.
- Persistió 1 error de colección dentro del scope real:

```text
tests/integration/test_opportunity_tracking_checklist.py
ImportError: cannot import name 'Project' from 'models.production'
```

## Resultado de unit tests

```text
170 passed, 103 warnings in 13.58s
```

Estado: OK.

## Resultado de integration tests

```text
ERROR tests/integration/test_opportunity_tracking_checklist.py
ImportError: cannot import name 'Project' from 'models.production'
```

Conclusión:

- Ya no falla por `from app import app`.
- El bloqueo actual es una incompatibilidad legacy/preexistente de imports/modelos en una prueba de integración concreta.
- No se mezcló esta corrección con Fase 1.
- Mini-fase propuesta: `Fase 1 Cleanup - integration tests import compatibility`.

## Resultado de import app

Comando:

```bash
PYTHONPATH=src python - <<'PY'
from app import app
print(type(app))
print(getattr(app, "title", None))
PY
```

Salida relevante:

```text
<class 'fastapi.applications.FastAPI'>
AILinkCinema
```

Estado: OK. No fue necesario tocar `src/app.py`.

## Resultado docker compose

Descubrimiento:

```text
./deploy/docker/docker-compose.vps.yml
./deploy/docker/docker-compose.local.yml
./cid-budget/docker-compose.yml
./comfysearch/docker-compose.yml
./ai-dubbing-legal-studio/docker-compose.yml
./ai-dubbing-legal-studio/docker-compose.prod.yml
```

Archivo validado para el backend CID actual:

```bash
docker compose -f deploy/docker/docker-compose.local.yml config
```

Resultado: OK. La configuración se resolvió correctamente y publica backend en `8010`.

## Resultado curls runtime

Comando de arranque usado:

```bash
PYTHONPATH=src python -m uvicorn app:app --host 127.0.0.1 --port 8010
```

Resultados:

- `GET /health/live` -> `200 OK`
- `GET /health/ready` -> `200 OK` con JSON estructurado; `status` actual: `degraded`
- `GET /health/startup` -> `200 OK` con JSON estructurado
- `GET /health/live` con `X-Request-ID: cid-test-001` -> header y body respetan `cid-test-001`
- `GET /ruta-inexistente` -> `404 Not Found`, pero devuelve `{"detail":"Not Found"}`

Conclusión runtime:

- El contrato de request id funciona en health endpoints.
- El contrato de error uniforme para 404 no está cumpliendo la expectativa enterprise (`error.request_id`).

## Resultado compileall

- `python -m compileall src/` ejecutó sin errores fatales.
- Observación: también recorrió `src/.venv/`, lo que indica que existe un entorno virtual dentro de `src/` en este workspace.

## Fase 1 Cleanup

### Fix aplicado al 404

- Se actualizó `src/core/errors.py` para registrar handlers tanto de `fastapi.HTTPException` como de `starlette.exceptions.HTTPException`.
- Se normalizó el cuerpo HTTP error a formato enterprise con `code`, `message`, `details` y `request_id`.
- Se añadió mapeo de `404 -> not_found`.
- `details` ahora sale como `{}` cuando no hay payload estructurado.

### Fix aplicado al integration import

- Se corrigió `tests/integration/test_opportunity_tracking_checklist.py` para usar el modelo `Project` desde `models.core`, que es donde realmente vive.
- Se modernizó ese test para usar `AsyncSessionLocal` y datos de prueba propios, evitando el patrón roto `async for db in get_db()` y el `NameError` implícito de `TestClient/app` no importados.
- No se tocaron modelos de base de datos ni migraciones.

### Comandos ejecutados en cleanup

```bash
/tmp/cid-phase1-venv/bin/python -m pytest tests/unit/test_error_handler.py -q
/tmp/cid-phase1-venv/bin/python -m pytest tests/integration/test_opportunity_tracking_checklist.py -q
python -m compileall src/
/tmp/cid-phase1-venv/bin/python -m pytest tests/unit/ -q
/tmp/cid-phase1-venv/bin/python -m pytest tests/integration/ -q
PYTHONPATH=src python -m uvicorn app:app --host 127.0.0.1 --port 8010
curl -i http://127.0.0.1:8010/health/live
curl -i http://127.0.0.1:8010/health/ready
curl -i http://127.0.0.1:8010/health/startup
curl -i http://127.0.0.1:8010/ruta-inexistente
curl -i -H "X-Request-ID: cid-test-001" http://127.0.0.1:8010/ruta-inexistente
```

### Resultados cleanup

- `tests/unit/test_error_handler.py` -> `5 passed`
- `tests/integration/test_opportunity_tracking_checklist.py` -> `1 passed`
- `tests/unit/` -> `171 passed, 106 warnings`
- Runtime 404 -> cuerpo uniforme enterprise y header `X-Request-ID` correcto

### Resultado de integration suite completa

```text
1 failed, 1 passed, 12 errors
```

Bloqueos detectados tras resolver el import puntual:

- múltiples tests usan `alembic upgrade head`, pero el repo tiene múltiples heads de Alembic (`Multiple head revisions are present`)
- varios tests que inicializan sqlite temporal quedan sin tablas core (`no such table: organizations`)
- `tests/integration/test_funding_dossier_export.py` falla por aserción funcional (`budget_summary.total_budget == 0.0` vs `875000.0` esperado)

Conclusión del cleanup:

- El bloqueo 404 quedó resuelto.
- El bloqueo de import de `test_opportunity_tracking_checklist.py` quedó resuelto.
- La suite de integración completa sigue en `NO-GO` por problemas preexistentes adicionales, distintos al scope de este cleanup.

## Errores fuera de scope vs legacy

### Errores fuera de scope ya neutralizados

- Recolección de `OLD/sensitive_review/legacy_projects/...`
- Recolección de `ai-dubbing-legal-studio/backend/tests/...`
- Recolección lateral de `cid-budget/tests/...`

### Errores legacy/preexistentes pendientes

- El host base de validación no es suficiente por sí solo para async tests (`pytest 9.0.3` + sin plugin); por eso se dejó preparado `requirements-dev.txt`.
- La suite `tests/integration/` completa tiene fallos adicionales preexistentes: múltiples heads de Alembic, esquemas sqlite incompletos en varios tests y una aserción funcional en `tests/integration/test_funding_dossier_export.py`.

## Estado Fase 1

`NO-GO`

Motivos:

1. `tests/integration/` no queda limpio; persisten fallos preexistentes de Alembic/schema y al menos una regresión funcional fuera del scope puntual de cleanup.

## GO / NO-GO para Fase 1.5

`NO-GO`

No avanzar a Fase 1.5 hasta cerrar como mínimo:

1. estrategia de migrations para tests con múltiples heads de Alembic
2. inicialización consistente de schema sqlite en integration tests que hoy arrancan sin tablas core
3. revisión funcional de `tests/integration/test_funding_dossier_export.py`

## Riesgos pendientes

- Riesgo de falsa señal verde si alguien ejecuta `python -m pytest` fuera de un venv preparado con `requirements-dev.txt`.
- Riesgo de mezclar pruebas activas con entornos auxiliares si se elimina o se rompe `testpaths = tests`.
- Riesgo de bloqueo sistémico en integration mientras convivan múltiples heads de Alembic sin objetivo explícito para test bootstrap.

## Recomendación para Fase 1.5

- No avanzar.
- Abrir una mini-fase acotada para estabilizar `tests/integration/` fuera del scope IA/ComfyUI.
- Después de esa mini-fase, repetir exactamente:

```bash
PATH="/tmp/cid-phase1-venv/bin:$PATH" python -m pytest --collect-only -q
PATH="/tmp/cid-phase1-venv/bin:$PATH" python -m pytest tests/unit/ -q
PATH="/tmp/cid-phase1-venv/bin:$PATH" python -m pytest tests/integration/ -q
PYTHONPATH=src python -m uvicorn app:app --host 127.0.0.1 --port 8010
```
