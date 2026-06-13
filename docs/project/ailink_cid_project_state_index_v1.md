# AILink/CID Project State Index v1

Fase: `AILINK/CID.PROJECT.STATE.INDEX.PHASE2`
Fecha: 2026-06-13
Tipo: índice maestro documental y test-only

Producto público: AILinkCinema.
Producto SaaS: CID — Cinematic Intelligence Direction.
Herramienta independiente: AILink Sync Dialogue.
Política técnica CID SaaS: PostgreSQL-only.
Etiqueta de seguridad: No runtime changes.
Estado de publicación: No production public release.

## 1. Propósito del índice maestro

Este índice maestro convierte la auditoría segura de baseline de Phase 1 en una
vista operativa del estado actual de AILinkCinema/CID. Su función es orientar
decisiones de fase: qué existe, qué está validado documentalmente o por tests,
qué falta, qué no debe tocarse todavía y qué debería priorizarse después.

Este índice no sustituye tests reales ni auditorías runtime. No declara
producción pública completa; no hay producción pública completa. No autoriza
cambios de backend, frontend, Docker,
Alembic, `.env`, modelos, base de datos, pagos, configuración ni scripts
operativos.

El cambio de nombre frente a la recomendación previa es intencional: Phase 1 recomendaba una fase de evidence/index; en Phase 2 se crea primero el índice maestro operativo para ordenar el estado del proyecto; la matriz/evidencia queda desplazada a una fase posterior recomendada.

Este índice no valida la existencia real de todos los documentos referenciados. Es una guía operativa documental y no sustituye una auditoría runtime, una revisión de despliegue, una validación VPS ni una certificación de producción.

## 2. Último HEAD/tag estable conocido

Evidencia de referencia para esta fase:

- HEAD: `c536367`.
- Tag: `ailink-cid-dev-stable-project-safe-baseline-audit-phase1-20260613`.
- Lectura: Phase 1 quedó consolidada como baseline segura documental. Phase 2
  parte de ese estado y no introduce runtime.

Nota de vigencia: este índice es una fotografía del estado en HEAD `c536367`; no representa estado permanente. Debe actualizarse cuando cambie el HEAD estable, tags, producción, VPS, CRM, landing, pagos o runtime.

## 3. Documentos de referencia principales

Referencias operativas:

- `docs/project/ailink_cid_safe_baseline_audit_v1.md`: baseline segura Phase 1.
- `docs/PRODUCTION_CANDIDATE_STATUS.md`: referencia honesta entre demo-ready,
  production candidate y producción pública.
- `docs/architecture/cid_landing_vs_cid_saas_boundary_v1.md`: frontera entre
  AILinkCinema landing y CID SaaS.
- `docs/architecture/cid_saas_model_contract_v1.md`: contrato documental del
  modelo CID SaaS.
- `directivas/cid_wsl_only_agent_rules.md`: regla WSL-only para trabajo seguro.
- `.agents/skills/cid-phase-guard/SKILL.md`: estructura de fase, no-goals y
  disciplina de commit/tag.
- `.agents/skills/cid-docs-contract-phase/SKILL.md`: contrato para fases
  documentales/test-only.

Referencias de producto:

- `docs/product/ailink_sync_dialogue_mvp_v1.md`.
- `docs/product/ailink_sync_dialogue_demo_readiness_v1.md`.
- `docs/product/ailink_sync_dialogue_demo_readiness_gating_audit_v1.md`.
- `docs/product/marketing/ailink_marketing_leads_operations_index_v1.md`.

## 4. Estado general de AILinkCinema

AILinkCinema es la marca/web pública y la capa comercial visible. Su función es
presentar servicios, soluciones, demo, pricing, captación y narrativa de valor.

Estado observado:

- La landing pública y CID SaaS comparten repositorio y build frontend.
- La landing puede vender servicios aislados y conducir hacia una demo CID.
- La landing no debe exponer rutas internas CID como si fueran navegación
  pública.
- El estado de demo comercial controlada existe como posibilidad, pero no hay
  producción pública completa.

Riesgo principal: mezclar mensajes de marketing, demo y SaaS interno puede crear
promesas indebidas. La regla de esta fase es no prometer capacidades no
implementadas ni validadas.

## 5. Estado general de CID SaaS

CID es el SaaS: CID — Cinematic Intelligence Direction. Es la plataforma
autenticada, plan-gated y organizada alrededor de producción audiovisual.

Estado observado:

- Hay contratos extensos sobre SaaS, roles, permisos, planes, módulos, créditos,
  jobs y activos.
- Hay rutas, servicios, esquemas, modelos y tests de contrato/gating en el repo.
- Las superficies runtime están inventariadas, no validadas para producción por
  este índice.
- PostgreSQL-only sigue siendo la política técnica de CID SaaS para nuevas
  fases.
- Billing real, pagos, legal público, TLS público, integraciones sensibles y
  limpieza de artefactos siguen sin cerrarse como producción completa.

Conclusión operativa: CID tiene base documental y técnica amplia, pero no debe
presentarse como producción pública completa ni modificarse sin fase explícita.

## 6. Estado de AILink Sync Dialogue

AILink Sync Dialogue es una herramienta independiente, local-first y orientada a
beta/demo. No es una prueba de madurez del SaaS CID completo.

Estado observado:

- Código localizado bajo `src/ailink_tools/sync_dialogue/`.
- Tests específicos cubren scanner local, matching, exports, reporte HTML, CLI y
  piezas documentales de demo.
- La propuesta de valor es convertir carpetas de rodaje en informes útiles para
  montaje.
- El mensaje de privacidad es central: el material audiovisual debe quedarse en
  el entorno local del cliente.

No debe prometer:

- Sincronización final automática.
- Waveform avanzado.
- XML/AAF/EDL profesional final.
- App instalable final.
- Pagos o cloud SaaS como capacidades cerradas.

## 7. Estado comercial/demo/beta

Estado operativo:

- Existe una línea de controlled commercial demo readiness.
- AILink Sync Dialogue está más cerca de beta/demo controlada que de producto
  público final.
- La demo debe usar material seguro y explicar límites actuales.
- No production public release.

Regla comercial:

- No vender demo como producción pública.
- No convertir beta/demo en promesa de disponibilidad general.
- No presentar módulos inventariados como capacidades productivas finales.

## 8. Estado legal/landing/leads

Landing:

- AILinkCinema es la marca/web pública.
- Landing y CID comparten build, pero deben mantenerse separados en mensaje y
  navegación.
- La separación fuerte de builds o rutas debe esperar fase específica.

Legal:

- La revisión legal pública sigue siendo una zona pendiente para publicación
  completa.
- No se deben introducir textos legales definitivos sin fase y revisión
  explícitas.

Leads:

- Existen documentos de marketing/leads y operaciones.
- Las fases de leads deben seguir siendo explícitas, auditables y separadas de
  runtime SaaS mientras no haya activación real aprobada.
- No activar CRM, n8n, formularios conectados ni automatizaciones reales desde
  este índice.

## 9. Estado de infraestructura/VPS

Estado observado:

- `docs/PRODUCTION_CANDIDATE_STATUS.md` mantiene la diferencia entre demo
  controlada y producción pública.
- TLS/443 público sigue pendiente para exposición VPS pública.
- ComfyUI es opcional para demo controlada y no queda validado por este índice.
- Backup/restore sigue siendo básico y operator-driven.
- Demo routes, experimental routes y postproduction routes deben mantenerse bajo
  flags seguros según el entorno.

Este índice no ejecuta Docker, no valida VPS, no valida redes, no valida TLS y no
certifica infraestructura de producción.

## 10. Estado de Codex Skills

Codex Skills está incorporado al flujo operativo del repo:

- `cid-phase-guard`: define fase, alcance, no-goals, validaciones y disciplina
  commit/tag.
- `cid-docs-contract-phase`: mantiene fases documentales/test-only sin cambios
  runtime.
- `cid-release-checklist`: referencia para cierre y publicación cuando el usuario
  lo solicite explícitamente.

Estado: Codex Skills sirve como contrato operativo para agentes, no como
validación runtime del producto.

## 11. Módulos o zonas sensibles

No tocar sin fase explícita:

- Auth, JWT, tenant context, permisos, roles y module access.
- Billing, créditos, AI job accounting y pagos.
- Modelos, migraciones, persistencia y configuración.
- Docker, compose overlays, TLS, VPS, redes y hostnames internos.
- ComfyUI, workers, queues, renders reales y job scheduler.
- Google Drive, Qdrant, n8n, CRM y cualquier integración externa.
- `src_frontend/src/App.tsx`, por la frontera landing/CID.
- Pricing y planes, por discrepancias documentales/configuracionales.
- Artefactos históricos, backups, exports, logs, caches y carpetas satélite.

Regla corta: no tocar runtime sin fase explícita.

## 12. Qué está validado

Validado o cubierto en el sentido documental/contractual observado:

- Phase 1 baseline segura quedó consolidada en `c536367`.
- Tests de configuración validan restricciones de producción en
  `tests/unit/test_config.py`.
- Hay múltiples tests de contrato/gating por rutas.
- Hay guards para WSL/repo, staging sensible y regresiones de persistencia local
  legacy.
- AILink Sync Dialogue cuenta con tests locales para piezas concretas.
- La frontera landing/CID y el modelo CID SaaS están documentados.

Importante: “validado” aquí no significa producción pública completa. Este índice
no sustituye smokes reales ni auditorías runtime.

## 13. Qué no existe todavía

No existe como capacidad cerrada de producción pública:

- Producción pública completa.
- Billing real y ciclo de pagos completo.
- Revisión legal pública cerrada.
- TLS/443 público certificado desde este índice.
- Separación definitiva de builds landing/CID.
- Activación real de CRM/n8n/leads conectados desde este índice.
- Certificación ComfyUI end-to-end para producción.
- Garantía de que todos los módulos inventariados estén listos para clientes.

## 14. Qué no debe tocarse sin fase explícita

No debe tocarse sin una fase específica, plan validado y pruebas definidas:

- Runtime backend o frontend.
- Docker, Alembic, `.env`, modelos, DB, pagos y configuración.
- Rutas de autenticación, tenant, permisos, planes, créditos y jobs.
- Infraestructura VPS/TLS/redes.
- Integraciones externas o APIs de coste/riesgo.
- Limpieza de artefactos históricos.
- Separación landing/CID.
- Automatizaciones de leads o CRM real.

## 15. Próximas fases recomendadas

1. `AILINK/CID.PROJECT.EVIDENCE.MATRIX.PHASE3`: matriz de evidencias por área,
   con docs, tests, gaps y owners.
2. `CID.SAAS.GATING.COVERAGE.AUDIT.1`: auditoría ruta por ruta de auth, tenant,
   module access y permisos.
3. `CID.SAAS.PRICING.CANONICALIZATION.1`: reconciliar pricing docs/config antes
   de pagos.
4. `AILINK.SYNC_DIALOGUE.DEMO.EVIDENCE.BASELINE.1`: evidencias reproducibles de
   beta/demo local-first.
5. `AILINK.LANDING.LEGAL.LEADS.READINESS.AUDIT.1`: separar mensaje público,
   legal mínimo y captación de leads antes de activaciones reales.
6. `CID.INFRA.VPS.PUBLICATION.READINESS.AUDIT.1`: auditoría documental y luego
   runtime, en fases separadas, para VPS/TLS/publicación.

## 16. Criterios para decidir la siguiente fase

Elegir la siguiente fase según:

- Riesgo: priorizar auth, tenant, pagos, infraestructura o legal si hay presión
  de publicación.
- Evidencia: no implementar sin contrato, tests o matriz de validación.
- Valor: priorizar lo que desbloquea demo segura, beta controlada o ventas sin
  promesas falsas.
- Aislamiento: preferir fases documentales/test-only antes de runtime en zonas
  sensibles.
- Reversibilidad: cambios pequeños, trazables y con validaciones claras.
- Seguridad: nunca saltarse WSL-only, guards, no secretos y no runtime changes
  cuando la fase sea documental.

## 17. Criterios de aceptación

- Documento creado en `docs/project/ailink_cid_project_state_index_v1.md`.
- Test creado en `tests/unit/test_ailink_cid_project_state_index.py`.
- El test verifica secciones y frases críticas.
- La fase queda estrictamente documental/test-only.
- No hay staging, commit, tag ni push.
- No hay runtime changes.
