# Sequence Semantic Context Integration

## Objetivo
- recuperar contexto semántico relevante desde Qdrant durante `sequence planning / render`
- enriquecer el planner con señales editoriales y de continuidad sin sustituir su lógica base

## Punto de integración
- `apps/api/src/services/sequence_planner_service.py`

## Entrada usada
- `project_id` obligatorio para activar búsqueda útil
- `sequence_id` opcional
- `script_text` como query principal para embeddings
- en esta primera versión el query se normaliza y se recorta antes de enviarse a embeddings/Qdrant

## Tipos priorizados
- `project_note`
- `sequence_note`
- `scene_note`
- `shot_note`
- `style_reference`
- `continuity_rule`

## Salida integrada
- `plan.semantic_context`
- `continuity_notes` enriquecido con `continuity_hints`
- `render_inputs.jobs[].render_context.semantic_context`
- refuerzo opcional del prompt positivo de render con `semantic_context.summary_text`
- salida comparativa por job:
  - `prompt_base`
  - `prompt_enriched`
  - `semantic_summary_used`
  - `semantic_enrichment_applied`

## Comportamiento
- el planner recupera contexto semántico relevante cuando hay `project_id`
- si encuentra contexto útil, lo resume y lo adjunta al plan y al `render_context`
- si no hay contexto, el planner sigue funcionando igual
- si embeddings o Qdrant fallan, el planner sigue funcionando y deja el error dentro de `semantic_context`
- si el refuerzo semántico de prompt está activado, añade `summary_text` recortado al prompt positivo
- si el refuerzo está desactivado, el planner usa solo `prompt_base`
- si no hay contexto útil o el refuerzo no aplica:
  - `semantic_enrichment_applied = false`
  - `prompt_enriched = prompt_base`
- por ejecución se pueden enviar overrides opcionales en el request:
  - `semantic_prompt_enrichment_enabled`
  - `semantic_prompt_enrichment_max_chars`
- si no llegan overrides, se usan los settings globales

## Nota de esta primera versión
- esta integración apoya al planner, no lo sustituye
- el filtrado de tipos útiles se hace en backend después de recuperar resultados de Qdrant
- la recuperación es opcional y no destructiva
- queda preparada para crecer después con queries más específicas por `scene_id` y `shot_id`
- configuración mínima usada:
  - `SEQUENCE_SEMANTIC_PROMPT_ENRICHMENT_ENABLED`
  - `SEQUENCE_SEMANTIC_PROMPT_ENRICHMENT_MAX_CHARS`
- esta salida comparativa permite inspeccionar el efecto del refuerzo semántico antes de exponer controles adicionales en frontend
