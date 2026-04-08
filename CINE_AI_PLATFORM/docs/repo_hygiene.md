# Repo Hygiene (Mision 02)

## Objetivo
Dejar el repositorio compartible y reproducible sin artefactos locales de entorno, build o dependencias.

## Excluir del repo y de un zip limpio
- `node_modules/`
- `dist/`, `dist-ssr/`, `build/`, `coverage/`
- `__pycache__/`, `*.pyc`, `*.pyo`, `*.pyd`
- `.venv/`, `venv/`
- `.env`, `.env.*` (excepto `.env.example`)
- `apps/api/data/*.db`, `apps/api/data/*.sqlite`
- `apps/api/data/active-storage.json`
- `apps/api/data/shots_export_*.json`
- `storage/assets/*`, `storage/outputs/*`, `storage/thumbs/*`

## Mantener en repo
- codigo fuente (`apps/api/src`, `apps/web/src`, etc.)
- documentacion
- archivos de configuracion de proyecto
- ejemplos de entorno (`apps/api/.env.example`, `apps/web/.env.example`)

## Nota operativa
- Backend oficial: `src.app:app`
- Frontend recomendado: `VITE_API_BASE_URL=http://127.0.0.1:3000`
