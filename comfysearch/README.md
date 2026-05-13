# ComfySearch — Buscador Semántico de Workflows para ComfyUI

Encuentra workflows de ComfyUI escribiendo en lenguaje natural:

```
"primer plano dramático estilo Nolan"
"contraplano LTXV con control de eje"
"restauración cartoon 4K con upscale"
"storyboard cinematográfico SDXL"
"doblaje con clonación de voz autorizada"
```

## Stack

- **Backend**: Flask + Qdrant + sentence-transformers
- **Frontend**: HTML/JS (sin dependencias)
- **Indexación**: extracción automática de nodos, tags, fases de producción
- **Ejecución**: envía workflows directamente a ComfyUI via API

## Inicio rápido

```bash
# 1. Levantar Qdrant
docker compose up -d qdrant

# 2. Instalar dependencias
cd apps/api
pip install -r requirements.txt

# 3. Indexar workflows
python scripts/scan_workflows.py
python scripts/ingest_to_qdrant.py

# 4. Lanzar API
python apps/api/app.py

# 5. Abrir
open http://localhost:5055
```

## Docker completo

```bash
docker compose up -d
# API en http://localhost:5055
```

## Estructura

```
comfysearch/
├── apps/
│   ├── api/
│   │   ├── app.py                 # Flask API
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── services/
│   │       ├── workflow_parser.py  # Extrae metadatos de JSON
│   │       ├── embedder.py         # Embeddings (sentence-transformers/Ollama/OpenAI)
│   │       ├── qdrant_store.py     # Almacén vectorial
│   │       └── comfy_client.py     # Envío a ComfyUI
│   └── web/
│       ├── templates/index.html    # Frontend
│       └── static/app.js
├── data/
│   ├── indexed/
│   └── manifests/
├── scripts/
│   ├── scan_workflows.py
│   ├── ingest_to_qdrant.py
│   └── run_search_demo.py
├── config/
│   ├── settings.yaml
│   └── workflow_roots.yaml
├── docker-compose.yml
├── .env.example
└── README.md
```

## API

| Método | Ruta | Descripción |
|--------|------|-------------|
| GET | / | Frontend |
| GET | /health | Health check |
| POST | /search | Búsqueda semántica |
| GET | /workflow/{id} | Detalle + JSON del workflow |
| POST | /run/{id} | Ejecutar en ComfyUI |
| POST | /reindex | Reindexar |
| GET | /scan | Listar workflows encontrados |
| GET | /stats | Estadísticas |

### Ejemplo de búsqueda

```bash
curl -X POST http://localhost:5055/search \
  -H "Content-Type: application/json" \
  -d '{"query": "contraplano dramático LTXV", "top_k": 5}'
```

### Ejemplo de ejecución

```bash
curl -X POST http://localhost:5055/run/<workflow_id> \
  -H "Content-Type: application/json" \
  -d '{"seed": 42, "positive_prompt": "cinematic shot"}'
```

## ComfyUI Multi-instancia

El sistema soporta 4 instancias de ComfyUI:

| Backend | Puerto | Uso |
|---------|--------|-----|
| still | 8188 | Imagen (SDXL, Flux) |
| video | 8189 | Video (WAN, LTXV) |
| dubbing | 8190 | Audio, TTS, voz, lipsync |
| lab | 8191 | Experimental, restauración |

Se detecta automáticamente según los nodos del workflow.
