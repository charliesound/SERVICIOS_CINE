# AILink/CID Codex Skills Roadmap v1

Fase: `AILINK/CID.CODEX.SKILLS.ROADMAP.PHASE3`
Fecha: 2026-06-13
Tipo: roadmap documental y test-only

Producto público: AILinkCinema.
Producto SaaS: CID — Cinematic Intelligence Direction.
Herramienta independiente: AILink Sync Dialogue.
Último HEAD estable conocido: `8de2215`.
Último tag estable conocido: `ailink-cid-dev-stable-project-state-index-phase2-20260613`.
Política técnica CID SaaS: PostgreSQL-only.
Etiqueta de seguridad: No runtime changes.
Estado de publicación: No production public release.
Regla de comunicación: No promises of unimplemented features.

## 1. Propósito del roadmap de skills

Este documento define el roadmap completo de Codex Skills necesarias para
trabajar AILinkCinema/CID con más seguridad, trazabilidad y disciplina de fase.
No implementa skills nuevas, no crea directorios bajo `.agents/skills` y no modifica runtime.

El objetivo es decidir qué skills conviene crear, en qué orden, con qué límites
y qué riesgos deben cubrir antes de permitir fases de runtime o de publicación.
Las skills futuras deben crearse por fases pequeñas y probadas, con documento,
test y validaciones propias.

Este roadmap no autoriza tocar backend/frontend/Docker/Alembic/.env/modelos/DB/pagos/configuración.

Las skills futuras listadas aquí son propuestas de roadmap, no autorización para implementarlas todas. Esta fase no crea nuevas skills y no se deben crear nuevos directorios bajo `.agents/skills` en esta fase.

Nota de ritmo operativo: no crear más de 1 skill por fase; no crear la siguiente skill hasta validar uso real de la anterior; este roadmap prioriza control y aprendizaje progresivo sobre cantidad de skills.

## 2. Relación con AGENTS.md, Codex Skills, OpenCode y auditorías externas

`AGENTS.md` sigue siendo la guía operativa obligatoria del repo. Las Codex
Skills deben complementar esa guía, no reemplazarla. Cuando una skill exista,
debe ayudar al agente a recordar scope, no-goals, validaciones, rutas sensibles
y criterios de cierre.

OpenCode se usa para ejecutar cambios reales dentro de WSL, con `.venv` activo y
con validaciones reproducibles. Las auditorías externas pueden orientar
arquitectura o revisión, pero no deben escribir código ni sustituir ejecuciones
locales verificadas desde `/opt/SERVICIOS_CINE`.

Regla operativa: un agente escribe, otro audita. En fases sensibles, OpenCode
puede implementar una fase pequeña y otro agente o revisión humana debe auditar
alcance, diff, claims y validaciones antes de cierre estable.

## 3. Skills existentes y para qué sirven

- `.agents/skills/cid-phase-guard/SKILL.md`: define fase, objetivo, archivos
  esperados, no-goals, validaciones, estado final y disciplina de commit/tag.
- `.agents/skills/cid-docs-contract-phase/SKILL.md`: protege fases
  documentales y contract tests para que no modifiquen comportamiento runtime.
- `.agents/skills/cid-release-checklist/SKILL.md`: orienta cierres de fase,
  guards, diff, estado Git, propuesta de commit/tag y limpieza de workspace.

Estas skills existentes son contratos operativos. No sustituyen tests reales,
guards ni auditoría humana.

## 4. Principios para crear nuevas skills

1. Crear una skill solo si reduce un riesgo repetido en una familia de fases.
2. Mantener cada skill pequeña, verificable y vinculada a un dominio claro.
3. Separar CID SaaS de AILink Sync Dialogue.
4. Mantener PostgreSQL-only como política obligatoria de CID SaaS.
5. Escribir no-goals tan claros como las acciones permitidas.
6. Incluir validaciones mínimas y criterios de cierre.
7. Evitar que una skill prometa capacidades no implementadas.
8. Crear cada skill en una fase propia con test documental.

## 5. Criterios para NO crear una skill

No crear una skill cuando:

- El problema aparece una sola vez y basta con instrucciones de fase.
- La skill mezclaría dominios sensibles sin owner claro.
- El área no tiene documento base, tests o contrato suficiente.
- La skill podría animar cambios amplios de runtime sin validación previa.
- El comportamiento esperado todavía está en debate.
- La skill duplicaría `AGENTS.md`, `cid-phase-guard` o `cid-docs-contract-phase`.
- El objetivo real es refactorizar código sin evidencia de riesgo repetido.

## 6. Roadmap de skills futuras

### 6.1 `cid-wsl-postgresql-safety`

- Categoría: seguridad base WSL/PostgreSQL.
- Objetivo: reforzar trabajo exclusivo en WSL y política PostgreSQL-only para
  CID SaaS.
- Cuando usarla: antes de fases que toquen persistencia, entorno local,
  configuración de pruebas o guards de base.
- Cuando NO usarla: fases puramente comerciales, copy o assets sin relación con
  entorno ni persistencia.
- Archivos que podría tocar: docs operativos, directivas de seguridad, tests de
  contrato documental.
- Archivos que no debe tocar: runtime, migraciones, modelos, `.env`, scripts
  operativos, credenciales.
- Riesgos que evita: contaminación Windows/WSL, regresiones de persistencia,
  confusión entre demo local y CID SaaS.
- Prioridad: alta.
- Fase recomendada de implementación: `AILINK/CID.SKILL.WSL.POSTGRESQL.SAFETY.1`.

### 6.2 `cid-backend-saas-contract`

- Categoría: backend SaaS CID.
- Objetivo: orientar cambios backend CID con contratos de alcance, tenant safety,
  rutas, servicios y pruebas cercanas.
- Cuando usarla: antes de tocar rutas, servicios o dependencias CID SaaS.
- Cuando NO usarla: cambios de documentación sin runtime o herramientas
  independientes como AILink Sync Dialogue.
- Archivos que podría tocar: docs de arquitectura, tests de contrato backend,
  rutas y servicios solo cuando una fase runtime lo autorice.
- Archivos que no debe tocar: frontend, Docker, `.env`, pagos reales,
  integraciones externas sin fase explícita.
- Riesgos que evita: cambios amplios, pérdida de boundaries y claims de
  producción no validados.
- Prioridad: alta.
- Fase recomendada de implementación: `CID.SKILL.BACKEND.SAAS.CONTRACT.1`.

### 6.3 `cid-ai-jobs-credit-billing-safety`

- Categoría: AI Jobs / credit ledger / billing.
- Objetivo: proteger jobs, credit ledger, costes, planes y billing para que no
  se mezclen cambios contables con cambios de UI o demo.
- Cuando usarla: fases de créditos, accounting, job lifecycle, pricing o billing.
- Cuando NO usarla: contenido comercial que no cambie contratos de plan ni
  comportamiento de cobro.
- Archivos que podría tocar: docs de pricing/costes, tests de accounting,
  contratos de planes.
- Archivos que no debe tocar: pasarelas reales, secretos, migraciones,
  configuración productiva o datos privados sin fase aprobada.
- Riesgos que evita: descuadres de crédito, promesas de pago real, cambios
  inseguros de pricing.
- Prioridad: alta.
- Fase recomendada de implementación: `CID.SKILL.AI.JOBS.CREDIT.BILLING.1`.

### 6.4 `cid-fastapi-route-tenant-permission-safety`

- Categoría: FastAPI / rutas / permisos / tenant safety.
- Objetivo: guiar cambios de rutas con auth, tenant context, module access,
  response models y errores seguros.
- Cuando usarla: toda fase que toque endpoints, dependencias de seguridad o
  gating por modulo/plan.
- Cuando NO usarla: docs comerciales, roadmap o tests puramente documentales.
- Archivos que podría tocar: rutas, dependencias, tests unitarios de gating y
  contratos OpenAPI cuando una fase runtime lo permita.
- Archivos que no debe tocar: modelos, migraciones, pagos, Docker o frontend
  salvo fase específica.
- Riesgos que evita: saltos de permisos, fugas cross-tenant, errores de API
  demasiado verbosos.
- Prioridad: alta.
- Fase recomendada de implementación: `CID.SKILL.FASTAPI.TENANT.PERMISSION.1`.

### 6.5 `ailink-sync-dialogue-local-first`

- Categoría: AILink Sync Dialogue.
- Objetivo: mantener AILink Sync Dialogue como herramienta separada, local-first
  y orientada a demo/beta controlada.
- Cuando usarla: fases de scanner local, matching, reportes, CLI, demo evidence
  o materiales de beta.
- Cuando NO usarla: cambios de CID SaaS, billing, tenant o runtime cloud.
- Archivos que podría tocar: docs/product de Sync Dialogue, tests locales,
  código de la herramienta solo con fase runtime explícita.
- Archivos que no debe tocar: CID SaaS, pagos, CRM real, landing SaaS interna,
  infraestructura VPS.
- Riesgos que evita: mezclar producto local con SaaS cloud, prometer sync final
  automático o subir material sensible.
- Prioridad: alta.
- Fase recomendada de implementación: `AILINK.SKILL.SYNC.DIALOGUE.LOCAL.FIRST.1`.

### 6.6 `ailink-commercial-claims-demo-beta`

- Categoría: comercial / claims / demo / beta.
- Objetivo: revisar mensajes de venta, demo y beta para no declarar capacidades
  no cerradas.
- Cuando usarla: fases de landing copy, deck, pricing narrativo, demo script,
  outreach o claims públicos.
- Cuando NO usarla: cambios técnicos internos sin superficie comercial.
- Archivos que podría tocar: docs comerciales, QA de demo, textos públicos y
  tests documentales.
- Archivos que no debe tocar: runtime, pagos, CRM real, configuración y
  despliegue.
- Riesgos que evita: promesas indebidas, confundir beta con producción pública,
  vender módulos inventariados como finalizados.
- Prioridad: alta.
- Fase recomendada de implementación: `AILINK.SKILL.COMMERCIAL.CLAIMS.DEMO.1`.

### 6.7 `ailink-landing-legal-rgpd`

- Categoría: landing / legal / RGPD.
- Objetivo: guiar fases de textos legales, privacidad, cookies, RGPD, claims
  públicos y separación landing/CID.
- Cuando usarla: cambios de legal, privacidad, consentimientos, formularios o
  textos de landing.
- Cuando NO usarla: backend interno, rutas protegidas o pruebas técnicas sin
  superficie pública.
- Archivos que podría tocar: docs legales, textos web, tests de copy legal.
- Archivos que no debe tocar: `.env`, CRM real, proveedores de pago, scripts
  operativos o configuración productiva.
- Riesgos que evita: textos legales prematuros, exposición pública indebida,
  mezcla entre marketing y SaaS autenticado.
- Prioridad: media-alta.
- Fase recomendada de implementación: `AILINK.SKILL.LANDING.LEGAL.RGPD.1`.

### 6.8 `ailink-marketing-leads-n8n-crm-safety`

- Categoría: marketing leads / n8n / CRM.
- Objetivo: controlar fases de leads, automatizaciones y CRM sin activar flujos
  reales no aprobados.
- Cuando usarla: docs o contratos de leads, n8n, CRM, formularios y operaciones
  comerciales.
- Cuando NO usarla: cambios de backend CID sin leads o automatizaciones.
- Archivos que podría tocar: docs de operaciones, specs de workflow, tests
  contractuales y fixtures seguros.
- Archivos que no debe tocar: credenciales, CRM real, pagos, runtime externo,
  datos privados o automatizaciones activas sin aprobación.
- Riesgos que evita: llamadas externas accidentales, filtrado de leads, workflows
  no auditables.
- Prioridad: media-alta.
- Fase recomendada de implementación: `AILINK.SKILL.MARKETING.LEADS.CRM.1`.

### 6.9 `cid-vps-docker-deploy-readiness`

- Categoría: VPS / Docker / despliegue.
- Objetivo: ordenar auditorías de despliegue, TLS, compose overlays, readiness y
  smokes sin cambiar infraestructura por accidente.
- Cuando usarla: fases de deployment readiness, smoke, VPS, TLS o compose.
- Cuando NO usarla: fases documentales sin infraestructura o cambios de producto
  no relacionados.
- Archivos que podría tocar: docs ops, runbooks y tests/smokes solo con fase
  específica.
- Archivos que no debe tocar: Docker, configuración productiva, secretos,
  certificados o redes sin instrucción explícita.
- Riesgos que evita: publicar antes de tiempo, romper demo controlada, confundir
  hostnames internos con validación externa.
- Prioridad: media.
- Fase recomendada de implementación: `CID.SKILL.VPS.DEPLOY.READINESS.1`.

### 6.10 `cid-frontend-ux-i18n-boundary`

- Categoría: frontend / UX / i18n.
- Objetivo: guiar cambios de UI manteniendo frontera landing/CID, i18n,
  accesibilidad, estados de carga/error y claims seguros.
- Cuando usarla: fases de paginas, rutas frontend, UX, copy de producto o
  separacion visual landing/CID.
- Cuando NO usarla: backend puro, docs internas o cambios de infraestructura.
- Archivos que podría tocar: docs UX, tests de copy, componentes y rutas solo
  con fase runtime autorizada.
- Archivos que no debe tocar: backend, pagos, modelos, Docker, `.env` y CRM real.
- Riesgos que evita: exponer navegacion interna, romper gating visual, mezclar
  landing pública con SaaS autenticado.
- Prioridad: media.
- Fase recomendada de implementación: `CID.SKILL.FRONTEND.UX.I18N.BOUNDARY.1`.

### 6.11 `cid-testing-qa-release-discipline`

- Categoría: testing / QA / release.
- Objetivo: consolidar criterios de test target, broader checks, guards, cierre
  de fase, propuesta de commit/tag y auditoría de workspace.
- Cuando usarla: cierre de fases medianas o altas, QA, release candidate,
  validaciones cruzadas.
- Cuando NO usarla: microcambios documentales cubiertos por
  `cid-docs-contract-phase` y `cid-release-checklist`.
- Archivos que podría tocar: docs QA, runbooks, tests documentales de release.
- Archivos que no debe tocar: runtime o scripts operativos sin fase explícita.
- Riesgos que evita: cierres sin validación, staging accidental, tags prematuros,
  olvidar guards.
- Prioridad: media.
- Fase recomendada de implementación: `CID.SKILL.TESTING.QA.RELEASE.1`.

## 7. Orden recomendado de implementación

1. `cid-wsl-postgresql-safety`.
2. `cid-fastapi-route-tenant-permission-safety`.
3. `cid-ai-jobs-credit-billing-safety`.
4. `ailink-sync-dialogue-local-first`.
5. `ailink-commercial-claims-demo-beta`.
6. `ailink-landing-legal-rgpd`.
7. `ailink-marketing-leads-n8n-crm-safety`.
8. `cid-backend-saas-contract`.
9. `cid-vps-docker-deploy-readiness`.
10. `cid-frontend-ux-i18n-boundary`.
11. `cid-testing-qa-release-discipline`.

La prioridad favorece primero seguridad, tenant, créditos, separación de
productos y claims. Las skills de despliegue y frontend deben esperar a que las
fronteras documentales estén más cerradas.

## 8. Skills que conviene posponer

Conviene posponer cualquier skill de:

- Pagos reales o pasarelas, hasta resolver pricing y contrato comercial.
- Publicación VPS productiva, hasta completar auditoría de readiness.
- Automatizaciones reales de CRM, hasta tener consentimiento, legal y dry-runs.
- Limpieza de artefactos históricos, hasta tener inventario y owner.
- Refactor masivo backend/frontend, hasta tener matriz de evidencias y cobertura.
- Generación real o render production-grade, hasta tener smokes controlados.

## 9. Riesgos de crear demasiadas skills demasiado pronto

- Fragmentar instrucciones y crear conflictos entre skills.
- Hacer que los agentes elijan una skill incorrecta por nombres solapados.
- Aumentar mantenimiento sin reducir riesgo real.
- Convertir recomendaciones en permisos implícitos de runtime.
- Ocultar que el contrato verdadero sigue estando en tests, guards, docs y
  auditoría humana.
- Crear falsa confianza sobre producción pública o capacidades no implementadas.

## 10. Cómo usar Codex y OpenCode sin que se pisen

- Codex debe leer skills, docs base y estado Git antes de proponer cambios.
- OpenCode debe ejecutar cambios reales solo dentro de WSL y solo cuando la fase
  tenga GO explícito.
- Las auditorías externas deben producir hallazgos, no modificar runtime.
- Un agente no debe sobrescribir trabajo del otro sin revisar diff y estado.
- El cierre debe reportar comandos reales, resultados y workspace.
- Regla operativa: un agente escribe, otro audita.

## 11. Relación con el índice maestro del proyecto

Este roadmap depende del índice maestro
`docs/project/ailink_cid_project_state_index_v1.md`, que describe el estado del
proyecto en la fase anterior. El índice maestro marca la frontera entre
AILinkCinema, CID SaaS y AILink Sync Dialogue, y recuerda que no hay producción
pública completa.

Este roadmap traduce esa fotografía a una estrategia de skills. No valida la
existencia real de todos los documentos referenciados y no sustituye auditoría
runtime.

## 12. Próximas fases recomendadas

1. `AILINK/CID.SKILL.WSL.POSTGRESQL.SAFETY.1`: crear la skill base de seguridad
   WSL/PostgreSQL con test documental.
2. `CID.SKILL.FASTAPI.TENANT.PERMISSION.1`: crear skill de rutas, permisos y
   tenant safety.
3. `CID.SKILL.AI.JOBS.CREDIT.BILLING.1`: crear skill de AI jobs, credit ledger y
   billing safety.
4. `AILINK.SKILL.SYNC.DIALOGUE.LOCAL.FIRST.1`: crear skill separada de Sync
   Dialogue local-first.
5. `AILINK.SKILL.COMMERCIAL.CLAIMS.DEMO.1`: crear skill de claims, demo y beta.
6. `AILINK/CID.PROJECT.EVIDENCE.MATRIX.PHASE4`: crear matriz de evidencias por
   área, documentos, tests, gaps y owners.

## 13. Criterios de aceptación

- Documento creado en `docs/project/ailink_cid_codex_skills_roadmap_v1.md`.
- Test creado en `tests/unit/test_ailink_cid_codex_skills_roadmap.py`.
- La fase queda estrictamente documental/test-only.
- no crear nuevas skills todavía.
- No editar `.agents/skills`.
- No hay staging, commit, tag ni push.
- No hay runtime changes.
- Las skills no sustituyen tests reales, guards ni auditoría humana.
