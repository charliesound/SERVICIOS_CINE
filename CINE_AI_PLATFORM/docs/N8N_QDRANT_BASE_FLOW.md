# N8N Qdrant Base Flow

## Workflow 1: bootstrap de coleccion
Archivo:
- `workflows/n8n/qdrant_bootstrap_collection.json`

Secuencia:
1. `Manual Trigger`
2. `Create Collection`
3. crear indexes base para `project_id`, `sequence_id`, `scene_id`, `shot_id`, `entity_type`, `tags`, `source`, `created_at`

Destino Qdrant:
- `http://qdrant:6333/collections/cine_project_context`

## Workflow 2: ingest de contexto
Archivo:
- `workflows/n8n/project_context_ingest.json`

Webhook:
- `POST /webhook/project-context-ingest`

Secuencia:
1. recibir payload
2. normalizar ids, tags, timestamps y `point_id`
3. validar `vector[]`
4. hacer upsert en `cine_project_context`
5. responder JSON con `ok`, `collection`, `point_id`, `payload`, `qdrant`

## Payload minimo esperado
```json
{
  "project_id": "project-001",
  "entity_type": "scene_note",
  "title": "Tension previa al asalto",
  "content": "La escena debe sentirse contenida y silenciosa.",
  "source": "writer_room",
  "vector": [0.12, -0.03, 0.44],
  "tags": ["tension", "silence"],
  "created_at": "2026-04-03T20:15:00Z"
}
```

## Payload completo soportado
```json
{
  "collection": "cine_project_context",
  "point_id": "custom-point-id",
  "vector": [0.12, -0.03, 0.44],
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
```

## Uso base
1. importar los dos workflows en n8n
2. ejecutar `qdrant_bootstrap_collection.json` una vez
3. activar `project_context_ingest.json`
4. enviar payloads con embeddings ya generados en `vector`
