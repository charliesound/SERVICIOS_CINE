# Integracion ComfyUI (externo por HTTP)

## Objetivo
Integrar render jobs MVP contra ComfyUI externo sin acoplar ComfyUI al despliegue Docker del proyecto.

## Principios
- ComfyUI es **opcional**.
- ComfyUI queda **fuera de Docker Compose**.
- El frontend no llama ComfyUI directamente.
- El backend actua como frontera y control de estado.

## Variables de entorno
- `COMFYUI_BASE_URL`
  - local: `http://127.0.0.1:8188`
  - WSL+Docker: `http://host.docker.internal:8188`
- `COMFYUI_TIMEOUT_SECONDS`
  - timeout global para submit y polling minimo.

## Cliente ComfyUI (actual)
Implementacion: `apps/api/src/services/comfyui_client.py`

Funciones principales:
- `check_availability()`
- `submit_prompt(payload)` -> `POST /prompt`
- `get_history(prompt_id)` -> `GET /history/{prompt_id}`
- `get_prompt_state(prompt_id)` -> normaliza estado (`running|succeeded|failed`)
- `poll_prompt_until_terminal(prompt_id)` -> polling hasta estado terminal o timeout

## Flujo real en render jobs
1. Backend crea job en `queued`.
2. Cambia a `running`.
3. Submit a ComfyUI (`/prompt`) y obtiene `prompt_id`.
4. Polling de `history/{prompt_id}`.
5. Cierre en:
   - `succeeded` si history confirma finalizacion verificable
   - `failed` si history/comfy reporta error manejable
   - `timeout` si expira la ventana de espera

## Diferencia clave
- **Prompt aceptado** (`/prompt` OK) no implica finalizacion.
- **Finalizacion verificada** requiere evidencia en `history` para marcar `succeeded`.

## Estado de salud
- `GET /api/health` -> estado base de API + integracion opcional.
- `GET /api/health/details` -> `health.integrations.comfyui`.
- `GET /api/ops/status` -> lectura operativa rapida para demo.

## Politica de exposicion
- No publicar ComfyUI en internet.
- Exponer solo Nginx + API.
- ComfyUI se consume via `COMFYUI_BASE_URL` desde backend.

## Limitaciones actuales
- No hay worker distribuido/cola externa.
- No hay media-management de outputs finales.
- Verificacion de finalizacion es minima (history polling), suficiente para homelab demo.
