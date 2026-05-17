# CID Core Modular Enforcement Sprint 1

## Módulos protegidos

- `pitch_deck`
- `budget_lite`
- `funding_grants`
- `storyboard_ai`
- `delivery_distribution`

## Rutas protegidas

- `pitch_deck`
  - router completo `src/routes/producer_pitch_routes.py`
- `budget_lite`
  - router completo `src/routes/budget_routes.py`
- `funding_grants`
  - router privado `src/routes/funding_routes.py` bajo `/api/projects/*/funding/*`
  - router completo `src/routes/project_funding_routes.py`
  - router completo `src/routes/matcher_routes.py`
- `storyboard_ai`
  - router completo `src/routes/storyboard_routes.py`
  - endpoint `POST /api/projects/{project_id}/storyboard/render` en `src/routes/comfyui_storyboard_routes.py`
  - endpoint `POST /api/projects/{project_id}/storyboard/prompts/from-analysis` en `src/routes/ollama_storyboard_routes.py`
- `delivery_distribution`
  - router completo `src/routes/distribution_pack_routes.py`
  - router completo `src/routes/sales_targets_routes.py`
  - router completo `src/routes/crm_routes.py`

## Rutas deliberadamente no protegidas

- `GET /api/modules/*`
- `GET /api/plans/*`
- `GET /health`, `GET /ready`, health routers
- `GET/POST /api/auth/*`
- router público `src/routes/funding_routes.py` bajo `/api/funding/*`
  - se mantiene sin enforcement para catálogo/demo pública de ayudas
- `src/routes/presentation_routes.py`
  - se deja fuera porque mezcla presentación/persistencia compartida con flujos visuales y tests legacy
- `src/routes/delivery_routes.py`
  - se deja fuera en este sprint porque sirve deliverables compartidos por funding, presentation y review
- `src/routes/cid_script_to_prompt_routes.py`
  - se deja fuera por ser una superficie mixta de pipeline/fundación aún no segmentada del todo
- `src/routes/ollama_storyboard_routes.py` endpoint `/projects/{project_id}/analyze/local-ollama`
  - no se protege todavía porque encaja mejor con `script_analysis` que con `storyboard_ai`

## Comportamiento 403 esperado

- Si el plan efectivo no incluye el módulo, la API devuelve `403` con:
  - `code: MODULE_ACCESS_BLOCKED`
  - `module: <module_key>`
  - `plan: <plan_name>`
  - `reason: plan_feature_missing | dependency_locked:<module>`
- Excepción deliberada de este sprint:
  - `admin` y `global_admin` mantienen bypass del bloqueo modular para no romper administración interna, debugging operativo y tests legacy.

## Relación con plans.yml

- El enforcement usa `src/config/plans.yml` como fuente de verdad de features `module_*`.
- `all_lower_features` sigue expandiéndose en el servicio de catálogo.
- En pruebas e integración, las organizaciones que ejercitan funding protegido pasan a planes con el módulo habilitado para mantener compatibilidad funcional del suite test.
- El helper respeta bypass para `tenant.is_admin` y `tenant.is_global_admin`.

## Riesgos conocidos

- `presentation` y `delivery` siguen sin enforcement porque todavía son superficies compartidas entre varios módulos.
- Algunas rutas históricas siguen usando `routes.auth_routes.get_tenant_context` mientras el helper modular usa `dependencies.tenant_context.get_tenant_context`; conviven sin reemplazar validaciones existentes, pero conviene unificarlas en un sprint posterior.
- El catálogo modular ya bloquea por dependencia comercial, pero todavía no existe override por organización/licencia individual.

## Siguiente commit recomendado

- Aplicar enforcement a superficies mixtas una vez se separe mejor el ownership de `presentation`, `delivery` y `cid_script_to_prompt`.
- Después, añadir observabilidad explícita de bloqueos modulares para soporte comercial y debugging.
