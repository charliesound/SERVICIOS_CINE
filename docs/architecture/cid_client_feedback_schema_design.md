# CID Client Feedback & Learning Schema — Design Document

## 1. Objetivo
Disenar la arquitectura para que CID aprenda de:
- correcciones de clientes
- aprobaciones
- rechazos
- preferencias creativas
- reglas de proyecto
- decisiones de produccion
- correcciones de personajes
- correcciones de localizaciones
- problemas de raccord
- feedback de prompts

Sin contaminar:
- otros proyectos
- otras organizaciones
- otros clientes
- memoria global del sistema

## 2. Estado actual
- `POST /api/projects/{project_id}/memory/answer` ya existe.
- `cid_memory` existe en Qdrant.
- `cid_screenwriting_theory` esta preservada.
- Ultimo commit base: `eab55b2 feat: improve CID RAG answer quality`.
- Esta fase es solo documentacion.

## 3. Modelo conceptual
La arquitectura debe separar claramente:
- `project_feedback`
- `organization_feedback`
- `answer_feedback`
- `approved_memory`
- `rejected_memory`
- `prompt_feedback`

Explicacion:
- `project_feedback` aplica a una pelicula o proyecto concreto.
- `organization_feedback` aplica a una productora, estudio o cliente a nivel organizacion.
- `answer_feedback` se vincula a una respuesta concreta de CID para auditar utilidad, error o correccion.
- `approved_memory` representa informacion aprobada explicitamente para aprendizaje reutilizable.
- `rejected_memory` almacena correcciones rechazadas o fuentes que no deben volver a reutilizarse.
- `prompt_feedback` permite aprender de prompts que funcionaron o fallaron sin mezclar ese aprendizaje con memoria aprobada automaticamente.

## 4. Tipos de feedback
Tipos minimos propuestos:
- `answer_helpful`
- `answer_wrong`
- `answer_partially_wrong`
- `approved_correction`
- `rejected_answer`
- `style_preference`
- `tone_preference`
- `project_rule`
- `character_correction`
- `location_correction`
- `raccord_correction`
- `storyboard_correction`
- `production_decision`
- `prompt_success_case`
- `prompt_failure_case`
- `source_blacklist`
- `source_preference`

## 5. Tablas propuestas
Diseno sin implementar.

### A) `cid_client_feedback`
Campos:
- `id`
- `organization_id`
- `project_id`
- `user_id`
- `feedback_type`
- `feedback_scope`
- `original_question`
- `original_answer`
- `corrected_answer`
- `feedback_text`
- `source_ids`
- `source_types`
- `approved_for_memory`
- `approved_by_user_id`
- `confidence`
- `status`
- `model_used`
- `prompt_version`
- `answer_version`
- `metadata_json`
- `created_at`
- `updated_at`

### B) `cid_feedback_memory_entries`
Campos:
- `id`
- `feedback_id`
- `organization_id`
- `project_id`
- `source_type`
- `source_id`
- `source_text`
- `approved_for_memory`
- `approved_by_user_id`
- `qdrant_point_id`
- `indexed_at`
- `confidence`
- `metadata_json`
- `created_at`
- `updated_at`

### C) `cid_answer_feedback_events`
Campos:
- `id`
- `feedback_id`
- `organization_id`
- `project_id`
- `answer_id`
- `model_used`
- `prompt_version`
- `answer_version`
- `action`
- `created_at`
- `metadata_json`

### D) `cid_project_learning_rules`
Campos:
- `id`
- `organization_id`
- `project_id`
- `rule_type`
- `rule_value`
- `priority`
- `active`
- `created_by_user_id`
- `created_at`
- `updated_at`
- `metadata_json`

### E) `cid_organization_learning_preferences`
Campos:
- `id`
- `organization_id`
- `preference_type`
- `preference_value`
- `priority`
- `active`
- `created_by_user_id`
- `created_at`
- `updated_at`
- `metadata_json`

### F) `cid_feedback_audit`
Campos:
- `id`
- `feedback_id`
- `organization_id`
- `project_id`
- `user_id`
- `action`
- `previous_status`
- `new_status`
- `previous_metadata_json`
- `new_metadata_json`
- `created_at`

Uso:
Registrar creacion, aprobacion, rechazo, edicion, borrado logico, indexacion y desindexacion de memoria.

## 6. Integracion con Qdrant
Nuevos `source_type` propuestos para `cid_memory`:
- `approved_correction`
- `style_preference`
- `project_rule`
- `character_correction`
- `location_correction`
- `raccord_correction`
- `storyboard_correction`
- `production_decision`
- `prompt_success_case`

Regla critica:
NO indexar feedback libre sin aprobacion.

Debe quedar claro que:
- `client_feedback` pendiente NO se indexa.
- `answer_wrong` NO se indexa.
- `rejected_answer` NO se indexa.
- `source_blacklist` NO se indexa en Qdrant; se usa como filtro desde PostgreSQL.
- `prompt_failure_case` NO se indexa como memoria positiva.
- `prompt_failure_case`, `source_blacklist`, `rejected_answer` y feedback pendiente quedan solo en PostgreSQL.
- Solo se indexa en Qdrant lo aprobado explicitamente.

## 7. Endpoints futuros
Propuesta sin implementar:
- `POST /api/projects/{project_id}/feedback/answer`
- `POST /api/projects/{project_id}/feedback/correction`
- `POST /api/projects/{project_id}/feedback/preference`
- `POST /api/projects/{project_id}/feedback/approve-memory`
- `GET /api/projects/{project_id}/feedback`
- `GET /api/projects/{project_id}/learning/status`
- `DELETE /api/projects/{project_id}/feedback/{feedback_id}`
- `POST /api/organizations/{organization_id}/feedback/preference`
- `GET /api/organizations/{organization_id}/learning/preferences`

## 8. UX futura
Acciones sugeridas:
- Util
- Incorrecto
- Corregir respuesta
- Guardar como regla del proyecto
- Guardar como preferencia del cliente
- No usar esta fuente
- Esta respuesta esta aprobada
- Este prompt ha funcionado
- Este resultado visual esta aprobado
- Marcar problema de raccord

Implementacion UX recomendada:
componentes React reutilizables siguiendo el design system existente, sin introducir nuevas dependencias de UI salvo decision posterior.

## 9. Seguridad y aislamiento
Requisitos:
- `organization_id` obligatorio.
- `project_id` obligatorio cuando aplique.
- feedback privado por defecto.
- nunca busqueda global por defecto.
- nunca mezclar proyectos.
- nunca mezclar organizaciones.
- no usar memoria de una productora en otra.
- aprendizaje global solo anonimizado en una fase futura.
- audit trail obligatorio.
- sanitizacion de `feedback_text` y `corrected_answer`.
- permisos por usuario y rol.
- filtros obligatorios `organization_id + project_id` en consultas RAG.
- no exponer `source_text` completo salvo permisos e `include_sources=true`.

## 10. Impacto futuro en `/memory/answer`
Orden de prioridad propuesto:
1. Correcciones aprobadas del proyecto.
2. Reglas activas del proyecto.
3. Preferencias de organizacion.
4. Fuentes originales: `script_text`, `storyboard_shot`, `production_breakdown`.
5. Memoria historica aprobada.
6. Conocimiento teorico `cid_screenwriting_theory` solo si se habilita explicitamente.

Explicacion:
- pre-ranking por reglas aprobadas y feedback del proyecto.
- exclusion de `source_blacklist` y `rejected_memory` antes de construir contexto.
- re-ranking por `confidence`, `priority`, actualidad y aprobacion.
- prompt enriquecido con reglas y preferencias aplicables al proyecto y a la organizacion.
- trazabilidad de fuentes para que el usuario vea que parte viene de guion, storyboard, breakdown o memoria aprobada.

## 11. Fases recomendadas
- Fase 0: diseno documental
- Fase 1: DB models + Alembic
- Fase 2: API backend
- Fase 3: frontend feedback UX
- Fase 4: Qdrant indexing de `approved_memory`
- Fase 5: integracion en `/memory/answer`
- Fase 6: tests y evals
- Fase 7: smoke runtime

## 12. Criterios GO/NO-GO
### GO
- documento creado
- no cambios de codigo
- no migraciones
- no DB
- no Qdrant
- `git diff --check` OK
- `backups/` no incluido
- `git status` debe mostrar unicamente el documento nuevo o modificado y `backups/` como untracked esperado antes del commit

### NO-GO
- falta aislamiento `organization_id/project_id`
- se propone indexar feedback no aprobado
- se mezcla memoria entre organizaciones
- se toca codigo o DB en esta fase

## 13. Riesgos
- contaminacion de memoria
- fuga de datos entre organizaciones
- feedback erroneo aprobado por accidente
- sobrecarga de contexto
- exceso de feedback pendiente
- `source_blacklist` mal aplicada
- futuras migraciones con rollback necesario

## 14. Preguntas abiertas
- quien puede aprobar memoria
- si `project_rule` necesita versionado
- cuanto tiempo conservar `rejected_memory`
- como anonimizar aprendizaje global futuro
- como mostrar al cliente que memoria esta activa

## 15. Validacion
Comandos de validacion documental:

```bash
git status --short
git diff -- docs/architecture/cid_client_feedback_schema_design.md
git diff --check
```
