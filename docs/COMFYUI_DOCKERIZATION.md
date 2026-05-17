# ComfyUI Dockerization Skeleton (Infra 8B)

## 1) Objetivo

- Definir una base Docker Compose para 5 instancias ComfyUI GPU sin tocar la instalacion nativa actual.
- Preparar validacion de configuracion (`docker compose config`) sin levantar contenedores.

## 2) Arquitectura de 5 servicios

- `comfyui-still` -> puerto 8188
- `comfyui-video` -> puerto 8189
- `comfyui-dubbing` -> puerto 8190
- `comfyui-restoration` -> puerto 8191
- `comfyui-3d` -> puerto 8192

Todos en profile `with-comfyui`, con bind en host `127.0.0.1` por defecto y red `private_net`.

## 3) Por que no exponer ComfyUI al usuario

- El usuario opera contra CID, no contra endpoints directos ComfyUI.
- CID controla routing por `task_type`, validaciones y fallback operativo.
- Reducir superficie de ataque evita exposicion de puertos sensibles y payloads de render.

## 4) Routing CID por tarea

- `still`/`storyboard` -> 8188
- `video`/`cine` -> 8189
- `dubbing`/`audio` -> 8190
- `restoration`/`conform`/`cleanup` -> 8191
- `3d` -> 8192

## 5) Modelos: bind mounts, sin copiar 2.6 TB

- Source of truth de modelos en host: `/mnt/i/COMFYUI_OK/models`.
- Los servicios montan `models` en modo read-only (`:ro`).
- No se duplican modelos grandes en volumen Docker.
- Source of truth operativo para I/O y workflows: `/mnt/g/COMFYUI_HUB`.
- `input`, `output`, `user` y `workflows` se montan en read-write.
- No usar symlinks de `~/ai/ComfyUI_instances/*` como fuente principal de modelos.

## 6) Imagen ComfyUI parametrizada

- `COMFYUI_IMAGE` queda obligatorio en compose: `${COMFYUI_IMAGE:?Set COMFYUI_IMAGE in .env}`.
- No se asume un tag concreto.
- Validar tag e imagen reales antes del primer `docker compose up`.

Ejemplos a evaluar:

- `aidockorg/comfyui-cuda:<tag>`
- una imagen custom interna compatible con ComfyUI

## 7) Primer arranque recomendado (cuando se habilite)

1. Levantar solo `comfyui-still` para validar imagen, CUDA, custom nodes y health.
2. Levantar `comfyui-video` y verificar VRAM y colas.
3. Levantar `comfyui-dubbing` y `comfyui-restoration`.
4. Levantar `comfyui-3d` y validar mounts compartidos de modelos.

## 8) Riesgos principales

- Compatibilidad de `custom_nodes` con la imagen elegida.
- Dependencias CUDA/cuDNN del contenedor.
- Saturacion de VRAM al correr 5 instancias simultaneas.
- Puertos ocupados (8188-8192) mientras siga ComfyUI nativo.
- Permisos de escritura en `input/output/user`.

## 9) Regla de seguridad de migracion

- No borrar ni desactivar ComfyUI nativo hasta validar:
  - health por instancia,
  - latencia y estabilidad,
  - routing CID extremo a extremo,
  - calidad de outputs esperados.

## 10) Comandos de validacion sin levantar

```bash
COMFYUI_IMAGE=local/comfyui-placeholder:latest \
docker compose -f compose.base.yml -f compose.comfyui.yml --profile with-comfyui config >/dev/null

COMFYUI_IMAGE=local/comfyui-placeholder:latest \
docker compose -f compose.base.yml -f compose.comfyui.yml -f compose.comfyui.gpu.yml --profile with-comfyui config >/dev/null

./scripts/smoke_comfyui_stack.sh
```

## Primer arranque seguro: still en puerto temporal 8288

- No detener ComfyUI nativo en esta fase.
- Si `8188` esta ocupado por native still, usar puerto host temporal.
- Configurar en entorno de prueba:

```bash
COMFYUI_STILL_HOST_PORT=8288
```

- El puerto interno del contenedor se mantiene en `8188`.
- URL de validacion aislada:

```text
http://127.0.0.1:8288/system_stats
```

- No conectar CID todavia al Docker still.
- No modificar `COMFYUI_STILL_BASE_URL` global salvo prueba aislada controlada.

## Imagen yanwk/comfyui-boot

- `yanwk/comfyui-boot` usa raiz interna de ComfyUI en `/root/ComfyUI`.
- No usar mounts en `/workspace/ComfyUI` con esta familia de imagenes.
- Definir `COMFYUI_CONTAINER_ROOT=/root/ComfyUI` para alinear modelos, `custom_nodes`, `input`, `output` y `user`.
- Los tags `megapak` pueden disparar bootstrap con descargas pesadas de modelos.
- Para CID backend conviene priorizar tags `slim`/`no-megapak` y reutilizar modelos host por bind mounts.
- Objetivo operativo: usar los modelos existentes del host, sin duplicar descargas.
- Primera validacion en `8288` debe limitarse a `GET /system_stats` y `GET /api/object_info`.
- Mantener `COMFYUI_CONTAINER_ROOT=/root/ComfyUI` para esta familia de imagenes.

## Validated Docker still candidate

- **Image**: `yanwk/comfyui-boot:cu130-slim-v2`
- **Host port**: `8288` (temporal, sin interferir con nativo 8188)
- **Container port**: `8188`
- **Container root**: `COMFYUI_CONTAINER_ROOT=/root/ComfyUI`
- **Models**: `/mnt/i/COMFYUI_OK/models` (read-only)
- **Hub**: `/mnt/g/COMFYUI_HUB` (read-write: input, output, user, workflows)

Validated via Infra 8E:

- `GET /system_stats` → HTTP 200 JSON
- `GET /api/object_info` → HTTP 200 JSON, 3158 nodes
- `GPU RTX 5090` visible (nvidia-smi, PyTorch 2.11.0+cu130)
- No login/proxy (no 302, no redirect)
- No large model auto-download (slim tag)
- CID routing confirmed via env override `COMFYUI_STILL_BASE_URL=http://127.0.0.1:8288`

**Warnings**:

- Do not use `megapak` tags for CID backend production unless explicitly desired.
- Healthcheck is currently `unhealthy` because the container lacks `python` binary (only `python3`); the API works regardless.
- This is a **temporary validation mode**; native 8188 remains the default still instance until full cutover is validated.

## Validated smoke results

### Infra 8G — Direct ComfyUI `/prompt`

- **Image**: `yanwk/comfyui-boot:cu130-slim-v2`
- **Host port**: `8288`
- **Checkpoint**: `realisticVisionV60B1_v51VAE.safetensors`
- **Workflow nodes**: `CheckpointLoaderSimple`, `CLIPTextEncode` (×2), `EmptyLatentImage`, `KSampler`, `VAEDecode`, `SaveImage`
- **Width/Height**: 512×512, steps=4, cfg=2.0, seed=14052026
- **Prompt ID**: `1448ee28-b775-4b51-a2a8-be4b4646f21e`
- **Duration**: 55.16 seconds (first load)
- **Output**: `/mnt/g/COMFYUI_HUB/output/still/CID_DOCKER_STILL_SMOKE_8G_00001_.png` (351,223 bytes)
- **Result**: **GO** — direct ComfyUI API validated

### Infra 8H — CID infrastructure smoke

- **CID layer used**: `ComfyUIFactory` → `ComfyUIClient` (internal service, no HTTP auth needed)
- **Routing env override**: `COMFYUI_STILL_BASE_URL=http://127.0.0.1:8288`
- **Aux env**: `ENABLE_COMFYUI_REAL_RENDER=true`, `AUTH_DISABLED=true`
- **Prompt ID**: `b3adfa6f-5089-4a16-b287-60bcdf94e001`
- **Output**: `/mnt/g/COMFYUI_HUB/output/still/CID_STILL_SMOKE_8H_00001_.png` (338,123 bytes)
- **Result**: **GO** — CID infrastructure routed to Docker still and generated successfully
- **Note**: HTTP render endpoint not yet validated with real auth (requires DB-backed user). The 8H test validates the internal CID infra layer.
- **Next functional milestone**: endpoint CID with real auth.
