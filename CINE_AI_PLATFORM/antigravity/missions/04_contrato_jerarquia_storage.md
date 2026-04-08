# Misión 04 — Cierre del contrato jerárquico de Storage

## Objetivo exacto
Definir, consolidar e implementar la jerarquía de consulta de storage para navegar correctamente entre:
- project
- sequence
- scene
- shot

## Problema actual
Ya existen endpoints de proyecto hacia:
- sequences
- scenes
- shots

Pero falta cerrar la navegación descendente fina y dejar el contrato total coherente.

## Alcance exacto
Esta misión debe:
1. documentar la jerarquía completa
2. revisar endpoints ya implementados
3. definir endpoints faltantes
4. implementar los endpoints que falten
5. unificar formatos de respuesta y error

## Endpoints ya existentes a respetar
- `GET /api/storage/project/{project_id}/sequences`
- `GET /api/storage/project/{project_id}/scenes`
- `GET /api/storage/project/{project_id}/shots`

## Endpoints probables a completar
- `GET /api/storage/sequence/{sequence_id}/scenes`
- `GET /api/storage/sequence/{sequence_id}/shots`
- `GET /api/storage/scene/{scene_id}/shots`
- `GET /api/storage/shot/{shot_id}`

## Reglas obligatorias
- normalización consistente de ids
- 404 semántico si el recurso raíz no existe
- 200 con lista vacía si el recurso existe pero no tiene hijos
- 500 con código interno estable por endpoint
- formatos homogéneos de respuesta

## Archivos objetivo
- `apps/api/src/routes/storage_routes.py`
- `apps/api/src/services/storage_service.py`
- documentación relacionada

## Entregables obligatorios
1. endpoints faltantes implementados
2. contrato documentado
3. documento:
   - `docs/api/storage_hierarchy_contract.md`

## Contenido mínimo del documento
- mapa de recursos
- endpoints existentes
- endpoints añadidos
- formato de respuestas
- errores por endpoint
- ejemplos de pruebas manuales PowerShell/curl

## Criterios de aceptación
- la jerarquía storage queda cerrada de forma coherente
- no hay contradicciones entre endpoints hermanos
- frontend puede navegar por la estructura sin lógica ad hoc

## Pruebas manuales mínimas
- proyecto existente / inexistente
- sequence existente / inexistente
- scene existente / inexistente
- resultados vacíos
- resultados múltiples

## Riesgos a vigilar
- relaciones inconsistentes entre sequence_id, scene_id y project_id
- duplicar lógica de filtrado
- formatos de error no homogéneos

## Siguiente misión encadenada
- `05_normalizacion_de_modelos_y_respuestas.md`