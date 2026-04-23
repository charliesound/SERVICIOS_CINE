# Docker local y VPS

## Archivos

- `deploy/docker/docker-compose.local.yml`: stack minimo local (`backend` + `frontend`)
- `deploy/docker/docker-compose.vps.yml`: stack minimo VPS (`backend` + `frontend` + `caddy`)
- `deploy/docker/.env.local`: valores listos para WSL local
- `deploy/docker/.env.vps`: valores base para VPS
- `docker-launch.bat`: lanzador desde Windows para local o VPS

## Local

El storage demo dentro de Docker usa la ruta interna `/data/demo_ingest`.

1. Edita `deploy/docker/.env.local` si quieres cambiar puertos o la ruta host montada.
2. Arranca:

```bat
docker-launch.bat local up
```

3. Accesos:

- frontend: `http://localhost:8080`
- backend: `http://localhost:8010`
- docs: `http://localhost:8010/docs`

## VPS

1. Asegura que el repo exista en el VPS en la ruta configurada.
2. Edita `deploy/docker/.env.vps`:
   - `CADDY_SITE=tu-dominio.com` para HTTPS automatico
   - o deja `:80` para HTTP simple
   - `HOST_DEMO_INGEST_PATH` para la ruta real del dataset en el servidor
3. Lanza:

```bat
docker-launch.bat vps up
```

El script pedira `VPS_USER`, `VPS_HOST` y opcionalmente `VPS_PATH`.

## Comandos utiles

```bat
docker-launch.bat local ps
docker-launch.bat local logs
docker-launch.bat local down

docker-launch.bat vps ps
docker-launch.bat vps logs
docker-launch.bat vps down
```

## Nota de storage demo

Cuando el stack corre dentro de Docker, el Storage Source debe apuntar a:

```text
/data/demo_ingest
```

no a la ruta host original.
