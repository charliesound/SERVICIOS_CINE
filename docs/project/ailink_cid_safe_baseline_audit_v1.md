# AILink/CID Safe Baseline Audit v1

Fase: `AILINK/CID.PROJECT.SAFE.BASELINE.AUDIT.PHASE1`
Fecha: 2026-06-13
Tipo: auditoría documental y test-only

Producto auditado: AILinkCinema.
Nombre CID expandido: CID — Cinematic Intelligence Direction.
Baseline operativo: PostgreSQL-only para nuevas fases CID SaaS.
Etiqueta de seguridad: No runtime changes.
Regla de comunicación: No promises of unimplemented features.

## 1. Objetivo

Auditar de forma segura el estado actual del proyecto AILinkCinema/CID para
identificar qué está creado, qué está validado, qué riesgos existen, qué código
parece estable y qué partes no deben tocarse todavía.

Esta fase no modifica comportamiento runtime. No implementa backend, no
implementa frontend, no toca Docker, no toca Alembic, no toca `.env`, no toca
modelos, no toca base de datos, no toca pagos, no toca configuración y no toca
scripts operativos.

## 2. Alcance y no objetivos

Alcance incluido:

- Lectura segura de estado Git, docs, directivas, tests y estructura principal.
- Inventario documental de módulos y superficies principales.
- Identificación de zonas estables, zonas sensibles y ruido operativo.
- Test unitario documental para comprobar que este informe existe y mantiene
  secciones críticas.

No objetivos:

- No refactorizar.
- No borrar archivos.
- No arreglar código.
- No cambiar lógica.
- No ejecutar integraciones externas.
- No hacer commit, tag ni push.
- No declarar producción pública lista.

## 3. Último HEAD/tag estable conocido

Evidencia local revisada:

- HEAD corto: `15e8bc1`.
- Rama: `main`.
- Remotos observados en decoración Git: `origin/main`, `origin/HEAD`.
- Commit: `15e8bc1 chore: add Codex skills base for AILinkCinema CID`.
- Tag estable en HEAD: `ailink-cid-dev-stable-codex-skills-base-phase1-20260613`.

Lectura: el último punto estable conocido para esta auditoría es el tag anterior,
que marca una fase de base de Codex Skills, no una certificación nueva de runtime.

## 4. Estado general del repo

Estado inicial de trabajo:

- `git status --short --untracked-files=all` no devolvio cambios antes de esta
  fase.
- El repositorio real auditado es `/opt/SERVICIOS_CINE` dentro de WSL Ubuntu.
- Existe una regla local WSL-only en `directivas/cid_wsl_only_agent_rules.md`.
- Hay un volumen amplio de código, docs, tests, artefactos locales y carpetas
  históricas o satélite.

Mapa principal observado:

- `src/`: backend FastAPI con rutas, servicios, modelos, esquemas,
  dependencias, middleware y repositorios.
- `src_frontend/`: frontend React + TypeScript + Vite con landing pública y CID
  compartiendo build.
- `tests/`: suite pytest con pruebas unitarias, de contrato, gating e
  integración.
- `docs/`: contratos de arquitectura, producto, operaciones, negocio y
  validación.
- `directivas/`: memoria operativa viva con reglas, roadmap y decisiones.
- `scripts/`: smokes, guards y utilidades operativas.
- `OLD/`, `backups/`, `exports/`, `logs/`, `tmp/`, `.tmp/`: posibles fuentes de
  ruido o artefactos que no deben confundirse con código estable.

## 5. Inventario de módulos principales

Nota sobre conteos: las cifras aproximadas de rutas, servicios, modelos, esquemas
y tests son una fotografía de esta auditoría. Sirven para orientar el baseline,
pero no son una garantía permanente ni sustituyen una medición nueva en fases
posteriores.

Backend observado:

- Rutas API: alrededor de 70 archivos bajo `src/routes/`.
- Servicios de dominio: alrededor de 167 archivos bajo `src/services/`.
- Modelos: alrededor de 33 archivos bajo `src/models/`.
- Esquemas: alrededor de 52 archivos bajo `src/schemas/`.
- Dependencias transversales: auth, seguridad, tenant context, module access,
  job orchestration y worker mock.
- Middleware: request id, rate limiter y security headers.
- Áreas funcionales visibles: proyectos, usuarios, auth, planes, módulos,
  créditos, AI jobs, storyboard, guion, prompt pipeline, concept art, delivery,
  distribución, funding, CRM, documentos, memoria/RAG, Qdrant, Google Drive,
  ComfyUI, editorial assembly, storage, review y reports.

Estas superficies runtime quedan observadas/inventariadas para esta auditoría;
no quedan validadas para producción por el hecho de aparecer en el inventario.

Frontend observado:

- `src_frontend/src/App.tsx` centraliza rutas.
- Pages principales incluyen dashboard, proyectos, planes, pricing, landing,
  pipeline builder, storyboard, budget, documentos, reports, queue, delivery,
  reviews, producer pitch, funding, CRM, storage y páginas públicas.
- Componentes de protección y gating: `ProtectedRoute`, `PublicRoute`,
  `CIDRoute`, `PlanRoute`, `PlanBadge` y paneles de estado.
- APIs y hooks separados por dominio.

Documentación observada:

- CID SaaS está fuertemente documentado en `docs/architecture/`.
- AILink Sync Dialogue está documentado en `docs/product/` con fases de MVP,
  demo, feedback, launch y marketing.
- `docs/PRODUCTION_CANDIDATE_STATUS.md` declara demo comercial controlada como
  posible, pero producción pública y full production-ready como no listas.

## 6. Estado de CID SaaS

CID SaaS existe como producto integrado y como contrato documental avanzado:

- `docs/architecture/cid_saas_model_contract_v1.md` define organización,
  proyecto, usuario, rol, permiso, plan, módulo, créditos, job y asset/documento.
- `docs/architecture/cid_landing_vs_cid_saas_boundary_v1.md` separa landing
  pública de CID SaaS autenticado y plan-gated.
- La política de nuevas fases CID SaaS se interpreta como PostgreSQL-only; los
  artefactos legacy locales no deben reabrir esa decisión sin fase canónica.
- Hay pruebas unitarias de gating para muchas rutas.
- Hay dependencias runtime para tenant context y module access.
- Hay modelos, servicios y rutas para créditos, AI jobs, planes y módulos.
- Esas superficies quedan observadas/inventariadas, no validadas para producción.

Estado de madurez:

- Fuerte base de contrato, rutas y pruebas de invariantes.
- No debe venderse como producción pública completa.
- Billing real, pagos, legal, TLS publico, integraciones sensibles y limpieza de
  artefactos siguen siendo zonas no cerradas según `docs/PRODUCTION_CANDIDATE_STATUS.md`.
- La canonicalización de pricing entre docs y configuración requiere fase
  propia antes de cualquier flujo de pagos.

## 7. Estado de AILink Sync Dialogue

AILink Sync Dialogue aparece como herramienta separada/local-first:

- Código observado en `src/ailink_tools/sync_dialogue/`.
- Componentes visibles: scanner local, matching, exports, schemas y reporte
  HTML.
- Tests unitarios específicos cubren CLI, scanner local, matching, exports,
  report HTML, landing/static docs, demo readiness y feedback.
- Documentos de producto describen MVP local con `ffprobe`/`ffmpeg`, reportes,
  CSV/JSON/PDF futuro o segun fase, y mensaje de privacidad.
- Sync Dialogue queda separado de CID SaaS: es una línea local-first de
  beta/demo controlada, no una prueba de madurez del SaaS completo.

Estado de madurez:

- La línea Sync Dialogue parece más cercana a demo/beta privada controlada que a
  producto SaaS cloud.
- El mensaje clave es local-first: no subir material audiovisual sensible.
- No debe prometer sincronización final automática, waveform avanzado, XML/AAF/EDL
  profesional final, app instalable final, pagos ni cloud SaaS como si estuvieran
  cerrados.

## 8. Estado de tests y guards

Estado observado:

- Hay alrededor de 217 tests unitarios directos bajo `tests/unit/`.
- Hay alrededor de 18 tests de integración directos bajo `tests/integration/`.
- Existen muchas pruebas de contrato documental y gating por ruta.
- `tests/unit/test_config.py` cubre validación de configuración de producción,
  secretos JWT, CORS, database URL y compatibilidad legacy.
- `scripts/dev/guard_wsl_repo.sh` valida ruta WSL, nested copy, estado Git,
  staged `.env`, staged DB files y patrones sensibles en diff staged.
- El segundo guard de regresiones de persistencia local legacy escanea diffs
  staged o working tree para evitar introducir dependencias no canónicas.

Lectura:

- La red de tests y guards es una fortaleza del repo.
- Muchas garantías son contractuales o estructurales, no equivalen por sí solas
  a certificación end-to-end de producción.
- Los guards deben ejecutarse al cierre de fases sensibles, incluso si no hay
  commit.

## 9. Zonas sensibles

No tocar sin fase especifica:

- Auth, JWT, tenant context, permisos, roles y module access.
- Billing, credit ledger, AI job accounting y cualquier camino de pago.
- Modelos, migraciones, base de datos y configuración de persistencia.
- Docker, compose overlays, TLS, redes, hostnames internos y despliegue.
- ComfyUI, renders reales, workers, queues y job scheduler.
- Google Drive, Qdrant, n8n, CRM, integraciones externas y secretos.
- `src_frontend/src/App.tsx`, porque mezcla landing pública y rutas internas.
- `src/config/plans.yml` y docs de pricing, por discrepancias documentadas.
- `OLD/`, backups, exports, logs y artefactos históricos: revisar antes de
  cualquier limpieza.

## 10. Código que parece estable

Estable aqui significa: con contrato, tests cercanos o patrones repetidos; no
significa libre de bugs ni production-ready publico.

- Skills Codex base: tag estable en HEAD y test `test_codex_skills_base.py`.
- Guards WSL/repo y guard de regresiones de base local legacy: existen y son
  ejecutables desde `scripts/dev/`.
- Gating contractual de muchas rutas: existe una familia amplia de tests
  `test_*_routes_gating_contract.py`.
- Configuracion core: `test_config.py` cubre validaciones de produccion y
  compatibilidad legacy.
- AILink Sync Dialogue local: tiene paquetes y tests propios para scanner,
  matching, exports y reportes.
- Documentación CID SaaS: contratos extensos sobre SaaS, roles, permisos,
  planes, módulos, créditos y boundaries.

## 11. Código que requiere revisión futura

- Superficies mixtas de módulo donde ownership no esté plenamente modelado por
  deliverable o proyecto.
- Pricing y planes: resolver discrepancia entre contrato comercial y
  configuración antes de billing real.
- Cola, workers y ComfyUI: validar con smokes reales controlados antes de
  afirmar robustez operativa.
- Integraciones externas: revisar secretos, consentimiento, errores, timeouts y
-  auditoría antes de activar en entornos públicos.
- Frontend landing/CID compartido: separar rutas o builds solo cuando haya
  criterios claros, no durante esta baseline.
- Artefactos históricos y carpetas legacy: auditar con inventario antes de
  limpiar.
- AILink Sync Dialogue: endurecer demo reproducible, muestras seguras,
  explicación de límites y evidencias antes de marketing fuerte.

## 12. Posibles fuentes de ruido

- Carpetas `OLD/`, `backups/`, `.tmp/`, `tmp/`, `exports/`, `logs/`, `storage/`
  y caches locales.
- `node_modules/`, `dist/`, `.venv/`, `venv/` y caches pytest.
- Archivos `.db` legacy visibles en el arbol, que no deben confundirse con
  dirección futura de CID SaaS.
- Docs históricos que pueden haber sido superados por `docs/PRODUCTION_CANDIDATE_STATUS.md`.
- Carpetas satelite como `CID_VOICE_CHATBOT`, `ai-dubbing-legal-studio`,
  `cid-budget` y `comfysearch`, fuera del nucleo si la fase no las nombra.
- Diferencias entre demo-ready, beta privada, production candidate y produccion
  publica.

## 13. Riesgos de tocar runtime

- Romper aislamiento multitenant por cambios aparentemente pequenos en rutas o
  servicios.
- Saltarse gating de modulo/plan al mover dependencias o centralizar rutas.
- Activar rutas demo, experimentales o postproduction en entornos indebidos.
- Introducir regresiones de persistencia o dependencias locales no canonicas.
- Mezclar landing publica y CID interno en navegacion, SEO o guards de rutas.
- Descuadrar créditos, jobs o billing con cambios en planes/configuración.
- Disparar renders, integraciones o APIs externas durante una fase de auditoria.
- Crear confianza falsa si se corrige runtime sin validación end-to-end.

## 14. Próximas fases recomendadas

1. `AILINK/CID.PROJECT.BASELINE.EVIDENCE.INDEX.PHASE2`: índice de evidencias por
   módulo con documentos, tests y gaps.
2. `CID.SAAS.PRICING.CANONICALIZATION.1`: reconciliar pricing docs/config antes
   de pagos.
3. `CID.SAAS.GATING.COVERAGE.AUDIT.1`: matriz ruta por ruta de auth, tenant,
   module access y permisos.
4. `AILINK.SYNC_DIALOGUE.DEMO.EVIDENCE.BASELINE.1`: evidencias reproducibles de
   demo local-first con muestras seguras.
5. `CID.RUNTIME.SMOKE.SAFE.READINESS.1`: smokes no destructivos para backend,
   frontend y guards, sin tocar datos reales.
6. `CID.ARTIFACTS.NOISE.QUARANTINE.AUDIT.1`: inventario de artefactos legacy sin
   borrar nada.

## 15. Criterios para decidir cuándo refactorizar

Refactorizar solo cuando se cumplan todos:

- Existe contrato o directiva vigente que define el comportamiento esperado.
- Hay tests antes del cambio o una fase previa crea tests de contrato.
- El área no está marcada como no-go o sensible sin owner claro.
- El diff puede ser pequeño, reversible y acotado.
- Se conocen rutas, modelos, datos y permisos afectados.
- Hay validaciones target y broader checks definidos antes de editar.
- La refactorización reduce riesgo real, duplicación peligrosa o complejidad
  operativa; no es estética.

No refactorizar cuando:

- El módulo mezcla billing, créditos, tenant, permisos o job execution sin
  cobertura suficiente.
- Hay discrepancia documental pendiente.
- El cambio requiere migraciones, Docker, secretos, pagos o integraciones reales
  no contempladas por la fase.
- La única motivación es ordenar código durante una auditoría.

## 16. Flujo operativo de esta auditoría

1. Activar `.venv` dentro de WSL.
2. Confirmar `/opt/SERVICIOS_CINE`.
3. Revisar `git status`.
4. Leer `AGENTS.md`, skills CID y directivas relevantes.
5. Leer docs, tests y estructura principal.
6. Escribir solo este documento y su test unitario documental.
7. Ejecutar validaciones de cierre.
8. Reportar resultados reales y no hacer commit/tag/push.

## 17. Valor para usuario y aceptación

Valor:

- Permite decidir próximas fases sin tocar runtime.
- Reduce el riesgo de refactor prematuro.
- Separa demo, beta, contrato y producción pública.
- Identifica zonas sensibles antes de nuevas implementaciones.

Criterios de aceptación:

- Documento creado en `docs/project/ailink_cid_safe_baseline_audit_v1.md`.
- Test creado en `tests/unit/test_ailink_cid_safe_baseline_audit.py`.
- El test verifica existencia y secciones críticas.
- La fase queda limitada a docs/test-only.
- Validaciones de cierre ejecutadas y reportadas.
