# BACKUP RESTORE PRIVATE

## Componentes soportados
- `api`
- `n8n`
- `qdrant`
- `nginx`
- `env` opcional

## Rutas usadas
- `API_DATA_PATH`
- `N8N_DATA_PATH`
- `QDRANT_STORAGE_PATH`
- `NGINX_LOG_PATH`

Se leen desde `.env.private`.  
Si no existe, se usa `.env.private.example` solo como fallback de referencia.

## Backup recomendado
Parar el stack antes del backup para snapshot limpio de SQLite y metadatos.

```powershell
powershell -ExecutionPolicy Bypass -File .\deploy\stop-private.ps1
powershell -ExecutionPolicy Bypass -File .\deploy\backup-private.ps1