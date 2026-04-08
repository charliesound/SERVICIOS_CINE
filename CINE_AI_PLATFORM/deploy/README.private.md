# PREDEPLOY PRIVATE PACK

Paquete preparado en laptop sobre disco externo para despliegue posterior en el ordenador de casa.

## Archivos usados
- `docker-compose.private.yml`
- `.env.private.example`
- `.env.private`
- `infra/nginx/default.private.conf`
- `deploy/predeploy-validate.ps1`
- `deploy/start-private.ps1`
- `deploy/stop-private.ps1`
- `deploy/start-comfy-wsl.ps1`
- `infra/scripts/check-comfy-bridge.ps1`
- `infra/scripts/smoke-private.ps1`
- `docs/COMFYUI_BRIDGE_PRIVATE.md`

## Layout persistente esperado en el disco externo
- `X:\CINE_AI_PLATFORM\storage\api\data`
- `X:\CINE_AI_PLATFORM\storage\n8n\data`
- `X:\CINE_AI_PLATFORM\storage\qdrant\storage`
- `X:\CINE_AI_PLATFORM\storage\nginx\logs`

## Fase 1: preparación en laptop

### 1. Crear el env privado

```powershell
Copy-Item .env.private.example .env.private