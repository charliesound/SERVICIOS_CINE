# AILinkCinema — Roadmap Técnico Post-Sprint 10

> Documento historico de planificacion. Algunas secciones (especialmente Sprint 11-12) ya no reflejan el estado real del codigo implementado.
> Estado operativo actual: `docs/PRODUCTION_CANDIDATE_STATUS.md`, `docs/SPRINT13_RUNBOOK.md`, `docs/RELEASE_DEMO_GUIDE.md`.
> Actualizacion Sprint 13.3: queue persistence minima sobre DB con recovery de restart ya implementada; los TODO de cola mas abajo quedaron desfasados parcialmente.

> Sprint 10 (Project + Script + Analyze + Storyboard) ✅ CERRADO
> Este documento: preparación Sprint 11 y Sprint 12. **SIN IMPLEMENTAR.**

---

## VEREDICTO SPRINT 10 — YA HECHO ✅

### Backend
| Componente | Archivo | Estado |
|---|---|---|
| `script_text` en modelo Project | `src/models/core.py:34` | ✅ |
| PUT `/projects/{id}/script` | `src/routes/project_routes.py:152` | ✅ |
| POST `/projects/{id}/analyze` | `src/routes/project_routes.py:309` | ✅ |
| POST `/projects/{id}/storyboard` | `src/routes/project_routes.py:373` | ✅ |
| `_parse_storyboard()` | `src/routes/project_routes.py:181` | ✅ |
| `create_script_document()` | `src/services/document_service.py:485` | ✅ |
| `extract_text_directly()` | `src/services/document_service.py:336` | ✅ |
| `DocumentSourceKind.SCRIPT_TEXT` | `src/models/document.py:27` | ✅ |

### Frontend
| Componente | Archivo | Estado |
|---|---|---|
| ProjectsPage | `src_frontend/src/pages/ProjectsPage.tsx` | ✅ |
| NewProjectPage | `src_frontend/src/pages/NewProjectPage.tsx` | ✅ |
| ProjectDetailPage con botones reales | `src_frontend/src/pages/ProjectDetailPage.tsx` | ✅ |
| `projectsApi.analyze()` | `src_frontend/src/api/projects.ts:43` | ✅ |
| `projectsApi.storyboard()` | `src_frontend/src/api/projects.ts:52` | ✅ |
| TypeScript build | `tsc --noEmit` | ✅ 0 errores |

---

## SPRINT 11 — History / Tracking / Recovery / Assets Persistentes

### 1. Job History por Proyecto

**Descripción:** Cada proyecto necesita un historial de operaciones ejecutadas (análisis, storyboard, renders, etc.).

**TODO técnico:**
- [ ] Crear `JobHistory` model en `src/models/core.py` o `src/models/history.py`
  - Campos: `id`, `project_id`, `operation_type` (analyze/storyboard/render), `status`, `result_payload` (JSON), `created_by`, `created_at`, `duration_ms`
  - Índices: `(project_id, created_at)`, `(created_by)`
- [ ] Crear `src/routes/history_routes.py`
  - `GET /api/projects/{id}/history` — listar historial del proyecto
  - `GET /api/history/{history_id}` — detalle de una operación
  - `POST /api/projects/{id}/history` — registrar operación (llamado internamente por analyze/storyboard)
- [ ] Modificar `analyze_project_script` en `project_routes.py` para persistir resultado en `JobHistory`
- [ ] Modificar `generate_storyboard` en `project_routes.py` para persistir resultado en `JobHistory`
- [ ] Crear schema `src/schemas/history_schema.py`: `JobHistoryResponse`, `JobHistoryListResponse`
- [ ] Crear `src_frontend/src/api/history.ts` con `getProjectHistory()`, `getHistoryItem()`
- [ ] Crear `src_frontend/src/pages/ProjectHistoryPage.tsx`
  - Lista cronológica de operaciones del proyecto
  - Estado: success/failed/processing
  - Expandir para ver payload (resultado del análisis, escenas del storyboard)
  - Link desde `ProjectDetailPage` hacia `/projects/{id}/history`

**Dependencias:**
- Sprint 10 (`project_routes.py` analyze + storyboard) — ya existente
- `Project` model — ya existente

**Riesgos:**
- El `result_payload` puede crecer mucho si el storyboard tiene 200 escenas. Considerar truncar o guardar en tabla separada.
- Polling de estado aún no existe para operaciones de análisis (solo existe para renders via `useJobs`).

**Archivos previsibles:**
- `src/models/history.py` (nuevo)
- `src/routes/history_routes.py` (nuevo)
- `src/schemas/history_schema.py` (nuevo)
- `src_frontend/src/api/history.ts` (nuevo)
- `src_frontend/src/pages/ProjectHistoryPage.tsx` (nuevo)
- `src/routes/project_routes.py` (modificar analyze + storyboard para guardar en JobHistory)
- `src_frontend/src/App.tsx` (agregar ruta `/projects/:id/history`)

---

### 2. Tracking de Jobs con Persistencia

**Descripción:** El sistema actual tiene cola en memoria (`queue_service.py QueueService`). Los jobs se pierden al reiniciar. Hay que persistirlos en DB.

**TODO técnico:**
- [ ] Crear `Job` model en `src/models/core.py` o `src/models/queue.py`
  - Campos: `id`, `organization_id`, `project_id`, `job_type` (render/analyze/storyboard), `status` (pending/running/success/failed), `backend`, `priority`, `retry_count`, `error_message`, `result_payload`, `created_by`, `created_at`, `updated_at`, `completed_at`
  - Índices: `(organization_id, created_at)`, `(project_id)`, `(status)`
- [ ] Modificar `src/services/queue_service.py`
  - `QueueService` guarda cada job en DB antes de encolar
  - `mark_succeeded()` / `mark_failed()` actualizan `completed_at` + `result_payload`
  - Al iniciar, carga jobs pendientes desde DB
- [ ] Modificar `src/services/job_scheduler.py`
  - Al arrancar, recupera jobs pendientes desde DB en lugar de solo memoria
  - Al completar, actualiza `Job` en DB (no solo ComfyUI)
- [ ] Modificar `src/routes/queue_routes.py`
  - `GET /api/queue/status` filtra desde DB
  - `GET /api/queue/status/{job_id}` retorna con más metadata
- [ ] Modificar `src_frontend/src/hooks/useQueue.ts`
  - El polling de `useJobQueueStatus` ya existe (3s). Asegurar que consulta endpoint actualizado.
- [ ] Asegurar que `GET /api/queue/status` retorna todos los jobs del usuario (no solo del backend en memoria)

**Dependencias:**
- `QueueService` singleton — ya existente en `src/services/queue_service.py`
- `JobScheduler` — ya existente en `src/services/job_scheduler.py`
- `useQueue` / `useJobs` hooks — ya existentes en frontend

**Riesgos:**
- Migración de schema: hay que crear la tabla `jobs` en la DB existente. Alembic migration necesaria.
- El scheduler actual hace polling de ComfyUI cada 5s. Persistir jobs no cambia la latencia de detección de completitud.
- Doble escritura: si ComfyUI falla y el scheduler no puede actualizar, el job queda en estado incorrecto. Necesita transacción.

**Archivos previsibles:**
- `src/models/queue.py` o extensión de `src/models/core.py` (nuevo modelo Job)
- `src/services/queue_service.py` (modificar — agregar persistencia)
- `src/services/job_scheduler.py` (modificar — cargar jobs desde DB al arrancar)
- `src/routes/queue_routes.py` (modificar — consultar DB)
- `src_frontend/src/hooks/useQueue.ts` (modificar — endpoints actualizados)

---

### 3. Recovery / Retry Robusto

**Descripción:** El retry actual es solo `max_retries=3` sin backoff. Para producción comercial se necesita retry inteligente + recovery de jobs huerfanos.

**TODO técnico:**
- [ ] Modificar `src/services/queue_service.py`
  - Agregar backoff exponencial: `delay = base_delay * 2^retry_count` (base=30s, max=10min)
  - Agregar circuit breaker: si 5 jobs fallan seguidos en un backend, marcarlo como `degraded` y no encolar por 5 min
  - Agregar dead letter tracking: jobs con `retry_count >= max_retries` se mueven a cola de muertos, no se reintentan automáticamente
  - Crear endpoint `GET /api/queue/dead-letter` para listar jobs fallidos permanentemente
- [ ] Modificar `src/services/job_scheduler.py`
  - Al arrancar, detectar jobs huerfanos (estado=running pero scheduler reiniciado) y re-intentarlos
  - Timeout configurable: el actual es 3600s hardcodeado, mover a config
- [ ] Modificar `src/routes/queue_routes.py`
  - `POST /api/queue/{job_id}/retry` — con parámetro opcional `force=true` para reintentar aunque exceda max_retries
  - `DELETE /api/queue/{job_id}` — cancelar y marcar como cancelled (no solo remove de cola)
- [ ] Modificar `src/models/queue.py` (Job model del punto anterior)
  - Campo `last_error` para guardar mensaje completo del último error
  - Campo `retry_after` para guardar timestamp del próximo retry
  - Campo `circuit_breaker_hits` por backend
- [ ] Frontend: `src_frontend/src/api/queue.ts`
  - `retryJob(jobId, force?)`
  - `cancelJob(jobId)`
  - `getDeadLetterJobs()`
- [ ] Frontend: agregar UI en `Dashboard.tsx` o crear `JobsPage.tsx`
  - Mostrar jobs fallidos con botón "Reintentar"
  - Mostrar jobs huerfanos con warning
  - Indicador de estado de backends (healthy/degraded)

**Dependencias:**
- Modelo `Job` persistido (Sprint 11 item 2)
- `QueueService` existente
- `JobScheduler` existente

**Riesgos:**
- Backoff exponencial puede hacer que un usuario espere 10 min para el retry. Comunicar ETA en UI.
- Circuit breaker puede afectar la experiencia si ComfyUI tiene problemas temporales. Documentar en UI.
- Jobs huerfanos: si ComfyUI completa un job pero el scheduler se reinició antes de actualizar, el job queda "running" para siempre. Recovery necesita comparar con historial real de ComfyUI.

**Archivos previsibles:**
- `src/models/queue.py` (extender)
- `src/services/queue_service.py` (modificar — backoff + circuit breaker)
- `src/services/job_scheduler.py` (modificar — orphan detection)
- `src/routes/queue_routes.py` (modificar — endpoints retry/cancel/dead-letter)
- `src_frontend/src/api/queue.ts` (modificar)
- `src_frontend/src/pages/Dashboard.tsx` (modificar — sección de jobs fallidos)

---

### 4. Media Assets Persistentes con Vínculo a Proyecto

**Descripción:** Los resultados del storyboard/breakdown son JSON efímero. Se necesita guardar los assets generados (imágenes de plano, PDFs de análisis, etc.) vinculados al proyecto.

**TODO técnico:**
- [ ] Verificar modelo `MediaAsset` existente en `src/models/storage.py:270`
  - Ya tiene: `id`, `organization_id`, `project_id`, `storage_source_id`, `file_name`, `canonical_path`, `mime_type`, `asset_type`
  - Extender si falta: agregar `source_job_id` (vincular al Job que generó el asset), `source_operation` (storyboard/breakdown/analyze)
- [ ] Modificar `_parse_storyboard()` en `project_routes.py`
  - Después de generar el storyboard JSON, guardar cada "shot" como `MediaAsset` con `asset_type=STORYBOARD_FRAME`
  - Guardar el PDF del análisis como `MediaAsset` con `asset_type=ANALYSIS_REPORT`
  - Usar `storage_service` para escribir archivos en disco/S3 y crear registro en DB
- [ ] Modificar `analyze_project_script`
  - Generar un PDF o JSON estructurado con el resultado del análisis
  - Guardar como `MediaAsset` vinculado al proyecto
- [ ] Crear `src/routes/media_routes.py`
  - `GET /api/projects/{id}/media` — listar assets del proyecto
  - `GET /api/media/{media_id}` — metadata del asset
  - `GET /api/media/{media_id}/download` — download real
- [ ] Crear `src_frontend/src/api/media.ts`
- [ ] Modificar `ProjectDetailPage.tsx`
  - Sección "Assets generados" que lista los `MediaAsset` del proyecto
  - Thumbnail para imágenes, icono para PDFs/JSON
- [ ] Crear `src_frontend/src/pages/ProjectAssetsPage.tsx`

**Dependencias:**
- `MediaAsset` model — ya existente en `src/models/storage.py`
- `storage_service` — ya existente en `src/services/storage_service.py`
- `_parse_storyboard()` — ya existente en `project_routes.py`

**Riesgos:**
- Guardar assets en disco local no escala a múltiples instancias. Requiere S3/MinIO para producción real.
- El storyboard genera JSON, no imágenes reales. Si se quiere visualizar como planche gráfico, se necesita un servicio de renderizado de storyboards (para Sprint 12 o más adelante).
- Espacio en disco: un proyecto con muchos análisis puede consumir mucho storage. Implementar cleanup policy.

**Archivos previsibles:**
- `src/models/storage.py` (modificar — agregar source_job_id, source_operation)
- `src/routes/project_routes.py` (modificar — guardar MediaAsset tras analyze/storyboard)
- `src/routes/media_routes.py` (nuevo)
- `src_frontend/src/api/media.ts` (nuevo)
- `src_frontend/src/pages/ProjectAssetsPage.tsx` (nuevo)
- `src_frontend/src/pages/ProjectDetailPage.tsx` (modificar — sección assets)

---

### 5. Vista History / Review

**Descripción:** Página dedicada para que el usuario revise todo lo que se ha hecho en su proyecto (historial + assets + jobs).

**TODO técnico:**
- [ ] Crear `src_frontend/src/pages/ProjectReviewPage.tsx`
  - Tres tabs: "Historial", "Assets", "Jobs"
  - Tab Historial: lista de `JobHistory` (análisis, storyboards) con estado y timestamp
  - Tab Assets: grid de `MediaAsset` con preview
  - Tab Jobs: lista de `Job` con estado de renders
- [ ] Modificar `src_frontend/src/App.tsx`
  - Agregar `/projects/:id/review` → `ProjectReviewPage`
  - Link desde `ProjectDetailPage` hacia `/projects/:id/review`
- [ ] Considerar: agregar filtro por tipo de operación y rango de fechas en `ProjectHistoryPage`

**Dependencias:**
- `JobHistory` model (Sprint 11 item 1)
- `MediaAsset` vinculado (Sprint 11 item 4)
- `Job` model persistido (Sprint 11 item 2)

**Riesgos:**
- Dependencia de múltiples modelos. Sprint 11 items 1, 2 y 4 deben estar terminados antes de esta página.
- La UI puede quedar compleja si hay muchos items. Implementar paginación desde el inicio.

**Archivos previsibles:**
- `src_frontend/src/pages/ProjectReviewPage.tsx` (nuevo — combina todo)
- `src_frontend/src/App.tsx` (modificar — agregar ruta)
- `src_frontend/src/pages/ProjectHistoryPage.tsx` (nuevo — Sprint 11 item 1)

---

## SPRINT 12 — Cuotas / Métricas / Export / Packaging Comercial

### 1. Cuotas por Plan Persistentes y Detalladas

**Descripción:** El sistema actual tiene `UserPlanTracker` en memoria (singleton con dict). No persiste entre arranques y no tiene granularidad temporal (day/month).

**TODO técnico:**
- [ ] Crear `UsageRecord` model en `src/models/billing.py` (nuevo archivo)
  - Campos: `id`, `organization_id`, `user_id`, `metric_type` (images_generated, video_seconds, storage_mb, api_calls, projects_created), `count`, `period_start` (date), `period_end` (date), `created_at`
  - Índice: `(organization_id, metric_type, period_start)` único
- [ ] Crear `UsageService` en `src/services/usage_service.py`
  - `record_usage(org_id, metric_type, count=1)` — upsert en UsageRecord
  - `get_usage(org_id, metric_type, period)` — obtener consumo actual
  - `check_quota(org_id, plan_name, metric_type)` — comparar con plans.yml
- [ ] Modificar `src/services/plan_limits_service.py`
  - `UserPlanTracker` guardar en DB (no solo memoria)
  - Al reiniciar, cargar desde `UsageRecord`
- [ ] Modificar `src/routes/render_routes.py`
  - Antes de aceptar job, llamar `usage_service.check_quota()`
  - Si excede cuota, retornar HTTP 429 con detalle: qué quota, cuánto usado, cuánto queda
- [ ] Modificar `src/routes/project_routes.py`
  - `POST /projects` — increment `projects_created` en UsageRecord
  - `POST /projects/{id}/analyze` — increment `analyses_run`
- [ ] Modificar `src_frontend/src/api/plan.ts`
  - `getMyUsage()` — consumo actual por métrica
  - Mostrar en `PlansPage.tsx`: barra de progreso por cuota vs límite
- [ ] Modificar `src_frontend/src/pages/PlansPage.tsx`
  - Gráficos de uso por métrica (barras o donuts)
  - Alerts cuando se acerca al límite (>80%)

**Dependencias:**
- `plans.yml` — ya existente en `src/config/plans.yml`
- `plan_limits_service.py` — ya existente
- `UserPlanTracker` — ya existente

**Riesgos:**
- Overhead de escritura en DB en cada job submit. Considerar batching (escribir cada N jobs o cada minuto).
- Migración de schema: crear tabla `usage_records`.
- Sincronización: si el scheduler de jobs actualiza `active_jobs` en memoria pero no en DB, puede haber inconsistency. Resolver en Sprint 11 item 2.

**Archivos previsibles:**
- `src/models/billing.py` (nuevo — UsageRecord)
- `src/services/usage_service.py` (nuevo — UsageService)
- `src/services/plan_limits_service.py` (modificar — persistir UserPlanTracker)
- `src/routes/render_routes.py` (modificar — check_quota)
- `src/routes/project_routes.py` (modificar — record_usage en analyze)
- `src_frontend/src/api/plan.ts` (modificar — getMyUsage)
- `src_frontend/src/pages/PlansPage.tsx` (modificar — UI de cuotas)

---

### 2. Métricas de Uso Detalladas por Organización

**Descripción:** Las métricas actuales (`metrics_service.py`) son globales del sistema. Se necesitan métricas por organización para dashboards comerciales.

**TODO técnico:**
- [ ] Crear `OrgMetrics` model en `src/models/billing.py`
  - Campos: `id`, `organization_id`, `period` (daily/weekly/monthly), `period_start`, `total_jobs`, `successful_jobs`, `failed_jobs`, `total_cost_estimate`, `storage_used_mb`, `api_calls`, `active_users`, `projects_count`, `created_at`
- [ ] Crear `OrgMetricsService` en `src/services/org_metrics_service.py`
  - `aggregate_daily(org_id)` — recalcula métricas diarias desde Job + UsageRecord
  - `get_trend(org_id, days)` — serie temporal de métricas
- [ ] Crear `GET /api/org/{org_id}/metrics` en `src/routes/org_routes.py` (o crear archivo)
  - Query params: `period` (daily/weekly/monthly), `days`
  - Retorna: jobs totales, tasa de éxito, uso de storage, consumo por plan
- [ ] Crear `src_frontend/src/pages/OrgMetricsPage.tsx`
  - Gráficos de tendencia (líneas/barras): jobs por día, tasa de éxito, storage
  - Comparar con límites del plan
  - Accessible desde CID sidebar (link en Settings o Dashboard)
- [ ] Modificar `Dashboard.tsx`
  - Reemplazar stats hardcodeadas por datos reales de `/api/org/{id}/metrics`

**Dependencias:**
- `Job` model persistido (Sprint 11 item 2)
- `UsageRecord` model (Sprint 12 item 1)
- `MetricsService` global — ya existente en `src/services/metrics_service.py`

**Riesgos:**
- Agregación diaria puede ser costosa si hay muchos jobs. Considerar materialized views o agregación incremental.
- Dashboard con muchos gráficos puede ser lento. Lazy load o paginación.

**Archivos previsibles:**
- `src/models/billing.py` (modificar — agregar OrgMetrics)
- `src/services/org_metrics_service.py` (nuevo)
- `src/routes/org_routes.py` o nuevo archivo de métricas
- `src_frontend/src/api/org.ts` (nuevo)
- `src_frontend/src/pages/OrgMetricsPage.tsx` (nuevo)
- `src_frontend/src/pages/Dashboard.tsx` (modificar)

---

### 3. Export PDF / ZIP / FCPXML

**Descripción:** No existen endpoints de exportación. El storyboard y análisis son JSON en la DB. Se necesita poder descargar como PDF profesional, ZIP con todos los assets, o FCPXML para edición en Premiere/Resolve.

**TODO técnico:**
- [ ] Crear `src/services/export_service.py`
  - `export_storyboard_pdf(project_id, history_id)` — genera PDF del storyboard con escenas, planos, descripciones. Usar `reportlab` o `weasyprint`.
  - `export_storyboard_zip(project_id)` — zip con PDF + JSON del storyboard + imágenes de assets
  - `export_analysis_pdf(project_id, history_id)` — PDF del análisis con doc type, confidence, resumen
  - `export_fcpxml(project_id)` — genera FCPXML con líneas de tiempo para Premiere (secuencias → clips)
- [ ] Crear `src/routes/export_routes.py`
  - `GET /api/projects/{id}/export/storyboard/pdf`
  - `GET /api/projects/{id}/export/storyboard/zip`
  - `GET /api/projects/{id}/export/analysis/pdf`
  - `GET /api/projects/{id}/export/fcpxml`
  - Todos retornan `StreamingResponse` con el archivo
- [ ] Agregar botones en `ProjectReviewPage.tsx` (Sprint 11 item 5)
  - "Descargar PDF" / "Descargar ZIP" / "Exportar FCPXML"
- [ ] Modificar `src/routes/project_routes.py`
  - Los endpoints de export necesitan el `project_id` para recuperar `script_text` y `JobHistory`
- [ ] Agregar verificación de plan en export
  - Solo `producer`/`studio`/`enterprise` pueden exportar ZIP y FCPXML
  - `free`/`demo` solo PDF del análisis

**Dependencias:**
- `JobHistory` (Sprint 11 item 1)
- `MediaAsset` vinculados (Sprint 11 item 4)
- `reportlab` o `weasyprint` (dependencia Python a agregar)

**Riesgos:**
- PDF generation en servidor es costoso. Procesar en background job, no request síncrono.
- FCPXML es complejo. Solo soportar caso básico (una secuencia por proyecto) en Sprint 12.
- Dependencia externa (`reportlab`/`weasyprint`) requiere instalación en el contenedor.

**Archivos previsibles:**
- `src/services/export_service.py` (nuevo)
- `src/routes/export_routes.py` (nuevo)
- `src_frontend/src/api/export.ts` (nuevo)
- `src_frontend/src/pages/ProjectReviewPage.tsx` (modificar — agregar botones de export)
- `requirements.txt` o `pyproject.toml` (modificar — agregar reportlab o weasyprint)

---

### 4. Packaging para Demo Comercial e Inversores

**Descripción:** El demo actual (`demo_service.py`) es funcional pero no es una experiencia comercial lista para inversores. Se necesita un flow de onboarding guiado + datos de ejemplo impresionantes.

**TODO técnico:**
- [ ] Crear demo premium dataset en `src/services/demo_service.py`
  - Proyecto real con nombre atractivo ("Cortometraje Nebula — Previsualización")
  - Script de 15+ escenas con diálogos completos
  - Storyboard pre-generado con 30+ planos
  - Assets de ejemplo (imágenes placeholder de Unsplash)
  - 3 secuencias con nombres creativos
  - 5+ personajes con descripciones
- [ ] Modificar `POST /api/demo/quick-start` en `src/routes/demo_routes.py`
  - Nuevo parámetro: `experience` (basic/premium)
  - Premium: crea proyecto completo con todos los datos de ejemplo
  - Retorna `project_id`, `demo_credentials`, `onboarding_tips`
- [ ] Modificar `src_frontend/src/pages/RegisterDemoPage.tsx`
  - Nuevo flujo: email → 选择 plan → experiencia demo (básica/premium) → auto-login → onboarding tour
  - Onboarding tour: 4 pasos con spotlight + tooltip
    1. "Bienvenido a AILinkCinema" — explica el producto
    2. "Tu primer proyecto" — muestra el proyecto demo
    3. "Analiza tu guion" — resalta botón de analizar
    4. "Genera tu storyboard" — resalta botón de storyboard
- [ ] Crear `src_frontend/src/components/OnboardingTour.tsx`
  - Usar librería existente o implementar con CSS
  - Guardar `onboarding_completed` en localStorage
- [ ] Crear landing page comercial mejorada para inversores
  - Si no existe, crear `src_frontend/src/pages/InvestorLandingPage.tsx`
  - Secciones: problema, solución, métricas, casos de uso, pricing, CTA demo
  - Screenshots reales del producto (no mockups)
- [ ] Agregar tracking de métricas de onboarding
  - `onboarding_started`, `onboarding_completed`, `first_project_created`, `first_analysis_run`
  - Guardar en `UsageRecord` con `metric_type=onboarding_milestone`
- [ ] Preparar assets para packaging
  - Screenshots de alta calidad de la app funcionando
  - Video demo corto (30-60s) embed en landing
  - PDF one-pager para inversores

**Dependencias:**
- `demo_service.py` — ya existente en `src/services/demo_service.py`
- `demo_routes.py` — ya existente en `src/routes/demo_routes.py`
- `RegisterDemoPage.tsx` — ya existente en frontend
- `OnboardingTour` — no existe aún

**Riesgos:**
- El demo premium con muchos datos puede tardar en generarse. Ejecutar en background o pre-generar y guardar como fixture.
- Landing page para inversores puede requerir copywriting profesional. Postergar a Sprint 13 si no es crítico.
- Tracking de onboarding necesita consentimiento de cookies (GDPR). Agregar banner de cookies si hay mercado EU.

**Archivos previsibles:**
- `src/services/demo_service.py` (modificar — demo premium dataset)
- `src/routes/demo_routes.py` (modificar — experience=premium)
- `src_frontend/src/pages/RegisterDemoPage.tsx` (modificar — flujo con experiencia)
- `src_frontend/src/components/OnboardingTour.tsx` (nuevo)
- `src_frontend/src/pages/InvestorLandingPage.tsx` (nuevo, o integrar en LandingPage.tsx existente)
- `src_frontend/src/store/onboarding.ts` (nuevo — estado del tour)
- `src/models/billing.py` (modificar — agregar onboarding_milestone metric)

---

## ORDEN RECOMENDADO DE IMPLEMENTACIÓN

### Sprint 11 (Items en orden de dependencia):
1. **Item 1** — JobHistory model + history routes (sin esto, los demás no tienen dondepersistir)
2. **Item 2** — Job persistence (sin esto, retry y tracking no son confiables)
3. **Item 3** — Recovery/retry (depende de 2)
4. **Item 4** — MediaAssets persistentes (depende de 1 y 2)
5. **Item 5** — ProjectReviewPage (depende de 1, 2 y 4)

### Sprint 12 (Items en orden de dependencia):
1. **Item 1** — Cuotas persistentes (base de todo billing)
2. **Item 2** — Métricas por org (depende de 1 y Sprint 11 item 2)
3. **Item 3** — Export (depende de Sprint 11 item 1 y 4)
4. **Item 4** — Packaging demo (depende de Sprint 11 item 5 y item 3)

---

## RESUMEN ARCHIVOS POR SPRINT

### Sprint 11
**Nuevos:**
- `src/models/history.py`
- `src/models/queue.py`
- `src/routes/history_routes.py`
- `src/routes/media_routes.py`
- `src/schemas/history_schema.py`
- `src_frontend/src/api/history.ts`
- `src_frontend/src/api/media.ts`
- `src_frontend/src/pages/ProjectHistoryPage.tsx`
- `src_frontend/src/pages/ProjectAssetsPage.tsx`

**Modificados:**
- `src/models/core.py`
- `src/models/storage.py`
- `src/services/queue_service.py`
- `src/services/job_scheduler.py`
- `src/services/document_service.py`
- `src/services/storage_service.py`
- `src/routes/queue_routes.py`
- `src/routes/project_routes.py`
- `src/routes/history_routes.py`
- `src_frontend/src/App.tsx`
- `src_frontend/src/hooks/useQueue.ts`
- `src_frontend/src/api/queue.ts`
- `src_frontend/src/pages/ProjectDetailPage.tsx`
- `src_frontend/src/pages/Dashboard.tsx`

### Sprint 12
**Nuevos:**
- `src/models/billing.py`
- `src/services/usage_service.py`
- `src/services/org_metrics_service.py`
- `src/services/export_service.py`
- `src/routes/export_routes.py`
- `src/routes/org_routes.py`
- `src_frontend/src/api/org.ts`
- `src_frontend/src/api/export.ts`
- `src_frontend/src/pages/OrgMetricsPage.tsx`
- `src_frontend/src/pages/InvestorLandingPage.tsx`
- `src_frontend/src/components/OnboardingTour.tsx`
- `src_frontend/src/store/onboarding.ts`

**Modificados:**
- `src/services/plan_limits_service.py`
- `src/routes/render_routes.py`
- `src/routes/project_routes.py`
- `src/routes/demo_routes.py`
- `src/services/demo_service.py`
- `src_frontend/src/api/plan.ts`
- `src_frontend/src/pages/PlansPage.tsx`
- `src_frontend/src/pages/Dashboard.tsx`
- `src_frontend/src/pages/RegisterDemoPage.tsx`
- `src_frontend/src/pages/ProjectReviewPage.tsx`
- `requirements.txt` / `pyproject.toml`

---

*Documento preparado por Senior Full-Stack Engineer — Sin implementación. Solo planificación.*
*Fecha: 2026-04-16 | Sprint 10 estado: ✅ CERRADO*
