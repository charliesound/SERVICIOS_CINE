# Estrategia de Backup y Restore (PRIVATE PACK)

Dado que la arquitectura asume que el despliegue vive portablemente en un disco duro extraíble, la persistencia recae en aislar las carpetas configuradas en `<unidad>:\` a través del flag `.env.private` sin acoplar el estado a los IDs de los contenedores Docker locales.

## Scope Definido
- `storage/api/data`: Base de datos SQLite y blobs/imágenes nativas del CRM CINE_AI.
- `storage/n8n/data`: Definiciones de workflows, ejecuciones guardadas y conexiones cifradas.
- `storage/qdrant/storage`: Almacén vectorial base para inferencia RAG.
- `.env.private`: Las llaves maestras e infra variables del runtime actual (OPCIONAL/CATÁSTROFE).

## Scripts de Acción Rápida 
Antes o después de ejecutar copias de seguridad debes consultar a los motores subyacentes:
- **Estado Rápido de Contenedores:** `.\deploy\status-private.ps1`
- **Volcado de Logs Críticos:** `.\deploy\logs-private.ps1 -Service api -Tail 100`

## Crear un Backup Defensivo Segregado
Para asegurar un snapshot sin corrupciones en los ficheros SQLite:
1. `.\deploy\stop-private.ps1`
2. `.\infra\scripts\backup-private.ps1`

*(Este script genera automáticamente un archivo ZIP empaquetado en el directorio `./backups/` iterando nativamente cada variable del `.env.private`).*

## Restauración de Datos (Restore Tools)
> [!WARNING]
> La restauración sobrescribe la topología origen de manera DESTRUCTIVA. Detén los servicios (`.\deploy\stop-private.ps1`) obligatoriamente antes de correr estos scripts, de lo contrario SQLite lockeará la escritura OS.

**Restore Seguro / Iterativo (Solo datos de la API):**
Sobrescribe únicamente lo que le compete al core software (Recomendado para rollbacks de código normal).
```powershell
.\infra\scripts\restore-private.ps1 -BackupZip .\backups\stack-private-backup-YYYYMMDD-HHmmss.zip
```

**Restore Full (Hard-Reset por Catástrofe):**
Extrae la topología completa (API + N8N + Qdrant + Env Keys). 
```powershell
.\infra\scripts\restore-private.ps1 -BackupZip .\backups\stack-private-backup-YYYYMMDD-HHmmss.zip -FullRestore
```

## Checklist Tras Recuperación
1. Ejecuta: `.\deploy\start-private.ps1`
2. Ejecuta: `.\deploy\status-private.ps1` *(Revisa que todos digan 'Up')*
3. Ejecuta validación canónica: `.\infra\scripts\smoke-private.ps1` 
 *(Si `api_health_ok = True`, el rollback se considera exitoso).*
