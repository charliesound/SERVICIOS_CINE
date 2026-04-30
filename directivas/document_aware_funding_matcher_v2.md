# Document-Aware Funding Matcher V2

## Objetivo

Extender el matcher financiero existente para combinar scoring estructural con evidencia documental privada indexada por proyecto, sin abrir UI nueva ni crear un matcher paralelo.

## Decisiones cerradas

- Se reutiliza `project_funding_matches` como persistencia unica de resultados clasicos y enriquecidos.
- Se diferencia el modo con `matcher_mode` (`classic` y `rag_enriched`).
- El scoring enriquecido preserva un `baseline_score` estructural y persiste un `match_score` final ajustado por evidencia documental.
- Todo retrieval documental usa filtros obligatorios por `organization_id` y `project_id`.
- La ejecucion enriquecida usa `ProjectJob` + `BackgroundTasks` como job ligero reproducible; no se introduce Celery, Redis ni orquestacion pesada.

## Pipeline enriquecido

1. Construir perfil base del proyecto con el matcher actual.
2. Leer requisitos estructurados del `FundingCall` y `FundingRequirement`.
3. Derivar consultas documentales concretas por oportunidad.
4. Ejecutar retrieval semantico contra el RAG del proyecto filtrado por tenant y proyecto.
5. Evaluar cada requisito en formato JSON auditable:
   - `requirement`
   - `status`: `met | partially_met | unmet | unknown`
   - `evidence_excerpt`
   - `reasoning`
   - `confidence`
6. Consolidar:
   - `match_score`
   - `fit_level`
   - `fit_summary`
   - `blocking_reasons_json`
   - `missing_documents_json`
   - `recommended_actions_json`
   - `evidence_chunks_json`
   - `confidence_level`
   - `evaluation_version`

## Persistencia minima

Campos adicionales en `project_funding_matches`:

- `baseline_score`
- `rag_enriched_score`
- `evidence_chunks_json`
- `rag_rationale`
- `rag_missing_requirements`
- `rag_confidence_level`
- `matcher_mode`
- `evaluation_version`

## Contratos API

- `POST /api/projects/{project_id}/funding/recompute-rag`
- `GET /api/projects/{project_id}/funding/matches-rag`
- `GET /api/projects/{project_id}/funding/matches/{match_id}/evidence`
- `GET /api/projects/{project_id}/funding/matcher-status`

## Restricciones activas

- No tocar dashboard ni conectores externos.
- No romper matcher clasico, catalogo, dossier, presentation, builder ni budget.
- No mezclar evidencia entre tenants.
- No introducir agentes autonomos ni prompts opacos.
