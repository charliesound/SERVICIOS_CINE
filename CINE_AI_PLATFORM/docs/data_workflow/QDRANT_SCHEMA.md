# Qdrant Vector Schema para Cine AI Platform

En esta fase fundacional, Qdrant servirá para establecer Vector Search y Retrieval-Augmented Generation (RAG) para mantener consistencia visual y narrativa entre proyectos.

## Colecciones Base Propuestas

### 1. `character_concepts`
Almacena descriptores conceptuales de los personajes. Permite agilizar la búsqueda de *loras*, *triggers*, o parecidos visuales cuando se planifica una escena recurrente.
- **Razón:** La persistencia e integración de personajes (Persistent Characters Workflow) manda.
- **Vector Base:** Embeddings de texto (ej. MiniLM o BGE locales) representando la descripción física y de personalidad.
- **Payload / Metadatos (JSON):**
  ```json
  {
    "character_id": "UUID",
    "project_id": "UUID",
    "name": "String",
    "lora_trigger": "String",
    "visual_description": "String"
  }
  ```

### 2. `shot_library`
Almacena metadatos y embeddings (texto/imagen) de planos ya generados exitosamente. Permite la retro-búsqueda visual (ej. "busca todos los planos del proyecto que tengan iluminación nocturna y cámara al hombro").
- **Razón:** Historial de tablero.
- **Vector Base:** CLIP Embedding (imagen final) o Text Embedding del prompt enriquecido.
- **Payload / Metadatos (JSON):**
  ```json
  {
    "shot_id": "UUID",
    "scene_id": "UUID",
    "sequence_id": "UUID",
    "project_id": "UUID",
    "prompt_used": "String",
    "status": "String (rendered, pending)"
  }
  ```

## Criterios Operativos (Qdrant en Docker)
- Se accede intrate-red vía: `http://qdrant:6333` (Rest) o puerto gRPC.
- N8n y la API (Backend) tienen acceso directo a `qdrant` dentro del `docker-compose.private.yml`.
