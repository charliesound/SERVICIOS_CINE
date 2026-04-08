# Misión 07 — Integración controlada con ComfyUI

## Objetivo exacto
Diseñar e implementar una integración controlada entre el sistema y ComfyUI, basada en contratos estables y desacoplados.

## Problema a evitar
No se debe integrar ComfyUI directamente de forma rígida ni atar el sistema a un único workflow, nombre de nodo o plantilla cerrada.

## Alcance exacto
Esta misión debe:
1. definir adaptador ComfyUI
2. definir payload de entrada desde shot/job
3. definir estrategia de selección de workflow
4. definir persistencia de outputs
5. definir captura de errores y estados
6. permitir evolución futura sin rehacer toda la arquitectura

## No alcance
Esta misión NO debe:
- convertir todo el sistema en un cliente de ComfyUI hardcodeado
- asumir un único workflow definitivo
- mezclar frontend con detalles internos del grafo de ComfyUI

## Archivos objetivo
- servicios de ejecución
- rutas de jobs/render
- utilidades de payload
- documentación de integración

## Reglas obligatorias
- separar contrato interno y payload ComfyUI
- no inventar endpoints inexistentes
- soportar evolución por templates/workflows
- registrar outputs y errores con trazabilidad

## Entregables obligatorios
- documento:
  - `docs/render/comfyui_integration.md`

## Contenido mínimo del documento
- arquitectura del adaptador
- payload interno
- mapping a payload ComfyUI
- estrategia de selección de workflow
- outputs
- errores
- reintentos
- pruebas manuales

## Criterios de aceptación
- integración desacoplada
- arquitectura extensible
- preparada para múltiples workflows
- compatible con futuras automatizaciones

## Riesgos a vigilar
- hardcodear demasiado pronto
- acoplar UI a detalles de ComfyUI
- no contemplar errores de validación y outputs parciales

## Siguiente misión encadenada
- `08_operativizacion_antigravity_y_opencode.md`