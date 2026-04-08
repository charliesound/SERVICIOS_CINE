# N8N Embed Ingest Flow

## Archivo
- `workflows/n8n/project_context_embed_and_ingest.json`

## Objetivo
- recibir payload textual
- llamar al servicio local de embeddings
- recibir `vector[]` de 384 dimensiones
- llamar al workflow `project_context_ingest`
- terminar con upsert en `cine_project_context`

## Webhook
- `POST /webhook/project-context-embed-ingest`

## Secuencia
1. `Webhook: Embed And Ingest`
2. `Normalize Request`
3. `Create Embedding` -> `http://host.docker.internal:8091/embed`
4. `Build Ingest Payload`
5. `Call Project Context Ingest` -> `http://127.0.0.1:5678/n8n/webhook/project-context-ingest`
6. `Build Response`
7. `Respond Success`

## Payload esperado
```json
{
  "text": "Plano nocturno con reflejos en asfalto mojado.",
  "project_id": "project-001",
  "sequence_id": "seq-010",
  "scene_id": "scene-020",
  "shot_id": "shot-030",
  "entity_type": "shot_note",
  "title": "Plano recurso calle mojada",
  "content": "Referencia nocturna con reflejos frios y camara baja.",
  "tags": ["night", "rain", "reference"],
  "source": "editorial_note",
  "created_at": "2026-04-03T20:15:00Z",
  "point_id": "project-001:seq-010:scene-020:shot-030:shot_note:custom"
}
```

## Response esperada
```json
{
  "ok": true,
  "embedding_model": "BAAI/bge-small-en-v1.5",
  "dimensions": 384,
  "collection": "cine_project_context",
  "point_id": "project-001:seq-010:scene-020:shot-030:shot_note:custom",
  "payload": {
    "project_id": "project-001",
    "entity_type": "shot_note"
  },
  "qdrant": {}
}
```

## Uso base
1. arrancar servicio local de embeddings en `127.0.0.1:8091`
2. importar y activar `project_context_ingest.json`
3. importar y activar `project_context_embed_and_ingest.json`
4. enviar payload textual al nuevo webhook
