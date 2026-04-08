# Automation Engine V1

Servicio independiente de enrutamiento inteligente de leads y contenidos para el ecosistema cine AI.

## Arquitectura

```
Web Ailink_Cinema ──┐
                    ├──> automation-engine ──> CID
CID ────────────────┤                        ├──> CINE_AI_PLATFORM
CINE_AI_PLATFORM ───┘                        └──> Web Ailink_Cinema
```

## Estructura

```
automation-engine/
  app/
    main.py                 # FastAPI entrypoint, endpoints
    config.py               # Settings via pydantic-settings + .env
    schemas/
      lead_event.py         # LeadEvent model
      script_event.py       # ScriptEvent model
      routing_result.py     # RoutingResult, ScriptRoutingResult
    services/
      directive_loader.py   # Carga directivas markdown
      llm_router.py         # LLM classification (opcional)
      classifier.py         # Keyword fallback + LLM integration
      dispatcher.py         # Orquestador principal de routing
    handlers/
      cid_handler.py        # Forward a CID
      cine_handler.py       # Forward a CINE_AI_PLATFORM
      web_handler.py        # Forward a Web Ailink_Cinema
    directivas/
      leads_classification.md
      campaign_routing.md
      guion_analysis.md
      storyboard_routing.md
  tests/
  requirements.txt
  .env.example
  Dockerfile
  README.md
```

## Endpoints

### GET /health
Health check del servicio.

### POST /route/lead
Clasifica y enruta un lead entrante.

**Request:**
```json
{
  "event_type": "lead_created",
  "source": "web_ailink_cinema",
  "payload": {
    "name": "Laura Martin",
    "email": "laura@atlascine.com",
    "company": "Atlas Cine Studios",
    "message": "Queremos una demo para storyboard IA de una escena de thriller",
    "project_interest": "storyboard IA",
    "source_channel": "website_form"
  }
}
```

**Response:**
```json
{
  "ok": true,
  "classification": "storyboard_ia",
  "lead_type": "inbound_lead",
  "priority": "medium",
  "recommended_campaign": "storyboard_ia_launch",
  "recommended_target": "cine_ai_platform",
  "recommended_secondary_target": "web_ailink_cinema",
  "next_action": "schedule_demo",
  "notes": "Routed via rule_based. Targets: cine_ai_platform, web_ailink_cinema"
}
```

### POST /route/script
Analiza y enruta un guion/escena.

**Request:**
```json
{
  "event_type": "script_received",
  "source": "cid_or_manual",
  "payload": {
    "title": "Escena demo thriller",
    "text": "INT. SALON - NOCHE. La lluvia golpea las ventanas mientras Marta entra con un cuchillo en la mano...",
    "goal": "storyboard_demo"
  }
}
```

**Response:**
```json
{
  "ok": true,
  "content_type": "scene_for_storyboard",
  "recommended_pipeline": "storyboard_pipeline",
  "priority": "medium",
  "notes": "Content: scene_for_storyboard. Pipeline: storyboard_pipeline. Confidence: rule_based"
}
```

## Ejecucion Local

```bash
cd automation-engine

# Crear venv
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Copiar .env
copy .env.example .env       # Windows
cp .env.example .env         # Linux/Mac

# Ejecutar
uvicorn app.main:app --reload --port 8000
```

El servicio arranca en `http://localhost:8000`.

Para desactivar dry_run y conectar OpenAI, edita `.env`:
```
DRY_RUN=false
OPENAI_API_KEY=sk-...
```

## Ejecucion con Docker

```bash
cd automation-engine

# Build
docker build -t automation-engine:v1 .

# Run
docker run -d --name automation-engine -p 8000:8000 --env-file .env automation-engine:v1
```

## Modo Dry Run

Por defecto `DRY_RUN=true`. En este modo:
- No se hacen llamadas a OpenAI
- La clasificacion usa reglas por palabras clave
- Los handlers solo loguean, no hacen HTTP real
- Ideal para desarrollo e integracion

Para produccion con LLM:
1. Set `DRY_RUN=false`
2. Configura `OPENAI_API_KEY`
3. Opcionalmente `OPENAI_BASE_URL` para proxies/compatibles

## Extension

Para agregar nuevas categorias de clasificacion:
1. Editar `INTEREST_KEYWORDS` en `classifier.py`
2. Agregar entrada en `routing_map` en `dispatcher.py`
3. Agregar entrada en `campaign_map` en `dispatcher.py`
4. Crear handler nuevo en `handlers/` si hace falta
5. Crear directiva markdown en `directivas/`
