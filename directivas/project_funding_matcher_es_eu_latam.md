# PROJECT FUNDING MATCHER ES/EU/LATAM MVP

## Objetivo
- Evaluar convocatorias institucionales por proyecto usando perfil real, breakdown, presupuesto y funding gap.
- Persistir resultados accionables por `project_id` y `organization_id`.
- Mantener este bloque separado de billing, dashboard final, alertas automaticas y application tooling.

## Datos reutilizados
- `projects`: titulo, logline, synopsis/script, estado base.
- `production_breakdowns`: senales de complejidad, escenas, departamentos.
- `project_budgets`: presupuesto total vigente.
- `project_funding_sources`: fondos privados secured / negotiating / projected y funding gap.
- `funding_sources`, `funding_calls`, `funding_requirements`: catalogo institucional ya cerrado.

## Persistencia minima

### project_funding_matches
- `project_id`, `organization_id`, `funding_call_id`
- `match_score`, `fit_level`, `fit_summary`
- `blocking_reasons`, `missing_documents`, `recommended_actions`
- `confidence_level`, `evaluation_version`, `computed_at`

No se introduce tabla adicional para checklist en esta fase; el checklist se consolida desde matches persistidos para evitar redundancia.

## Perfil financiable derivado
- `type_of_work` desde titulo/logline/synopsis/script.
- `phase` desde estado del proyecto, breakdown y presencia de presupuesto/fondos.
- `countries_involved` desde texto del proyecto.
- `breakdown_summary` desde `production_breakdowns`.
- `budget_total` desde `project_budgets`.
- `funding_gap` y estado privado desde `project_funding_sources`.
- `keywords` desde proyecto + breakdown.
- `coproduction_interest` inferido por paises y lenguaje del proyecto.

## Reglas MVP de matching
- Espana: prioriza elegibilidad territorial espanola, tipo de obra, fase y relacion presupuesto/ayuda.
- Europa: prioriza cooperacion, multiterritorio y elegibilidad europea.
- Iberoamerica / LatAm: prioriza coproduccion, codesarrollo y presencia iberoamericana.
- Siempre revisa:
  - region_scope
  - opportunity_type
  - phase compatibility
  - work type compatibility
  - territorial compatibility
  - collaboration rules
  - budget / max award relation
  - funding gap relevance
  - applicant hints
  - deadline proximity
  - document gaps detectables

## Salidas requeridas por convocatoria
- `match_score` 0-100
- `fit_level`: `high|medium|low|blocked`
- `fit_summary`
- `blocking_reasons_json`
- `missing_documents_json`
- `recommended_actions_json`
- `confidence_level`
- `evaluation_version`

## Endpoints MVP
- `POST /api/projects/{project_id}/funding/recompute`
- `GET /api/projects/{project_id}/funding/matches`
- `GET /api/projects/{project_id}/funding/checklist`
- `GET /api/projects/{project_id}/funding/profile`

## Seguridad
- Tenant-safe absoluto por `project_id + organization_id`.
- Tenant B no puede recalcular ni leer matches de A.
- El catalogo institucional sigue siendo comun/publico; los resultados del matcher no.

## Criterio de cierre
- Matcher usable por proyecto.
- Matching ES/EU/LATAM con score, razones y acciones.
- Checklist accionable consolidado.
- Persistencia limpia sin duplicados por recompute.
- Sin abrir dashboard complejo, billing, alertas automaticas ni dossier especializado.

## Metadata
- created: 2026-04-22
- status: MVP
- owner: backend/product logic
