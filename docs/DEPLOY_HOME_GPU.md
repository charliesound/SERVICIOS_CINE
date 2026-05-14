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
