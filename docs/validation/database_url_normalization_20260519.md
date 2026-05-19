# Database URL Normalization — TECH-DEBT 1

## Metadata

| Campo | Valor |
|---|---|
| **Commit base** | `9068ca7` docs: add visual bible storyboard phase 2b.1 smoke validation |
| **Fecha** | 2026-05-19 |
| **Rama** | `main` |

## Problema detectado

Durante FASE 2B.1 (smoke test `visual_bible_storyboard_phase2b_1_smoke_20260519.md`) se detectó que:
- El `.env` local del desarrollador apunta a `/tmp/ailinkcinema.db`
- El runtime real (FastAPI) usa `/opt/SERVICIOS_CINE/ailinkcinema_s2.db`

Esto provoca:
- Alembic apunta a `/tmp/ailinkcinema.db` (lee `.env` via `load_dotenv()`)
- Pydantic Settings (`core.config`) lee `.env` y obtiene `/tmp/ailinkcinema.db`
- El runtime (`database.py`) usa la capa legacy (`config.get_database_settings()`) que resuelve desde `config.yaml` → `ailinkcinema_s2.db`
- Dos bases de datos con distinto estado de migraciones

## Causa raíz

| Fuente | Cómo obtiene DATABASE_URL | Resultado |
|---|---|---|
| `database.py` (runtime) | `config.get_database_url()` → `os.getenv()` → `config.yaml` → default | ✅ `ailinkcinema_s2.db` |
| `core.config.Settings` (Pydantic) | Lee `.env` | ❌ `/tmp/ailinkcinema.db` (según lo que tenga `.env`) |
| `alembic/env.py` | `load_dotenv()` → `os.getenv("DATABASE_URL")` | ❌ `/tmp/ailinkcinema.db` |
| `config.yaml` | Valor fijo | ✅ `sqlite+aiosqlite:///./ailinkcinema_s2.db` |
| `src/config.py` default | `_DEFAULT_DATABASE_URL` | ✅ `/opt/SERVICIOS_CINE/ailinkcinema_s2.db` |

La causa es que:
1. `database.py` (el runtime) lee desde la capa legacy (`config.py` → `config.yaml`), NO desde Pydantic Settings.
2. Pydantic Settings lee `.env` directamente.
3. Alembic lee `.env` via `load_dotenv()`.
4. El `.env` del desarrollador tiene `DATABASE_URL=sqlite+aiosqlite:////tmp/ailinkcinema.db` (un path diferente al estándar).

## Estándar elegido

**Desarrollo local:** `sqlite+aiosqlite:///./ailinkcinema_s2.db`

La base `ailinkcinema_s2.db` es la que ya usa el runtime y la que está documentada en `config.yaml`. Se adopta como estándar único para desarrollo local.

## Archivos revisados

| Archivo | Estado |
|---|---|
| `.env` (local, git-ignored) | ❌ Usa `/tmp/ailinkcinema.db` — requiere que el desarrollador lo actualice |
| `.env.example` | ✅ Actualizado |
| `.env.home.example` | ✅ Actualizado |
| `.env.vps.example` | ✅ Actualizado |
| `src/core/config.py` | ✅ Default añadido: `"sqlite+aiosqlite:///./ailinkcinema_s2.db"` |
| `src/config.py` | ✅ Ya correcto (default y fallback apuntan a `_s2.db`) |
| `src/config/config.yaml` | ✅ Ya correcto (`sqlite+aiosqlite:///./ailinkcinema_s2.db`) |
| `src/database.py` | ✅ Ya correcto (lee de legacy config que resuelve a `_s2.db`) |
| `alembic/env.py` | ⚠️ Sin cambios — depende de `DATABASE_URL` de entorno; leerá lo que tenga `.env` |
| `compose.base.yml` | ✅ Actualizado |
| `compose.home.yml` | ✅ Actualizado |
| `compose.vps.yml` | ✅ Actualizado |
| `deploy/docker/*` | ✅ Ya correcto (usa `ailinkcinema_s2.db`) |

## Archivos modificados

1. `.env.example` — línea 61: comentario y default `DATABASE_URL` actualizados a `ailinkcinema_s2.db`
2. `.env.home.example` — línea 12: `DATABASE_URL` actualizado
3. `.env.vps.example` — línea 12: `DATABASE_URL` actualizado
4. `src/core/config.py` — línea 46: default `database_url` cambiado de `""` a `"sqlite+aiosqlite:///./ailinkcinema_s2.db"`
5. `compose.base.yml` — línea 21: default compose actualizado
6. `compose.home.yml` — línea 25: default compose actualizado
7. `compose.vps.yml` — línea 25: default compose actualizado
8. `scripts/diagnose_database_config.py` — **CREADO**: diagnóstico multi-capa de DATABASE_URL

## FIX 2026-05-19 — False MISALIGNMENT in diagnose script

Se identificó que `scripts/diagnose_database_config.py` comparaba strings en vez de
paths resueltos, causando falsos MISALIGNMENT entre:
- `sqlite+aiosqlite:////opt/SERVICIOS_CINE/ailinkcinema_s2.db`
- `sqlite+aiosqlite:///./ailinkcinema_s2.db`

**Fix:** Se añadió `resolve_sqlite_path()` que normaliza cualquier formato SQLite URL a
`Path` absoluto resuelto. La comparación ahora usa `Path.resolve()`.

## Validaciones ejecutadas

| Validación | Resultado |
|---|---|
| `py_compile src/core/config.py` | ✅ OK |
| `py_compile src/config.py` | ✅ OK |
| `py_compile src/database.py` | ✅ OK |
| `py_compile scripts/diagnose_database_config.py` | ✅ OK |
| `.env` local corregido manualmente (no trackeado) | ✅ `DATABASE_URL=sqlite+aiosqlite:///./ailinkcinema_s2.db` |
| `alembic upgrade head` ejecutado | ✅ |
| `alembic current` | ✅ `20260519_000001 (head)` |
| `alembic heads` | ✅ `20260519_000001 (head)` |
| `sqlite3 ailinkcinema_s2.db "SELECT version_num FROM alembic_version"` | ✅ `20260519_000001` |
| `sqlite3 ailinkcinema_s2.db ".tables" | grep project_visual_bibles` | ✅ exists |
| Backend health check | ✅ `{"name":"AILinkCinema","status":"ok","env":"development"}` |

### Diagnóstico final

```
$ python scripts/diagnose_database_config.py

  Runtime (database)     | sqlite+aiosqlite:////opt/SERVICIOS_CINE/ailinkcinema_s2...
  Pydantic (settings)    | sqlite+aiosqlite:///./ailinkcinema_s2.db
  Legacy (config.py)     | sqlite+aiosqlite:///./ailinkcinema_s2.db
  Alembic (load_dotenv)  | sqlite+aiosqlite:///./ailinkcinema_s2.db

  ✅ ALIGNMENT OK — all layers resolve to: /opt/SERVICIOS_CINE/ailinkcinema_s2.db
```

### Archivo modificado

1. `scripts/diagnose_database_config.py` — **MODIFICADO**: se añadió `resolve_sqlite_path()` y la comparación ahora usa `Path.resolve()` en vez de strings brutos.

## Riesgos — TODOS RESUELTOS

| Riesgo anterior | Estado |
|---|---|
| `.env` local con path divergente | ✅ Corregido manualmente a `./ailinkcinema_s2.db` |
| Migraciones pendientes en `_s2.db` | ✅ `alembic upgrade head` ejecutado, current = `20260519_000001` |
| Tabla `project_visual_bibles` faltante | ✅ Existe en `ailinkcinema_s2.db` |
| Dos DBs activas | ✅ `/tmp/ailinkcinema.db` queda obsoleta; todo apunta a `_s2.db` |
| Diagnóstico falso MISALIGNMENT | ✅ `resolve_sqlite_path()` compara paths absolutos resueltos |

## Veredicto

**GO** ✅ — Normalización completada. Todos los riesgos resueltos.

- Las 4 capas (Runtime, Pydantic, Legacy, Alembic) resuelven al mismo archivo.
- `.env` local actualizado a `./ailinkcinema_s2.db`.
- `alembic current` = `20260519_000001 (head)`.
- Tabla `project_visual_bibles` presente.
- Diagnóstico muestra `✅ ALIGNMENT OK`.
