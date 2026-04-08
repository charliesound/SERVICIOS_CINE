# Propuesta de auth minima para demos remotas

## Objetivo
Aplicar una capa de acceso realista para demo sin rehacer autenticacion completa de la app.

## Recomendacion principal

### Si usas Tailscale (recomendado para equipo interno)
- Auth se delega a identidad de tailnet + ACL.
- Solo dispositivos/usuarios aprobados alcanzan `web`/`api`.

### Si usas Cloudflare Tunnel (audiencia externa)
- Activar Cloudflare Access delante del hostname demo.
- Politica minima:
  - One-time PIN por email o IdP controlado
  - Session TTL corta (por ejemplo 2-8 horas)
  - revocar accesos al terminar demo

## Por que no auth in-app en este sprint
- Restriccion de cambios minimos y no rehacer arquitectura.
- Se evita romper frontend actual.
- El control de acceso se aplica en la capa de transporte remoto.

## Hardening minimo adicional
- `ENABLE_LEGACY_ROUTES=false` en modo demo
- `CORS_ORIGINS` limitado al origen real de demo
- no exponer puertos de API/ComfyUI publicamente

## Riesgo residual
- Sin auth funcional dentro de la app, el acceso depende totalmente de la capa remota (Tailscale/Cloudflare Access).
