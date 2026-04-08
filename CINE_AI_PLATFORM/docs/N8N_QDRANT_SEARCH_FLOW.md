# N8N Qdrant Search Flow

## Archivo
- `workflows/n8n/project_context_search.json`

## Objetivo
- recibir consulta textual
- generar embedding local de 384 dimensiones
- buscar en `cine_project_context`
- aplicar filtros por metadatos si se envian
- responder resultados normalizados

## Webhook
- `POST /webhook/project-context-search`

## Payload esperado
```json
{
  "text": "lluvia nocturna reflejos tension",
  "project_id": "project-001",
  "sequence_id": "seq-010",
  "scene_id": "scene-020",
  "shot_id": "shot-030",
  "entity_type": "shot_note",
  "tags": ["night", "rain"],
  "source": "editorial_note",
  "limit": 5
}
```

## Secuencia
1. `Webhook: Project Context Search`
2. `Normalize Search Request`
3. `Create Query Embedding` -> `http://host.docker.internal:8091/embed`
4. `Build Search Request`
5. `Search Qdrant` -> `http://qdrant:6333/collections/cine_project_context/points/search`
6. `Normalize Search Results`
7. `Respond Search Results`

## Filtros soportados
- `project_id` obligatorio
- `sequence_id`
- `scene_id`
- `shot_id`
- `entity_type`
- `tags`
- `source`
- `limit` opcional, default `5`, max `20`

## Respuesta normalizada
```json
{
  "ok": true,
  "collection": "cine_project_context",
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "dimensions": 384,
  "query": {
    "text": "lluvia nocturna reflejos tension",
    "project_id": "project-001"
  },
  "count": 1,
  "results": [
    {
      "point_id": "project-001:seq-010:scene-020:shot-030:shot_note:custom",
      "score": 0.91,
      "project_id": "project-001",
      "sequence_id": "seq-010",
      "scene_id": "scene-020",
      "shot_id": "shot-030",
      "entity_type": "shot_note",
      "title": "Plano recurso calle mojada",
      "content": "Referencia nocturna con reflejos frios y camara baja.",
      "tags": ["night", "rain", "reference"],
      "source": "editorial_note",
      "created_at": "2026-04-03T20:15:00Z"
    }
  ]
}
```

## Uso base
1. arrancar servicio local de embeddings en `127.0.0.1:8091`
2. importar y activar `project_context_search.json`
3. enviar payloads de consulta textual al webhook
