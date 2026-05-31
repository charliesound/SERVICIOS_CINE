# CID.RAG.QDRANT.CREATE.1 — Creación de colección Qdrant `cid_memory`

## Fecha
2026-05-31

## Comandos usados

### Pre-creación audit
```bash
python scripts/qdrant/inspect_qdrant_collections.py
```
→ 1 colección: `cid_screenwriting_theory` (2773 pts, 96d, Cosine)

### Verificar que no existe
```bash
curl -s http://127.0.0.1:6333/collections/cid_memory
```
→ `Not found: Collection cid_memory doesn't exist!`

### Crear colección
```bash
curl -s -X PUT "http://127.0.0.1:6333/collections/cid_memory" \
  -H "Content-Type: application/json" \
  -d '{"vectors": {"size": 768, "distance": "Cosine"}}'
```
→ `{"result": true, "status": "ok"}`

### Validar creación
```bash
curl -s http://127.0.0.1:6333/collections/cid_memory | jq .
python scripts/qdrant/inspect_qdrant_collections.py
```

## Resultado de creación

| Atributo | Valor |
|---|---|
| Colección | `cid_memory` |
| Status | `green` |
| Vector size | 768 |
| Distance | Cosine |
| Points | 0 |
| Shards | 1 |
| On-disk payload | true |
| HNSW m/ef | 16/100 |
| Index threshold | 10000 |

### Colecciones existentes después de creación

| Colección | Puntos | Vector size | Estado |
|---|---|---|---|
| `cid_screenwriting_theory` | 2773 | 96 | ✅ Preservada |
| `cid_memory` | 0 | 768 | ✅ Creada |

## Configuración final

```json
{
  "name": "cid_memory",
  "vectors": { "size": 768, "distance": "Cosine" },
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

## Rollback seguro

Si es necesario eliminar `cid_memory` (solo la colección vacía, sin datos):

```bash
curl -s -X DELETE "http://127.0.0.1:6333/collections/cid_memory"
```

Esto **no afecta** a `cid_screenwriting_theory` ni a ningún otro dato.

## Próximos pasos

| Fase | Objetivo |
|---|---|
| **CID.RAG.EMBEDDINGS.PIPELINE.1** | Implementar chunking → embeddings → upsert en `src/services/rag/` |
| **CID.RAG.SEARCH.API.1** | Endpoints `/api/rag/search` y `/api/rag/ask` |

## Checklist GO

- [x] `cid_memory` creada con vector_size=768, distance=Cosine
- [x] `cid_screenwriting_theory` preservada con 2773 puntos
- [x] No se insertaron puntos en `cid_memory` (points_count=0)
- [x] No hay errores en Qdrant (status: green)
- [x] Script dry-run de inspección sigue funcionando
- [x] Rollback documentado
