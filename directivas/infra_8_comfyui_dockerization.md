# Infra 8 — ComfyUI Dockerization

## Estado validado

### Infra 8E — Imagen candidata

- **Imagen candidata GO**: `yanwk/comfyui-boot:cu130-slim-v2`
- **Puerto temporal de validacion**: `8288`
- **Natiavo 8188**: sigue vivo como fallback.
- **CID routing**: confirmado via env override `COMFYUI_STILL_BASE_URL=http://127.0.0.1:8288`.
- **Health**: API responde HTTP 200; healthcheck Docker esta `unhealthy` por `python` binario ausente (solo `python3`).

### Infra 8G — Primer `/prompt` directo

- **Resultado**: **GO**
- Checkpoint: `realisticVisionV60B1_v51VAE.safetensors`
- Output: `CID_DOCKER_STILL_SMOKE_8G_00001_.png` (351 KB)
- Duracion: 55.16s
- Sin OOM, sin login/redirect, GPU RTX 5090 visible.

### Infra 8H — Smoke infrastructura CID

- **Resultado**: **GO**
- Capa usada: `ComfyUIFactory` → `ComfyUIClient`
- Env override: `COMFYUI_STILL_BASE_URL=http://127.0.0.1:8288`
- Output: `CID_STILL_SMOKE_8H_00001_.png` (338 KB)
- HTTP render endpoint no validado aun (requiere auth real con DB).

## Proximos pasos

1. **Infra 8I** (documentacion y runbook cutover) — completado.
2. **Infra 8J**: endpoint CID con auth real contra Docker still 8288.
3. **Infra 8K**: cutover still 8188 nativo → Docker 8188.
4. **Infra 8L**: extender estrategia a video/dubbing/restoration/3d por instancia.

## Archivos clave

- `compose.comfyui.yml`
- `.env.home.example`
- `docs/COMFYUI_DOCKERIZATION.md`
- `docs/DEPLOY_HOME_GPU.md`
- `docs/CUTOVER_COMFYUI_STILL_DOCKER.md`
