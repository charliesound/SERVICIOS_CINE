# Estrategia de acceso remoto (homelab)

## Contexto real
- Servidor principal en casa: Windows + WSL2.
- Stack publicado por Docker Compose: `web` (nginx + SPA) y `api`.
- ComfyUI permanece fuera de Docker y no se publica.

## Opcion A: Cloudflare Tunnel

### Como funciona
- `cloudflared` crea un tunel saliente desde casa hacia Cloudflare.
- Se publica un hostname HTTPS (por ejemplo `cine-demo.tudominio.com`).
- Nginx interno sigue resolviendo `/` y proxy `/api` a `api:3000`.

### Ventajas
- No requiere abrir puertos en router.
- Enlace HTTPS facil de compartir para demos externas.
- Permite capa de acceso con Cloudflare Access (OTP/IdP).

### Riesgos
- Endpoint publico (aunque protegido por Access).
- Dependencia de servicio externo Cloudflare.

### Configuracion minima recomendada
1. Exponer solo `http://localhost:8080` por tunnel.
2. Activar Cloudflare Access para la aplicacion.
3. Ajustar `CORS_ORIGINS` al dominio publico del tunnel.

## Opcion B: Tailscale

### Como funciona
- Servidor casa y laptop remota se unen a la misma tailnet.
- Acceso privado punto a punto a `http://<host-tailnet>:8080`.

### Ventajas
- No hay endpoint publico abierto.
- Seguridad fuerte por identidad de dispositivos/usuarios.
- Menor superficie de ataque para demos internas.

### Riesgos
- Requiere cliente Tailscale en laptop/usuarios autorizados.
- Menos practico para audiencia externa sin acceso tailnet.

### Configuracion minima recomendada
1. Mantener `WEB_PORT_BIND=8080`.
2. Ajustar `CORS_ORIGINS` con URL tailnet usada en demo.
3. Mantener ACL tailnet estricta para el servidor demo.

## Recomendacion principal para demo remoto
- **Principal:** Tailscale para demos operadas solo por el equipo (maxima seguridad y simplicidad operativa).
- **Alternativa para invitados externos:** Cloudflare Tunnel + Cloudflare Access temporal.
- Capa adicional opcional: auth basica reversible en nginx (`docs/security/demo_proxy_basic_auth.md`).

## Regla de seguridad no negociable
- ComfyUI no se expone ni por Cloudflare ni por Tailscale de forma publica.
- Solo el backend (`api`) consume `COMFYUI_BASE_URL` en red privada/controlada.
