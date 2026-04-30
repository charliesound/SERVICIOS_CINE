# Sprint 13 Runbook

Sprint 13 se certifica ejecutando todo dentro de WSL real sobre `/opt/SERVICIOS_CINE`.

## 1. Levantar backend

```bash
cd /opt/SERVICIOS_CINE/src
APP_ENV=demo ENABLE_DEMO_ROUTES=1 ENABLE_EXPERIMENTAL_ROUTES=0 ENABLE_POSTPRODUCTION_ROUTES=0 ./.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

## 2. Levantar frontend

```bash
cd /opt/SERVICIOS_CINE/src_frontend
npm run dev
```

## 3. Sembrar demo

```bash
curl -X POST http://127.0.0.1:8000/api/demo/quick-start
```

## 4. Smoke reproducible Sprint 13

El smoke arranca un backend temporal con una SQLite aislada en `/tmp`, ejecuta login, persistencia de plan, upgrade interno, proyecto, analyze, storyboard, jobs/assets/history y export JSON/ZIP.

```bash
cd /opt/SERVICIOS_CINE
src/.venv/bin/python scripts/smoke_sprint13_rc.py
```

Variables opcionales:

```bash
SMOKE_PORT=8015 src/.venv/bin/python scripts/smoke_sprint13_rc.py
SMOKE_KEEP_DB=1 src/.venv/bin/python scripts/smoke_sprint13_rc.py
SMOKE_DATABASE_URL=sqlite+aiosqlite:////tmp/servicios_cine_s13_manual.db src/.venv/bin/python scripts/smoke_sprint13_rc.py
```

## 5. Validar build frontend

```bash
cd /opt/SERVICIOS_CINE
bash scripts/build_frontend_wsl.sh
```

Comando equivalente directo:

```bash
cd /opt/SERVICIOS_CINE/src_frontend
npm run build
```

## 6. Validacion minima manual

1. Login con `demo_free@servicios-cine.com / demo123`
2. Verificar `GET /api/auth/me` => `plan=free`
3. Ejecutar `POST /api/plans/change` con `producer`
4. Verificar `GET /api/auth/me` y `GET /api/plans/me` => `plan=producer`
5. Crear proyecto, cargar guion, ejecutar analyze y storyboard
6. Verificar jobs, assets, metrics, export JSON y export ZIP

## 7. Reinicio / recovery baseline

Validar queue restart recovery real con `QUEUE_PERSISTENCE_MODE=db` y compatibilidad de `memory`:

```bash
cd /opt/SERVICIOS_CINE
src/.venv/bin/python scripts/smoke_restart_recovery.py
```

El smoke verifica:

1. `running -> failed` con `recovery_reason=backend_restart`
2. `queued -> queued` tras reinicio
3. `scheduled -> queued` tras reinicio
4. modo `memory` sigue aceptando jobs

## 8. Backup / rollback basico

SQLite local:

```bash
mkdir -p /opt/SERVICIOS_CINE/backups
cp /opt/SERVICIOS_CINE/src/ailinkcinema_s2.db /opt/SERVICIOS_CINE/backups/ailinkcinema_s2.$(date +%Y%m%d_%H%M%S).db
```

Rollback rapido:

```bash
cp /opt/SERVICIOS_CINE/backups/<backup>.db /opt/SERVICIOS_CINE/src/ailinkcinema_s2.db
```
