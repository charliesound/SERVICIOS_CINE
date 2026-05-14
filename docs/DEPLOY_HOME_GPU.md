# Deploy Home GPU Seguro (RTX 5090)

## 1) Objetivo

- PC de casa con RTX 5090 como servidor principal GPU para AILinkCinema.
- Laptop externo accede por red privada Tailscale.
- VPS futuro actua como proxy/orquestador, no como nodo GPU principal.

## 2) Topologia recomendada

Laptop -> Tailscale -> PC casa -> Docker GPU stack

## 3) Regla critica de seguridad

- No abrir puertos del router.
- No exponer PostgreSQL, Redis, Qdrant ni Ollama a internet publica.
- ComfyUI solo en red privada y con control de acceso.

## 4) Tailscale (flujo base)

1. Instalar Tailscale en PC casa.
2. Ejecutar `tailscale up` en PC casa.
3. Instalar Tailscale en laptop.
4. Verificar conectividad privada con `tailscale status` y MagicDNS/IP `100.x.x.x`.

## 5) Binds y acceso remoto

- `127.0.0.1` es el bind mas seguro para servicios sensibles.
- Un servicio en `127.0.0.1` no es accesible directamente desde otro equipo (incluida la laptop por Tailscale).
- Para exponer solo lo necesario a la laptop:
  - usar Tailscale Serve, o
  - usar Caddy con autenticacion y reverse proxy controlado.

## 6) Servicios recomendados

- Frontend y backend publicados via Caddy/Tailscale (no puertos crudos).
- n8n protegido (solo acceso privado/autenticado).
- ComfyUI privado (sin exposicion WAN).
- Ollama solo para backend interno o proxy privado.
- Bases de datos siempre privadas, nunca publicas.

## Acceso remoto privado con Tailscale Serve

- Tailscale Serve comparte servicios locales solo dentro del tailnet.
- No es lo mismo que Funnel.
- Funnel expone servicios a internet publico; no usar Funnel salvo demo controlada.
- Un servicio escuchando en `127.0.0.1` no es accesible directamente desde la laptop por IP Tailscale.
- Para acceso remoto desde laptop usar Tailscale Serve o Caddy interno.

Pasos base (manual, fuera del repo):

1. Ejecutar `tailscale up`.
2. Verificar estado con `tailscale status`.

Ejemplos de exposicion privada en tailnet:

```bash
# Backend
tailscale serve --bg 8010
# o equivalente
tailscale serve --bg localhost:8010

# n8n (solo si esta protegido)
tailscale serve --bg 5678

# ComfyUI (solo administracion privada y no permanente)
tailscale serve --bg 8188
```

Gestion del estado de Serve:

```bash
tailscale serve status
tailscale serve off
```

Advertencias:

- No exponer PostgreSQL, Redis, Qdrant ni Ollama con Tailscale Serve.
- No usar Funnel para Ollama/ComfyUI.
- Restringir acceso con ACLs de Tailscale si hay mas dispositivos o usuarios.
- Los puertos ComfyUI 8188-8192 son sensibles; no exponerlos todos por defecto.

## 7) Diagnostico rapido

```bash
ss -ltnp
docker ps
tailscale status
curl http://127.0.0.1:11434/api/tags
```

## 8) Nota ComfyUI

- Cambiar lanzamiento de ComfyUI de `--listen 0.0.0.0` a `--listen 127.0.0.1` (o equivalente).
- No exponer puertos 8188-8192 en LAN/WAN sin autenticacion fuerte.

## 9) VPS futuro (patron recomendado)

- VPS publica solo HTTPS via Caddy.
- VPS unido a la misma tailnet Tailscale.
- Ollama y ComfyUI siguen en PC casa (GPU).
- Variables del VPS (`OLLAMA_BASE_URL`, `COMFYUI_*`) apuntan a IP Tailscale o MagicDNS del PC casa.

## 10) Checklist de seguridad

- [ ] Sin puertos abiertos en router domestico.
- [ ] PostgreSQL/Redis/Qdrant/Ollama con bind local o acceso privado controlado.
- [ ] ComfyUI sin bind publico por defecto.
- [ ] n8n detras de acceso privado/autenticado.
- [ ] Tailscale operativo en PC casa y laptop.
- [ ] Accesos remotos auditados y minimizados.

## Referencia ComfyUI Docker

- Ver `docs/COMFYUI_DOCKERIZATION.md` para el skeleton Docker (Infra 8B).
- Ese documento define solo base de compose y validaciones de config, sin apagar ComfyUI nativo.
- Para el primer smoke Docker still sin impacto, usar puerto temporal `8288` (`COMFYUI_STILL_HOST_PORT=8288`).
- Con imagenes `yanwk/comfyui-boot`, usar `COMFYUI_CONTAINER_ROOT=/root/ComfyUI`.
- Evitar tags `megapak` en produccion CID; preferir `slim`/`no-megapak` para no descargar modelos duplicados.

## Routing interno de ComfyUI por CID

- El usuario entra a CID; no selecciona URLs de ComfyUI manualmente.
- CID decide internamente la instancia ComfyUI segun `task_type`, workflow y capacidades.
- ComfyUI no debe exponerse como interfaz de usuario normal.

Mapa operativo:

- still/storyboard -> 8188
- video/cine -> 8189
- dubbing/audio -> 8190
- restoration/conform/cleanup -> 8191
- 3D -> 8192

Entornos:

- En Docker Home, el backend usa `host.docker.internal` para alcanzar ComfyUI nativo.
- En VPS sin GPU, el backend usa IP Tailscale/MagicDNS del PC casa.

Comportamiento esperado:

- Si una instancia esta caida, CID debe devolver error de capacidad/backend no disponible.
