# CID.RAG.MEMORY.DESIGN.1 — Memoria Semántica / RAG

## 1. Estado actual del stack

```
┌──────────────────────────────────────────────────────────────┐
│                      SERVICIOS CINE                          │
├─────────────┬───────────────┬──────────┬────────────────────┤
│  CID        │  n8n          │  Qdrant  │  ComfySearch       │
│  PostgreSQL │  PostgreSQL   │  1.17.0  │  (api externa)     │
│  schema cid │  schema pub   │  6333    │                    │
├─────────────┴───────────────┴──────────┴────────────────────┤
│  Frontend React                                             │
└──────────────────────────────────────────────────────────────┘
```

### 1.1 Qdrant audit

| Atributo | Valor |
|---|---|
| Contenedor | `ailinkcinema_qdrant` (Up, healthy) |
| Imagen | `qdrant/qdrant:latest` |
| Puerto REST | 6333 (127.0.0.1) |
| Puerto gRPC | 6334 (127.0.0.1) |
| Red | `private_net` (`ailinkcinema_private`, 172.20.0.4) — resuelto vía CID.RAG.QDRANT.NETWORK.PORTABLE.1 |
| Volumen | `qdrant_data` persistente |
| Colecciones | 1: `cid_screenwriting_theory` |
| Puntos | 2773 |
| Vector size | 96 |
| Distancia | Cosine |
| Payload schema | Sin schema definido (payload libre) |

**Colección existente: `cid_screenwriting_theory`**
| Campo | Ejemplo | Uso |
|---|---|---|
| `author` | `"El"`, `"Creacion"` | Autor del documento fuente |
| `title` | `"Guion robert mckee"` | Título |
| `chapter` | `""` | Capítulo (vacío) |
| `topic` | `"screenwriting_theory"` | Tópico fijo |
| `source_file` | `"data/theory/screenwriting/El-Guion-robert-mckee.pdf"` | Ruta del PDF original |
| `chunk_index` | `593` | Índice del chunk |
| `chunk_text` | `"de conflicto internos..."` | Texto completo del chunk |

**Origen de la colección**: Importada por `comfysearch/scripts/ingest_to_qdrant.py`. Son PDFs de teoría de guion (McKee, etc.), no datos de proyectos CID.

### 1.2 CID data audit (candidatos a RAG)

| Tabla | Con texto | Avg len | Max len | Observación |
|---|---|---|---|---|
| `projects` | 11 | 36,065 | 159,319 | Scripts completos — necesitan chunking |
| `storyboard_shots` | 773 | 509 | 1,588 | Narrative text por shot, ideales para RAG |
| `production_breakdowns` | 10 | 3,316 | 10,000 | Análisis de producción |
| `funding_opportunities` | 3 | 65 | 71 | Muy corto, poca utilidad actual |
| `project_visual_bibles` | 0 | — | — | Sin datos |
| `characters` | 0 | — | — | Sin datos |
| `crm_contacts` | 0 | — | — | Sin datos |
| `document_chunks` | 0 | — | — | Tabla vacía, pre-diseñada para RAG |
| `document_assets` | — | — | — | 68 archivos, sin texto extraído |
| `project_documents` | — | — | — | 0 filas — pipeline de documentos no implementado |

### 1.3 Embedding references en src/

**Cero**. No hay código de embeddings, vectores, Qdrant ni RAG en `src/`. El pipeline de `document_chunks` se diseñó (migración de esquema) pero nunca se implementó el código de negocio.

## 2. Arquitectura de memoria semántica propuesta

### 2.1 Estrategia: colección única con filtros

**Colección única** `cid_memory` con payload rico para filtrado por entidad/proyecto/organización, en lugar de una colección por entidad.

**Razones**:
- Qdrant permite filtrado eficiente por payload (`must`, `must_not`, `filter`)
- Simplifica el search: un solo endpoint, un solo índice HNSW
- Reduce mantenimiento (no migrar esquemas de colecciones por entidad)
- La colección existente `cid_screenwriting_theory` se puede migrar a `cid_memory` con payload normalizado

### 2.2 Payload mínimo

```json
{
  "project_id": "uuid",
  "organization_id": "uuid",
  "source_table": "storyboard_shots | projects | production_breakdowns | document_chunks",
  "source_id": "uuid (PK de la fila origen)",
  "content_type": "narrative_text | script_text | breakdown_text | chunk_text | character_bio",
  "text": "contenido textual del chunk",
  "chunk_index": 0,
  "total_chunks": 10,
  "metadata": {
    "title": "nombre del proyecto o documento",
    "scene_heading": "INT. CASA - DÍA",
    "shot_type": "medium",
    "character_name": "Juan"
  },
  "created_at": "2026-05-30T12:00:00Z",
  "updated_at": "2026-05-30T12:00:00Z"
}
```

### 2.3 Campos clave para filtrado Qdrant

| Campo | Indexado | Uso |
|---|---|---|
| `project_id` | Keyword | Filtrar por proyecto |
| `organization_id` | Keyword | Filtrar por tenant |
| `source_table` | Keyword | Filtrar por tipo de entidad |
| `content_type` | Keyword | Filtrar por tipo de contenido |
| `source_id` | Keyword | Lookup exacto |
| `chunk_index` | Integer | Ordenar chunks |

### 2.4 Vector embedding

| Parámetro | Valor inicial | Justificación |
|---|---|---|
| Dimensión | 768 | nomic-embed-text (Ollama) |
| Distancia | Cosine | Estándar para texto |
| Modelo | `nomic-embed-text:v1.5` | Local, 768d, licencia Apache 2 |
| On disk | false (RAM) | 2773 pts × 768 dims × 4 bytes ≈ 8.5 MB — despreciable |

## 3. Pipeline de embeddings

### 3.1 Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────┐
│  CID DB     │────▶│  Chunker     │────▶│  Embedder   │────▶│  Qdrant   │
│  PostgreSQL │     │  (Python)    │     │  (Ollama)   │     │  upsert   │
└─────────────┘     └──────────────┘     └─────────────┘     └───────────┘
       │                   │                     │                   │
       │                   │  ┌──────────────┐   │                   │
       │                   │  │  Splitter     │   │                   │
       │                   │  │  · token      │   │                   │
       │                   │  │  · sentence   │   │                   │
       │                   │  │  · semantic   │   │                   │
       │                   │  └──────────────┘   │                   │
       ▼                   ▼                     ▼                   ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌───────────┐
│  src/       │     │  src/        │     │  Ollama     │     │  Qdrant   │
│  services/  │     │  services/   │     │  container  │     │  REST     │
│  rag/       │     │  rag/        │     │             │     │  6333     │
└─────────────┘     └──────────────┘     └─────────────┘     └───────────┘
```

### 3.2 Chunking

| Estrategia | Para | Tamaño | Overlap |
|---|---|---|---|
| Token-based | `projects.script_text` | 512 tokens | 64 |
| Sentence-based | `storyboard_shots.narrative_text` | 1 shot = 1 chunk | N/A |
| Fixed-size | `production_breakdowns.script_text` | 1024 chars | 128 |
| Semantic | `document_chunks.chunk_text` | Variable (párrafo) | 0 |

El chunking debe preservar:
- `project_id` (heredado de la fuente)
- `organization_id` (heredado)
- `source_table` y `source_id` (para trazabilidad)
- `chunk_index` y `total_chunks` (para reordenamiento)

### 3.3 Embedding model

| Opción | Modelo | Dims | Donde | Costo | Latencia |
|---|---|---|---|---|---|
| **Recomendado** | `nomic-embed-text:v1.5` | 768 | Ollama local | Gratis | ~50ms |
| Alternativa | `mxbai-embed-large:v1` | 1024 | Ollama local | Gratis | ~80ms |
| Alternativa | `bge-m3` | 1024 | Ollama o docker | Gratis | ~100ms |
| Cloud opcional | `text-embedding-3-small` | 512 | OpenAI API | $0.02/1K | ~200ms |
| Cloud opcional | `text-embedding-004` | 768 | Gemini API | Gratis tier | ~300ms |

**Recomendación inicial**: `nomic-embed-text:v1.5` en Ollama (misma instancia que ya corre en el stack). Produce embeddings de 768 dimensiones, licencia Apache 2, funciona offline.

### 3.4 Qdrant upsert

```python
# Pseudocódigo del upsert
def upsert_to_qdrant(points: list[dict]):
    """
    points: lista de dicts con:
      - id: str (UUID v5 basado en source_table + source_id + chunk_index)
      - vector: list[float] (embeddings)
      - payload: dict (ver §2.2)
    """
    response = requests.put(
        "http://qdrant:6333/collections/cid_memory/points",
        json={
            "points": [
                {
                    "id": point["id"],
                    "vector": point["vector"],
                    "payload": point["payload"],
                }
                for point in points
            ]
        },
    )
```

**Idempotencia**: Usar `UUID v5` (namespace + `f"{source_table}:{source_id}:{chunk_index}"`) para que el mismo chunk siempre tenga el mismo ID. Qdrant + upsert = overwrite silencioso.

### 3.5 Search

```python
def search_qdrant(
    query_text: str,
    project_id: str | None = None,
    organization_id: str | None = None,
    source_table: str | None = None,
    limit: int = 10,
    threshold: float = 0.7,
) -> list[dict]:
    """
    Búsqueda semántica con filtros opcionales por proyecto, organización y fuente.
    """
    query_vector = embed(query_text)  # Ollama nomic-embed-text

    filters = []
    if project_id:
        filters.append({"key": "project_id", "match": {"value": project_id}})
    if organization_id:
        filters.append({"key": "organization_id", "match": {"value": organization_id}})
    if source_table:
        filters.append({"key": "source_table", "match": {"value": source_table}})

    payload = {
        "vector": query_vector,
        "limit": limit,
        "with_payload": True,
        "score_threshold": threshold,
    }
    if filters:
        payload["filter"] = {"must": filters}

    response = requests.post(
        "http://qdrant:6333/collections/cid_memory/points/search",
        json=payload,
    )
    return response.json()["result"]
```

### 3.6 Re-rank opcional

Para queries donde el recall importa más que la latencia:

- **Cross-encoder local**: `ms-marco-MiniLM-L-6-v2` en Ollama (o modelo ONNX)
- **Alternativa**: re-rank por similitud de coseno sobre el score de Qdrant (threshold ajustable)
- **Cuándo**: búsquedas multi-chunk o respuestas RAG completas (no search simple)

### 3.7 Respuesta RAG

```python
def rag_answer(query: str, project_id: str) -> str:
    # 1. Buscar chunks relevantes
    chunks = search_qdrant(query, project_id=project_id, limit=5)

    # 2. Construir contexto
    context = "\n\n".join([c["payload"]["text"] for c in chunks])

    # 3. Prompt + LLM (Ollama)
    prompt = f"""Contexto cinematográfico:
{context}

Pregunta: {query}

Responde basándote únicamente en el contexto proporcionado."""

    response = requests.post(
        "http://ollama:11434/api/generate",
        json={"model": "llama3.2", "prompt": prompt, "stream": False},
    )
    return response.json()["response"]
```

## 4. API endpoints futuros

### 4.1 CID REST API (nuevos endpoints en `src/routes/rag.py`)

| Método | Endpoint | Descripción |
|---|---|---|
| `POST` | `/api/rag/ingest/{source_table}/{source_id}` | Ingestar un registro específico |
| `POST` | `/api/rag/ingest/{source_table}` | Re-ingestar toda una tabla (background job) |
| `GET` | `/api/rag/search?q=...&project_id=...` | Búsqueda semántica pública |
| `GET` | `/api/rag/ask?q=...&project_id=...` | Respuesta RAG completa (contexto + LLM) |
| `DELETE` | `/api/rag/{source_table}/{source_id}` | Eliminar embeddings de un registro |
| `GET` | `/api/rag/status` | Estado del pipeline (total indexed, last sync) |

### 4.2 Triggers de ingestión

| Evento | Acción |
|---|---|
| `storyboard_shots` INSERT/UPDATE | Ingest automático del shot |
| `projects.script_text` UPDATE | Re-chunking y re-ingest del script completo |
| `project_documents` INSERT (extracted_text != null) | Chunking + ingest del documento |
| `production_breakdowns` INSERT/UPDATE | Ingest del breakdown |

### 4.3 Webhook (opcional)

```json
POST /api/rag/webhook/ingest
{
  "source_table": "storyboard_shots",
  "source_id": "uuid",
  "action": "upsert | delete"
}
```

## 5. Colecciones Qdrant propuestas

### 5.1 Fase 1: Colección única

```json
{
  "name": "cid_memory",
  "vectors": {
    "size": 768,
    "distance": "Cosine"
  },
  "optimizer_config": {
    "indexing_threshold": 10000
  }
}
```

### 5.2 Fase 2 (futuro): Colecciones separadas (si el volumen lo justifica)

| Colección | Fuentes | Estimación puntos |
|---|---|---|
| `cid_scripts` | projects, project_documents, document_chunks | ~5000 |
| `cid_shots` | storyboard_shots | ~1000 |
| `cid_breakdowns` | production_breakdowns | ~100 |
| `cid_theory` | screenwriting theory (colección existente migrada) | ~3000 |

## 6. Modelos de embeddings

### 6.1 Recomendación (fase 1)

| Componente | Modelo | Proveedor | Estrategia |
|---|---|---|---|
| Embeddings | `nomic-embed-text:v1.5` | Ollama | Local, 768d, Apache 2 |
| LLM RAG | `llama3.2` (8B) | Ollama | Local, 8K contexto |
| Re-rank | `ms-marco-MiniLM-L-6-v2` | Ollama/ONNX | Local, opcional |

### 6.2 Alternativas cloud (fase 2+)

| Proveedor | Modelo embedding | Dims | Latencia | Costo |
|---|---|---|---|---|
| OpenAI | `text-embedding-3-small` | 512 | ~200ms | $0.02/1M tokens |
| OpenAI | `text-embedding-3-large` | 3072 | ~300ms | $0.13/1M tokens |
| Gemini | `text-embedding-004` | 768 | ~150ms | Gratis (60 QPM) |
| Cohere | `embed-multilingual-v3.0` | 1024 | ~200ms | Gratis trial |

## 7. Fases de implementación

| Fase | Descripción | Dependencias | Esfuerzo est. |
|---|---|---|---|
| **CID.RAG.QDRANT.SCHEMA.1** | Crear colección `cid_memory` en Qdrant (vía REST API), migrar `cid_screenwriting_theory` a `cid_memory` con payload normalizado | Qdrant operativo | 1 día |
| **CID.RAG.EMBEDDINGS.PIPELINE.1** | Implementar pipeline de chunking + embeddings + upsert en `src/services/rag/`. Integrar con Ollama (`nomic-embed-text`). Ingestar projects, storyboard_shots, production_breakdowns | CID.RAG.QDRANT.SCHEMA.1 | 3-5 días |
| **CID.RAG.SEARCH.API.1** | Implementar endpoints `/api/rag/search` y `/api/rag/ask` en FastAPI. Integrar con frontend React (caja de búsqueda semántica). | CID.RAG.EMBEDDINGS.PIPELINE.1 | 3-5 días |
| **CID.RAG.FLOWISE.BRIDGE.1** | Integrar CID RAG como herramienta disponible para Flowise. Endpoint `/api/rag/search` expuesto como herramienta/tool compatible con Flowise Agent. | CID.RAG.SEARCH.API.1 | 2 días |

### 7.1 Roadmap visual

```
Semana 1: CID.RAG.QDRANT.SCHEMA.1
Semana 2: CID.RAG.EMBEDDINGS.PIPELINE.1
Semana 3: CID.RAG.SEARCH.API.1
Semana 4: CID.RAG.FLOWISE.BRIDGE.1
```

## 8. Estado de acciones pendientes

### 8.1 Red Qdrant
**✅ SOLUCIONADO** vía `CID.RAG.QDRANT.NETWORK.PORTABLE.1`. `ailinkcinema_qdrant` está en `private_net` (`ailinkcinema_private`, 172.20.0.4), accesible desde backend y comfysearch via `http://qdrant:6333`.

El healthcheck sigue usando `/dev/tcp` (bash shell) pero la conectividad interna funciona correctamente. No requiere port mapping entre contenedores.

### 8.2 Estrategia de IDs
Usar `UUID v5` determinístico para cada punto Qdrant:

```python
import uuid
point_id = uuid.uuid5(uuid.NAMESPACE_DNS, f"{source_table}:{source_id}:{chunk_index}")
```

Ventaja: re-upsert del mismo chunk siempre produce el mismo ID. No hay duplicados.

### 8.3 Workers de ingestión
Los ingest de tablas completas deben ejecutarse como background jobs (no bloquear HTTP request):

- Opción A: Celery + Redis (si se implementa Redis)
- Opción B: FastAPI BackgroundTasks (para volúmenes pequeños)
- Opción C: Task queue simple en asyncio
- Opción D: n8n workflow trigger

**Recomendación**: FastAPI BackgroundTasks para Fase 1, migrar a Celery/Redis si el volumen justifica.

### 8.4 Filtro multi-tenant
TODO search endpoint DEBE aplicar `organization_id` como filtro implícito (igual que el resto de CID). Nunca mostrar puntos de otra organización.

## 9. Seguridad

- El search endpoint requiere autenticación JWT
- `organization_id` se extrae del token (nunca del body/query params)
- Project-scoped: solo devuelve resultados de proyectos donde el usuario es miembro
- Payload no contiene datos sensibles (passwords, tokens, API keys)
- El endpoint `/api/rag/ingest` es admin-only y requiere validación de tenant
- Rate limiting en `/api/rag/search` y `/api/rag/ask` (100 req/min por usuario)

## 10. Métricas y monitoreo

| Métrica | Instrumentación |
|---|---|
| Puntos totales en Qdrant | Cron + healthcheck |
| Latencia de embeddings | Métrica Prometheus en pipeline |
| Latencia de search | Métrica en endpoint |
| Tasa de acierto / recall | Evaluación offline |
| Errores de upsert | Log + alerta |
| Errores de Ollama | Healthcheck + fallback |

## 11. Arquitectura final recomendada

```
                    ┌──────────────────┐
                    │  Frontend React   │
                    │  caja búsqueda    │
                    └────────┬─────────┘
                             │ HTTP (JWT)
                    ┌────────▼─────────┐
                    │  CID Backend     │
                    │  (FastAPI)       │
                    │  src/routes/     │
                    │  rag.py          │
                    │  src/services/   │
                    │  rag/            │
                    │   ├─ chunker.py  │
                    │   ├─ embedder.py │
                    │   ├─ qdrant.py   │
                    │   └─ rag.py     │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
  ┌──────▼──────┐   ┌───────▼────────┐   ┌──────▼──────┐
  │  PostgreSQL  │   │  Ollama        │   │  Qdrant     │
  │  schema cid  │   │  nomic-embed   │   │  cid_memory │
  │               │   │  llama3.2      │   │              │
  └──────────────┘   └────────────────┘   └─────────────┘
```

**Principios**: 
- Pipeline asíncrono (no bloquear requests de usuario para embeddings)
- Idempotencia (mismo chunk = mismo UUID)
- Multi-tenant (organization_id siempre filtrado)
- Extensible (nuevas source_table se agregan con configuración, no código nuevo)

## 12. Priorización de ingestion

| Prioridad | Tabla | Motivo |
|---|---|---|
| P0 | `storyboard_shots` | 773 shots con narrative text rico — impacto inmediato en búsqueda semántica |
| P1 | `projects` | 11 scripts completos — chunking pesado pero contenido valioso |
| P2 | `production_breakdowns` | 10 breakdowns — datos estructurados de producción |
| P3 | `project_visual_bibles` (cuando tenga datos) | Notas de dirección visual |
| P4 | `characters` (cuando tenga datos) | Biografías de personajes |
| P5 | `crm_contacts` (cuando tenga datos) | Contactos de industria |

## 13. Resumen ejecutivo

- **Qdrant está listo**: contenedor operativo, colección existente (`cid_screenwriting_theory`, 2773 pts)
- **CID tiene datos**: 773 storyboard_shots, 11 projects scripts, 10 production_breakdowns listos para RAG
- **Pipeline cero**: no hay código de embeddings ni RAG en `src/` — todo por construir
- **Modelo embeddings**: `nomic-embed-text:v1.5` (Ollama, local, 768d, Apache 2)
- **Colección única**: `cid_memory` con payload rico para filtrado multi-tenant
- **Arquitectura**: chunker → embedder → qdrant upsert → search → (opcional) rerank → LLM RAG
- **API futura**: `/api/rag/ingest`, `/api/rag/search`, `/api/rag/ask`
- **Fases**: Qdrant schema → Pipeline embeddings → Search API → Flowise bridge (~4 semanas)
