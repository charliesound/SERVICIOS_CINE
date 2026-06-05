# CID SaaS Plans and Modules Matrix v1

Version: 1.0
Status: SPEC (documental, no implementation)
Date: 2026-06-05
Owners: CID Architecture / CID Product
Scope: AILinkCinema CID SaaS product (planes, modulos, creditos, limites, reglas comerciales).
Companion docs:
- `docs/architecture/cid_saas_model_contract_v1.md` (modelo SaaS, 22 roles, planes, creditos).
- `docs/architecture/cid_roles_permissions_matrix_v1.md` (matriz operativa de roles, permisos, modulos).
- `docs/architecture/backend_gating_contract_v1.md` (cierre P0/P1, 8 patrones de router, 8 P2 manual review).
- `docs/architecture/sound_ingest_field_recorders_spec_v1.md` (modulo Sound Ingest).
- `docs/business/cid_pricing_canonicalization_needed_v1.md` (canonizacion de pricing pendiente).
- `docs/business/cid_pricing_competitive_baseline_v1.md` (baseline competitivo de pricing).
- `docs/business/cid_credits_business_model_v1.md` (modelo de creditos por operacion).

## 1. Proposito

Convertir el contrato SaaS de CID en una matriz comercial operativa. Esta matriz es la fuente de verdad para:

- Que incluye cada plan comercial.
- Que limites aplica cada plan (usuarios, proyectos, almacenamiento, jobs, exports, integraciones).
- Cuantos creditos incluye cada plan y como se compran bolsas adicionales.
- Que modulos estan disponibles, limitados, son add-on, no estan incluidos o son exclusivos Enterprise.
- Como se diferencian demo client, private beta y public SaaS.
- Que reglas de upgrade aplica el sistema cuando un usuario toca un limite.
- Que eventos de auditoria se registran.
- Que fases tecnicas se derivan de este documento.

Sirve como base futura para plan gates, module gates, credit gates y frontend visibility. No es marketing, no es landing, no es pricing publico: es la forma del producto que la ingenieria consume.

Regla de oro: **el cliente nunca compra tecnologia, compra resultados**. La matriz se lee desde el resultado (desarrollo, financiacion, produccion, rodaje, postproducción, delivery, distribucion, promocion) y desde ahi define que modulos, creditos y limites requiere cada plan.

## 2. Alcance

- **CID es la plataforma SaaS integral.** Es el producto que el cliente contrata, usa, factura y renueva. El modelo de organizacion, proyecto, usuario, rol, permiso, plan, modulo, credito, job y asset descrito en `cid_saas_model_contract_v1.md` se mantiene.
- **AILinkCinema puede vender modulos o captar leads**, pero no debe redefinir el contrato de producto. La landing publica de AILinkCinema es un canal comercial, no el producto. Si AILinkCinema vende un modulo suelto, ese modulo debe existir y estar disponible en CID bajo un plan compatible (incluido, add-on o Enterprise). Si vende algo que CID no ofrece, hay un problema de coherencia comercial.
- **Esta fase no implementa codigo.** Es documental.
- **Esta fase no cambia permisos backend.** El contrato de gating cerrado y la matriz de roles/permisos se mantienen como estan.
- **Esta fase no cambia frontend.** Las decisiones de UI para mostrar/ocultar modulos se derivan, no se aplican.
- **Esta fase no cambia modelos de datos.** El schema vendra en fases posteriores.

## 3. Planes comerciales

CID ofrece 5 planes comerciales. El plan Enterprise es contractual y se negocia caso por caso; los otros 4 son self-service con opcion de demo client o private beta.

| Plan | Posicionamiento | Usuario objetivo | Compromiso de compra |
|---|---|---|---|
| **Starter** | Entrada, productor independiente o cortometraje | Productora pequena, freelance consolidado, escuela. | Trial 14 dias o compra directa. |
| **Pro** | Estandar de mercado, productora pequena-mediana | Productora pequena-mediana, agencia, equipo creativo hibrido. | Trial 14 dias o compra directa. |
| **Studio** | Produccion profesional, multiples proyectos | Productora mediana, estudio, broadcaster. | Trial 14 dias + onboarding asistido. |
| **Premium** | Alto volumen, integracion, auditoria avanzada | Productora grande, agencia internacional, broadcaster. | Onboarding comercial, contrato anual recomendado. |
| **Enterprise** | Custom, seguridad, residencia de datos, soporte dedicado | Major studio, broadcaster, plataforma de distribucion, institucion publica. | Contrato anual o plurianual, SLA contractual. |

Reglas comunes:

- **Trial**: 14 dias con plan Pro activado, requiere tarjeta, cancela sin cargo. No se factura hasta el dia 15.
- **Anual**: 2 meses bonificados al pagar anual (efectivo, no prorrateado en factura). Disponible en Starter, Pro, Studio y Premium.
- **Cambio de plan**: pro rata al dia, con efecto inmediato. Downgrade activa periodo de gracia (ver seccion 12).
- **Add-ons**: se contratan aparte, tienen precio aparte, requieren plan minimo (lo indica la matriz). Add-on sin plan compatible no se puede activar.

## 4. Estados de modulo

Cada modulo tiene exactamente uno de estos cinco estados en cada plan. El estado define si el modulo esta disponible, hasta donde, y como se adquiere.

- **included** (`I`): modulo disponible sin coste adicional, dentro de los limites del plan.
- **limited** (`L`): modulo disponible, con cuota mensual o por uso. Superada la cuota, requiere compra de creditos adicionales o upgrade de plan. La cuota concreta se indica en la columna de notas.
- **add_on** (`A`): modulo no incluido en el plan base. Se contrata aparte con su precio de add-on. El precio y la disponibilidad dependen del plan minimo requerido.
- **not_included** (`N`): modulo no disponible en este plan. No se puede activar ni comprar como add-on. Para acceder, hay que cambiar de plan.
- **enterprise_only** (`E`): modulo reservado al plan Enterprise, con SSO y soporte dedicado. No se ofrece como add-on en planes inferiores.

Reglas adicionales:

- `I` con cuota explicita: el modulo aparece como `I` y la cuota concreta va en notas (por ejemplo, `I (50 hojas/mes)`).
- `A` no es `N`: el modulo se puede comprar; en `N` no.
- `E` es absoluto: solo Enterprise. Si una empresa quiere `E` sin ser Enterprise, se negocia un override comercial y se registra como tal en auditoria.
- Los limites de los `L` se calculan mensualmente. Si el cliente paga anual, las cuotas mensuales se mantienen iguales (no se acumulan).

## 5. Matriz de modulos por plan

21 modulos canónicos. La columna `Notas` concreta cuotas de `L` y restricciones de `A`. El sufijo `(C)` en la celda indica que el estado puede cambiar segun override comercial (Enterprise, beta, demo, promo).

### 5.1 Catalogo de modulos (21)

Cada modulo tiene un `module_key` canonico, un nombre publico y un resumen funcional. Los `module_key` siguen la convencion snake_case y se usaran en el codigo y en `/api/capabilities`.

| # | `module_key` | Nombre publico | Resumen funcional |
|---|---|---|---|
| 1 | `project_hub` | Development / Project Hub | Memoria del proyecto, resumen ejecutivo, glosario, decisiones, KPIs cross-modulo. |
| 2 | `screenwriting` | Screenwriting | Edicion de guion, analisis narrativo IA, anotaciones, export a PDF. |
| 3 | `character_bible` | Character Bible | Biblia de personaje: descripcion, arco, vesturario, maquillaje, casting, raccord. |
| 4 | `storyboard` | Storyboard | Hojas de storyboard, previz, render IA (imagen y video), export. |
| 5 | `shotlist` | Shotlist | Shotlist, EDL, planos tecnicos, integracion con camara. |
| 6 | `shooting_plan` | Shooting Plan | Plan de rodaje, calendario, localizaciones, recursos, alertas. |
| 7 | `budget` | Budget | Presupuesto, lineas de coste, control real vs estimado, export. |
| 8 | `financing` | Financing / Grants | Dossieres de financiacion, grants, materiales de pitch, inversion. |
| 9 | `production_mgmt` | Production Management | Gestion integral de produccion: equipo, localizaciones, transporte, catering, permisos. |
| 10 | `crew_cast` | Crew / Cast | Gestion de crew, cast, disponibilidad, contratos, pruebas, base de datos. |
| 11 | `media_ingest` | Media Ingest | Ingesta generica de material (video, foto, audio, documentos), catalogo, manifests. |
| 12 | `sound_ingest` | Sound Ingest | Ingesta especializada de audio de campo, transcripcion, etiquetado IA. Ver spec dedicada. |
| 13 | `postproduction` | Postproduction | Montaje, color, VFX, postproduccion de sonido, integracion. |
| 14 | `dubbing_localization` | Dubbing / Localization | Doblaje, subtitulado, localizacion, gestion de idiomas. |
| 15 | `delivery` | Delivery | Masters, QC, deliverables por plataforma (broadcast, streaming, festival). |
| 16 | `distribution` | Distribution | Distribucion, festivales, agentes, ventas internacionales, materiales comerciales. |
| 17 | `marketing_promotion` | Marketing / Promotion | Trailer, teasers, campanas, redes, prensa, kit de prensa. |
| 18 | `analytics` | Analytics / Reports | Dashboards, KPIs, consumo por modulo, por proyecto, por miembro. |
| 19 | `integrations_api` | Integrations / API | Integraciones externas (n8n, Drive, Frame.io, Slack) y API publica. |
| 20 | `ai_traceability` | AI Traceability | Trazabilidad de jobs IA: motor, modelo, prompt version, input hash, output asset, creditos. |
| 21 | `admin_billing_org` | Admin / Billing / Organization | Gestion de organizacion: miembros, planes, modulos add-on, billing, SSO, dominios. |

### 5.2 Mapeo a `cid_saas_model_contract_v1.md`

Los 19 modulos del contrato SaaS v1 se reconcilian con estos 21. Esta matriz agrega granularidad donde el contrato SaaS no llegaba.

| `module_key` (esta matriz) | Modulo equivalente en contrato SaaS v1 | Cambio |
|---|---|---|
| `project_hub` | `project_memory` | Renombrado, alcance ampliado a resumen ejecutivo cross-modulo. |
| `screenwriting` | `script_analysis` | Renombrado, incluye edicion de guion ademas de analisis. |
| `character_bible` | `character_bible` | Sin cambio. |
| `storyboard` | `storyboard_ai` | Renombrado, incluye edicion manual ademas de IA. |
| `shotlist` | `shotlist` | Sin cambio. |
| `shooting_plan` | `shooting_plan` | Sin cambio. |
| `budget` | `budget` | Sin cambio. |
| `financing` | `funding` | Renombrado, separacion explicita de grants. |
| `production_mgmt` | (nuevo) | Nuevo. Cubre la gestion integral de produccion que el contrato SaaS no modelaba. |
| `crew_cast` | (parte de `character_bible` casting + nuevo) | Elevado a modulo propio; `character_bible` retiene solo la descripcion del personaje. |
| `media_ingest` | (nuevo) | Nuevo. Ingesta generica distinta a `sound_ingest`. |
| `sound_ingest` | `sound_ingest` | Sin cambio. |
| `postproduction` | (nuevo) | Nuevo. Agrega montage, color, vfx, post sonido. |
| `dubbing_localization` | (parte de `ai_pipeline_builder`) | Elevado a modulo propio. |
| `delivery` | `delivery` | Sin cambio. |
| `distribution` | `distribution_pack` | Renombrado, alcance ampliado a festivales y agentes. |
| `marketing_promotion` | `producer_pitch` + `crm_sales` | Fusion: pitch financiero y CRM comercial se unen bajo marketing. |
| `analytics` | `admin_analytics` | Renombrado, alcance ampliado a KPIs cross-proyecto. |
| `integrations_api` | `integrations_n8n` + `advanced_exports` | Fusion: integraciones externas y API publica. |
| `ai_traceability` | (nuevo) | Nuevo. Modulo transversal de trazabilidad. |
| `admin_billing_org` | (parte de organizacion) | Elevado a modulo. |

Esta reconciliacion queda abierta: cualquier ajuste se aplica primero en el contrato SaaS v2 (ver seccion 18).

### 5.3 Matriz principal (21 modulos x 5 planes)

Estados: `I` = included, `L` = limited, `A` = add_on, `N` = not_included, `E` = enterprise_only.

| Modulo | Starter | Pro | Studio | Premium | Enterprise |
|---|---|---|---|---|---|
| `project_hub` | I (1 proyecto) | I (3 proyectos) | I (10 proyectos) | I (25 proyectos) | I (custom) |
| `screenwriting` | I (1 guion) | I (5 guiones) | I (20 guiones) | I (60 guiones) | I (custom) |
| `character_bible` | L (3 biblias/mes) | I (15 biblias/mes) | I (60 biblias/mes) | I (250 biblias/mes) | I (custom) |
| `storyboard` | L (20 hojas/mes) | I (100 hojas/mes) | I (500 hojas/mes) | I (2.000 hojas/mes) | I (custom) |
| `shotlist` | N | I (100 planos/proyecto) | I (500 planos/proyecto) | I (2.000 planos/proyecto) | I (custom) |
| `shooting_plan` | N | I (3 planes/proyecto) | I (10 planes/proyecto) | I (ilimitado) | I (custom) |
| `budget` | I (1 presupuesto) | I (5 presupuestos) | I (20 presupuestos) | I (60 presupuestos) | I (custom) |
| `financing` | N | L (5 pitches/mes) | I (25 pitches/mes) | I (100 pitches/mes) | I (custom) |
| `production_mgmt` | N | A | I (10 proyectos) | I (ilimitado) | I (custom) |
| `crew_cast` | N | A | I (50 miembros/proyecto) | I (ilimitado) | I (custom) |
| `media_ingest` | L (10 GB/mes) | I (50 GB/mes) | I (250 GB/mes) | I (1 TB/mes) | I (custom) |
| `sound_ingest` | N | A (50 GB ingestados/mes) | I (250 GB/mes) | I (1 TB/mes) | I (custom) |
| `postproduction` | N | A | I (1 master simultaneo) | I (5 masters simultaneos) | I (custom) |
| `dubbing_localization` | N | A | A (2 idiomas) | I (10 idiomas) | I (custom) |
| `delivery` | N | A | I (50 entregas/mes) | I (200 entregas/mes) | I (custom) |
| `distribution` | N | A | I (20 packs/mes) | I (100 packs/mes) | I (custom) |
| `marketing_promotion` | N | A | I (5 campanas/proyecto) | I (ilimitado) | I (custom) |
| `analytics` | N | N | A | I (dashboards completos) | I (custom) |
| `integrations_api` | N | A (3 integraciones) | I (10 integraciones) | I (API publica incluida) | I (custom, API completa) |
| `ai_traceability` | I (basico) | I (estandar) | I (avanzado) | I (auditable + export) | I (full + cross-organization) |
| `admin_billing_org` | I (1 admin) | I (3 admins) | I (10 admins) | I (20 admins) | I (custom) |

Notas de la matriz:

- Las cuotas entre parentesis son limites mensuales o por proyecto segun indique la nota; las cuotas mensuales se resetean al cierre del ciclo.
- `I (custom)` en Enterprise significa que el limite se negocia caso por caso; el valor por defecto de fallback es el de Premium, ajustable al alza sin pago adicional.
- `A` en `production_mgmt` para Pro indica que el modulo se contrata como add-on con un minimo de plan Pro; no esta disponible en Starter.
- `dubbing_localization` es `A` en Studio (no incluido en plan base) porque depende de capacidades de transcripcion y voz que pueden no estar en todos los casos de uso.
- `analytics` es `N` en Pro: el cliente Pro ve los dashboards basicos de su plan pero no analytics cross-proyecto ni custom.
- `ai_traceability` esta en `I` desde Starter porque es un requisito legal y de auditoria minimo; el alcance (basico, estandar, avanzado, auditable, full) escala con el plan.

## 6. Creditos incluidos por plan

Los creditos son la unidad de cobro por uso de IA y por operaciones pesadas. Cada plan incluye una cuota mensual; el cliente puede comprar bolsas adicionales (ver seccion 7) o hacer upgrade de plan.

| Plan | Creditos incluidos / mes | Uso principal |
|---|---|---|
| **Starter** | 500 | Analisis textual, metadata, recomendaciones pequenas. |
| **Pro** | 2.000 | Analisis extendido, presupuestos, RAG, informes. |
| **Studio** | 7.500 | Storyboard a escala, edicion asistida, transcripcion. |
| **Premium** | 20.000 | Produccion a escala, multiples masters, VFX, integraciones. |
| **Enterprise** | Contractual | Pool mensual negociado en el contrato; minimo de 50.000 recomendado. |

Reglas:

- Los creditos `included_monthly_remaining` se resetean al cierre del ciclo de facturacion.
- No hacen rollover por defecto; excepcion: planes Enterprise (negociados) o promos explicitas con fecha.
- El saldo se calcula como `included_monthly_remaining + purchased_balance + adjustment_credits - reserved_active - consumed_period` (ver contrato SaaS seccion 9).
- Si el saldo es insuficiente, la accion se rechaza con `402 Payment Required` y mensaje accionable (ver seccion 12).
- El `ai_traceability` modulo consume una cantidad pequena de creditos por evento auditable; este coste esta incluido en el plan.

## 7. Bolsas adicionales

CREDITO EXTRA que el cliente puede comprar sin cambiar de plan. Se aplican sobre el saldo `purchased_balance` y tienen caducidad a 12 meses.

| Plan compatible | Bolsa | Precio orientativo | Ratio €/credito | Notas |
|---|---|---|---|---|
| Starter | +500 creditos | 49 € | 0,098 €/cr | Bolsa pequena para escalar. |
| Pro | +1.500 creditos | 119 € | 0,079 €/cr | Estándar. |
| Pro | +3.000 creditos | 229 € | 0,076 €/cr | Bono por volumen. |
| Studio | +10.000 creditos | 699 € | 0,069 €/cr | Produccion a escala. |
| Premium | Custom / add-on | Contractual | Segun contrato | Negociado caso por caso. |
| Enterprise | Contractual | Contractual | Contractual | Incluido en pool mensual o bolsa extra. |

Reglas:

- Las bolsas se compran en cualquier momento del ciclo de facturacion.
- Se facturan al momento de la compra; no son recurrentes.
- Caducan a 12 meses desde la compra; el sistema avisa 30, 15 y 1 dias antes.
- Una bolsa comprada en un plan no se transfiere automaticamente si el cliente hace downgrade a un plan incompatible; en ese caso, las bolsas no consumidas se mantienen durante 30 dias (periodo de gracia) y caducan al cambiar.
- Enterprise puede tener bolsas de cualquier tamano; el precio se negocia.

## 8. Limites por plan

Tabla de limites por plan. Los valores cuantitativos se concretan en la seccion 9.

| Dimension | Definicion | Aplicacion |
|---|---|---|
| Organizaciones incluidas | Numero de tenants contratables bajo la suscripcion. | 1 por plan. Enterprise puede tener varias. |
| Usuarios incluidos | Numero de miembros activos en la organizacion. | Por plan. |
| Usuarios adicionales | Coste o disponibilidad de usuarios extra. | Por plan; ver seccion 9. |
| Proyectos activos | Numero de proyectos en estado distinto de `archivado`. | Por plan. |
| Almacenamiento incluido | Capacidad total en GB de la organizacion. | Por plan. |
| Jobs IA concurrentes | Numero de jobs de IA ejecutandose simultaneamente en la organizacion. | Por plan. |
| Exportaciones | Numero y tipo de exports permitidos por mes. | Por plan. |
| Integraciones externas | Numero de conexiones a servicios externos activas. | Por plan. |
| API access | Disponibilidad y limites de la API publica. | Por plan. |
| Soporte | Nivel de soporte: estandar, prioritario, dedicado. | Por plan. |
| Auditoria | Retencion y granularidad del log. | Por plan. |
| Retencion de datos | Tiempo que los datos se conservan tras baja o archivado. | Por plan. |
| Trazabilidad IA | Nivel de detalle del modulo `ai_traceability`. | Por plan. |

## 9. Propuesta orientativa de limites

Valores cuantitativos concretos. Se ajustan con la oferta final en cada mercado y se versionan en este documento. La canonicalizacion frente a `src/config/plans.yml` se trata en `cid_pricing_canonicalization_needed_v1.md` y se cierra en la fase `CID.SAAS.PRICING.CANONICALIZATION.1`.

### 9.1 Starter

- 1 organizacion.
- 1 proyecto activo.
- 2 usuarios incluidos. Usuarios adicionales: no disponibles (upgrade a Pro).
- 10 GB de almacenamiento.
- 1 job IA concurrente.
- Exports basicos: PDF, MP4 720p. Limite: 10 exports/mes.
- 1 integracion externa (solo `media_ingest` basico).
- Sin API publica.
- Soporte estandar (email, respuesta en 48h laborables).
- Auditoria basica: 30 dias, sin export.
- Retencion de datos: 90 dias tras baja.
- Trazabilidad IA: nivel basico (job_id, provider, model, output_asset).

### 9.2 Pro

- 1 organizacion.
- 3 proyectos activos.
- 5 usuarios incluidos. Usuarios adicionales: +1 por 19 €/mes.
- 50 GB de almacenamiento.
- 2 jobs IA concurrentes.
- Exports profesionales: PDF, MP4 1080p, EDL basico, AAF. Limite: 50 exports/mes.
- 3 integraciones externas (Drive, Frame.io, n8n).
- API publica en modo lectura (GET). Limite: 1.000 requests/dia.
- Soporte prioritario ligero (email + chat, respuesta en 24h laborables).
- Auditoria estandar: 90 dias, export CSV.
- Retencion de datos: 180 dias tras baja.
- Trazabilidad IA: nivel estandar (anadido input_hash, prompt_version, credit_estimate, credits_charged).

### 9.3 Studio

- 1 organizacion.
- 10 proyectos activos.
- 15 usuarios incluidos. Usuarios adicionales: +1 por 15 €/mes.
- 250 GB de almacenamiento.
- 4 jobs IA concurrentes.
- Exports profesionales avanzados: PDF, MP4 4K, ProRes, DNxHR, EDL completo, AAF, IMF, M+E. Limite: 200 exports/mes.
- 10 integraciones externas.
- API publica en modo lectura/escritura. Limite: 10.000 requests/dia.
- Soporte prioritario (email + chat + telefono horario, respuesta en 8h laborables).
- Auditoria avanzada: 180 dias, export CSV/JSON, filtros custom.
- Retencion de datos: 365 dias tras baja.
- Trazabilidad IA: nivel avanzado (anadido parametros, parent_job_id, trace_id, replay).

### 9.4 Premium

- 1 organizacion.
- 25 proyectos activos.
- 30 usuarios incluidos. Usuarios adicionales: +1 por 12 €/mes.
- 1 TB de almacenamiento.
- 8 jobs IA concurrentes.
- Exports completos: incluye export cross-project, batch, automatizacion via API. Limite: 1.000 exports/mes.
- Integraciones externas ilimitadas.
- API publica completa. Limite: 100.000 requests/dia, rate limit configurable.
- Auditoria completa: 365 dias, export CSV/JSON, filtros custom, alertas, dashboard de admin.
- Retencion de datos: 730 dias tras baja.
- Trazabilidad IA: auditable + export completo a CSV/JSON.
- Soporte prioritario alto (email + chat + telefono 12x5, respuesta en 4h).
- Account manager opcional (no incluido en plan, contratable como add-on).

### 9.5 Enterprise

- Organizaciones, proyectos y usuarios segun contrato (minimo recomendado: 1 organizacion, 50 proyectos, 50 usuarios).
- Almacenamiento contractual (minimo 10 TB; tipico 100 TB - 1 PB).
- Concurrencia IA contractual (minimo 16 jobs concurrentes; tipico 32-64).
- API completa: limites segun contrato, rate limit configurable, IP allowlist, webhooks.
- Integraciones custom: desarrollo dedicado de conectores a medida.
- SSO/SAML/OIDC opcional (incluido en la mayoria de contratos Enterprise).
- Soporte dedicado 24/7 con SLA contractual (tipico: P1 1h, P2 4h, P3 8h).
- Despliegue custom opcional: on-premise, VPC dedicada, region geografica especifica, residencia de datos EU/EE.UU./LATAM.
- Account manager dedicado.
- Auditoria contractual: retencion ampliada (1-7 anos), export cross-organization, alertas avanzadas, integracion con SIEM del cliente.
- Trazabilidad IA full: cross-organization, replay historico, export a sistemas externos.

## 10. demo client / private beta / public SaaS

CID se ofrece en tres modos comerciales. Cada modo tiene objetivo, limites, creditos, acceso a modulos, riesgo comercial y criterio de conversion propios.

### 10.1 demo client

- **Objetivo**: mostrar el producto a un prospecto cualificado, sin compromiso de compra, durante un periodo corto. El cliente ve la UI y puede ejecutar acciones limitadas.
- **Limites**: 1 organizacion, 1 proyecto activo, 1 usuario, 5 GB de almacenamiento, 1 job IA concurrente, 50 creditos totales (no renovables), 5 exports totales, 0 integraciones.
- **Creditos**: 50 creditos one-shot, no se compran bolsas, no hay rollover.
- **Acceso a modulos**: solo `project_hub`, `screenwriting` (read + analisis), `character_bible` (read), `budget` (read), `ai_traceability` (read). El resto esta oculto o en candado.
- **Riesgo comercial**: bajo si el prospecto es cualificado; medio si se regala a leads frios porque consume capacidad del cluster.
- **Criterio de conversion**: a `private beta` si el prospecto pasa a evaluacion, o a `public SaaS` trial Pro si el prospecto es self-service.
- **Reglas tecnicas**: el tenant demo se crea con `is_demo=true`; el backend reconoce el flag y aplica los limites sin necesidad de plan. La conversion a trial Pro requiere migrar el tenant a un plan real.

### 10.2 private beta

- **Objetivo**: evaluar el producto con un conjunto cerrado de clientes pioneros, recoger feedback, validar pricing y comportamiento bajo carga real. Acceso gratuito o bonificado.
- **Limites**: configurables por invitacion. Tipico: 1 organizacion, 3 proyectos activos, 5 usuarios, 50 GB, 2 jobs IA concurrentes, 1.000 creditos/mes (renovables mientras dure la beta), 50 exports/mes, 3 integraciones.
- **Creditos**: cuota mensual renovable mientras la beta este activa. Sin bolsas adicionales; si se agotan, se reactiva la cuota (politica de no-spam).
- **Acceso a modulos**: modulos completos del plan Pro o Studio segun el beta. Modulos experimentales (`ai_traceability` avanzado, `dubbing_localization` con IA generativa) pueden activarse como `E` o `A` con override beta.
- **Riesgo comercial**: medio. El beta tester recibe capacidad real; si se va, hay churn potencial. Si se queda, hay conversion a plan de pago. Hay que gestionar bien la transicion.
- **Criterio de conversion**: a `public SaaS` plan Pro o superior al cierre del beta, con onboarding asistido y posible lock-in de precio durante 3 meses.
- **Reglas tecnicas**: el tenant beta se crea con `is_beta=true`, `beta_end_date`, `beta_plan_key`. El backend enforza limites y vencimientos. La conversion a plan de pago requiere actualizar el `plan_key` y limpiar los flags beta.

### 10.3 public SaaS

- **Objetivo**: producto comercial general, disponible para cualquier cliente que pague o este en trial.
- **Limites**: los de la seccion 9 por plan. Trial 14 dias con Pro activado.
- **Creditos**: cuota del plan + bolsas adicionales.
- **Acceso a modulos**: la matriz principal (seccion 5.3) segun plan contratado.
- **Riesgo comercial**: bajo en ingresos pero alto en soporte si la documentacion es insuficiente. El reto es el ratio conversion trial -> pago.
- **Criterio de conversion**: trial -> pago a Pro, Studio, Premium o Enterprise segun el tamano del proyecto del cliente. Si el trial expira sin conversion, el tenant pasa a estado `expired` y los datos se conservan 30 dias antes de archivar.
- **Reglas tecnicas**: el tenant publico se crea con `plan_key=pro` (trial) o el plan elegido. El backend enforza limites y vencimientos. Cambio de plan via `billing.manage`.

### 10.4 Tabla resumen de modos

| Dimension | demo client | private beta | public SaaS |
|---|---|---|---|
| Organizaciones | 1 | 1 | 1 (Enterprise: varias) |
| Usuarios | 1 | 5 (tipico) | 2 / 5 / 15 / 30 / custom |
| Proyectos | 1 | 3 | 1 / 3 / 10 / 25 / custom |
| Almacenamiento | 5 GB | 50 GB | 10 GB / 50 GB / 250 GB / 1 TB / custom |
| Creditos totales | 50 (one-shot) | 1.000/mes (renovables) | 500 / 2.000 / 7.500 / 20.000 / custom |
| Modulos | 5 basicos | Plan Pro/Studio + experimentales | Por plan (matriz seccion 5) |
| Soporte | Email | Email + onboarding | Por plan (matriz seccion 9) |
| Riesgo comercial | Bajo | Medio | Bajo/alto segun conversion |
| Conversion tipica | -> beta o trial | -> plan pago | (es el destino) |

## 11. Reglas de upgrade

Comportamiento esperado del sistema cuando el usuario toca un limite o un bloqueo. Cada caso define: trigger, respuesta backend, mensaje al usuario, accion posible.

### 11.1 Modulo bloqueado por plan

- **Trigger**: el usuario intenta acceder a un modulo `not_included` (`N`) o `enterprise_only` (`E`) en su plan.
- **Backend**: `403 Forbidden` con `code=module_blocked`. Evento `module_blocked` en auditoria.
- **Mensaje**: "El modulo [nombre] no esta disponible en tu plan [plan]. Para usarlo, sube a [plan superior] o activalo como add-on (si esta disponible)."
- **Accion posible**: ver detalle del plan superior, contratar add-on (si `A`), contactar a un admin.

### 11.2 Modulo limited requiere upgrade

- **Trigger**: el usuario agoto la cuota mensual de un modulo `limited` (`L`).
- **Backend**: `429 Too Many Requests` con `code=quota_exceeded`. Evento `limit_reached` en auditoria.
- **Mensaje**: "Has llegado al limite de [cuota] de tu plan [plan] este mes. El contador se reinicia el dia 1. Si necesitas mas, compra creditos adicionales o sube a [plan superior]."
- **Accion posible**: comprar bolsa, upgrade plan, esperar al reset.

### 11.3 Creditos agotados

- **Trigger**: el usuario intenta lanzar una accion de IA y el saldo es insuficiente para `credit_estimate`.
- **Backend**: `402 Payment Required` con `code=insufficient_credits`. Evento `credit_exhausted` en auditoria.
- **Mensaje**: "Esta accion cuesta unos [N] creditos. Tu saldo actual es [M]. Tienes dos opciones: comprar un paquete de [paquete] creditos ([precio]) o subir a [plan] para [cuota] creditos/mes."
- **Accion posible**: comprar bolsa, upgrade plan, cancelar la accion.

### 11.4 Almacenamiento agotado

- **Trigger**: una subida de asset excede el almacenamiento disponible.
- **Backend**: `507 Insufficient Storage` con `code=storage_exceeded`. Evento `limit_reached` en auditoria.
- **Mensaje**: "Has llegado al limite de [N] GB de almacenamiento. Libera espacio eliminando assets no usados o sube a [plan] para mas capacidad."
- **Accion posible**: eliminar assets (con cuidado), upgrade plan, contratar add-on de almacenamiento (si existe).

### 11.5 Usuarios agotados

- **Trigger**: un `organization_admin` intenta invitar a un usuario nuevo y la organizacion esta en el maximo.
- **Backend**: `403 Forbidden` con `code=user_limit_reached`. Evento `limit_reached` en auditoria.
- **Mensaje**: "Tu plan [plan] incluye [N] usuarios. Tienes [M] usuarios adicionales disponibles contratandolos por [precio]/mes, o puedes subir a [plan] para [N2] usuarios."
- **Accion posible**: contratar usuarios adicionales, upgrade plan, revocar usuarios inactivos.

### 11.6 Proyectos activos agotados

- **Trigger**: un `organization_admin` o `productor` intenta crear un proyecto nuevo y la organizacion esta en el maximo.
- **Backend**: `403 Forbidden` con `code=project_limit_reached`. Evento `limit_reached` en auditoria.
- **Mensaje**: "Tu plan [plan] incluye [N] proyectos activos. Archiva proyectos finalizados o sube a [plan] para mas capacidad."
- **Accion posible**: archivar proyectos, upgrade plan, contactar admin.

### 11.7 Exportacion premium requerida

- **Trigger**: el usuario solicita un export que su plan no incluye (ProRes 4K en Starter, IMF en Pro, batch cross-project en Studio).
- **Backend**: `403 Forbidden` con `code=export_not_available`. Evento `export_blocked` en auditoria.
- **Mensaje**: "El formato [formato] no esta disponible en tu plan [plan]. Disponible en [plan] o superior."
- **Accion posible**: usar formato alternativo, upgrade plan.

### 11.8 Integracion no incluida

- **Trigger**: el usuario intenta conectar una integracion externa (n8n, Drive, Frame.io) que su plan no incluye.
- **Backend**: `403 Forbidden` con `code=integration_not_available`. Evento `module_blocked` en auditoria.
- **Mensaje**: "La integracion [nombre] no esta incluida en tu plan [plan]. Puedes activarla como add-on por [precio]/mes o subir a [plan]."
- **Accion posible**: contratar add-on, upgrade plan, usar alternativa manual.

### 11.9 API no disponible

- **Trigger**: el usuario hace una llamada a la API publica con un token de un plan sin API, o supera el rate limit.
- **Backend**: `403 Forbidden` (sin API) o `429 Too Many Requests` (rate limit). Evento `api_access_denied` o `limit_reached`.
- **Mensaje**: "La API publica no esta disponible en tu plan [plan]. Sube a Pro para acceso de lectura o Studio para lectura/escritura." O: "Has superado el rate limit de [N] requests/dia de tu plan [plan]."
- **Accion posible**: upgrade plan, esperar al reset, contratar add-on de API.

### 11.10 Plan cancelado

- **Trigger**: el `organization_owner` cancela la suscripcion, o el impago supera el periodo de gracia.
- **Backend**: la organizacion pasa a estado `suspended` con `suspended_at` y `suspension_reason`. Los endpoints bloquean escritura y devuelven `423 Locked`. Los proyectos quedan en read-only.
- **Mensaje**: "Tu suscripcion esta suspendida. Para reactivar el acceso, actualiza el metodo de pago o contacta a soporte."
- **Accion posible**: actualizar pago, contactar soporte, exportar datos durante el periodo legal.

### 11.11 Trial o beta caducada

- **Trigger**: el periodo de trial o beta ha expirado sin conversion a plan de pago.
- **Backend**: la organizacion pasa a estado `expired`. Despues de 30 dias, pasa a `archived`.
- **Mensaje**: "Tu periodo de [trial/beta] ha finalizado. Para continuar usando CID, elige un plan. Tus datos se conservan [N] dias."
- **Accion posible**: contratar plan, exportar datos, contactar soporte.

## 12. Comportamiento esperado backend / frontend

Coordinacion entre backend y frontend para que la matriz se aplique de forma coherente.

- **El backend es la fuente de verdad.** Toda decision de plan, modulo, credito, limite, export o integracion se enforza en el backend. El frontend puede mentir; el backend no.
- **El frontend solo oculta, muestra o explica.** Su funcion es evitar friccion: no muestra acciones que el backend rechazaria, y muestra mensajes contextuales cuando una accion no esta disponible.
- **Nunca confiar unicamente en frontend visibility.** Es una regla de seguridad, no solo de UX. Un usuario con DevTools puede saltarse cualquier visibilidad de frontend; el gating del backend es la unica defensa.
- **Conexiones futuras con dependencias de gating** (orden de desarrollo):
  1. `get_tenant_context` (existente, ya enforza tenant).
  2. `validate_project_access` (existente, ya enforza ownership de proyecto).
  3. `require_write_permission` (existente, ya enforza escritura).
  4. `require_module_access(module_key)` (existente, ya enforza modulo por plan).
  5. `require_permission(permission_key)` (futuro, enforza permiso especifico contra la matriz de roles).
  6. `require_credit(credit_estimate)` (futuro, enforza saldo y ejecuta reserva/cargo/rollback).
  7. `plan_gates` (futuro, agrega enforza de limites de plan: usuarios, proyectos, almacenamiento).
  8. `module_gates` (futuro, complementa `require_module_access` con quotas y add-ons).
- **Las respuestas de bloqueo deben ser explicables para el usuario.** Todo codigo de error (4xx) lleva un `code` canonico y un `message` en lenguaje del rol, no en jerga tecnica. El usuario siempre entiende que necesita hacer para desbloquear.
- **El frontend consume `/api/capabilities`** (futuro) para construir su UI. `/api/capabilities` devuelve la matriz efectiva: para el usuario actual, en el proyecto actual, con su plan actual, que modulos ve, que limites tiene, que acciones puede ejecutar, cuanto credito le queda.
- **El cache de `/api/capabilities` es corto** (60 segundos) y se invalida al cambiar plan, al activar/desactivar add-on, al comprar creditos, al cambiar de proyecto, y al expirar el token.

## 13. Relacion con creditos

Los creditos se consumen en cuatro niveles segun el coste computacional y operativo de la accion. Esta clasificacion guia la documentacion de precios y la explicacion al cliente.

### 13.1 Coste bajo (1-10 creditos)

- Analisis textual: resumen ejecutivo, extraccion de entidades, lectura rapida de documento.
- Metadata: generacion de tags, keywords, categorizacion.
- Recomendaciones pequenas: sugerencias de mejora, listado de inconsistencias.
- Validaciones automaticas: comprobacion de formato, de schema, de reglas de negocio.
- RAG ligero: preguntas sobre el guion o el proyecto, sin generar contenido nuevo.
- Eventos de auditoria IA: registro de cada accion auditable.

Uso tipico: cualquier usuario en cualquier momento. No es un evento notable; entra en la cuota mensual sin friccion.

### 13.2 Coste medio (10-100 creditos)

- Desglose narrativo: estructura del guion, arcos, dialogo, conflictos.
- Presupuesto: generacion inicial, ajustes, control real vs estimado.
- Informes largos: pitch deck, dossier de financiacion, one-pager, executive summary.
- RAG avanzado: preguntas con contexto amplio, citacion de fuentes, resumen de proyecto completo.
- Analisis de mercado: benchmarking, competidores, tendencias, oportunidades de financiacion.
- Analisis de audio: transcripcion, etiquetado, deteccion de eventos (ver `sound_ingest` spec).
- Match de casting: propuesta de elenco basada en biblia.
- Generacion de copy: tagline, sinopsis, logline, descripcion para festivales.

Uso tipico: 1-3 veces por sesion de trabajo. El usuario ve el consumo acumularse y decide conscientemente cuando lanzarlo.

### 13.3 Coste alto (100-1.000 creditos)

- Storyboard image generation: cada hoja consume 30-60 creditos (segun calidad).
- Concept art: cada lamina consume 40-90 creditos.
- Video: generacion de previz, clip explicativo, animacion de prueba.
- Dubbing: doblaje de dialogo, sincronizacion labial, generacion de voz.
- Restoration: limpieza de audio, mejora de video, upscaling, colorization.
- Heavy AI jobs: modelos grandes, multi-modal, agentes, pipelines complejos.
- Render ComfyUI: renders pesados con multiples pasadas, varios modelos.
- Simulacion VFX: planos con elementos generados, integracion, composicion.

Uso tipico: pocas veces por sesion, concentradas en momentos creativos clave. El usuario ve el consumo disparar y debe confirmar antes de lanzar.

### 13.4 Coste contractual (no-credito)

- Procesos Enterprise: jobs dedicados en GPU, modelos custom, fine-tuning.
- GPU dedicada: capacidad reservada para el cliente fuera del pool compartido.
- Integraciones custom: desarrollo de conectores a medida, no facturable por credito.
- Soporte dedicado: account manager, soporte 24/7, onboarding a medida.
- Despliegue custom: on-premise, VPC dedicada, region especifica.

Uso tipico:Enterprise, no cliente self-service. El coste se negocia en el contrato y se factura de forma independiente, no como creditos.

## 14. Relacion con modulos audiovisuales

CID debe ser vendible por resultados, no por herramientas. Los modulos se agrupan en ocho areas de resultado que el cliente entiende y valora. Internamente, cada area se controla por plan, modulo, credito, rol y estado del proyecto (ver contrato SaaS y matriz de roles).

### 14.1 Las ocho areas de resultado

1. **Desarrollo**: project_hub, screenwriting, character_bible. Resultado: guion + biblia + memoria del proyecto. Valor para el cliente: claridad creativa desde el dia 1.
2. **Financiacion**: financing, budget, producer_pitch (parte de marketing). Resultado: dossier, deck, presupuesto, plan financiero. Valor: capacidad de captar inversion.
3. **Produccion**: production_mgmt, crew_cast, budget, shooting_plan. Resultado: equipo confirmado, localizaciones, calendario, presupuesto bajo control. Valor: la pelicula se puede hacer.
4. **Rodaje**: shotlist, shooting_plan, media_ingest, sound_ingest. Resultado: material rodado con metadatos completos, audio de calidad, catalogado. Valor: la pelicula existe en bruto.
5. **Postproduccion**: postproduction, sound_ingest (post), media_ingest (post), ai_traceability. Resultado: master final, color, VFX, mezcla, mastered. Valor: la pelicula esta terminada.
6. **Delivery**: delivery, dubbing_localization. Resultado: masters por plataforma, doblajes, subtitulos, QC. Valor: la pelicula llega al publico.
7. **Distribucion**: distribution, marketing_promotion, analytics. Resultado: presencia en mercados, festivales, materiales comerciales, datos de impacto. Valor: la pelicula se ve y se vende.
8. **Promocion**: marketing_promotion, distribution (parte), analytics. Resultado: trailer, teasers, campanas, prensa, kit. Valor: la pelicula se conoce.

### 14.2 Control interno vs venta externa

Aunque la venta externa es por area de resultado, el control interno es por modulo, plan, credito, rol y estado. Esto significa:

- Un cliente Pro no compra "desarrollo" sueltos; compra un plan Pro que incluye los modulos `project_hub`, `screenwriting`, `character_bible` (con cuota) y `budget`. Si quiere `shotlist`, debe tener Pro o superior.
- Un Enterprise que quiere un modulo de "postproduccion" avanzado ya lo tiene porque su plan lo incluye; el override se hace por quota o por integracion custom.
- El cliente nunca ve modulos sueltos como "storyboard" o "dubbing" en la landing; ve areas de resultado y deja que el sistema decida que modulos las componen.
- Internamente, el equipo de operaciones y soporte ve modulos; externamente, el cliente y el comercial ven areas.

## 15. Casos limite

12 casos limite que la matriz debe resolver de forma consistente.

### 15.1 Proyecto archivado

- El `productor` o `organization_admin` archiva un proyecto. Estado: `archived`.
- Efectos: escritura bloqueada en todos los modulos; lectura permitida solo para miembros con `audit.read`; `ai_traceability` muestra el historial completo.
- Backups: el proyecto sigue contando para almacenamiento durante 30 dias; despues, se mueve a archivo frio (storage economico).
- Reactivacion: solo `project_admin` puede reactivar; el sistema exige justificacion y registra `project_state_changed` en auditoria.

### 15.2 Organizacion sin creditos

- Saldo `credit_balance` = 0 y no hay reservas activas.
- Backend sigue respondiendo para `read`; rechaza cualquier accion que requiera `ai.run` con `402 Payment Required`.
- Los miembros no pueden ejecutar jobs IA; pueden dejar de hacerlo y ver mensajes contextuales en la UI.
- El `billing_admin` o `organization_admin` puede comprar bolsas o cambiar de plan; ambos quedan registrados en auditoria.

### 15.3 Plan cancelado

- `organization_owner` cancela la suscripcion. Estado: `suspended`.
- Escritura bloqueada (`423 Locked`); lectura permitida con throttling reducido.
- Datos conservados durante el periodo legal (90-365 dias segun plan); despues, archivo frio.
- Reactivacion: actualizar pago; el `suspended_at` se limpia y el plan se reactiva con prorrateo.

### 15.4 Usuario externo invitado

- Productora externa X invita a Ana de la Productora Y a un proyecto como `direccion_arte` externo.
- Ana ve solo el proyecto donde esta invitada; no ve otros proyectos de la Productora X.
- Si Productora X concede `client_feedback.write` adicional, Ana lo tiene solo en ese proyecto.
- Si intenta acceder por URL a otro proyecto, recibe `404` o `403`; el gating nunca expone la existencia del otro proyecto.
- Creditos: Ana no consume creditos de Productora X; si lanza una accion IA, se carga a la organizacion donde esta invitada (Productora X) o falla si Productora X no tiene saldo.

### 15.5 Reviewer externo

- Carlos es invitado como `revisor_invitado` a un proyecto con `expires_at=30 dias`.
- Ve lo que el productor decide mostrarle; deja feedback opcional.
- Sin acceso a creditos, billing, admin, otros proyectos.
- Al expirar `expires_at`, el acceso se revoca automaticamente; el sistema envia recordatorio 7 dias antes.

### 15.6 Productor con varios proyectos

- Pedro es `productor` en 3 proyectos de la Productora X. Todos cuentan para la cuota de proyectos del plan.
- Si la Productora X esta en Pro con limite de 3 proyectos, Pedro no puede crear un cuarto sin upgrade.
- El consumo de creditos de Pedro se carga a la organizacion, no al proyecto individual.
- Pedro puede tener dashboards distintos para cada proyecto; el panel de organizacion le da la vista agregada.

### 15.7 Beta convertida a SaaS publico

- Cliente beta esta en `private beta` con `beta_plan_key=studio` y `beta_end_date=2026-09-01`.
- Decide quedarse: contrata plan Studio publico.
- Migracion: el sistema actualiza `plan_key=studio`, limpia `is_beta` y `beta_end_date`, mantiene los datos y proyectos, recalcula la cuota de creditos.
- El cliente mantiene los creditos no consumidos; las bolsas beta se transforman en `purchased_balance` con su fecha de compra original.

### 15.8 Enterprise con contrato especial

- Cliente Enterprise tiene un contrato a medida: 5 modulos `enterprise_only` (`E`) que no son publicos.
- Los modulos se registran en `organization.custom_modules` con `availability=E` y `justification`.
- El backend los reconoce via override; el frontend los muestra solo a miembros con `audit.read` o `admin.organization`.
- Cualquier auditoria debe poder identificar que un modulo es custom y que organizacion lo tiene; esto queda en el evento `enterprise_override_applied`.

### 15.9 Modulo comprado como add-on

- Cliente Pro compra `production_mgmt` como add-on por 99 €/mes.
- El sistema activa el modulo con `availability=add_on_active`, `expires_at` segun ciclo de facturacion, y `auto_renew=true` (por defecto).
- Si el cliente cancela el add-on, el modulo pasa a `availability=add_on_cancelled` y al cierre del ciclo a `not_included` segun la matriz.
- El cliente no pierde datos generados durante el add-on; solo pierde acceso de escritura y nuevos jobs.

### 15.10 Downgrade de plan

- Cliente Studio baja a Pro.
- Efecto inmediato: el plan Pro aplica, los modulos `add_on` se mantienen hasta el cierre del ciclo, los modulos `not_included` en Pro pasan a `graced` durante 30 dias.
- En `graced`: los assets son visibles pero no editables; los jobs IA fallan; los exports se bloquean.
- El sistema avisa al cliente en T-7, T-1 y T-0 del periodo de gracia; al expirar, los modulos `graced` pasan a no disponibles y los datos se mueven a archivo frio.
- Excepcion: el `project_hub` y `ai_traceability` nunca se degradan; el cliente puede seguir leyendo historico.

### 15.11 Exceso de almacenamiento

- Cliente Pro usa 60 GB de 50 GB permitidos.
- Bloqueo: el sistema rechaza nuevas subidas con `507 Insufficient Storage`; los jobs IA que requieren assets fallan.
- Periodo de gracia: 7 dias para que el cliente libere espacio o upgrade. Pasado el periodo, el sistema no borra nada (no destructivo) pero no permite nuevas subidas.
- Opcion: contratar add-on de almacenamiento (cuando exista) o upgrade de plan.

### 15.12 Job IA en curso durante agotamiento de creditos

- Cliente Pro inicia un render de storyboard con `credit_estimate=60`. Saldo actual: 30.
- Backend rechaza la solicitud con `402 Payment Required`; el job no se inicia.
- Si el job ya esta en curso y el saldo se agota (por ejemplo, el cliente agota el saldo desde otra sesion), el job actual termina pero los siguientes fallan.
- Politica: no se cobra retroactivamente; el job en curso consume lo que reservo al inicio (reserva + cargo al final). Si el job falla por timeout, hace rollback.
- Audit: `ai_action_requested`, `credit_reserved`, `credit_charged` o `credit_rolled_back` quedan registrados con `actor_id` y `organization_id`.

## 16. Auditoria

10 eventos que el sistema deberia registrar cuando la matriz se implemente. Se anexan a los 28 del contrato SaaS (seccion 15 de `cid_saas_model_contract_v1.md`) y a los 9 de la matriz de roles/permisos (seccion 12 de `cid_roles_permissions_matrix_v1.md`).

| Evento | Cuando se registra | Campos clave |
|---|---|---|
| `plan_changed` | Un `organization_admin` cambia el plan de la suscripcion. | `actor_id`, `organization_id`, `old_plan`, `new_plan`, `pro_rata_amount`, `effective_at`. |
| `module_enabled` | Un modulo pasa a disponible (compra de add-on, upgrade, override). | `actor_id`, `organization_id`, `module_key`, `reason` (purchase / upgrade / override), `expires_at`. |
| `module_disabled` | Un modulo pasa a no disponible (cancelacion, downgrade, fin de override). | `actor_id`, `organization_id`, `module_key`, `reason`, `grace_period_end`. |
| `credit_package_purchased` | Un usuario compra una bolsa de creditos. | `actor_id`, `organization_id`, `package_key`, `credits`, `amount_eur`, `payment_id`. |
| `credit_exhausted` | El saldo de la organizacion llega a 0 (o por debajo del siguiente job). | `actor_id`, `organization_id`, `last_balance`, `last_action_blocked`. |
| `limit_reached` | Cualquier limite de plan (usuarios, proyectos, almacenamiento, exports, integraciones) se alcanza. | `actor_id`, `organization_id`, `limit_type`, `current_value`, `max_value`, `plan_key`. |
| `upgrade_prompt_shown` | El frontend muestra un mensaje de upgrade al usuario. | `actor_id`, `organization_id`, `trigger` (module_blocked / limit_reached / credit_exhausted), `shown_at`. |
| `export_blocked` | El backend rechaza un export por formato no disponible o cuota agotada. | `actor_id`, `organization_id`, `format`, `plan_key`, `reason`. |
| `api_access_denied` | El backend rechaza una llamada a la API publica por plan, rate limit o scope. | `actor_id`, `organization_id`, `endpoint`, `plan_key`, `reason` (plan / rate_limit / scope). |
| `enterprise_override_applied` | Se aplica un override Enterprise (modulo custom, permiso custom, quota custom). | `actor_id` (preferiblemente global_admin), `organization_id`, `override_type`, `justification`, `scope`. |

Reglas comunes:

- Append-only. Las correcciones se hacen con un evento `audit_event_corrected` que referencia al anterior.
- El log nunca expone secretos, claves de API, prompts crudos ni contenido de los inputs del cliente.
- El cliente puede descargar su propio log desde el panel de admin (`org_role=admin` o `org_role=billing`). Enterprise puede configurar retention mas larga.
- Los eventos `limit_reached` y `credit_exhausted` son senales comerciales: el sistema puede disparar un aviso al account manager o al equipo de ventas para outreach proactivo.

## 17. Roadmap tecnico derivado

Fases tecnicas futuras que aplican esta matriz. Se ejecutan en orden, cada una con su propio spec, implementacion backend/frontend y cierre de validacion.

1. **CID.SAAS.PLAN.GATES.BACKEND.1**: persistir la matriz de planes, quotas y overrides. Tablas `plan`, `plan_module_quota`, `plan_limit`, `organization_override`. Endpoints admin con `require_write_permission` + `admin.organization`. Test contract por router.
2. **CID.SAAS.MODULE.GATES.BACKEND.1**: extender `require_module_access` para que aplique las 5 estados (included, limited, add_on, not_included, enterprise_only) y la cuota del modulo. Migrar routers existentes. Test contract por modulo.
3. **CID.SAAS.CREDIT.GATES.BACKEND.1**: implementar `require_credit(credit_estimate)`. Tablas `credit_ledger`, `credit_reservation`, `credit_charge`, `credit_rollback`, `credit_purchase`. Middleware que rechaza con `402` si saldo insuficiente y registra eventos audit.
4. **CID.SAAS.FRONTEND.PLAN.VISIBILITY.1**: `/api/capabilities` que devuelve la matriz efectiva del usuario en el proyecto. Frontend consume y construye sidebar, botones, dashboards, mensajes de upgrade. Cache corto con invalidacion por cambio de plan/add-on/creditos/proyecto.
5. **CID.SAAS.BILLING.STRIPE.MODEL.1**: integracion con Stripe para suscripciones, add-ons, compra de creditos, prorrateo. Webhooks idempotentes. Sincronizacion entre Stripe y el ledger interno.
6. **CID.SAAS.ADMIN.BILLING.UI.1**: panel de admin para gestionar plan, modulos add-on, bolsas de creditos, historial de pagos, facturas. UI conectada a `/api/billing/*` con gating.
7. **CID.SAAS.USAGE.AUDIT.LOGS.1**: persistencia de los 10 eventos de la seccion 16. UI de admin para consultar y exportar. Alertas automaticas para `limit_reached` y `credit_exhausted`.

Fases de soporte (no bloqueantes, planificables en paralelo):

- **CID.SAAS.PRICING.CANONICALIZATION.1**: resolver la discrepancia entre pricing docs y `src/config/plans.yml`. Esta fase es prerequisito de `BILLING.STRIPE.MODEL.1`.
- **CID.SAAS.DEMO.CLIENT.1**: soporte explicito para el modo `demo client` con flag `is_demo=true`, limites enforzados sin plan, y conversion automatica a `private beta` o `public SaaS` trial Pro.
- **CID.SAAS.PRIVATE.BETA.1**: soporte para `is_beta=true`, `beta_end_date`, override de quotas y conversion a plan de pago.
- **CID.SAAS.ENTERPRISE.OVERRIDE.1**: soporte para `organization.custom_modules`, `custom_permissions`, `custom_quotas` con `enterprise_override_applied` en auditoria.
- **CID.SAAS.PLAN.GRACE.PERIOD.1**: implementar la maquina de estados de downgrade con periodo de gracia configurable por plan y modulo.

## 18. Criterio GO

Esta matriz v1 se considera **GO** para guiar las fases tecnicas futuras cuando se cumplen todos los puntos siguientes:

1. Crea unicamente `docs/architecture/cid_plans_modules_matrix_v1.md`. No modifica ningun otro archivo.
2. Es coherente con `cid_saas_model_contract_v1.md`:
   - 5 planes (Starter, Pro, Studio, Premium, Enterprise) con la misma nomenclatura y posicionamiento.
   - 22 roles no se contradicen; los modulos de esta matriz se mapean a los 19 del contrato SaaS en la seccion 5.2.
   - El modelo de creditos (incluidos + bolsas + reservado/cargado/rollback) es consistente.
3. Es coherente con `cid_roles_permissions_matrix_v1.md`:
   - Los 31 permisos base no se contradicen; la matriz de modulos por plan respeta la asignacion rol x modulo.
   - Los 8 roles especiales (organization_owner, organization_admin, project_admin, billing_admin, external_reviewer, global_admin, service_account, ai_worker) mantienen su scope.
4. No modifica codigo fuente (`src/`, `src_frontend/`, `tests/`, `scripts/`, `alembic/`).
5. No modifica backend (no se cambia el gating cerrado, no se introducen endpoints, no se modifican routers).
6. No modifica frontend (no se cambian componentes, paginas, contextos, ni se introduce `/api/capabilities` todavia).
7. No modifica `.env`, `backups/`, `*.db`, Docker, compose.
8. `git diff --check` pasa sin warnings ni errores.
9. `bash scripts/dev/guard_wsl_repo.sh` pasa los 8 checks (PWD WSL, sin Windows path, sin copia anidada, sin `.env` staged, sin `*.db` staged, sin JSON sensible staged, sin secretos en policy dirs).
10. `git status --short --untracked-files=all` muestra unicamente `?? docs/architecture/cid_plans_modules_matrix_v1.md`.

Cuando todos estos puntos se cumplen, la matriz sirve como base contractual y documental para:

- Disenar `CID.SAAS.PLAN.GATES.BACKEND.1` y `CID.SAAS.MODULE.GATES.BACKEND.1`.
- Disenar `/api/capabilities` y la UI de plan/creditos/add-ons.
- Iniciar la canonicalizacion de pricing (prerequisito de Stripe).

La matriz no implementa nada. Es un GO de diseno, suficiente para que las fases 1-3 del roadmap arranquen con un modelo de planes, modulos, creditos y limites estable, sin tener que revisarlo en cada sprint.

## 19. Estilo y forma

- Documento tecnico en Markdown.
- Espanol claro, conciso, sin marketing.
- Tablas operativas siempre que se compare mas de dos elementos.
- Codigos en backticks para `module_key`, `plan_key`, `role_key`, `permission_key`.
- Diagramas solo cuando aportan (no ASCII art decorativo).
- Sin emojis (regla de estilo del repo).
- Sin `code blocks` de marketing (no se incluyen "testimonios", "ventajas competitivas", ni "casos de exito").
- Cada seccion tiene titulo, cuerpo y, si aplica, tabla o lista.
- Las referencias a companeros (contrato SaaS, matriz de roles, gating backend) son siempre con ruta relativa al archivo.
- Los numeros economicos son orientativos; la canonicalizacion final se hara en `CID.SAAS.PRICING.CANONICALIZATION.1`.
