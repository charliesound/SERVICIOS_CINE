# Backend Semantic Context

## Rutas nuevas
- `POST /api/context/semantic/ingest`
- `POST /api/context/semantic/search`

## Dependencias runtime
- embeddings service local
- colección Qdrant `cine_project_context`

## Request base para ingest

```json
{
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
  "point_id": "project-001:seq-010:scene-020:shot-030:shot_note:custom",
  "text": "Plano recurso calle mojada. Referencia nocturna con reflejos frios y camara baja."
}