# Embeddings Strategy

## Decision base
- servicio local HTTP simple
- modelo: `BAAI/bge-small-en-v1.5`
- libreria: `fastembed`
- dimensiones objetivo: `384`

## Endpoint minimo
- `POST /embed`

## Request minimo
```json
{
  "text": "Plano nocturno con reflejos en asfalto mojado.",
  "metadata": {
    "project_id": "project-001",
    "entity_type": "shot_note"
  }
}
```

## Response minima
```json
{
  "ok": true,
  "model": "BAAI/bge-small-en-v1.5",
  "dimensions": 384,
  "vector": [0.1, -0.2, 0.3],
  "metadata": {
    "project_id": "project-001",
    "entity_type": "shot_note"
  }
}
```

## Uso previsto
1. recibir `text`
2. generar embedding local de 384 dimensiones
3. reenviar `vector` a backend o n8n
4. n8n hace upsert en `cine_project_context`

## Integracion base con n8n
- n8n puede llamar este servicio con `HTTP Request`
- despues reutiliza `project_context_ingest.json`
- el payload final hacia Qdrant debe incluir `vector[]`

## Ruta de servicio
- codigo: `services/embeddings/app.py`
- request ejemplo: `services/embeddings/sample_request.json`
