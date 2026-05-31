# PostgreSQL Runtime — CID Migration

## 1. Resumen ejecutivo

- **Fecha**: 2026-05-30
- **Motivo**: SQLite producía errores `database is locked` en operaciones concurrentes sobre `project_jobs` y `job_history`. PostgreSQL elimina este cuello de botella.
- **Estado**: GO FINAL — backend funcionando sobre PostgreSQL sin SQLite. Commits `2f00641` (primera migración), `47a0ba1` (bind seguro, server_settings asyncpg, compose.home.yml con DATABASE_URL PostgreSQL). Tag: `cid-dev-stable-postgres-runtime-switchover-20260531`.

## 2. Arquitectura actual

```
┌─────────────────────────────────────────────────────────┐
│                     SERVICIOS CINE                      │
├──────────────┬──────────────┬───────────────────────────┤
│  CID         │  n8n         │  Qdrant · Ollama · Comfy  │
│  (PostgreSQL)│  (PostgreSQL)│                           │
│  schema cid  │  schema pub  │                           │
├──────────────┴──────────────┴───────────────────────────┤
│                    Frontend React                        │
└─────────────────────────────────────────────────────────┘
```

Ambos schemas (`cid` y `public`) comparten la misma instancia PostgreSQL en `127.0.0.1:5432`.

## 3. Datos migrados

| Tabla | Filas |
|---|---|
| `users` | 13 |
| `organizations` | 12 |
| `projects` | 17 |
| `media_assets` | 293 |
| `storyboard_shots` | 773 |
| `project_jobs` | 389 |
| `job_history` | 5390 |
| Otras tablas (resto del schema `cid`) | Según esquema |

## 4. Conteos finales

| Tabla | Conteo |
|---|---|
| `users` | 13 |
| `organizations` | 12 |
| `projects` | 17 |
| `media_assets` | 293 |
| `storyboard_shots` | 773 |
| `project_jobs` | 389 |
| `job_history` | 5390 |

Una fila de `job_history` fue descartada por tener `created_at = ' A shadowy figure appears '` (dato corrupto pre-existente, no introducido por la migración).

## 5. Schema layout

```
PostgreSQL (ailinkcinema)
├── cid                    # CID — todas las tablas de negocio
│   ├── users
│   ├── organizations
│   ├── projects
│   ├── media_assets
│   ├── storyboard_shots
│   ├── project_jobs
│   ├── job_history
│   └── ... (85 tablas en total + alembic_version)
│
└── public                 # n8n — solo tablas n8n_* + schema_migrations
    ├── n8n_*
    └── schema_migrations
```

## 6. Runtime

- `DATABASE_URL`: `postgresql+asyncpg://ailinkcinema:****@ailinkcinema_postgres:5432/ailinkcinema` (desde `compose.home.yml`, no desde `.env`)
- `search_path`: `cid,public` configurado vía `server_settings` en `src/database.py:62` (commit `47a0ba1` cambió de `options` a `server_settings` para compatibilidad asyncpg)
- Alembic usa `psycopg2` (sync) con `version_table_schema="cid"` y `options: -c search_path=cid`
- Contenedor PostgreSQL: `ailinkcinema_postgres` (16-alpine, healthy)

## 7. Rollback

> ⚠️ A partir de `47a0ba1`, `DATABASE_URL` está hardcodeada en `compose.home.yml` (no en `.env`). Rollback requiere revertir ambos.

1. Revertir `compose.home.yml`:
   ```bash
   git checkout 2f00641~1 -- compose.home.yml
   ```
   (Restaura la versión con `DATABASE_URL: sqlite+aiosqlite:///./ailinkcinema_s2.db`)
2. Revertir `src/database.py` si se usó server_settings:
   ```bash
   git checkout 2f00641~1 -- src/database.py
   ```
3. Verificar que existe `ailinkcinema_s2.db` (backup en `backups/`).
4. Reconstruir e iniciar backend:
   ```bash
   docker compose -f compose.base.yml -f compose.home.yml build backend
   docker compose -f compose.base.yml -f compose.home.yml up -d backend
   ```
5. Verificar salud:
   ```bash
   curl http://127.0.0.1:8000/health
   ```

## 8. Smoke tests

Post-migración se validaron manualmente:

- `POST /api/auth/login` → 200 + JWT
- `GET /api/auth/me` → usuario `ailinkcinema@ailinkcinema.com` role=ADMIN
- `GET /api/projects/` → 3 proyectos visibles (multi-tenant)
- `GET /api/projects/{id}/storyboard` → shots disponibles
- `GET /api/queue/status` → cola operativa
- 0 ocurrencias de `sqlite locked` en logs del backend
- 0 tablas no-n8n escritas en schema `public`

## 9. Lessons learned

- SQLite no escala para tablas de alta concurrencia como `project_jobs` y `job_history` con múltiples escrituras simultáneas.
- PostgreSQL elimina por completo los errores `database is locked`.
- La migración requiere orden topológico por FK y manejo de tipos (booleanos, varchar(N), timestamps).
- El schema `cid` aísla las tablas de negocio de las tablas `n8n` en `public`, permitiendo coexistencia sin interferencias.
- `alembic/env.py` debe manejar tanto SQLite como PostgreSQL condicionalmente para compatibilidad de tests.

## 10. Próximas fases

- Cloudflare Tunnel para acceso externo seguro — ✅ docs creadas en `CID.INFRA.DOMAIN.TUNNEL.1`
- RAG cinematográfico con Qdrant — diseño en `docs/architecture/cid_memory_rag_design.md`
- pgvector (futuro, cuando exista pipeline de embeddings en `src/`)
- Flowise (orquestación visual de workflows IA)
- Redis (caché de sesiones y colas)
