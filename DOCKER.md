# SERVICIOS_CINE - Docker actual

Este documento refleja la configuracion Docker activa del proyecto en WSL2/Ubuntu.

## Stack actual

- `backend` -> API principal FastAPI en puerto `8000`
- `frontend` -> frontend principal compilado, servido por Caddy
- `cine-api` -> API de `CINE_AI_PLATFORM` en puerto `3001`
- `cine-web` -> frontend de `CINE_AI_PLATFORM` en puerto `8080`
- `automation-engine` -> motor de automatizacion en puerto `8001`
- `n8n` -> automatizaciones en puerto `5678`
- `qdrant` -> vector DB en puertos `6333` y `6334`
- `redis` -> cache/cola en puerto `6379`
- `caddy` -> reverse proxy en `80` y `443`

## Archivos clave

- `docker-compose.yml`
- `Caddyfile`
- `.env`
- `README_WSL2.md`
- `README_TAILSCALE.md`

## Arranque rapido

```bash
cd /opt/SERVICIOS_CINE
docker-compose up -d --build
docker-compose ps
```

Logs:

```bash
docker-compose logs -f
```

Detener:

```bash
docker-compose down
```

## URLs principales

### Local

- App principal: `http://localhost`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- CINE Web: `http://localhost/cine/`
- CINE API: `http://localhost/cine/api/`
- Automation: `http://localhost/automation/health`
- n8n: `http://localhost/n8n/`
- Qdrant: `http://localhost/qdrant/collections`

### Tailscale

- App principal: `http://100.105.161.84`
- Backend API: `http://100.105.161.84:8000`
- API Docs: `http://100.105.161.84:8000/docs`
- CINE Web: `http://100.105.161.84/cine/`
- CINE API: `http://100.105.161.84/cine/api/`
- Automation: `http://100.105.161.84/automation/health`
- n8n: `http://100.105.161.84/n8n/`
- Qdrant: `http://100.105.161.84/qdrant/collections`

## Validacion rapida

```bash
curl http://localhost:8000/health
curl http://localhost/automation/health
curl http://localhost/cine/health
curl http://localhost/n8n/
curl http://localhost/qdrant/collections
```

## ComfyUI

Los backends ComfyUI siguen corriendo fuera de Docker y el backend los consume por `host.docker.internal`.

Puertos esperados:

- `8188` still
- `8189` video
- `8190` dubbing
- `8191` lab

Verificacion:

```bash
docker exec -it servicios_cine_backend curl http://host.docker.internal:8188/system_stats
```

## Troubleshooting

### El stack no arranca

```bash
docker-compose ps
docker-compose logs --tail=100
```

### Reconstruir desde cero

```bash
docker-compose up -d --build
```

### Caddy responde pero una ruta falla

```bash
docker-compose logs caddy --tail=100
```

### HTTPS muestra advertencia

El certificado es autofirmado. Usa HTTP o acepta la excepcion del navegador.

## Referencias

- WSL2: `README_WSL2.md`
- Tailscale: `README_TAILSCALE.md`
