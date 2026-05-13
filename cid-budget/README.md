# CID Budget Estimator — Standalone App

App independiente de presupuestación audiovisual. Integrable en CID.

## Stack
- Backend: FastAPI
- Frontend: React + TypeScript
- DB: SQLite (standalone) / PostgreSQL (CID)
- Auth: JWT compartido con CID

## Arranque standalone
```bash
docker compose up -d
# API: http://localhost:8500
# UI:  http://localhost:8501
```

## Arranque integrado en CID
CID detecta automáticamente esta app mediante `cid-manifest.json`.
Las rutas `/api/budget/*` se integran en el router de CID.
La UI se muestra en `/projects/:projectId/budget`.

## Precio
- Standalone: 19€/mes
- Incluida en CID: sí
