# Qdrant Base Schema

## Collection base
- Nombre: `cine_project_context`
- Vector size: `384`
- Distance: `Cosine`
- Uso: contexto editorial, narrativo y operativo de proyecto cinematográfico

## Nota sobre embeddings
Esta colección está preparada para vectores de **384 dimensiones**.  
Todos los payloads enviados al workflow de ingest deben incluir un `vector[]` con exactamente esa dimensionalidad.

## Payload base

```json
{
  "project_id": "project-001",
  "sequence_id": "seq-010",
  "scene_id": "scene-020",
  "shot_id": "shot-030",
  "entity_type": "shot_note",
  "title": "Plano recurso calle mojada",
  "content": "Referencia nocturna con reflejos fríos y cámara baja.",
  "tags": ["night", "rain", "reference"],
  "source": "editorial_note",
  "created_at": "2026-04-03T20:15:00Z"
}