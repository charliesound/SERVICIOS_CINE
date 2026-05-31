# CID.RAG.QDRANT.SCHEMA.1 — Qdrant cid_memory Schema Design

## 1. Resumen ejecutivo

- **Colección única `cid_memory`** con payload indexado para filtrado multi-tenant.
- **Todas las fuentes** de contenido semántico de CID convergen en una sola colección.
- **Payload rico** con 18 campos: identificadores, metadatos, control de versiones y visibilidad.
- **Embeddings 768d con Cosine distance** usando `nomic-embed-text:v1.5` en Ollama.
- **Colección existente `cid_screenwriting_theory`** permanece intacta. Migración opcional en fase futura (CID.RAG.QDRANT.MIGRATE.1).
- **No se crea la colección en esta fase.** Fase de diseño y documentación únicamente.

## 2. Estado actual de Qdrant

| Atributo | Valor |
|---|---|
| Contenedor | `ailinkcinema_qdrant` |
| Estado | Up (healthy) |
| Versión | 1.17.0 |
| Puerto REST | 6333 (127.0.0.1) |
| Puerto gRPC | 6334 (127.0.0.1) |
| Red Docker | `private_net` (172.20.0.4), accesible como `http://qdrant:6333` |
| Colecciones | 1: `cid_screenwriting_theory` |
| Volumen | `qdrant_data` (persistente) |

## 3. Colección existente: `cid_screenwriting_theory`

| Atributo | Valor |
|---|---|
| Puntos | 2773 |
| Vector size | 96 |
| Distance | Cosine |
| Shards | 1 |
| On-disk payload | true |
| Índice HNSW | No construido (threshold 10000, no alcanzado) |
| Payload schema | Libre (sin schema definido) |

### Payload actual

| Campo | Ejemplo |
|---|---|
| `author` | `"El"`, `"Creacion"` |
| `title` | `"Guion robert mckee"`, `"Creacion"` |
| `chapter` | `""` |
| `topic` | `"screenwriting_theory"` |
| `source_file` | `"data/theory/screenwriting/El-Guion-robert-mckee.pdf"` |
| `chunk_index` | `593` |
| `chunk_text` | `"de conflicto internos..."` |

### Notas
- Los embeddings (96d) fueron generados con un modelo no especificado en el payload.
- No hay `project_id` ni `organization_id` — es contenido global de teoría de guion.
- Es segura para coexistir con `cid_memory`.

## 4. Diseño de colección `cid_memory`

### 4.1 Configuración de colección

```json
{
  "name": "cid_memory",
  "vectors": {
    "size": 768,
    "distance": "Cosine"
  },
  "shard_number": 1,
  "replication_factor": 1,
  "on_disk_payload": true,
  "hnsw_config": {
    "m": 16,
    "ef_construct": 100,
    "full_scan_threshold": 10000,
    "on_disk": false
  },
  "optimizer_config": {
    "indexing_threshold": 10000,
    "flush_interval_sec": 5
  }
}
```

**Justificaciones**:
- `size: 768` — compatible con `nomic-embed-text:v1.5` (Ollama). Alternativas: 1024 (mxbai-embed-large), 512 (text-embedding-3-small).
- `distance: Cosine` — estándar para texto, mismo que la colección existente.
- `on_disk_payload: true` — el payload puede crecer sin consumir RAM.
- `indexing_threshold: 10000` — construir índice HNSW solo cuando haya suficientes puntos.
- `on_disk: false` — vectores en RAM para velocidad; si el volumen crece, reconsiderar.

### 4.2 Payload mínimo

| Campo | Tipo | Indexado | Requerido | Descripción |
|---|---|---|---|---|
| `project_id` | `keyword` | ✅ Sí | No | UUID del proyecto. Null para contenido global/teoría. |
| `organization_id` | `keyword` | ✅ Sí | Sí | UUID de la organización (tenant). Siempre requerido. |
| `source_type` | `keyword` | ✅ Sí | Sí | Tipo de fuente (ver §4.3). |
| `source_id` | `keyword` | ✅ Sí | Sí | UUID o identificador único del registro origen. |
| `source_table` | `keyword` | ✅ Sí | Sí | Tabla PostgreSQL origen (ej. `storyboard_shots`). |
| `title` | `text` | No | No | Título descriptivo del chunk o documento. |
| `text` | `text` | No | Sí | Contenido textual del chunk. |
| `chunk_index` | `integer` | ✅ Sí | No | Índice del chunk dentro del documento fuente (0-based). |
| `chunk_count` | `integer` | No | No | Total de chunks del documento fuente. |
| `language` | `keyword` | ✅ Sí | No | Código ISO del idioma (ej. `es`, `en`). Default `es`. |
| `tags` | `list<keyword>` | ✅ Sí | No | Etiquetas libres para filtrar o agrupar. |
| `created_at` | `datetime` | No | Sí | Timestamp de creación del punto. |
| `updated_at` | `datetime` | No | No | Timestamp de última actualización. |
| `version` | `integer` | No | No | Versión del dato (incrementa con cada re-ingest). |
| `visibility` | `keyword` | ✅ Sí | No | `private` (default), `organization`, `public`. |
| `embedding_model` | `keyword` | No | No | Nombre del modelo usado para generar el embedding. |
| `metadata` | `object` | No | No | Objeto JSON libre para metadatos específicos de la fuente. |

**Total: 18 campos.** 8 indexados para filtrado eficiente, 10 sin indexar.

### 4.3 Source types (`source_type`)

| source_type | source_table(s) | Descripción | Prioridad ingestión |
|---|---|---|---|
| `script` | `projects` | Guion completo de un proyecto. Chunking por tokens. | P1 |
| `scene` | `scenes` (si existe) | Escena individual dentro de un guion. | P2 |
| `storyboard_shot` | `storyboard_shots` | Narrativa de cada shot del storyboard. 1 shot = 1 chunk. | P0 |
| `visual_bible` | `project_visual_bibles` | Notas de dirección visual (paleta, tono, referencias). | P2 |
| `character_bible` | `characters` | Biografía y descripción de personajes. | P3 |
| `director_note` | `project_notes` (si existe) | Notas del director sobre escenas o secuencias. | P2 |
| `production_breakdown` | `production_breakdowns` | Desglose de producción. Chunking por 1024 chars. | P2 |
| `document` | `document_chunks`, `project_documents` | Documentos subidos (PDFs, manuales). | P1 |
| `theory` | `cid_screenwriting_theory` | Teoría de guion (colección existente, migración futura). | P4 |
| `workflow_trace` | `workflow_executions` (futuro) | Trazas de ejecución de workflows. | P4 |
| `prompt_asset` | `comfyui_prompts` (futuro) | Prompts de ComfyUI almacenados como assets. | P3 |
| `asset_version` | `asset_versions` (futuro) | Versiones de assets generados. | P4 |

### 4.4 Ejemplo de payload completo

```json
{
  "project_id": "22e145780c004e4e848df9a8ffbea3d0",
  "organization_id": "61a8604bdf1440d8858e2154301c828f",
  "source_type": "storyboard_shot",
  "source_id": "41447ecd-880b-48ec-9ccd-c64d4563a1ed",
  "source_table": "storyboard_shots",
  "title": "INT. CASA - DÍA — Juan entra en la cocina",
  "text": "Juan cruza la puerta de la cocina, mira a su alrededor con desconfianza. La luz de la mañana entra por la ventana.",
  "chunk_index": 0,
  "chunk_count": 1,
  "language": "es",
  "tags": ["interior", "dia", "casa", "juan"],
  "created_at": "2026-05-30T12:00:00Z",
  "updated_at": "2026-05-30T12:00:00Z",
  "version": 1,
  "visibility": "private",
  "embedding_model": "nomic-embed-text:v1.5",
  "metadata": {
    "scene_heading": "INT. CASA - DÍA",
    "shot_type": "medium",
    "character_name": "Juan",
    "sequence_id": "seq_001",
    "sequence_order": 1
  }
}
```

## 5. Estrategia de embeddings

### 5.1 Modelo recomendado

| Parámetro | Valor |
|---|---|
| Modelo | `nomic-embed-text:v1.5` |
| Proveedor | Ollama (local, `ailinkcinema_ollama:11434`) |
| Vector size | 768 |
| Distance | Cosine |
| Licencia | Apache 2.0 |
| Latencia esperada | ~50ms por embedding |

### 5.2 Alternativas

| Modelo | Vector size | Latencia | Costo |
|---|---|---|---|
| `nomic-embed-text:v1.5` | 768 | ~50ms | Gratis (local) |
| `mxbai-embed-large:v1` | 1024 | ~80ms | Gratis (local) |
| `bge-m3` | 1024 | ~100ms | Gratis (local) |
| `text-embedding-3-small` (OpenAI) | 512 | ~200ms | $0.02/1M tokens |
| `text-embedding-004` (Gemini) | 768 | ~150ms | Gratis tier |

### 5.3 Pipeline de embedding

```
text → chunker → chunk_text → Ollama embed → [768 floats] → Qdrant upsert
```

Pseudocódigo:

```python
import requests
import uuid

def embed_text(text: str) -> list[float]:
    resp = requests.post(
        "http://ollama:11434/api/embeddings",
        json={"model": "nomic-embed-text:v1.5", "prompt": text},
        timeout=30,
    )
    return resp.json()["embedding"]

def upsert_point(payload: dict):
    point_id = uuid.uuid5(uuid.NAMESPACE_DNS,
        f"{payload['source_table']}:{payload['source_id']}:{payload.get('chunk_index', 0)}")
    vector = embed_text(payload["text"])
    point = {"id": str(point_id), "vector": vector, "payload": payload}
    requests.put(
        "http://qdrant:6333/collections/cid_memory/points",
        json={"points": [point]},
        timeout=10,
    )
```

### 5.4 Idempotencia

- Cada punto usa `UUID v5` determinístico basado en `source_table:source_id:chunk_index`.
- Re-upsert del mismo chunk siempre produce el mismo UUID → overwrite silencioso.
- No hay duplicados ni orphan data.

## 6. Estrategia de ingestión

### 6.1 Prioridades

| Prioridad | source_type | Tabla | Estimación puntos | Esfuerzo |
|---|---|---|---|---|
| **P0** | `storyboard_shot` | `storyboard_shots` | ~773 | Bajo (1 shot = 1 chunk) |
| **P1** | `script` | `projects.script_text` | ~5000 (11 proyectos × ~500 chunks) | Alto (chunking + embeddings) |
| **P1** | `document` | `project_documents` | Variable | Medio |
| **P2** | `visual_bible` | `project_visual_bibles` | ~14 | Bajo |
| **P2** | `director_note` | (futura) | Variable | Medio |
| **P2** | `production_breakdown` | `production_breakdowns` | ~100 | Bajo |
| **P3** | `character_bible` | `characters` | ~10 | Bajo |
| **P4** | `theory` | Migrar desde `cid_screenwriting_theory` | 2773 | Medio |
| **P4** | `workflow_trace` | (futura) | Variable | Alto |

### 6.2 Estrategia de chunking

| source_type | Método | Tamaño | Overlap |
|---|---|---|---|
| `storyboard_shot` | 1 shot = 1 chunk | Variable (texto completo) | N/A |
| `script` | Token-based | 512 tokens | 64 tokens |
| `visual_bible` | Documento completo (si < 512 tokens) | Variable | N/A |
| `production_breakdown` | Fixed-size chars | 1024 chars | 128 chars |
| `document` | Token-based (depende del tipo) | 512-1024 tokens | 64-128 tokens |
| `theory` | Mantener chunking existente | Variable (ya chunked) | N/A |

### 6.3 Estrategia de actualización

- **Upsert siempre**: mismo UUID v5 → Qdrant sobrescribe.
- **Trigger**: INSERT/UPDATE en tabla origen → background job → re-chunk → re-embed → upsert.
- **Full re-index**: job manual que recorre la tabla completa y upsert todos los puntos.

### 6.4 Estrategia de borrado

- **Borrado físico**: DELETE de puntos Qdrant por filtro `source_table + source_id`.
- **Borrado lógico**: No implementado en Qdrant. Alternativa: marcar `visibility: "deleted"` y excluir en search.
- **Borrado por proyecto**: DELETE con filtro `project_id`.

## 7. Filtros de búsqueda

### 7.1 Filtros obligatorios (implícitos)

- `organization_id` — extraído del JWT, siempre aplicado.
- `visibility` — si el usuario no es admin, excluir `visibility: "private"` de otras organizaciones.

### 7.2 Filtros opcionales

| Parámetro API | Filtro Qdrant |
|---|---|
| `project_id` | `must: [{ key: "project_id", match: { value: project_id } }]` |
| `source_type` | `must: [{ key: "source_type", match: { value: source_type } }]` |
| `tags` | `must: [{ key: "tags", match: { value: tag } }]` (repetir por tag) |
| `language` | `must: [{ key: "language", match: { value: lang } }]` |
| `chunk_index > N` | `must: [{ key: "chunk_index", range: { gte: N } }]` |

### 7.3 Ejemplo de search request a Qdrant

```json
POST /collections/cid_memory/points/search
{
  "vector": [0.123, ...],
  "limit": 10,
  "with_payload": true,
  "score_threshold": 0.7,
  "filter": {
    "must": [
      { "key": "organization_id", "match": { "value": "61a8604bdf1440d8858e2154301c828f" } },
      { "key": "project_id", "match": { "value": "22e145780c004e4e848df9a8ffbea3d0" } },
      { "key": "source_type", "match": { "value": "storyboard_shot" } }
    ],
    "must_not": [
      { "key": "visibility", "match": { "value": "deleted" } }
    ]
  }
}
```

## 8. Colección existente: estrategia de migración (futura)

La colección `cid_screenwriting_theory` (2773 pts, 96d) se migrará a `cid_memory` en una fase posterior:

1. **Re-embed**: los puntos actuales tienen vector size 96 (modelo anterior). Re-embed con `nomic-embed-text:v1.5` produce 768d.
2. **Normalizar payload**: mapear campos antiguos a nuevo schema:
   - `chunk_text` → `text`
   - `source_file` → `metadata.source_file`
   - `topic` → `tags: ["screenwriting_theory"]`
   - `organization_id` → null (contenido global)
3. **Upsert batch** a `cid_memory`.
4. **Preservar** `cid_screenwriting_theory` como respaldo hasta validar.

**No se ejecuta en esta fase.** Pendiente de CID.RAG.QDRANT.MIGRATE.1.

## 9. Plan de implementación por fases

| Fase | Descripción | Dependencias | Esfuerzo est. |
|---|---|---|---|
| **CID.RAG.QDRANT.SCHEMA.1** | ✅ Diseño de schema completo + auditoría (esta fase) | Qdrant operativo | Completado |
| **CID.RAG.QDRANT.CREATE.1** | Crear colección `cid_memory` vía API + configurar payload index fields | CID.RAG.QDRANT.SCHEMA.1 | 1 día |
| **CID.RAG.EMBEDDINGS.PIPELINE.1** | Implementar pipeline chunking → embeddings → upsert en `src/services/rag/` | CID.RAG.QDRANT.CREATE.1 | 3-5 días |
| **CID.RAG.SEARCH.API.1** | Endpoints `/api/rag/search`, `/api/rag/ask` | CID.RAG.EMBEDDINGS.PIPELINE.1 | 3-5 días |
| **CID.RAG.QDRANT.MIGRATE.1** | Migrar `cid_screenwriting_theory` → `cid_memory` | CID.RAG.QDRANT.CREATE.1 | 1 día |
| **CID.RAG.FLOWISE.BRIDGE.1** | Integrar RAG como herramienta Flowise | CID.RAG.SEARCH.API.1 | 2 días |

## 10. Riesgos

| Riesgo | Impacto | Mitigación |
|---|---|---|
| **Payload schema definido sin indexación** | Búsqueda lenta en filtros no indexados | Indexar todos los campos de filtro (8 campos en §4.2) |
| **Mezcla de modelos de embeddings** | Búsqueda inexacta si se mezclan vectores de distintos modelos | Almacenar `embedding_model` en payload. Re-embed al cambiar de modelo. |
| **Crecimiento sin control** | Qdrant consume RAM/CPU | Monitorear points_count, establecer `indexing_threshold`, usar `on_disk_payload: true` |
| **Corrupción de payload** | Datos inconsistentes | Validar payload antes de upsert. `source_type` debe ser uno de los definidos. |
| **Multi-tenant leak** | Fuga de datos entre organizaciones | `organization_id` siempre filtrado. Extraído del JWT, nunca del body. |
| **Colección existente con 96d** | No puede coexistir en `cid_memory` (768d) | Mantener colección separada hasta migrar. |

## 11. Checklist GO/NO-GO

### GO — Requisitos cumplidos:

- [x] Qdrant operativo y saludable (v1.17.0, green status)
- [x] Red interna funcional (`qdrant:6333` resuelve desde backend)
- [x] Colección existente documentada (cid_screenwriting_theory, 2773 pts, 96d)
- [x] Payload schema diseñado con 18 campos
- [x] 12 source types definidos con prioridades
- [x] Estrategia de chunking por source type
- [x] Estrategia de embeddings (nomic-embed-text:v1.5, 768d, Cosine)
- [x] Idempotencia vía UUID v5
- [x] Filtros multi-tenant diseñados
- [x] Estrategia de actualización y borrado
- [x] Plan de migración de colección existente
- [x] Fases de implementación definidas
- [x] Script dry-run de auditoría disponible (`scripts/qdrant/inspect_qdrant_collections.py`)

### NO-GO si:

- [ ] No se ha verificado que `nomic-embed-text:v1.5` está disponible en Ollama.
- [ ] No hay un pipeline de embeddings implementado en `src/`.
- [ ] No se ha creado la colección `cid_memory` (fase CID.RAG.QDRANT.CREATE.1).
- [ ] No hay endpoints de búsqueda implementados.

### Veredicto

**CID.RAG.QDRANT.SCHEMA.1: GO** — El diseño de schema está completo y documentado. La implementación puede comenzar con CID.RAG.QDRANT.CREATE.1.

## 12. Archivos relacionados

- `docs/architecture/cid_memory_rag_design.md` — Diseño de arquitectura RAG general.
- `docs/architecture/pgvector_audit.md` — Auditoría pgvector (NO-GO inmediato).
- `scripts/qdrant/inspect_qdrant_collections.py` — Script dry-run de auditoría Qdrant.
- `.env.example` — Variables de configuración de Qdrant y Ollama.
- `compose.data.yml` — Definición del contenedor Qdrant.
