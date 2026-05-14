# Infra 8 — ComfyUI Dockerization

## Estado validado (Infra 8E)

- **Imagen candidata GO**: `yanwk/comfyui-boot:cu130-slim-v2`
- **Puerto temporal de validacion**: `8288`
- **Natiavo 8188**: sigue vivo como fallback.
- **CID routing**: confirmado via env override `COMFYUI_STILL_BASE_URL=http://127.0.0.1:8288`.
- **Health**: API responde HTTP 200; healthcheck Docker esta `unhealthy` por `python` binario ausente (solo `python3`).
- **No generar** hasta Infra 8G.
- **No `/prompt`** hasta autorizacion explicita.

## Proximo paso

**Infra 8G**: primer `/prompt` minimo controlado con workflow tiny/safe, pocos pasos, output en `/mnt/g/COMFYUI_HUB/output/still`. Sin tocar nativo 8188.

## Archivos clave

- `compose.comfyui.yml`
- `.env.home.example`
- `docs/COMFYUI_DOCKERIZATION.md`
- `docs/DEPLOY_HOME_GPU.md`
