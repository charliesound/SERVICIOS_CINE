# Auth basica de demo en proxy (nginx)

## Objetivo
Agregar una capa minima y reversible de autenticacion para demos remotas sin tocar auth in-app.

## Estado de implementacion
- Config base sin auth: `infra/nginx/default.conf`
- Config con auth: `infra/nginx/default.auth.conf`
- Override compose para auth: `deploy/docker-compose.wsl.demo-auth.yml`
- Secrets locales no versionados: `deploy/secrets/.htpasswd`

## Activacion (pasos exactos)
1. Definir credenciales en `.env.demo` (no en repo):

```bash
DEMO_BASIC_AUTH_USER=demo
DEMO_BASIC_AUTH_PASS=<password-seguro>
```

2. Arrancar con auth:

```bash
bash scripts/demo_start.sh --env .env.demo --with-basic-auth
```

El script genera `deploy/secrets/.htpasswd` y aplica override de nginx con auth.

## Desactivacion
Arrancar sin flag de auth:

```bash
bash scripts/demo_start.sh --env .env.demo
```

Opcional: borrar secreto local generado:

```bash
rm -f deploy/secrets/.htpasswd
```

## Riesgos y limitaciones
- Es auth basica HTTP en proxy, no auth de aplicacion.
- Si se usa Cloudflare Tunnel, mantener Cloudflare Access como capa principal.
- Si se usa Tailscale, auth basica puede ser opcional (defensa adicional).
- No almacenar contrasenas reales en archivos versionados.

## Compatibilidad frontend
- La SPA no se rompe: el navegador pide credenciales una vez y mantiene sesion basic auth para `/` y `/api`.
