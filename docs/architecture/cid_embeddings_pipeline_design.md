# Diseño del Pipeline de Embeddings para CID (RAG)

## 1. Auditoría de fuentes candidatas en PostgreSQL

| Tabla | Descripción | Comentario de idoneidad |
|-------|--------------|--------------------------|
| `projects.script_text` | Texto completo del guion del proyecto. | Fuente primaria de contenido narrativo. |
| `storyboard_shots` | Información de cada shot del storyboard (descripción, referencias visuales). | Gran valor semántico para búsquedas visual‑textuales. |
| `media_assets` | Metadatos de assets multimedia (tipo, tags, descripción, ruta). | Excelente fuente para recuperación basada en assets. |
| `project_jobs` | Jobs de render/composición, incluye prompts y trazabilidad de salida. | Permite indexar prompts y resultados de ComfyUI. |
| `job_history` | Histórico de ejecuciones de jobs. | Util para auditoría pero menos relevante para búsqueda directa. |
| `production_breakdowns` | Desglose de producción (escenas, unidades, recursos). | Puede servir como documentos de planificación. |
| `visual_bible` (si existe) | Guías visuales y referencias de estilo. | Fuente complementaria de estilo visual. |
| `character_bible` (si existe) | Descripciones de personajes, arcos, atributos. | Útil para búsquedas de caracteres/roles. |
| `director_notes` (si existe) | Comentarios y decisiones del director. | Valor agregado para contexto creativo. |

## 2. Fuentes iniciales recomendadas para MVP

- **`projects.script_text`** – texto del guion, chunked por escenas.
- **`storyboard_shots`** – un punto por shot.
- **`media_assets`** – metadata de assets (tipo, tags, descripción).
- **`project_jobs`** – prompts de render/composición cuando contienen trazabilidad útil.

Estas fuentes cubren contenido narrativo, visual y de generación, ofreciendo una base sólida para pruebas de relevancia.

## 3. Estrategia de Chunking

| Fuente | Unidad de chunk | Tamaño objetivo | Comentario |
|--------|----------------|----------------|-----------|
| `projects.script_text` | Escena o bloque de 800‑1200 tokens (≈ 4‑6 párrafos). | 800‑1200 tokens | Preserva continuidad semántica y permite búsquedas por escena. |
| `storyboard_shots` | 1 shot → 1 punto. | 1 punto por shot | Cada shot ya es una unidad lógica con descripción y referencias. |
| `project_jobs` (prompts) | 1 prompt/render job → 1 punto. | 1 punto por prompt | Mantiene trazabilidad entre prompt y salida. |
| `media_assets` | 1 asset metadata → 1 punto. | 1 punto por asset | Incluye tags, descripción, tipo, ruta. |
| `production_breakdowns` | Unidad de desglose (p.ej., “unit” o “scene”) → 1 punto. | 1 punto por unidad |

### Chunking implementation sketch (pseudocode)
```python
def chunk_script(text: str) -> List[str]:
    # split by double newline (scene separator)
    scenes = text.split("\n\n")
    chunks = []
    for scene in scenes:
        tokens = tokenizer.encode(scene)
        # split further if >1200 tokens
        for i in range(0, len(tokens), 1000):
            chunk = tokenizer.decode(tokens[i:i+1000])
            chunks.append(chunk)
    return chunks
```

## 4. Estrategia de Idempotencia

- **UUID v5 determinístico** basado en los siguientes componentes concatenados:
  ```
  f"{organization_id}:{project_id}:{source_table}:{source_id}:{chunk_index}:{version}"```
- `version` permite forzar re‑indexado (e.g., al cambiar algoritmo de chunking).
- Antes de **upsert** a Qdrant, se verifica si el UUID ya existe; si es idéntico, se ignora la inserción.
- **Re‑indexado por proyecto**: se listan todos los puntos con `payload.project_id` y se comparan timestamps/versions; se actualizan solo los que cambian.

## 5. Diseño de Servicios Backend

```
src/
├─ services/
│   ├─ rag_embedding_service.py      # Obtiene embeddings desde provider
│   ├─ qdrant_memory_service.py      # Wrapper de Qdrant (upsert, search, status)
│   └─ cid_memory_ingestion_service.py # Orquesta extracción, chunking, idempotencia, upsert
└─ api/
    └─ routes/
        └─ memory_routes.py           # Endpoints definidos abajo
```

### RAGEmbeddingService
- `embed_texts(texts: List[str]) -> List[List[float]]`
- Selecciona provider via env `EMBEDDING_PROVIDER`.
- Actualmente usa Ollama client; futura extensión a OpenAI.

### QdrantMemoryService
- `upsert(points: List[PointStruct])`
- `search(query_vec, filter)`
- `status(project_id)` → número de points, última actualización.

### CIDMemoryIngestionService
- `index_project(project_id: UUID)`
  1. Verifica permisos (org from JWT).
  2. Consulta fuentes seleccionadas (SQL vía async ORM).
  3. Aplica chunking según tabla.
  4. Genera UUID v5 determinístico.
  5. Llama a `RAGEmbeddingService` → embeddings.
  6. Upserta a Qdrant vía `QdrantMemoryService`.

## 6. Endpoints mínimos (FastAPI)

```python
@router.post("/api/projects/{project_id}/memory/index")
async def index_memory(
    project_id: UUID,
    background: BackgroundTasks,
    request: Request,
    user=Depends(get_current_user),
):
    # Validar organización y permisos
    background.add_task(
        CIDMemoryIngestionService().index_project, project_id
    )
    return {"detail": "Indexación iniciada"}

@router.get("/api/projects/{project_id}/memory/status")
async def memory_status(project_id: UUID, user=Depends(get_current_user)):
    status = await QdrantMemoryService().status(project_id)
    return status

class SearchPayload(BaseModel):
    query: str
    top_k: int = 10
    filters: Optional[dict] = None

@router.post("/api/projects/{project_id}/memory/search")
async def search_memory(
    project_id: UUID,
    payload: SearchPayload,
    user=Depends(get_current_user),
):
    query_vec = await RAGEmbeddingService().embed_texts([payload.query])
    results = await QdrantMemoryService().search(
        query_vec[0], payload.top_k, payload.filters, project_id
    )
    return results
```

## 7. Seguridad

- **JWT** incluye `organization_id` y `user_id`. Nunca confiar en valores de cuerpo de solicitud.
- Cada endpoint valida que `project_id` pertenezca a la organización del JWT.
- Filtros obligatorios en búsquedas: `filter = {"must": [{"key": "organization_id", "match": {"value": org_id}}, {"key": "project_id", "match": {"value": project_id}}]}`
- Sólo usuarios con rol `admin` de la organización pueden ejecutar búsquedas **globales** (sin `project_id`).
- Todas las llamadas a Qdrant usan TLS (configurable en env `QDRANT_TLS`).

## 8. Provider de Embeddings

### Configuración vía variables de entorno
```
EMBEDDING_PROVIDER=ollama           # "ollama" o "openai"
EMBEDDING_MODEL=nomic-embed-text:v1.5
EMBEDDING_VECTOR_SIZE=768
OLLAMA_URL=http://ollama:11434
OPENAI_API_KEY=...   # Sólo si provider == openai
```
- El provider se inicializa una única vez al arranque del proceso.
- Se provee una **factory** que devuelve la implementación concreta.
- **Futuro**: Añadir `openai` con `text-embedding-ada-002` (dim 1536) y un conversor de tamaño.

## 9. Plan de Pruebas

| Tipo | Objetivo | Alcance |
|------|----------|---------|
| **Unit** | Chunking de script | `test_chunk_script` asegura que cada chunk ≤ 1200 tokens y que la cantidad esperada de chunks se genera. |
| **Unit** | UUID determinístico | `test_uuid_consistency` verifica que dos ejecuciones con mismos parámetros generan el mismo UUID. |
| **Mock Provider** | `EmbeddingProviderMock` devuelve vectores constantes; se verifica que `RAGEmbeddingService` delega correctamente. |
| **Integration** | Upsert payload | Usa un Qdrant client en modo **in‑memory** (`qdrant-client` con `:memory:`) para comprobar que `upsert` crea puntos con los metadatos esperados. |
| **Integration** | Search con filtros | Inserta varios puntos y verifica que la búsqueda con `organization_id`/`project_id` devuelve exclusivamente los permitidos. |
| **Smoke** | Indexado completo de un proyecto QA | Ejecutar endpoint `/memory/index` contra base de datos de pruebas (una película corta) y validar que `status.points_count` > 0. |

## 10. Informe entregable

1. **Fuentes MVP** – lista y justificación (ver sección 2).
2. **Arquitectura de servicios** – diagramas de componentes y flujos (textual descripción arriba).
3. **Endpoints propuestos** – firmas, payloads, respuestas (ver sección 6).
4. **Esquema de payload final** – ejemplo de punto Qdrant:
   ```json
   {
     "id": "uuid-v5-string",
     "vector": [0.12, ...],
     "payload": {
       "organization_id": "org-123",
       "project_id": "proj-456",
       "source_table": "projects.script_text",
       "source_id": 789,
       "chunk_index": 3,
       "text": "...",
       "created_at": "2026-05-31T13:45:00Z"
     }
   }
   ```
5. **Riesgos**
   - **Duplicados** si el algoritmo de chunking cambia sin actualizar `version`.
   - **Latencia** al generar embeddings en masa (mitigar con batching y workers).
   - **Pérdida de consistencia** si la tabla fuente se modifica sin re‑indexado.
   - **Seguridad**: exposición accidental de `organization_id` en logs.
6. **Plan de implementación por fases**
   - *Fase 1*: PoC en entorno local con proyecto de ejemplo → validar chunking y upsert.
   - *Fase 2*: Exponer endpoint `/index` en staging, pruebas de carga.
   - *Fase 3*: Añadir provider OpenAI, pruebas de compatibilidad.
   - *Fase 4*: Monitoreo y alertas de Qdrant (tamaño, latencia).
7. **Criterios GO/NO‑GO** para pasar a OpenCode
   - **GO**: Todas las pruebas unitarias pasan, `status.points_count` incrementa >0 en el proyecto QA, latencia de búsqueda < 200 ms con 10 k points.
   - **NO‑GO**: Duplicados detectados en re‑indexado, fallos de permiso en endpoints, exposición de secretos en logs.

---

**Próximos pasos**: Tras revisión y aprobación de este diseño, se podrá iniciar la fase de implementación siguiendo el plan por fases arriba descrito.
