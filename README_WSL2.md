# SERVICIOS_CINE en WSL2

Guia rapida para ejecutar `SERVICIOS_CINE` en Ubuntu sobre WSL2 con Docker, Caddy y acceso por Tailscale.

## Requisitos

- Windows 11 con WSL2 habilitado
- Ubuntu en WSL2
- Docker Desktop con integracion WSL2 activa
- Tailscale instalado en WSL2 o en Windows
- Proyecto ubicado en `/opt/SERVICIOS_CINE`

## Estructura que se levanta

- `backend` -> API principal FastAPI en `src/`
- `frontend` -> app principal React/Vite en `src_frontend/`
- `cine-api` -> API de `CINE_AI_PLATFORM`
- `cine-web` -> frontend de `CINE_AI_PLATFORM`
- `automation-engine` -> motor de automatizacion
- `n8n` -> automatizaciones
- `qdrant` -> vector DB
- `redis` -> cache/cola
- `caddy` -> proxy y punto de entrada

## Variables importantes

Revisa `.env` antes de levantar el stack:

```env
LOCAL_WSL_IP=172.24.174.31
TAILSCALE_IP=100.104.219.15
PUBLIC_HOST=ailinkcinema
PUBLIC_PROTOCOL=http
```

Si cambia tu IP de Tailscale, actualiza al menos:

- `TAILSCALE_IP`
- `PUBLIC_HOST`
- `CINE_CORS_ORIGINS`
- `CINE_FRONTEND_ORIGINS`

## Arranque

```bash
cd /opt/SERVICIOS_CINE
docker-compose up -d --build
docker-compose ps
```

Para ver logs:

```bash
docker-compose logs -f
```

Para reiniciar:

```bash
docker-compose restart
```

Para detener:

```bash
docker-compose down
```

## URLs locales

- Landing principal: `http://localhost`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- CINE Web: `http://localhost/cine/`
- CINE API: `http://localhost/cine/api/`
- Automation: `http://localhost/automation/health`
- n8n: `http://localhost/n8n/`
- Qdrant: `http://localhost/qdrant/collections`

## URLs por Tailscale

- Landing principal: `http://ailinkcinema`
- Backend API: `http://ailinkcinema:8000`
- API Docs: `http://ailinkcinema/docs`
- CINE Web: `http://ailinkcinema/cine/`
- CINE API: `http://ailinkcinema/cine/api/`
- Automation: `http://ailinkcinema/automation/health`
- n8n: `http://ailinkcinema/n8n/`
- Qdrant: `http://ailinkcinema/qdrant/collections`

## Acceso protegido

- La landing `/` es publica.
- Las rutas `/cine/`, `/app`, `/n8n/`, `/qdrant/`, `/automation/`, `/docs`, `/redoc` y `/openapi.json` requieren autenticacion basica.
- Las credenciales operativas no se documentan en el repo y se administran desde `.env`.

## Verificaciones rapidas

```bash
curl http://localhost:8000/health
curl http://localhost/automation/health
curl http://localhost/cine/health
curl http://localhost:5678/
curl http://localhost:6333/collections
```

## HTTPS local

El proyecto usa un certificado autofirmado en `certs/` para Caddy.

Regla recomendada:

- usa `http://` para trabajo diario y acceso por Tailscale
- usa `https://` solo si necesitas probar TLS localmente

- `https://localhost`
- `https://localhost/cine/`
- `https://localhost/n8n/`
- `https://localhost/qdrant/collections`

El navegador puede mostrar advertencia de seguridad. Eso es normal con certificados autofirmados.

## Tailscale

Para comprobar la IP en WSL2:

```bash
tailscale ip -4
```

Si quieres usar nombre amigable en tu laptop Windows, añade al archivo `C:\Windows\System32\drivers\etc\hosts`:

```text
100.104.219.15    ailinkcinema
```

Entonces puedes entrar con:

```text
http://ailinkcinema
http://ailinkcinema/cine/
http://ailinkcinema/n8n/
```

## Troubleshooting

### Docker no levanta el stack

```bash
docker-compose ps
docker-compose logs --tail=50
```

Si hace falta, reconstruye:

```bash
docker-compose up -d --build
```

### Caddy responde pero una ruta falla

Revisa el proxy:

```bash
docker-compose logs caddy --tail=100
```

Rutas esperadas:

- `/` -> frontend principal
- `/cine/` -> CINE Web
- `/cine/api/` -> CINE API
- `/automation/` -> automation-engine
- `/n8n/` -> n8n
- `/qdrant/` -> qdrant

### HTTPS muestra advertencia

Es normal porque el certificado es autofirmado.

- En Chrome o Edge: `Avanzado` -> continuar
- En Firefox: `Avanzado` -> aceptar riesgo

Si no quieres esa advertencia, usa HTTP o instala el certificado en tu sistema.

### El navegador tarda mucho o no abre por Tailscale

Comprueba:

```bash
tailscale ip -4
docker-compose ps
curl http://ailinkcinema
```

Y desde la laptop:

- que ambos equipos estan en el mismo tailnet
- que la IP usada coincide con `tailscale ip -4`
- que no estas usando una IP vieja de WSL2 en vez de la de Tailscale

### n8n no abre en `/n8n/`

Prueba primero el contenedor directo:

```bash
curl http://localhost:5678/
```

Luego el proxy:

```bash
curl http://localhost/n8n/
```

### Qdrant devuelve 404 en la raiz

Es normal. Usa endpoints reales, por ejemplo:

```bash
curl http://localhost/qdrant/collections
```

### CINE no carga bien bajo `/cine/`

Reconstruye el frontend de CINE para asegurar el `base path`:

```bash
docker-compose up -d --build cine-web caddy
```

## Archivos clave

- `docker-compose.yml`
- `Caddyfile`
- `.env`
- `README.md`
- `README_TAILSCALE.md`
