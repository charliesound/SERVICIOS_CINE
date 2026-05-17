# CID Modular Commercial Roadmap

## Resumen ejecutivo

- CID ya contiene una base real de producto modular: autenticacion, proyectos, planes, permisos, analisis de guion, storyboard, funding, pitch, distribution, CRM y editorial/post.
- El repositorio esta listo para demos controladas y pilotos asistidos, pero no para venta self-serve ni produccion publica sin acompanamiento operativo.
- La mayor fortaleza actual es la trazabilidad de proyecto y la cantidad de modulos con backend, frontend y tests reales.
- La mayor debilidad comercial actual es la falta de hardening transversal: billing real, enforcement completo de permisos, demos empaquetadas por modulo, datos semilla comerciales y documentacion de uso por SKU.
- La decision futura de arquitectura hibrida VPS + PC GPU encaja especialmente bien para Storyboard AI, Pipeline Builder, Sound Post AI y flujos ComfyUI/Ollama, pero hoy debe considerarse solo como restriccion de roadmap.
- Recomendacion principal: vender primero modulos orientados a desarrollo y financiacion, donde la madurez funcional y el valor comercial ya estan mas cerca.

## Estado general de CID

- Fuente operativa actual: `src/core/app_factory.py`, `src/routes/project_routes.py`, `src/config/plans.yml`, `docs/PRODUCTION_CANDIDATE_STATUS.md`, `docs/RELEASE_DEMO_GUIDE.md`.
- Runtime oficial actual: `compose.base.yml` + `compose.home.yml` o `compose.vps.yml`, con frontend en `src_frontend/` y backend en `src/`.
- Estado honesto del producto: demo comercial controlada SI, produccion publica NO, billing real NO, postproduction feature-flagged, GPU/ComfyUI opcional para demo.
- Hay evidencia real de multi-tenant, planes, permisos y exportaciones; la monetizacion actual sigue siendo manual/interna.

## Definicion de modulo vendible

Un modulo se considera vendible cuando cumple como minimo:

1. Pantalla propia o workflow propio visible desde dashboard o navegacion.
2. Endpoint funcional en backend con persistencia real.
3. Datos guardados por proyecto y organizacion.
4. Control por plan y/o permiso.
5. Exportacion util para el comprador: PDF, CSV, JSON, Markdown o ZIP segun el caso.
6. Demo reproducible con datos reales o semilla controlada.
7. Tests minimos de backend y smoke operativo.
8. Documentacion de uso y limites del modulo.
9. Copy comercial honesto, sin claims no soportados.
10. Precio orientativo y pack recomendado.

## Tabla de modulos

| Modulo | Estado tecnico | Estado comercial | Precio orientativo | Nota corta |
|---|---|---|---:|---|
| CID Core | PARCIAL AVANZADO | PARCIAL INICIAL | 29-49 EUR/mes base | Base SaaS real sin billing self-serve |
| CID Script Analysis Pro | PARCIAL AVANZADO | PARCIAL AVANZADO | 79-149 EUR/mes | Buen candidato de entrada |
| CID Pitch Deck | PARCIAL AVANZADO | PARCIAL AVANZADO | 99-179 EUR/mes | Muy vendible para productores |
| CID Storyboard AI | PARCIAL AVANZADO | PARCIAL AVANZADO | 149-299 EUR/mes + creditos | Fuerte demo visual, depende GPU |
| CID Pipeline Builder | PARCIAL AVANZADO | PARCIAL INICIAL | 129-249 EUR/mes | MVP solido pero simulado |
| CID Breakdown | PARCIAL INICIAL | PENDIENTE | 79-129 EUR/mes | Tiene datos, no experiencia propia |
| CID Budget Lite | PARCIAL AVANZADO | PARCIAL AVANZADO | 89-149 EUR/mes | Exporta JSON/CSV, necesita robustez |
| CID Production Manager Lite | PARCIAL INICIAL | PENDIENTE | 99-199 EUR/mes | Backend existe, UX modular no |
| CID Call Sheet | PENDIENTE | PENDIENTE | 49-99 EUR/mes | Sin evidencia de modulo actual |
| CID Legal Documents | PARCIAL INICIAL | PENDIENTE | 79-149 EUR/mes | Documentos genericos, no paquete legal |
| CID Funding & Grants | HECHO | PARCIAL AVANZADO | 149-249 EUR/mes | Uno de los modulos mas maduros |
| CID Postproduction | PARCIAL AVANZADO | PARCIAL INICIAL | 199-399 EUR/mes | Editorial fuerte, post global no cerrada |
| CID Sound Post AI | PARCIAL INICIAL | PENDIENTE | 149-249 EUR/mes | Senales tecnicas, sin workspace propio |
| CID Delivery & Distribution | PARCIAL AVANZADO | PARCIAL AVANZADO | 119-229 EUR/mes | Distribution pack y delivery reales |

## Estado tecnico por modulo

- CID Core - Backend: `src/routes/auth_routes.py`, `src/routes/project_routes.py`, `src/routes/plan_routes.py`; servicios: `src/services/account_service.py`, `src/services/plan_limits_service.py`, `src/services/tenant_access_service.py`; modelos/schemas: `src/models/core.py`, `src/schemas/auth_schema.py`, `src/schemas/plan_schema.py`; frontend: `src_frontend/src/pages/ProjectsPage.tsx`, `src_frontend/src/pages/ProjectDashboardPage.tsx`, `src_frontend/src/pages/PlansPage.tsx`; endpoints: `/api/auth/*`, `/api/projects`, `/api/projects/{project_id}/dashboard`, `/api/plans/*`; planes/permisos: `billing_plan`, `PlanRoute`, badges de plan; export: JSON/ZIP de proyecto; tests: multitenancy y tenant access; dependencia: base de todos; gap: billing real, perfil, invoices y activacion automatica.
- CID Script Analysis Pro - Backend: `src/routes/intake_routes.py`, `src/routes/script_version_routes.py`; servicios: `src/services/script_intake_service.py`, `src/services/script_version_service.py`, `src/services/script_synopsis_service.py`; modelos: `src/models/script_versioning.py`, `src/models/narrative.py`; frontend: `src_frontend/src/pages/ProjectDetailPage.tsx`; endpoints: analisis, resumen, breakdown, versions, change reports; planes: limitado por `max_analyses`; export: indirecta via proyecto/pitch/funding; tests: `tests/integration/test_project_script_analysis_flow.py`; dependencia: alimenta Breakdown, Budget, Funding, Pitch y Storyboard; gap: SKU propio, export directo y UX mas enfocada.
- CID Pitch Deck - Backend: `src/routes/producer_pitch_routes.py`, `src/routes/presentation_routes.py`; servicios: `src/services/producer_pitch_service.py`, `src/services/presentation_service.py`, `src/services/pdf_service.py`; modelos/schemas: `src/models/producer_pitch.py`, `src/schemas/presentation_schema.py`; frontend: `src_frontend/src/pages/ProducerPitchPackPage.tsx`; endpoints: generar, aprobar y exportar JSON/Markdown/ZIP y filmstrip/PDF; planes/permisos: `producer_pack.*`; export: PDF, JSON, Markdown, ZIP; tests: `tests/integration/test_presentation_visual_validation.py`, `scripts/smoke_producer_pitch_pack.py`; dependencia: Script, Budget, Funding, Storyboard, Delivery; gap: textos comerciales por vertical y plantillas premium.
- CID Storyboard AI - Backend: `src/routes/storyboard_routes.py`, `src/routes/cid_script_to_prompt_routes.py`, `src/routes/cid_visual_reference_routes.py`; servicios: `src/services/storyboard_service.py`, `src/services/comfyui_storyboard_render_service.py`, `src/services/prompt_revision_service.py`; modelos/schemas: `src/models/storyboard.py`, `src/schemas/storyboard_schema.py`; frontend: `src_frontend/src/pages/StoryboardBuilderPage.tsx`; endpoints: opciones, secuencias, generate, render, dry-run; planes: limitado por `max_storyboards`; export: no paquete comercial dedicado visible; tests: storyboard unit tests y `tests/integration/test_manual_shot_editor.py`; dependencia: Script + GPU local/ComfyUI/Ollama; gap: export storyboard, costes GPU y operacion hibrida cerrada.
- CID Pipeline Builder - Backend: `src/routes/cid_pipeline_routes.py`; servicios: `src/services/cid_pipeline_builder_service.py`, `src/services/cid_pipeline_validation_service.py`, `src/services/cid_pipeline_simulated_job_service.py`; schemas: `src/schemas/cid_pipeline_schema.py`; frontend: `src_frontend/src/pages/CIDPipelineBuilderPage.tsx`; endpoints: presets, generate, validate, execute, jobs; planes/permisos: integrable con tareas permitidas por plan; export: no visible; tests: base indirecta en `tests/unit/test_cid_script_to_prompt_pipeline.py`; dependencia: Core + ComfyUI/Ollama + legal gate; gap: ejecucion real, casos por vertical y pricing por consumo.
- CID Breakdown - Backend: `src/routes/intake_routes.py`, `src/services/script_intake_service.py`; modelos: `src/models/production.py`; frontend: embebido en `src_frontend/src/pages/ProjectDetailPage.tsx`; endpoints: `/breakdown/scenes` y `/breakdown/departments`; planes/permisos: sin modulo visual de pago propio; export: no visible; tests: cobertura indirecta en script flow; dependencia: Script Analysis; gap: pagina propia, exportacion, aprobacion humana y nomenclatura vendible.
- CID Budget Lite - Backend: `src/routes/budget_routes.py`; servicios: `src/services/budget_estimator_service.py`, `src/services/budget_rules.py`; modelos: `src/models/budget_estimator.py`; frontend: `src_frontend/src/pages/BudgetEstimatorPage.tsx`; endpoints: listado, generate, active, export JSON/CSV; planes/permisos: aparece como modulo de dashboard; export: JSON y CSV; tests: smoke `scripts/smoke_budget_estimator.py`; dependencia: Script + Breakdown; gap: test suite formal, export PDF/XLSX y explicabilidad comercial.
- CID Production Manager Lite - Backend: `src/routes/project_member_routes.py`, `src/routes/change_governance_routes.py`, `src/routes/shooting_plan_routes.py`, `src/routes/shotlist_routes.py`; servicios: `src/services/project_access_service.py`, `src/services/change_governance_service.py`, `src/services/shotlist_service.py`; modelos: `src/models/project_member.py`, `src/models/change_governance.py`; frontend: evidencia de marketing en `src_frontend/src/pages/ProducerSolutionPage.tsx` y `src_frontend/src/pages/SolutionDetailPage.tsx`; endpoints: members, change requests, shooting plans, planned shots; planes/permisos: roles y dashboards por rol; export: no visible; tests: smoke `scripts/smoke_project_access_control.py`; dependencia: Core + Breakdown + Storyboard + Budget; gap: workspace dedicado de operacion diaria.
- CID Call Sheet - Backend/frontend/tests: sin evidencia en `src/routes`, `src/services`, `src/models`, `src_frontend`, `tests`; planes/export: no aplica; dependencia futura: Production Manager + Breakdown + Budget; gap: modulo completo pendiente.
- CID Legal Documents - Backend: `src/routes/project_document_routes.py`, `src/routes/document_routes.py`; servicios: `src/services/project_document_service.py`, `src/services/project_document_rag_service.py`, `src/services/document_service.py`; modelos/schemas: `src/models/document.py`, `src/schemas/project_document_schema.py`, `src/schemas/project_document_rag_schema.py`; frontend: `src_frontend/src/pages/DocumentsPage.tsx`, `src_frontend/src/pages/DocumentDetailPage.tsx`; endpoints: documents CRUD, reindex, ask, ingestion; planes/permisos: sidebar `Documentos`; export: reportes derivados mas que paquetes legales; tests: `test_project_private_documents.py`, `test_project_document_rag.py`; dependencia: Core + RAG + Funding; gap: contratos/permits/templates y bundle legal comercializable.
- CID Funding & Grants - Backend: `src/routes/funding_routes.py`, `src/routes/project_funding_routes.py`, `src/routes/matcher_routes.py`; servicios: `src/services/funding_matcher_service.py`, `src/services/funding_dossier_service.py`, `src/services/project_funding_service.py`; modelos/schemas: `src/models/production.py`, `src/models/matcher.py`, `src/schemas/funding_catalog_schema.py`; frontend: `src_frontend/src/pages/ProjectFundingPage.tsx`; endpoints: opportunities, dossier, matches, checklist, profile, matcher; planes/permisos: encaja con producer role; export: dossier PDF y flujos de evidencia; tests: varias integraciones funding; dependencia: Script, Budget, Documents; gap: curacion continua de catalogo y packaging comercial por pais.
- CID Postproduction - Backend: `src/routes/editorial_routes.py`, `src/routes/postproduction_routes.py`; servicios: `src/services/assembly_service.py`, `src/services/editorial_reconciliation_service.py`, `src/services/fcpxml_export_service.py`, `src/services/davinci_platform_package_service.py`; modelos/schemas: `src/models/postproduction.py`, `src/schemas/editorial_schema.py`; frontend: `src_frontend/src/pages/EditorialAssemblyPage.tsx`, `src_frontend/src/pages/IngestScansPage.tsx`; endpoints: assembly, reconcile, audio metadata, FCPXML, package export; planes/permisos: rol editor y permisos editorial/davinci; export: FCPXML y ZIP editorial; tests: smokes editoriales; dependencia: media scan, reports, delivery; gap: producto post global aun feature-flagged y no listo para venta masiva.
- CID Sound Post AI - Backend: `src/routes/dubbing_bridge_routes.py`, partes de `src/routes/editorial_routes.py`; servicios: `src/services/audio_metadata_service.py`, `src/services/fcpxml_dual_system_variant_service.py`; modelos: audio metadata en `src/models/postproduction.py`; frontend: senales en `src_frontend/src/data/solutionsContent.ts` y modo `sound` de pipeline; endpoints: audio metadata, dubbing bridge; planes/export: no visibles; tests: smokes BWF/iXML y reconcile; dependencia: Postproduction + Pipeline + GPU; gap: pantalla propia, automatismos y SKU entendible.
- CID Delivery & Distribution - Backend: `src/routes/delivery_routes.py`, `src/routes/distribution_pack_routes.py`, `src/routes/sales_targets_routes.py`, `src/routes/crm_routes.py`; servicios: `src/services/delivery_service.py`, `src/services/distribution_pack_service.py`, `src/services/sales_target_service.py`, `src/services/crm_service.py`; modelos/schemas: `src/models/delivery.py`, `src/models/distribution.py`, `src/models/crm.py`, `src/schemas/delivery_schema.py`; frontend: `src_frontend/src/pages/DistributionPackPage.tsx`, `src_frontend/src/pages/DeliveryOverviewPage.tsx`, `src_frontend/src/pages/CommercialCrmPage.tsx`; endpoints: deliverables, downloads, distribution packs, sales opportunities, CRM; planes/permisos: distribution/crm roles; export: JSON, Markdown, ZIP, downloads; tests: `scripts/smoke_distribution_pack.py`, `scripts/smoke_commercial_crm.py`; dependencia: Pitch + Funding + Review + Editorial; gap: unificar CRM con delivery como oferta comercial coherente.

## Estado comercial por modulo

- Mas cercanos a vender con poco desarrollo adicional: Script Analysis Pro, Pitch Deck, Funding & Grants, Budget Lite, Delivery & Distribution.
- Muy buenos para demo visual pero dependientes de operacion hibrida y pricing por consumo: Storyboard AI y Pipeline Builder.
- Requieren producto adicional antes de vender como SKU independiente: Breakdown, Production Manager Lite, Legal Documents, Sound Post AI.
- No vender todavia como modulo independiente: Call Sheet.
- Postproduction se puede vender mejor como servicio asistido o enterprise pilot, no como self-serve.

## Dependencias entre modulos

- CID Core es base obligatoria para identidad, proyectos, tenancy, planes y permisos.
- Script Analysis Pro es la fuente primaria para Breakdown, Budget Lite, Funding & Grants, Pitch Deck y Storyboard AI.
- Breakdown alimenta Budget Lite, Production Manager Lite y Call Sheet.
- Budget Lite y Funding & Grants enriquecen Pitch Deck y Distribution.
- Legal Documents aporta evidencia a Funding & Grants y futuros flujos legales.
- Delivery & Distribution depende de Pitch Deck, CRM, Review y salidas editoriales.
- Postproduction y Sound Post AI dependen de Media/Reports/Editorial y no deben aislarse comercialmente demasiado pronto.

## Orden recomendado de construccion y venta

1. CID Core modular.
2. CID Script Analysis Pro.
3. CID Pitch Deck.
4. CID Funding & Grants.
5. CID Storyboard AI.
6. CID Breakdown.
7. CID Budget Lite.
8. CID Delivery & Distribution.
9. CID Legal Documents.
10. CID Production Manager Lite.
11. CID Call Sheet.
12. CID Pipeline Builder.
13. CID Postproduction.
14. CID Sound Post AI.

## Packs comerciales

| Pack | Modulos recomendados | Precio orientativo |
|---|---|---:|
| Development Pack | CID Core + Script Analysis Pro + Storyboard AI + Pitch Deck | 299-499 EUR/mes |
| Production Pack | CID Core + Breakdown + Budget Lite + Production Manager Lite + Call Sheet | 249-449 EUR/mes |
| Funding Pack | CID Core + Pitch Deck + Funding & Grants + Legal Documents | 279-479 EUR/mes |
| Post Pack | CID Core + Postproduction + Sound Post AI + Delivery & Distribution | 399-799 EUR/mes |
| Enterprise Pack | Todos los modulos + soporte + despliegue hibrido asistido | desde 1,200 EUR/mes + setup |

## Backlog por fases

- Sprint 0 - Auditoria modular: congelar matriz de modulos, pricing, permisos, demos y ownership documental.
- Sprint 1 - CID Core modular: separar core comercialmente, definir onboarding, planes modulares y acceso por SKU.
- Sprint 2 - Script Analysis Pro: SKU propio, export directo, demo guiada y textos comerciales cerrados.
- Sprint 3 - Pitch Deck: plantillas premium, version demo de dossier y cierre de export PDF/ZIP comercial.
- Sprint 4 - Storyboard AI: pricing por creditos/GPU, export storyboard, runbook hibrido y demo estable.
- Sprint 5 - Breakdown: pantalla propia, validacion humana, export y dependencia clara desde Script.
- Sprint 6 - Budget Lite: formalizar reglas, mejorar tests y cerrar export util para ventas/pilotos.
- Sprint 7 - Production Manager Lite: consolidar miembros, cambios, shooting plan y workspace operativo unico.
- Sprint 8 - Call Sheet: crear objeto, pantalla, export PDF y flujo de aprobacion.
- Sprint 9 - Legal Documents / Funding: paquetizar contratos, permisos, grants y evidencias por convocatoria.

## Riesgos

- Billing manual: impide vender self-serve aunque varios modulos ya parezcan empaquetables.
- Permisos incompletos: `docs/ROLE_BASED_DASHBOARDS_AND_PERMISSIONS.md` reconoce enforcement backend parcial.
- Documentacion desalineada: `docs/CID_PRODUCT_FUNCTIONAL_MAP.md` se ha quedado atras respecto al codigo actual.
- Dependencia GPU privada: Storyboard, Pipeline y partes de Sound/Post requieren operacion hibrida bien definida antes de escalar.
- Postproduction no debe prometerse como listo general si sigue feature-flagged y descrito como no production-ready.

## Decisiones pendientes

- Si los modulos se venderan como add-ons sobre CID Core o como bundles cerrados por rol.
- Si el pricing principal sera por usuario, por proyecto, por creditos GPU o mixto.
- Si Funding & Grants se paquetiza por geografia o como catalogo unico.
- Si Delivery & Distribution incluye CRM o se vende como pack separado.
- Si Storyboard AI y Pipeline Builder se ofrecen solo en pilotos asistidos durante la fase inicial.

## Criterios GO/NO-GO para pasar al siguiente modulo

- GO solo si el modulo anterior tiene pantalla propia, endpoint funcional, persistencia, demo reproducible y control por plan o permiso.
- GO solo si existe al menos un export util y un smoke o test minimo.
- GO solo si el copy comercial no promete mas de lo soportado por el repositorio.
- NO-GO si el flujo depende de operaciones manuales no documentadas.
- NO-GO si el modulo necesita otro modulo previo que aun no tenga contrato estable.

## Archivos inspeccionados

- Estructura: `src/`, `src/routes/`, `src/services/`, `src/schemas/`, `src/models/`, `src/config/`, `src_frontend/`, `docs/`, `tests/`, `scripts/`.
- Backend clave: `src/core/app_factory.py`, `src/routes/project_routes.py`, `src/routes/plan_routes.py`, `src/routes/intake_routes.py`, `src/routes/storyboard_routes.py`, `src/routes/producer_pitch_routes.py`, `src/routes/distribution_pack_routes.py`, `src/routes/editorial_routes.py`.
- Config/infra: `src/config/plans.yml`, `.env.example`, `compose.base.yml`, `compose.home.yml`, `compose.vps.yml`, `compose.data.yml`, `compose.n8n.yml`.
- Frontend clave: paginas y componentes auditados en `src_frontend/src/pages/` y `src_frontend/src/components/` segun cada modulo.
- Documentacion/directivas: `docs/PRODUCTION_CANDIDATE_STATUS.md`, `docs/RELEASE_DEMO_GUIDE.md`, `docs/CID_PRODUCT_FUNCTIONAL_MAP.md`, `docs/CID_V1_COMMERCIAL_POSITIONING.md`, `docs/CID_PIPELINE_BUILDER_MVP.md`, `docs/PRODUCER_PITCH_PACK.md`, `docs/DISTRIBUTION_CINEMAS_PLATFORMS_PACK.md`, `docs/COMMERCIAL_CRM.md`, `docs/ROLE_BASED_DASHBOARDS_AND_PERMISSIONS.md`, `directivas/ailinkcinema_sprints_locked_roadmap.md`, `directivas/ailinkcinema_commercial_launch_kit_v1.md`.

## Archivos creados

- `docs/product/CID_MODULAR_COMMERCIAL_ROADMAP.md`

## Resumen de hallazgos

- El repositorio ya contiene mas modulos reales de los que reflejan algunos documentos historicos.
- La mejor zona comercial inmediata es desarrollo/preproduccion: Script, Pitch, Funding, Budget y Storyboard.
- La suite ya tiene base SaaS multi-tenant suficiente para pilots asistidos, pero no para suscripcion automatizada.
- Delivery, Distribution y CRM existen y permiten construir una oferta comercial mas fuerte de final de pipeline.
- Postproduction y Sound Post deben venderse con prudencia como piloto asistido o enterprise, no como modulo masivo inmediato.

## Recomendacion del siguiente sprint

- Siguiente sprint recomendado: Sprint 1 - CID Core modular.
- Motivo: sin separar Core, planes, permisos, SKU y narrativa de acceso, los demas modulos no pueden venderse de forma limpia aunque funcionen tecnicamente.
- Entregable de salida esperado: matriz SKU -> permiso -> pantalla -> endpoint -> export -> demo por modulo, con especial foco en Script Analysis Pro como primer modulo comercial despues de Core.
