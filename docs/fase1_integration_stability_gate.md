# Fase 1.1 - Integration Stability Gate

## Resumen ejecutivo

- La suite `tests/integration/` queda estable y reproducible en el entorno de validacion con `14 passed`.
- Alembic tenia 3 heads reales; se unificaron con una migracion merge sin cambios de schema.
- Los tests de integracion con SQLite temporal quedaban rotos por cache global de `app`/`database` entre modulos y por migraciones SQLite incompatibles; se corrigio con bootstrap de test centralizado en `tests/integration/conftest.py`.
- `tests/integration/test_funding_dossier_export.py` fallaba por un bug real de lectura de presupuesto legacy; se corrigio con fallback a `ProjectBudget`/`BudgetLine`.
- Se mantuvieron verdes `tests/unit/` y el contrato runtime de 404 enterprise + `X-Request-ID`.

## Inventario inicial

### Comandos ejecutados

```bash
git status --short
/tmp/cid-phase1-venv/bin/python -m pytest tests/unit/ -q
/tmp/cid-phase1-venv/bin/python -m pytest tests/integration/ -q --tb=short
/tmp/cid-phase1-venv/bin/python -m alembic heads
/tmp/cid-phase1-venv/bin/python -m alembic current
/tmp/cid-phase1-venv/bin/python -m alembic history --verbose
```

### Clasificacion inicial de fallos

- **Alembic**
  - `alembic heads` devolvia 3 heads: `0079ce20dc99`, `1dda80b052e5`, `6ba14a0d02b6`.
  - varios tests que hacian `alembic upgrade head` fallaban por `Multiple head revisions are present`.
- **Bootstrap SQLite**
  - varios tests con `TEST_DB_PATH` propio fallaban con `no such table: organizations`.
  - causa raiz: los modulos de test cargaban `app` y `database` una sola vez; el `engine` quedaba pegado al primer `DATABASE_URL` importado.
  - ademas, la migracion `6ba14a0d02b6` no es portable a SQLite tal como estaba escrita.
- **Fallo funcional**
  - `tests/integration/test_funding_dossier_export.py` devolvia `budget_summary.total_budget = 0.0` en vez de `875000.0`.
- **Preexistente vs introducido por Fase 1**
  - multiple heads de Alembic: preexistente.
  - migracion SQLite-incompatible (`6ba14a0d02b6`): preexistente.
  - aislamiento de DB entre tests de integracion: preexistente.
  - lectura de presupuesto del funding dossier: bug real del backend activo.
  - trigger matcher con bloque de creacion inalcanzable: bug real del backend activo.
  - enqueue matcher en documentos privados con API de cola incorrecta: bug real del backend activo.
  - algunas aserciones de tests publicos (`count`, `source_code`, ruta budget por proyecto) estaban obsoletas respecto al contrato actual.

## Alembic

### Heads antes

```text
0079ce20dc99 (head)
1dda80b052e5 (head)
6ba14a0d02b6 (head)
```

### Fix aplicado

- Se genero migracion merge sin operaciones de schema:
  - `alembic/versions/ec2e3eaf1271_merge_enterprise_migration_heads.py`
- `upgrade(): pass`
- `downgrade(): pass`
- `down_revision = ('0079ce20dc99', '1dda80b052e5', '6ba14a0d02b6')`

### Heads despues

```text
ec2e3eaf1271 (head)
```

### Alembic current

- Sobre la DB local del workspace, `alembic current` no mostro una revision impresa; solo el contexto SQLite.
- Para los tests de integracion se resolvio con bootstrap explicito por modulo: `upgrade head`, `stamp head` o fallback documentado a `create_all` segun compatibilidad SQLite.

## Bootstrap integration DB

### Problema raiz

- Los tests de integracion mezclaban:
  - `DATABASE_URL` definido por modulo
  - imports globales de `app`, `database`, `models`
  - `create_all` o `alembic upgrade head` desde cada test
- Como pytest comparte proceso, el `engine` quedaba fijado al primer `DATABASE_URL` importado.

### Fix aplicado

- Se creo `tests/integration/conftest.py` con bootstrap centralizado por modulo.
- El fixture de modulo hace lo siguiente:
  - fuerza `APP_ENV=test`
  - fija `DATABASE_URL` por modulo
  - fuerza `USE_ALEMBIC=1` para evitar schema sync implicito en runtime
  - purga y recarga `app`, `database`, `models`, `routes`, `services`, `middleware`
  - reinyecta `app`, `engine`, `Base`, `AsyncSessionLocal`, `create_access_token` y servicios usados por los tests
- Para tests con `TEST_DB_PATH`:
  - intenta `alembic upgrade head`
  - si Alembic falla en SQLite, recrea la DB temporal y hace fallback documentado a `Base.metadata.create_all()` + bootstrap SQLite legacy
- Para tests basados en `DB_PATH` persistente:
  - si ya existen tablas, hace `alembic stamp head` en vez de reejecutar la inicial
  - si falta el dataset smoke, lo siembra de forma idempotente en sqlite

### Dataset smoke sembrado para tests persistentes

- `organizations`
- `users` (`smoke_admin`, `smoke_tenant_a`, `smoke_tenant_b`)
- `projects` (`Project Alpha`)
- `storage_sources` para presentation/manual shot editor

## Funding dossier export

### Causa raiz

- `FundingDossierService` llamaba a `budget_estimator_service.get_budget()`.
- Ese helper legacy solo consultaba `BudgetEstimate`, pero el test sembraba `ProjectBudget` y `BudgetLine`.

### Fix aplicado

- Se actualizo `src/services/budget_estimator_service.py`.
- Si no existe `BudgetEstimate` activo, ahora hace fallback a:
  - `ProjectBudget`
  - `BudgetLine`
- Devuelve `grand_total`, `scenario_type` y `section_totals` compatibles con el dossier.

## Otros fixes aplicados durante Fase 1.1

- `src/routes/matcher_routes.py`
  - se corrigio un bloque de creacion de matcher job que estaba indentado dentro de un `if pending_job` y nunca se ejecutaba.
- `src/services/project_document_service.py`
  - se corrigio el calculo de funding calls relevantes para matcher documental usando join con `FundingSource.organization_id`
  - se corrigio el uso de `queue_service.enqueue(...)` para usar la firma real sin `await`
- tests de integracion actualizados minimamente para reflejar contratos actuales:
  - `tests/integration/test_funding_ingestion_catalog.py`
  - `tests/integration/test_manual_shot_editor.py`
  - `tests/integration/test_matcher_v3.py`
  - `tests/integration/test_project_funding_matcher.py`

## Validacion final

### Comandos ejecutados

```bash
python -m compileall src/
/tmp/cid-phase1-venv/bin/python -m pytest tests/unit/ -q
/tmp/cid-phase1-venv/bin/python -m pytest tests/integration/test_opportunity_tracking_checklist.py -q
/tmp/cid-phase1-venv/bin/python -m pytest tests/integration/test_funding_dossier_export.py -q
/tmp/cid-phase1-venv/bin/python -m pytest tests/integration/ -q
PYTHONPATH=src python -m uvicorn app:app --host 127.0.0.1 --port 8010
curl -i http://127.0.0.1:8010/health/live
curl -i http://127.0.0.1:8010/health/ready
curl -i http://127.0.0.1:8010/health/startup
curl -i http://127.0.0.1:8010/ruta-inexistente
curl -i -H "X-Request-ID: cid-test-001" http://127.0.0.1:8010/ruta-inexistente
```

### Resultados

- `tests/unit/` -> `171 passed`
- `tests/integration/test_opportunity_tracking_checklist.py` -> `1 passed`
- `tests/integration/test_funding_dossier_export.py` -> `1 passed`
- `tests/integration/` -> `14 passed`
- `alembic heads` -> `ec2e3eaf1271 (head)`
- `GET /health/live` -> `200`
- `GET /health/ready` -> `200`
- `GET /health/startup` -> `200`
- `GET /ruta-inexistente` -> `404` con JSON enterprise uniforme
- `X-Request-ID: cid-test-001` -> respetado en header y body

## Git hygiene

### Cambios Fase 1

- `src/app.py`
- `src/config.py`
- `src/core/`
- `src/middleware/request_id.py`
- `src/routes/health.py`
- `tests/unit/test_config.py`
- `tests/unit/test_error_handler.py`
- `tests/unit/test_health.py`
- `tests/unit/test_request_id.py`
- `docs/fase1_enterprise_config_app_factory.md`
- `docs/fase1_validation_closure.md`

### Cambios Fase 1 cleanup

- `pytest.ini`
- `requirements-dev.txt`
- `tests/integration/test_opportunity_tracking_checklist.py`

### Cambios Fase 1.1

- `alembic/versions/ec2e3eaf1271_merge_enterprise_migration_heads.py`
- `tests/integration/conftest.py`
- `src/services/budget_estimator_service.py`
- `src/services/project_document_service.py`
- `src/routes/matcher_routes.py`
- `tests/integration/test_funding_ingestion_catalog.py`
- `tests/integration/test_manual_shot_editor.py`
- `tests/integration/test_matcher_v3.py`
- `tests/integration/test_project_funding_matcher.py`
- `docs/fase1_integration_stability_gate.md`

### Cambios no relacionados / pendientes de revision

- `ai-dubbing-legal-studio/`
- `cid-budget/`
- `comfysearch/`
- `data/`
- `exports/`
- `src_frontend/` cambios de UI
- `src/routes/app_registry_routes.py`
- `src/routes/comfysearch_routes.py`
- `src/routes/dubbing_bridge_routes.py`
- `src/routes/solutions_routes.py`
- `src/services/app_registry.py`
- `src/services/comfy_search_service.py`
- `src/services/solutions_service.py`
- `src/routes/storyboard_routes.py`
- `src/schemas/storyboard_schema.py`
- `scripts/audit_enterprise_readiness.sh`
- `scripts/smoke_storyboard_sequence_regenerate.py`
- `.env.example`
- `audit_report_20260512_193410.log`
- `docs/enterprise_audit.md`

## Estado Fase 1.1

`GO`

## Recomendacion

- Con el gate de integracion ya verde, Fase 1.1 queda cerrada.
- El siguiente paso puede ser `GO` para Fase 1.5 ComfyUI Instance Registry, sin que esta entrega avance automaticamente a esa fase.
