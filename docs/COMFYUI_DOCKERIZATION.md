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

- Los servicios montan `models` desde rutas host existentes.
- No se duplican modelos grandes en volumen Docker.
- `comfyui-3d` puede apuntar a `ComfyUI-image/models` cuando comparten inode/datos.

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
