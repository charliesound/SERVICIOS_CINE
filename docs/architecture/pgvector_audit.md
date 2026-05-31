# CID.PGVECTOR.AUDIT.1 — pgvector Viability Audit

## 1. PostgreSQL Environment

| Atributo | Valor |
|---|---|
| Versión | PostgreSQL 16.13 on x86_64-pc-linux-musl (Alpine) |
| Database | `ailinkcinema` |
| Schemas | `cid` (CID), `public` (n8n), `information_schema`, `pg_catalog` |
| search_path (default) | `"$user", public` (cid se añade en `src/database.py` vía `connect_args`) |
| Extensiones instaladas | `plpgsql` 1.0, `uuid-ossp` 1.1 |

## 2. pgvector

### Disponibilidad
```
pg_available_extensions → NO contiene vector
pg_extension            → NO instalado
```

**Motivo**: `postgres:16-alpine` no incluye pgvector. La extensión debe compilarse desde fuente o usarse la imagen oficial `pgvector/pgvector:0.8.0-pg16` (basada en Alpine, aprox. 480 MB vs 100 MB de postgres:16-alpine).

### Acción necesaria
Reemplazar `image: postgres:16-alpine` por `image: pgvector/pgvector:0.8.0-pg16` en `compose.data.yml`.

### Costos
- ~380 MB extra en imagen
- Recrear contenedor PostgreSQL (pérdida de estado si no se migra volumen)
- Si se mantiene volumen persistente (external: false → default named volume), el reemplazo de imagen es transparente

## 3. CID Candidate Tables (todas existen en schema `cid`)

| Tabla | Columnas | Ya tiene embedding? |
|---|---|---|
| `document_chunks` | 10 (id, document_id, project_id, org_id, chunk_index, chunk_text, chunk_tokens_estimate, **embedding_payload**, metadata_json, created_at) | Sí, `embedding_payload TEXT` (JSON serializado) |
| `document_assets` | 13 | No — metadatos de archivos subidos |
| `projects` | 7 | No — script_text TEXT para chunking |
| `storyboard_shots` | 19 | No — narrative_text, scene_heading |
| `project_visual_bibles` | 14 | No — director_notes, custom_prompt_tags |
| `characters` | 5 | No — name, description |
| `production_breakdowns` | 9 | No — script_text, breakdown_json |
| `crm_contacts` | 21 | No — notes, tags, genres |
| `funding_opportunities` | 6 | No — title, description |

## 4. Embedding References in Current `src/`

**Cero referencias.** El código activo de CID (`src/`) no contiene:

- `embedding` / `embeddings`
- `vector` (en contexto semántico)
- `qdrant`
- `rag` (en código funcional)

### Dónde SÍ existen (fuera de `src/`)

| Ubicación | Contenido |
|---|---|
| `comfysearch/` | Servicio completo: `embedder.py`, `qdrant_store.py`, `ingest_to_qdrant.py`, `run_search_demo.py`, `app.py` (FastAPI) |
| `alembic/versions/20260422_000007_document_chunks_rag.py` | Migración que creó `document_chunks` con `embedding_payload TEXT` |
| `OLD/sensitive_review/legacy_projects/CINE_AI_PLATFORM/` | Qdrant + embeddings + pipelines n8n (legacy, no migrado) |
| `.github/workflows/*-smoke.yml` | Mencionan Qdrant en validaciones del data stack |

## 5. Qdrant

| Contenedor | Estado | Puerto | Imagen |
|---|---|---|---|
| `ailinkcinema_qdrant` | **Up (healthy)** | 6333 (REST), 6334 (gRPC) | `qdrant/qdrant:latest` |
| `qdrant` | Exited (3 weeks) | — | `qdrant/qdrant:v1.16.3` |
| `web-leads-qdrant` | Exited (3 weeks) | — | `qdrant/qdrant:latest` |

- Definido en `compose.data.yml` bajo perfil `with-qdrant`
- Volumen persistente: `qdrant_data`
- Red: `private_net`
- ComfySearch ya tiene integración funcional con Qdrant

No se ejecutó consulta a colecciones (el contenedor corre en red `private_net`, no expuesta directamente desde WSL2 sin docker exec). Se requiere `docker exec` para inspeccionar colecciones.

## 6. Flowise

**No existe configuración ni integración activa.** Cero referencias fuera de `OLD/`. No hay servicio en `compose.base.yml`, `compose.data.yml`, ni `compose.home.yml`. Pendiente de planificación — no hay stack ni dependencia.

## 7. Delivery

### GO / NO-GO pgvector

**NO-GO** para instalación inmediata. Razones:

1. **pgvector no disponible** en `postgres:16-alpine` actual — requiere cambiar la imagen Docker y recrear el contenedor
2. **Qdrant ya está operativo** y saludable en el stack — no hay necesidad urgente
3. **Cero código de embeddings** en `src/` — no hay pipeline que aproveche pgvector hoy
4. **ComfySearch** ya cubre búsqueda semántica con Qdrant

### Qdrant vs pgvector — Recomendación

| Aspecto | Qdrant | pgvector |
|---|---|---|
| Estado actual | **Running, healthy** | No disponible |
| Integración CID | vía ComfySearch (externa) | Directa en PostgreSQL |
| Esfuerzo migración | Ninguno (ya funcional) | Cambio imagen PG + migración columnas |
| Independencia | Servicio separado, escala propia | Atado a operaciones de PG |
| Transaccionalidad | Dos sistemas (Qdrant + PG) | Un solo sistema |
| Madurez en el stack | ComfySearch lo usa | Sin código cliente |

**Recomendación**: Mantener Qdrant como vector store principal. pgvector queda como **futura optimización** cuando CID necesite embeddings transaccionales (ej. escritura de embeddings en misma transacción que el documento).

### Arquitectura recomendada (inmediata)

```
CID Backend (src/)
  └── document_chunks.embedding_payload TEXT
        ↑ (bridge — compatible con ambos)
ComfySearch → Qdrant (búsqueda semántica)
```

### Fases propuestas

| Fase | Objetivo | Dependencias |
|---|---|---|
| **CID.PGVECTOR.INSTALL.1** | Cambiar imagen PG, instalar extensión, verificar `CREATE EXTENSION vector` | Decisión GO |
| **CID.PGVECTOR.SCHEMA.1** | Agregar columna `embedding vector(1536)` a tablas candidatas, migrar datos desde `embedding_payload TEXT` | CID.PGVECTOR.INSTALL.1 |
| **CID.RAG.MEMORY.DESIGN.1** | Diseñar arquitectura de memoria semántica: qué se embedding, cuándo, pipeline de chunking, modelo de embeddings, Qdrant vs pgvector definitivo | Auditoría completa |

### Entregable inmediato
- Mantener Qdrant como vector store activo
- Documentar `document_chunks.embedding_payload` como columna puente
- Diferir pgvector hasta que haya un pipeline de embeddings en `src/`
- Flowise fuera del roadmap inmediato
