# CID / AILinkCinema — Runbook de Desarrollo Local

## Estado actual validado

Repositorio: `/opt/SERVICIOS_CINE`  
Backend dev: `http://127.0.0.1:8010`  
Frontend dev: `http://localhost:3001`

## Scripts disponibles

### Arrancar backend

```bash
cd /opt/SERVICIOS_CINE
./scripts/start_cid_backend_dev.sh
```

Backend interno:

```bash
PYTHONPATH=/opt/SERVICIOS_CINE/src
python -m uvicorn app:app --host 0.0.0.0 --port 8010 --reload --reload-dir src
```

### Arrancar frontend

```bash
cd /opt/SERVICIOS_CINE
./scripts/start_cid_frontend_dev.sh
```

URL:

```bash
http://localhost:3001
```

### Ver estado del sistema

```bash
cd /opt/SERVICIOS_CINE
./scripts/status_cid_dev.sh
```

Muestra:

- Backend 8010
- Frontend 3001
- Health backend
- Apps registradas
- Soluciones CID
- Instancias ComfyUI
- Workflows detectados por ComfySearch

### Parar entorno dev

```bash
cd /opt/SERVICIOS_CINE
./scripts/stop_cid_dev.sh
```

### Smoke rápido

```bash
cd /opt/SERVICIOS_CINE
./scripts/smoke_cid_dev.sh
```

Valida:

- `/health`
- `/api/apps`
- `/api/solutions`
- `/api/v1/comfyui/instances`
- `/api/comfysearch/scan`

### Validación completa

```bash
cd /opt/SERVICIOS_CINE
./scripts/validate_cid_dev.sh
```

Ejecuta:

- `py_compile` de rutas y servicios críticos
- tests unitarios de ComfyUI Instance Registry
- build frontend
- smoke backend

Resultado esperado:

```bash
CID DEV VALIDATION: PASS
```

## URLs útiles

```text
Backend health:
http://127.0.0.1:8010/health

ComfyUI instances:
http://127.0.0.1:8010/api/v1/comfyui/instances

Apps:
http://127.0.0.1:8010/api/apps

Solutions:
http://127.0.0.1:8010/api/solutions

ComfySearch scan:
http://127.0.0.1:8010/api/comfysearch/scan

Frontend:
http://localhost:3001
```

## Warnings conocidos no bloqueantes

- Warnings de deprecación en Pydantic/datetime.
- Warning de Vite por chunk superior a 500 kB.
- Warning de Vite por import dinámico/estático de `auth.ts`.

## Estado GO

El entorno queda validado cuando:

```bash
./scripts/validate_cid_dev.sh
```

termina con:

```bash
CID DEV VALIDATION: PASS
```
