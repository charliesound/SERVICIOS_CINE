# Misión 06 — Preparación de la capa de jobs y pipeline de render

## Objetivo exacto
Preparar una arquitectura clara para conectar la jerarquía narrativa/storage con la futura ejecución de renders, jobs y workflows externos.

## Contexto
El proyecto debe evolucionar hacia integración con:
- ComfyUI
- jobs de render
- storyboards
- continuidad visual
- outputs persistidos

Pero no conviene conectar render real antes de estabilizar el modelo de datos y el contrato de navegación.

## Alcance exacto
Esta misión debe:
1. revisar la capa actual de jobs
2. identificar cómo se relaciona con shots
3. definir contrato mínimo entre shot y job
4. definir payload base para ejecución futura
5. proponer carpeta/flujo de outputs
6. dejar documentada la integración futura con ComfyUI

## No alcance
Esta misión NO debe:
- implementar aún render real extremo
- rehacer pipelines completos de generación
- acoplar el sistema a un workflow fijo de ComfyUI

## Archivos objetivo
- `apps/api/src/routes/**/*jobs*`
- `apps/api/src/services/**/*jobs*`
- `apps/api/src/models/**/*`
- `storage/**/*`
- documentación existente de fases o render

## Entregables obligatorios
- documento:
  - `docs/render/jobs_render_contract.md`

## Contenido mínimo del documento
- relación entre shot y job
- payload mínimo para lanzar job
- estados posibles del job
- persistencia de outputs
- rutas recomendadas
- puntos de acoplamiento con ComfyUI
- riesgos de integración

## Criterios de aceptación
- queda definido cómo un shot puede transformarse en un job ejecutable
- no se introduce acoplamiento prematuro
- queda un contrato claro para siguientes fases

## Riesgos a vigilar
- intentar conectar ComfyUI demasiado pronto
- definir payloads rígidos y poco extensibles
- mezclar storage narrativo con ejecución técnica sin separación

## Siguiente misión encadenada
- `07_integracion_controlada_comfyui.md`