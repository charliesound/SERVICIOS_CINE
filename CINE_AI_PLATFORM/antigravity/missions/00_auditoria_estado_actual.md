# Misión 00 — Auditoría del estado actual del proyecto

## Objetivo exacto
Realizar una auditoría técnica del estado actual de CINE_AI_PLATFORM para identificar:
- backend oficial
- frontend oficial
- rutas activas y legacy
- capa de storage realmente utilizada
- deuda técnica inmediata
- prioridades de ejecución

## Contexto
El proyecto contiene varias capas que parecen pertenecer a distintas fases:
- `apps/api/src/main.py`
- `apps/api/src/app.py`
- rutas legacy de dominio (`/projects`, `/shots`, `/jobs`, etc.)
- rutas más recientes de storage (`/api/storage/...`)
- frontend Vite/React aún conectado a endpoints legacy

Además, el repo contiene artefactos de entorno y build que dificultan el trabajo automatizado:
- `.venv`
- `node_modules`
- `dist`
- `.git`
- `.env` reales

## Alcance exacto
Esta misión debe:
1. inspeccionar la estructura actual del repo
2. identificar el entrypoint backend real
3. identificar el entrypoint frontend real
4. enumerar rutas legacy y rutas nuevas
5. detectar duplicidades o conflictos de arquitectura
6. producir un informe accionable

## No alcance
Esta misión NO debe:
- refactorizar código
- borrar archivos
- migrar rutas
- cambiar contratos API
- tocar frontend o backend salvo para leer y analizar

## Archivos a inspeccionar obligatoriamente
- `apps/api/src/app.py`
- `apps/api/src/main.py`
- `apps/api/src/routes/**/*.py`
- `apps/api/src/services/**/*.py`
- `apps/web/src/**/*`
- `docs/**/*`
- `README.md`
- `requirements.txt`
- `package.json`
- `.gitignore`

## Entregable obligatorio
Crear documento:
- `docs/audits/estado_actual_repo.md`

## Contenido mínimo del entregable
- árbol resumido del proyecto
- backend oficial propuesto
- frontend oficial propuesto
- rutas activas detectadas
- rutas legacy detectadas
- duplicidades
- riesgos técnicos
- bloque siguiente recomendado
- orden recomendado de migración

## Criterios de aceptación
- el informe diferencia claramente lo legacy de lo vigente
- identifica una única dirección de continuidad técnica
- deja propuesto el backend oficial
- deja propuesta la siguiente misión a ejecutar

## Riesgos a vigilar
- coexistencia de dos entrypoints backend
- frontend consumiendo contratos ya desalineados
- ruido de dependencias y build dentro del repo
- mezcla de fases antiguas y nuevas

## Siguiente misión encadenada
- `01_unificacion_backend_oficial.md`