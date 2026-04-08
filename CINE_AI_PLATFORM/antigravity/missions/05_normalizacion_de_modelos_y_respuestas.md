# Misión 05 — Normalización de modelos y respuestas API

## Objetivo exacto
Unificar el estilo de las respuestas del backend para que el sistema tenga contratos estables, predecibles y fáciles de consumir por frontend y automatizaciones.

## Problema actual
A medida que el proyecto ha evolucionado, es posible que existan variaciones en:
- forma de `ok`
- shape de `error`
- nombres de claves
- objetos `storage`
- estructura de payloads
- códigos internos de error

## Alcance exacto
Esta misión debe:
1. auditar la forma actual de las respuestas
2. definir plantillas de respuesta de éxito
3. definir plantillas de error
4. aplicar normalización en rutas storage críticas
5. documentar la convención

## No alcance
Esta misión NO debe:
- rediseñar toda la aplicación
- cambiar semántica de negocio
- introducir frameworks adicionales de validación si no son necesarios

## Archivos objetivo
- `apps/api/src/routes/**/*.py`
- helpers o utilidades de respuesta si existen
- documentación API

## Convención objetivo
Todas las rutas relevantes deben converger hacia patrones consistentes como:
- `ok`
- `storage.backend` cuando aplique
- id del recurso raíz
- colección o entidad
- `count` cuando aplique
- bloque `error.code` y `error.message` en errores

## Entregables obligatorios
- normalización aplicada al menos en storage API
- documento:
  - `docs/api/response_conventions.md`

## Criterios de aceptación
- respuestas homogéneas
- errores homogéneos
- menos lógica condicional en frontend
- más facilidad para OpenCode y futuras pruebas

## Riesgos a vigilar
- romper consumidores existentes
- cambiar demasiados endpoints a la vez sin control
- documentar una convención que el código no cumple realmente

## Siguiente misión encadenada
- `06_preparacion_jobs_y_render_pipeline.md`