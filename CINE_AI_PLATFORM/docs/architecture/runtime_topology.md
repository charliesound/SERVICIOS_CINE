# Runtime topology (Windows + WSL)

## Topologia real del despliegue actual

```text
      Laptop cliente
            |
            | Wi-Fi / hotspot
            v
        Movil hotspot
            |
            | red local temporal
            v
  Servidor en casa (Windows + WSL2)
            |
            | Docker network interna
            v
      [cine-web container]
      nginx (infra/nginx/default.conf)
            |
            | proxy /api/*
            v
      [cine-api container]
      uvicorn src.app:app
            |
            | bind mount persistente
            v
      apps/api/data (host filesystem)

      ComfyUI externo (fuera Docker)
      accesible solo por backend via COMFYUI_BASE_URL
```

## Servicios Docker activos
Definidos en `deploy/docker-compose.wsl.yml`:

- `api`
  - build: `apps/api/Dockerfile`
  - runtime: `python -m uvicorn src.app:app --host 0.0.0.0 --port 3000`
  - persistencia: `../apps/api/data:/app/data`
  - red interna: visible para `web` como `api:3000`
- `web`
  - build: `apps/web/Dockerfile`
  - sirve SPA en nginx
  - usa `infra/nginx/default.conf` montado en runtime
  - publica puerto host `${WEB_PORT_BIND:-8080}`

## Frontera de red
- Expuesto al cliente: puerto web (`:8080` por defecto).
- API puede consumirse via nginx (`/api`) desde el mismo host/URL.
- ComfyUI no se publica en Compose ni en nginx.

## Capa de acceso remoto seguro
- Opcion A: Tailscale (recomendada para demo operada por equipo interno).
- Opcion B: Cloudflare Tunnel + Access (para compartir con invitados externos).
- En ambos casos, el destino remoto es solo `web` (`:8080`) y su `/api` proxied.
- ComfyUI queda fuera de ambas capas.

## Frontera funcional
- Oficial backend para datos: `/api/storage/*`
- Legacy temporal: `/projects`, `/scenes`, `/shots`, `/jobs` (controlado por `ENABLE_LEGACY_ROUTES`)
- ComfyUI: integracion opcional desde backend (cliente minimo + health extendido)

## Flujo operativo en demo remota (laptop + hotspot movil)
1. Servidor en casa o laptop-servidor levanta stack Docker en WSL.
2. Movil hotspot crea red temporal para clientes demo.
3. Laptop cliente en la misma red abre `http://<IP_SERVIDOR>:8080`.
4. Nginx resuelve frontend y enruta `/api` al backend interno.
5. Backend consulta ComfyUI por `COMFYUI_BASE_URL` sin exponerlo al publico.

## Puntos de fallo conocidos
- Si `web` cae: no hay acceso UI aunque API siga viva.
- Si `api` cae: nginx devuelve errores en `/api`.
- Si ComfyUI cae: UI/API siguen operativas, pero funciones de render quedaran degradadas (estado visible en `/api/health/details`).
