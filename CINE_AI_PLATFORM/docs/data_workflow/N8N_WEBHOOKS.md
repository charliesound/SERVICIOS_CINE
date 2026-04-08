# N8N Workflows y Webhooks Base

El objetivo de n8n en el **Private Pack** es actuar de intermediario (Async Queue, Retry Engine) entre la API sincrónica y el motor asíncrono de ComfyUI en WSL2.

## Arquitectura de Ejecución

1. **API (Backend) -> N8N:** Llama a un Webhook sincrónico o encolable enviando el payload del Shot.
2. **N8N -> ComfyUI:** N8n traduce o enjabona el payload hacia el `/prompt` de ComfyUI.
3. **ComfyUI -> N8N / API:** Tras renderizar el Job, n8n guarda la imagen y comunica al backend la actualización del registro en Base de datos (vía SQLite directo o vía Endpoint interno de la API).

## 1. Webhook Core: `/webhook/render-shot`

- **Método:** `POST`
- **Autenticación Base:** Header Auth (Ver `.env.private.example` para `N8N_ENCRYPTION_KEY` u otro Header Token).
- **Estructura Payload Esperada (Backend -> n8n):**
  ```json
  {
    "action": "trigger_render",
    "project_id": "123e4567-e89b-12d3...",
    "scene_id": "123e4567-...",
    "shot_id": "123e4567-...",
    "comfy_workflow_override": null,
    "prompt_data": {
       "positive": "Ext. Mars surface, cinematic lighting, raw photo",
       "negative": "text, watermark, poor anatomy, deformed",
       "seed": 102456,
       "steps": 25
    }
  }
  ```

## 2. Acceso a Variables Entorno
Asegúrate de configurar los nodos con la funcionalidad Expression usando `$env` global si pasas variables en compose, o directamente llamando a `http://host.docker.internal:8188` (puente seguro de WSL2).
