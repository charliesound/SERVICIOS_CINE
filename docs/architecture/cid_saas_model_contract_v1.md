# CID SaaS Model Contract v1

Version: 1.0
Status: SPEC (documental, no implementation)
Date: 2026-06-05
Owners: CID Architecture / CID Product
Scope: AILinkCinema CID SaaS product (authenticated app, plan-gated, multitenancy-aware).
Companion docs:
- `docs/architecture/backend_gating_contract_v1.md` (P0/P1 closure, 8 router patterns, 8 P2 manual-review entries)
- `docs/architecture/cid_landing_vs_cid_saas_boundary_v1.md` (CID vs AILinkCinema landing boundary)
- `docs/architecture/sound_ingest_field_recorders_spec_v1.md` (sound_ingest module reference)
- `docs/business/cid_pricing_canonicalization_needed_v1.md` (pricing discrepancy doc vs code)
- `docs/business/cid_pricing_competitive_baseline_v1.md` (competitive pricing baseline)
- `docs/business/cid_credits_business_model_v1.md` (credit cost examples)

## 1. Resumen ejecutivo

CID es un SaaS de producción audiovisual asistido por IA. La unidad de venta no es la herramienta: es el resultado de producción entregable (guion analizado, biblia de personaje, storyboard, presupuesto, plan de rodaje, paquete de delivery, etc.).

Este contrato define el modelo de datos y de negocio que el producto expone hacia el cliente, hacia el backend y hacia el frontend. Es la fuente de verdad documental para:

- Cómo se organiza un cliente (organización, proyectos, miembros, roles).
- Qué puede hacer cada persona (permisos derivados del rol y del plan).
- Qué módulos están disponibles en cada plan (matriz módulos x plan).
- Cómo se cobra el uso de IA (créditos reservados, consumidos, auditables, con rollback).
- Qué límites aplica el sistema (por organización, plan, proyecto, usuario, módulo, job concurrente).
- Cómo se muestra, bloquea y desbloquea el acceso en frontend y backend (relación con el contrato de gating).
- Qué se audita y qué eventos son canónicos.

El contrato no implementa nada. Define la forma que tendrán la implementación de backend, el modelo de datos y la UX de frontend cuando lleguen las fases de `CID.SAAS.ROLES.PERMISSIONS.MATRIX.1`, `CID.SAAS.PLANS.MODULES.MATRIX.1` y sucesivas (ver roadmap en sección 16).

Regla de oro: **el cliente nunca compra tecnología, compra resultados**. Lo que aparece en pantalla, en factura y en soporte es el resultado entregable, no el modelo de IA que lo generó.

## 2. Principios del modelo SaaS

CID modela diez entidades canónicas. Toda decisión de producto, pricing, gating y auditoría se reduce a cómo se combinan estas diez.

1. **Organización (`organization_id`)**: cliente contractual. Posee billing, planes, créditos, miembros y proyectos. Es el tenant del multitenancy.
2. **Proyecto (`project_id`)**: unidad de producción dentro de una organización. Un cortometraje, una serie, un anuncio, un reel. Tiene su propio equipo, su propio crédito reservado y su propio historial.
3. **Usuario (`user_id`)**: identidad global, autentica contra CID. Pertenece a una o varias organizaciones mediante membresía. No existe usuario sin organización.
4. **Rol (`role_key`)**: función dentro de un proyecto o de la organización (Productor, Director, Sonidista, Cliente externo, Admin). Define permisos por defecto.
5. **Permiso (`permission_key`)**: acción atómica autorizada, en notación `domain.action` (por ejemplo, `project.read`, `ai.run`, `billing.manage`). Es lo que el backend enforza y lo que el frontend oculta cuando no aplica.
6. **Plan (`plan_key`)**: nivel comercial contratado (Starter, Pro, Studio, Premium, Enterprise). Determina módulos incluidos, límites y créditos mensuales.
7. **Módulo (`module_key`)**: capacidad de producto (storyboard_ai, concept_art, sound_ingest, delivery, etc.). Disponible, limitado, add-on o no incluido según plan.
8. **Crédito (`credit_balance`)**: unidad de cobro del uso de IA y de operaciones pesadas. Se compra, se incluye, se reserva, se consume, se rollbacka. Es la moneda interna auditable.
9. **Job (`job_id`)**: ejecución de una acción costosa o asíncrona (render de storyboard, transcripción, análisis de guion, generación de pitch). Tiene estado, trazas y cargo de crédito asociado.
10. **Asset/Documento (`asset_id`, `document_id`)**: el resultado entregable. Un storyboard renderizado, un PDF de presupuesto, un EDL, un master ProRes, una biblia de personaje, un paquete de delivery. Es lo que el cliente ve, descarga y firma.

Reglas derivadas:

- **Una organización, muchos proyectos.** Un usuario, muchas membresías. Un proyecto, muchos roles, un cargo de producción a la vez por rol principal.
- **Un plan, una matriz.** Lo que el plan no incluye, no se puede activar ni comprar suelto (salvo add-on explícito o upgrade a Enterprise).
- **Un crédito, un evento.** Cada cargo de crédito está asociado a un `job_id` y un `asset_id`. Sin job no hay cargo.
- **Un permiso, una decisión.** El backend decide; el frontend nunca debe mostrar lo que el backend denegaría.
- **Una auditoría, un evento inmutable.** Los eventos no se borran ni se reescriben; se anexan.

## 3. Modelo de organizaciones

La organización es el tenant. Representa al cliente contractual: una productora, una agencia, un equipo freelance consolidado, una escuela, un broadcaster, una marca.

**Identidad:**

- `organization_id` (UUID, inmutable).
- `legal_name` (razón social o nombre comercial).
- `slug` (subdominio futuro, por ejemplo `acme.cid.app`).
- `country`, `tax_id`, `billing_email` (datos de factura).
- `created_at`, `suspended_at` (estado).

**Tenancy y aislamiento:**

- Todo recurso (proyecto, usuario, asset, job, evento) lleva `organization_id`.
- El backend filtra por `organization_id` en toda consulta (defensa en profundidad, además del gating por plan y por rol).
- Ningún job, asset, evento o crédito cruza organizaciones. Las excepciones (admin global, soporte nivel 3, migración manual) requieren flag explícito y quedan registradas en auditoría.

**Membresía:**

- Una organización tiene N miembros (`user_id` + `org_role`).
- `org_role` puede ser `owner`, `admin`, `member`, `billing`.
- `owner`: máxima autoridad, transfiere propiedad, no eliminable mientras sea único.
- `admin`: gestión de miembros, planes, módulos add-on, facturación.
- `billing`: solo ve y gestiona suscripción y facturas, no producción.
- `member`: usuario regular con rol de proyecto, no administra la organización.

**Proyectos:**

- Una organización tiene M proyectos. Cada proyecto tiene `project_id`, `name`, `type` (largometraje, cortometraje, serie, anuncio, videoclip, branded, doc, otro), `status` (pre-producción, producción, postproducción, delivery, archivado) y `lead_user_id` (responsable principal, normalmente el productor del proyecto).

**Límites a nivel de organización (los concreta el plan):**

- Número máximo de proyectos activos.
- Número máximo de miembros.
- Almacenamiento total en GB.
- Créditos mensuales incluidos.
- Número de integraciones externas activas (n8n, Slack, Drive, Frame.io, etc.).

**Facturación:**

- La organización es el sujeto de facturación. Un cliente puede tener varias organizaciones si gestiona entidades legales separadas, pero cada una se factura aparte.
- Cambios de plan se aplican a nivel organización. Pro cuota si el cambio es a mitad de ciclo, con redondeo al día.

**Desactivación y baja:**

- `suspended_at` bloquea acceso de todos los miembros pero conserva datos durante el periodo legal.
- `deleted_at` mueve a archivo frío tras el periodo legal; los datos siguen exportables bajo solicitud mientras no se purguen físicamente.

## 4. Modelo de usuarios

El usuario es identidad global. Una persona puede pertenecer a varias organizaciones (productor que trabaja para dos productoras; freelancer; inversor que mira dos productoras; admin de plataforma).

**Identidad:**

- `user_id` (UUID, inmutable).
- `email` (único, validado, sirve de login).
- `full_name`, `display_name`, `avatar_url`.
- `auth_provider` (email+password, OAuth Google, OAuth Microsoft, magic link; el sistema soporta varios, no obliga a uno).
- `status` (`active`, `invited`, `suspended`, `deactivated`).
- `created_at`, `last_login_at`, `deactivated_at`.

**Membresía:**

- Un usuario tiene 0..N membresías activas. Una membresía es `(user_id, organization_id, org_role, joined_at)`.
- Si un usuario no tiene membresía activa, no puede entrar al producto. La pantalla de login lo redirige a una pantalla de "no perteneces a ninguna organización" con CTA a crear organización o a esperar invitación.

**Tipos de usuario (subtipos a efectos de UX y permisos):**

- **Interno del equipo de producción**: pertenece a la productora, tiene rol de proyecto, trabaja a diario. Caso por defecto.
- **Cliente externo / Brand owner**: pertenece a la organización cliente del proyecto, no produce, solo revisa y aprueba. Permisos limitados a `project.read` en proyectos donde está invitado, `feedback.write` y `approval.write`.
- **Invitado / Revisor externo**: usuario externo a la organización, invitado a un proyecto concreto, sin acceso al resto. Permisos solo sobre el proyecto invitado. Caso típico: un director invitado, un consultor, un评委, un actor top que revisa su biblia.
- **Global admin (plataforma)**: usuario de CID staff con permisos de soporte nivel 3. Accede a cualquier organización solo mediante flag `support_session=true`, con justificación obligatoria, y la sesión queda registrada en auditoría con scope explícito.

**Roles dentro del producto vs roles de proyecto:**

- `org_role` (owner/admin/member/billing) gobierna la organización.
- `project_role` (los 22 roles definidos en la sección 5) gobierna un proyecto concreto.
- Un mismo usuario puede tener `org_role=admin` y `project_role=Productor` en el proyecto A, y `org_role=member` y `project_role=Director` en el proyecto B. Esto es válido y debe soportarlo el modelo.

**Desactivación:**

- Un usuario `deactivated` no puede autenticarse. Sus assets y créditos quedan asignados a la organización, no se borran. Un admin puede reactivar (re-asignando a una membresía) pero no reutilizar el `user_id` (es inmutable, un usuario desactivado lo es para siempre; se crea uno nuevo si vuelve).

**Trazabilidad:**

- Toda acción registra `user_id`, `organization_id` y, si aplica, `project_id`. Esto es lo que permite auditoría forense, facturación y soporte.

## 5. Roles reales de producción audiovisual

CID modela 22 roles de proyecto. Cada rol tiene propósito, módulos donde opera, permisos por defecto y restricciones. Los roles derivan del flujo real de producción, no de la jerga técnica de SaaS.

Convención: `(*)` indica que el rol es típicamente también `org_role=admin` o `org_role=owner`. El resto son `org_role=member` salvo cuando el rol es externo.

| # | `role_key` | Propósito | Módulos donde opera | Permisos por defecto | Restricciones |
|---|---|---|---|---|---|
| 1 | `productor` (*) | Responsable de viabilidad, presupuesto, financiación, entrega. Decide. | Todos los de gestión, financiación, presupuesto, delivery. | `project.read`, `project.write`, `ai.run`, `credits.view`, `credits.purchase`, `team.invite`, `export.generate`, `delivery.publish`. | No edita arte visual directamente. |
| 2 | `productor_ejecutivo` (*) | Supervisa múltiples proyectos, alineación estratégica. | Todos en modo lectura, presupuesto y financiación en escritura. | `project.read`, `budget.write`, `funding.write`, `export.generate`. | No ejecuta IA pesada. |
| 3 | `jefe_produccion` | Ejecuta el plan de producción día a día, coordina equipos. | `shooting_plan`, `shotlist`, `budget`, `project_memory`. | `project.read`, `project.write`, `ai.run`, `export.generate`. | No edita guion. |
| 4 | `director` (*) | Responsable creativo principal. Aprueba tratamiento y montaje. | `script_analysis`, `storyboard_ai`, `concept_art`, `shooting_plan`, `client_feedback`. | `project.read`, `project.write`, `ai.run`, `feedback.write`, `approval.write`. | No edita presupuesto. |
| 5 | `ayudante_direccion` | Apoya al director, lleva la agenda, distribuye llamadas. | `script_analysis`, `shooting_plan`, `shotlist`. | `project.read`, `project.write`, `ai.run`. | No aprueba. |
| 6 | `script_continuidad` | Garantiza raccord y consistencia entre planos. | `script_analysis`, `character_bible`, `shotlist`, `project_memory`. | `project.read`, `project.write`, `ai.run`. | No edita storyboard final. |
| 7 | `direccion_fotografia` | Define look, lente, luz. Dirige cámara. | `concept_art`, `storyboard_ai`, `shooting_plan`, `shotlist`, `shotlist_camera`. | `project.read`, `project.write`, `ai.run`, `export.generate`. | No edita guion. |
| 8 | `camara` | Opera cámara. No decide plano. | `shotlist`, `shotlist_camera`. | `project.read`, `project.write`. | No ejecuta IA. |
| 9 | `dit_data_wrangler` | Ingesta, organiza y respalda material en set. | `shotlist`, `integrations_drive`, `project_memory`. | `project.read`, `project.write`, `asset.upload`, `export.generate`. | No edita guion ni storyboard. |
| 10 | `sonido_directo` | Captura audio en set. Es autoridad sobre la calidad sonora original. | `sound_ingest`, `shooting_plan`, `shotlist`. | `project.read`, `project.write`, `asset.upload`, `ai.run` (solo módulos de audio). | No edita visual. |
| 11 | `direccion_arte` | Define y ejecuta diseño de producción. | `concept_art`, `character_bible`, `shotlist`. | `project.read`, `project.write`, `ai.run`, `export.generate`. | No edita guion. |
| 12 | `vestuario` | Diseño y ejecución de vestuario. | `character_bible`, `concept_art`. | `project.read`, `project.write`, `ai.run`. | No edita presupuesto. |
| 13 | `maquillaje_peluqueria` | Diseño y ejecución de maquillaje y peluquería. | `character_bible`, `concept_art`. | `project.read`, `project.write`, `ai.run`. | No edita presupuesto. |
| 14 | `casting` | Selección de elenco. | `character_bible`, `producer_pitch`. | `project.read`, `project.write`, `ai.run`. | No edita storyboard. |
| 15 | `montaje` | Edición narrativa. | `script_analysis`, `shotlist`, `project_memory`. | `project.read`, `project.write`, `ai.run`, `export.generate`. | No edita presupuesto. |
| 16 | `postproduccion_sonido` | Diseño sonoro, mezcla, edición de diálogo, Foley. | `sound_ingest`, `project_memory`. | `project.read`, `project.write`, `asset.upload`, `ai.run` (módulos de audio), `export.generate`. | No edita visual. |
| 17 | `vfx` | Efectos visuales, composición, simulaciones. | `storyboard_ai`, `concept_art`, `shotlist`. | `project.read`, `project.write`, `ai.run`, `export.generate`. | No edita guion narrativo. |
| 18 | `color` | Etalonaje y dirección de color. | `shotlist`, `export.generate`. | `project.read`, `project.write`, `ai.run`, `export.generate`. | No edita guion. |
| 19 | `delivery` | Entrega técnica: masters, QC, deliverables por plataforma. | `delivery`, `distribution_pack`. | `project.read`, `export.generate`, `delivery.publish`. | No edita producción. |
| 20 | `distribucion_ventas` | Comercialización, festivales, ventas internacionales, agentes. | `producer_pitch`, `distribution_pack`, `funding`. | `project.read`, `export.generate`, `delivery.publish`. | No edita contenido creativo. |
| 21 | `cliente_externo` | Marca o cliente final. Solo revisa y aprueba. | `client_feedback`, `producer_pitch`, `delivery` (en modo preview). | `project.read` (solo donde invitado), `feedback.write`, `approval.write`. | No edita nada. No ve costos internos. |
| 22 | `revisor_invitado` | Consultor,评委,评委,评委,评委 externo, actor top invitado. Acceso a un solo proyecto. | Igual que `cliente_externo` pero acotado a un proyecto puntual. | `project.read` (un solo proyecto), `feedback.write` (opcional). | Sin acceso a créditos, sin acceso a otros proyectos. |

**Notas de aplicación:**

- Un usuario puede acumular varios `project_role` en el mismo proyecto (por ejemplo, `director` y `montaje` en una pieza personal). El sistema permite asignar múltiples roles por usuario-proyecto; los permisos son la unión.
- `cliente_externo` y `revisor_invitado` **nunca** ven precios internos, márgenes, créditos consumidos ni datos de billing.
- Los roles marcados `(*)` suelen coincidir con `org_role=admin`, pero no es obligatorio (una productora de un solo socio puede tener al dueño como `productor` y a la vez `org_role=owner`).
- El sistema puede proponer roles automáticamente al invitar miembros según el `email` y el dominio (heurística, no verdad legal), pero la asignación final siempre la confirma un `admin` o `owner`.

## 6. Permisos base

Los permisos son atómicos, en notación `domain.action`, en snake_case, y constituyen la única interfaz que el backend enforza para decidir si una acción procede. Cualquier acción nueva del producto requiere un permiso nuevo o la reutilización de uno existente.

Lista canónica de permisos base (25):

| Permiso | Significado |
|---|---|
| `project.read` | Ver metadatos y assets de un proyecto. |
| `project.write` | Editar metadatos del proyecto (nombre, tipo, estado, lead). |
| `project.delete` | Archivar o eliminar un proyecto. |
| `project.archive` | Mover un proyecto a estado archivado. |
| `team.invite` | Invitar miembros a la organización o al proyecto. |
| `team.remove` | Quitar miembros. |
| `team.role.assign` | Cambiar roles de proyecto a un miembro. |
| `script.read` | Ver guion y sus análisis. |
| `script.write` | Editar guion. |
| `script.analyze` | Lanzar análisis IA del guion. |
| `storyboard.create` | Crear hoja de storyboard. |
| `storyboard.render` | Renderizar storyboard con IA. |
| `concept_art.create` | Crear lámina de concept art. |
| `concept_art.render` | Renderizar concept art con IA. |
| `character_bible.write` | Editar biblia de personaje. |
| `budget.read` | Ver presupuesto. |
| `budget.write` | Editar presupuesto. |
| `shooting_plan.write` | Editar plan de rodaje. |
| `shotlist.write` | Editar shotlist. |
| `funding.write` | Editar solicitudes de financiación y materiales de pitch. |
| `pitch.generate` | Generar material de pitch (deck, one-pager). |
| `sound.upload` | Subir audio a `sound_ingest`. |
| `sound.process` | Procesar/etiquetar audio con IA. |
| `delivery.publish` | Publicar entregable a cliente o plataforma. |
| `export.generate` | Exportar PDF, EDL, AAF, paquete de delivery, etc. |
| `ai.run` | Permiso paraguas para ejecutar cualquier job de IA. Se evalúa junto al permiso específico del módulo (por ejemplo, `storyboard.render` + `ai.run`). |
| `credits.view` | Ver saldo y consumo de créditos. |
| `credits.purchase` | Comprar paquete de créditos adicional. |
| `billing.manage` | Cambiar plan, gestionar método de pago, descargar facturas. |
| `admin.organization` | Configuración general de la organización (logos, dominios, SSO). |
| `admin.platform` | Permiso exclusivo de staff CID. No asignable a clientes. |

**Reglas de aplicación:**

- El backend siempre enforza permisos. Frontend los usa solo para esconder UI, no como única defensa.
- `admin.organization` y `admin.platform` nunca se delegan a `cliente_externo` ni `revisor_invitado`.
- `billing.manage` y `credits.purchase` son de la organización, no del proyecto. Solo org-roles `owner`, `admin` y `billing` los tienen.
- Un permiso nuevo no se añade por producto: se añade por contrato y queda versionado en este documento antes de implementarse.

## 7. Planes comerciales

CID ofrece 5 planes comerciales. Los precios y cuotas se alinean con `docs/business/cid_pricing_competitive_baseline_v1.md` y se documentan aquí como contrato; la canonicalización final frente a `src/config/plans.yml` se trata en la sección 17 (Riesgos) y en `cid_pricing_canonicalization_needed_v1.md`.

| Plan | Precio mensual | Usuarios incluidos | Proyectos activos | Almacenamiento | Créditos IA/mes | Módulos core | Add-ons permitidos | Upsell natural |
|---|---|---|---|---|---|---|---|---|
| **Starter** | 99 €/mes | 3 | 1 | 50 GB | 2.000 | `script_analysis`, `project_memory`, `budget`, `client_feedback`. | `storyboard_ai`, `concept_art`, `character_bible` (limitado). | Pro. |
| **Pro** | 299 €/mes | 10 | 5 | 250 GB | 10.000 | Todo Starter + `storyboard_ai`, `concept_art`, `character_bible`, `shotlist`, `shooting_plan`, `funding`, `producer_pitch`. | `sound_ingest`, `delivery`, `distribution_pack`, `ai_pipeline_builder`. | Studio. |
| **Studio** | 799 €/mes | 25 | 20 | 1 TB | 40.000 | Todo Pro + `sound_ingest`, `delivery`, `distribution_pack`, `client_feedback` avanzado. | `integrations_n8n`, `advanced_exports`, `ai_pipeline_builder` extendido. | Premium. |
| **Premium** | 1.490 €/mes | 60 | 60 | 5 TB | 150.000 | Todo Studio + `ai_pipeline_builder`, `integrations_n8n`, `advanced_exports`, `admin_analytics`. | SSO, audit logs extendidos, soporte prioritario. | Enterprise. |
| **Enterprise** | desde 3.500 €/mes (custom) | Ilimitado | Ilimitado | Custom | Custom (pool mensual negociado) | Todos los módulos. | Custom: SSO, SAML, on-premise opcional, soporte 24/7, account manager, integraciones a medida. | Negocio a negocio. |

**Notas comerciales:**

- **Trial**: 14 días con Pro activado, requiere tarjeta, cancela sin cargo. No se factura hasta el día 15.
- **Anual**: 2 meses bonificados al pagar anual (efectivo, no prorrateado en factura). Disponible en Starter, Pro, Studio y Premium.
- **Cambio de plan**: pro rata al día, con efecto inmediato. Si es downgrade, los activos超出 del nuevo plan quedan en modo solo-lectura durante 30 días (periodo de gracia) mientras el cliente decide qué migrar o archivar.
- **Add-ons**: se contratan aparte, tienen precio aparte, requieren plan mínimo (lo indica la matriz). Add-on sin plan compatible no se puede activar.
- **Educación / sin ánimo de lucro**: descuento del 50% sobre Pro y Studio, sujeto a verificación. No se ofrece Starter bonificado.

## 8. Matriz modulos x plan

Esta es la matriz canónica módulo x plan. Valores posibles: `incluido` (I), `limitado` (L), `add-on` (A), `no incluido` (N), `enterprise` (E). Los límites cuantitativos de los `L` se indican en la columna de notas.

19 módulos:

1. `script_analysis`
2. `project_memory`
3. `storyboard_ai`
4. `concept_art`
5. `character_bible`
6. `budget`
7. `shooting_plan`
8. `shotlist`
9. `funding`
10. `producer_pitch`
11. `delivery`
12. `distribution_pack`
13. `sound_ingest`
14. `client_feedback`
15. `crm_sales`
16. `ai_pipeline_builder`
17. `integrations_n8n`
18. `advanced_exports`
19. `admin_analytics`

| Módulo | Starter | Pro | Studio | Premium | Enterprise |
|---|---|---|---|---|---|
| `script_analysis` | I | I | I | I | I |
| `project_memory` | I | I | I | I | I |
| `storyboard_ai` | A (L: 20 hojas/mes) | I (L: 100 hojas/mes) | I (L: 500/mes) | I (L: 2.000/mes) | I (custom) |
| `concept_art` | A (L: 10 láminas/mes) | I (L: 50/mes) | I (L: 200/mes) | I (L: 800/mes) | I (custom) |
| `character_bible` | A (L: 3 biblias/mes) | I (L: 15/mes) | I (L: 60/mes) | I (L: 250/mes) | I (custom) |
| `budget` | I | I | I | I | I |
| `shooting_plan` | N | I | I | I | I |
| `shotlist` | N | I | I | I | I |
| `funding` | N | I (L: 5 pitches/mes) | I (L: 25/mes) | I (L: 100/mes) | I (custom) |
| `producer_pitch` | N | I | I | I | I |
| `delivery` | N | A | I (L: 50 entregas/mes) | I (L: 200/mes) | I (custom) |
| `distribution_pack` | N | A | I (L: 20 packs/mes) | I (L: 100/mes) | I (custom) |
| `sound_ingest` | N | A (L: 50 GB ingestados/mes) | I (L: 250 GB/mes) | I (L: 1 TB/mes) | I (custom) |
| `client_feedback` | I (L: 2 proyectos) | I (L: 5 proyectos) | I (L: 20 proyectos) | I (L: 60 proyectos) | I (custom) |
| `crm_sales` | N | N | A | I | I |
| `ai_pipeline_builder` | N | A | A | I | I |
| `integrations_n8n` | N | A | A | I | I |
| `advanced_exports` | N | A | A | I | I |
| `admin_analytics` | N | N | A | I | I |

**Reglas:**

- `I` con `L:` significa incluido con cuota; superado el límite, se requiere comprar créditos adicionales o subir de plan.
- `A` significa que el módulo no está incluido en el plan base; se contrata aparte con su precio de add-on.
- `N` significa no disponible; no se puede activar ni comprar como add-on; hay que cambiar de plan.
- `E` (no usado arriba; reservado) significaría exclusivo Enterprise, con SSO y soporte dedicado.

## 9. Modelo de creditos

El crédito es la unidad interna de cobro por uso de IA y por operaciones pesadas. Es independiente del precio del plan: un plan incluye una cuota mensual y el cliente puede comprar paquetes adicionales.

**Entidad de saldo (a nivel organización):**

- `credit_balance`: saldo disponible en un instante. No es un número entero estático: se calcula como `included_monthly_remaining + purchased_balance + adjustment_credits - reserved_active - consumed_period`.
- `included_monthly_remaining`: créditos del plan del mes en curso, no consumidos aún. Se resetean al cierre del ciclo, no rollover por defecto (ver excepciones).
- `purchased_balance`: créditos comprados como add-on, no consumidos. Tienen caducidad (ver expiration).
- `adjustment_credits`: regalados por soporte (compensaciones, promos, errores de plataforma). Auditable.
- `reserved_active`: créditos bloqueados por jobs en curso, no consumidos todavía.
- `consumed_period`: créditos ya consumidos en el mes en curso (informativo).

**Estados de un crédito:**

1. **Disponible**: parte de `included_monthly_remaining` o `purchased_balance`. Puede reservarse.
2. **Reservado**: bloqueado para un job en curso. Si el job falla, se libera. Si el job termina, pasa a consumido.
3. **Consumido**: ya gastado, no se recupera salvo rollback explícito.
4. **Caducado**: parte de `purchased_balance` o `included_monthly_remaining` (en planes sin rollover) que llegó a su fecha de expiración.

**Reserva, cargo y rollback (flujo obligatorio):**

1. Usuario lanza una acción de IA. Backend estima `credit_estimate` con base en la tabla de coste por acción.
2. Backend verifica saldo `>= credit_estimate`. Si no, rechaza con `402 Payment Required` y mensaje accionable (ver sección 13).
3. Backend reserva el crédito: `reserved_active += credit_estimate`, registra `credit_reservation_id`.
4. Job se ejecuta.
5. Si el job termina OK, backend convierte reserva en consumo: `reserved_active -= credit_estimate`, `consumed_period += credit_estimate`, registra `credit_charge_id`.
6. Si el job falla por error recuperable (timeout, error de proveedor, validación), backend hace rollback: `reserved_active -= credit_estimate`, registra `credit_rollback_id` con motivo.
7. Si el job falla por error del usuario (input inválido, cancelación), se consume la reserva íntegramente (política de no-spam).

**Tabla de coste por acción (referencia; valores orientativos a confirmar en `CID.SAAS.CREDITS.USAGE.MODEL.1`):**

| Acción | Coste (créditos) | Notas |
|---|---|---|
| Análisis de guion (hasta 30 págs) | 20 | `script.analyze` |
| Análisis de guion (30-90 págs) | 50 | |
| Análisis de guion (>90 págs) | 100 | |
| Hoja de storyboard (estándar) | 30 | `storyboard.render` |
| Hoja de storyboard (alta calidad) | 60 | flag alta calidad |
| Lámina de concept art (estándar) | 40 | `concept_art.render` |
| Lámina de concept art (alta calidad) | 90 | |
| Entrada de biblia de personaje | 25 | `character_bible.write` |
| Generación de presupuesto base | 40 | |
| Plan de rodaje (semanal) | 30 | |
| Shotlist (100 planos) | 25 | |
| Generación de pitch (deck) | 80 | `pitch.generate` |
| Ingesta de audio (por hora) | 15 | `sound_ingest` |
| Transcripción de audio (por hora) | 25 | |
| Generación de paquete de delivery | 60 | `delivery.publish` |
| Distribución pack | 40 | `distribution_pack` |
| Export avanzado (EDL/AAF/ProRes) | 20 | `export.generate` |

**Expiración y rollover:**

- Créditos `included_monthly_remaining`: no hacen rollover por defecto. Excepciones: planes Enterprise (negociados), o promos explícitas con fecha.
- Créditos `purchased_balance`: caducan a los 12 meses desde la compra. CID avisa 30, 15 y 1 días antes.
- `adjustment_credits`: no caducan mientras la organización esté activa, salvo que se indique lo contrario en el motivo.

**Visualización para el cliente:**

- Widget de créditos en el topbar: saldo actual, próximo reset, tendencia del mes.
- El cliente externo y el revisor invitado **nunca** ven créditos.
- El productor y el admin ven consumo por módulo, por proyecto y por miembro.

## 10. Consumo IA y trazabilidad

Toda ejecución de IA registra un job con los campos siguientes. Sin estos campos, el job no se considera auditable y no debería poder ejecutarse en producción.

**Campos obligatorios de un job (`job_id`):**

- `job_id` (UUID).
- `organization_id`, `project_id`, `user_id` (multi-tenancy y trazabilidad).
- `module_key` (por ejemplo, `storyboard_ai`).
- `permission_key_used` (permiso específico que se evaluó, por ejemplo `storyboard.render`).
- `action_type` (estandarizado, por ejemplo `render_storyboard_sheet`).
- `provider` (motor IA ejecutado: `ollama`, `openai`, `anthropic`, `gemini`, `comfyui`, `n8n`, `flowise`, `mock`).
- `model` (modelo concreto, por ejemplo `gpt-4o`, `claude-sonnet-4-6`, `gemini-2.5-pro`, `comfyui:flux1-dev-fp8`).
- `input_hash` (SHA-256 del input normalizado; permite reproducir el job sin guardar el input crudo cuando no aplica por privacidad).
- `input_summary` (texto o metadatos no sensibles, por ejemplo "guion 78 págs, idioma es-ES").
- `output_asset_id` o `output_document_id` (referencia al entregable generado).
- `prompt_version` (versión del prompt usado, registrado en un catálogo versionado).
- `parameters` (parámetros del job, jsonb: temperatura, semilla, tamaño, etc.).
- `credit_estimate` (créditos reservados al inicio).
- `credits_charged` (créditos consumidos al final; igual a `credit_estimate` salvo overrides).
- `status` (`queued`, `running`, `succeeded`, `failed`, `cancelled`).
- `error_code`, `error_message` (si aplica).
- `created_at`, `started_at`, `completed_at`.
- `duration_ms`.
- `parent_job_id` (para jobs encadenados, por ejemplo, un `shotlist.generate` que dispara varios `storyboard.render` hijos).
- `trace_id` (id de correlación para logs distribuidos).

**Reglas:**

- `input_hash` es obligatorio. No guardar el input crudo si contiene guion confidencial del cliente, pero sí guardar el hash para reproducir y para detectar re-trabajos.
- `output_asset_id` debe existir antes de marcar el job como `succeeded`. No cerrar un job exitoso sin asset.
- `prompt_version` debe corresponder a un prompt registrado en el catálogo. No se permite ejecutar un prompt no versionado.
- `provider` y `model` los elige el sistema según configuración del plan y disponibilidad, no el usuario final. El usuario solo ve el resultado.
- `credits_charged` se escribe una sola vez, al cierre del job. Cualquier ajuste posterior se hace mediante un evento de auditoría `credit_adjustment` (no se sobreescribe el cargo original).

**Trazabilidad visible al cliente:**

- En la ficha del asset generado, el cliente ve: módulo, fecha, autor (nombre del usuario), coste estimado en créditos y, si el plan lo permite, motor y modelo.
- El cliente externo y el revisor invitado ven: módulo, fecha, autor, coste en créditos **oculto por defecto**, motor y modelo **oculto por defecto**.
- En Enterprise, el admin puede activar visibilidad de motor/modelo para auditorías internas.

## 11. Motores IA

CID orquesta motores IA heterogéneos. El cliente no ve cuál se usó: ve el resultado. El sistema elige el motor en función de:

- Tipo de acción (texto, imagen, audio, multimodal).
- Configuración del plan (motor por defecto, motores permitidos, motores premium).
- Disponibilidad y coste (caída del proveedor, presupuesto agotado, latencia).
- Política de datos (residencia, no envío a terceros, modo local obligatorio).

**Motores soportados (v1):**

- **Ollama (default)**: motor local, por defecto en Starter, Pro y Studio. Modelos Llama, Qwen, Mistral y otros open-weight. Coste en créditos bajo, sin envío de datos a terceros.
- **OpenAI**: motor opcional, disponible en planes Pro, Studio, Premium, Enterprise. Modelos GPT-4o, GPT-4.1, o1, etc. Coste mayor en créditos.
- **Anthropic**: motor opcional, disponible en Pro+. Modelos Claude Sonnet, Opus. Coste mayor.
- **Gemini**: motor opcional, disponible en Pro+. Modelos Gemini 2.5 Pro, Flash. Coste mayor.
- **ComfyUI**: motor de imagen y video, usado por `storyboard_ai`, `concept_art`, `character_bible`. Local por defecto, opcionalmente en servidor dedicado Enterprise. Sin API pública de pago, pero consume GPU y por tanto créditos.
- **n8n / Flowise**: orquestadores de pipelines. No son motores en sí, pero ejecutan jobs compuestos. Disponibles en Studio, Premium y Enterprise (o como add-on).

**Reglas de selección y aislamiento:**

- El cliente no elige motor. El sistema lo hace con base en la configuración.
- Los planes tienen `default_provider` y `allowed_providers`. Por ejemplo, Starter tiene `default_provider=ollama` y `allowed_providers=[ollama]`. Premium tiene `default_provider=ollama` y `allowed_providers=[ollama, openai, anthropic, gemini, comfyui]`.
- Enterprise puede fijar políticas: `data_residency=EU`, `no_external_providers`, `local_only=true`, etc.
- Ningún motor externo recibe datos del cliente sin flag explícito del plan. Por defecto, Ollama + ComfyUI locales.
- El log del job siempre registra el motor y el modelo exactos, con fines de auditoría y reproducibilidad.

**Lo que el cliente ve:**

- Resultado entregable.
- Coste en créditos.
- Tiempo de ejecución.
- (En planes que lo permiten) Motor y modelo, como metadato de la ficha del asset.
- Nunca: claves de API, endpoints internos, prompts crudos, datos sensibles del prompt engineering.

## 12. Limites

Los límites se aplican en cinco dimensiones: organización, plan, proyecto, usuario y módulo. Toda superación de límite genera un evento `limit_exceeded` y, en su caso, un bloqueo (ver sección 13).

**Limites por organización (configurables por plan):**

- Número de miembros activos.
- Número de proyectos activos (no archivados).
- Almacenamiento total en GB.
- Créditos IA mensuales incluidos.
- Número de integraciones externas activas.
- Número de dominios custom permitidos.
- Número de SSO providers activos.

**Limites por proyecto (configurables por plan y por tipo de proyecto):**

- Número de miembros asignados al proyecto.
- Número de assets totales.
- Almacenamiento del proyecto en GB.
- Tamaño máximo por asset (por ejemplo, master ProRes hasta 200 GB).
- Créditos reservados por el proyecto (opcional; un admin puede asignar pool propio al proyecto).

**Limites por usuario:**

- Número de jobs concurrentes del usuario (típico: 3).
- Número de uploads pendientes del usuario.
- Tamaño máximo de subida individual.
- Frecuencia de acciones (rate limit por minuto y por hora, anti-abuso).

**Limites por modulo (ver matriz seccion 8):**

- Cuotas mensuales: hojas de storyboard, láminas de concept art, biblias, pitches, GB de audio ingestado, etc.
- Tamaño máximo de input.
- Tiempo máximo de ejecución de un job.
- Número de reintentos automáticos.

**Limites de jobs concurrentes globales (a nivel plataforma):**

- Jobs totales en cola (típico: 500 simultáneos en Standard, 5.000 en Premium, custom en Enterprise).
- Jobs por motor (para no saturar Ollama local o ComfyUI).
- Latencia objetivo P95 por tipo de acción (SLA interno).

**Limites de exportaciones e integraciones:**

- Número de exports avanzados por mes.
- Número de sincronizaciones con n8n / Drive / Frame.io por mes.
- Ancho de banda de subida/descarga por organización.

**Comportamiento al alcanzar un limite:**

- Soft limit (90% del máximo): warning al usuario, sin bloqueo.
- Hard limit (100%): bloqueo del intento con `429 Too Many Requests` o `402 Payment Required` según el caso, con mensaje accionable y CTA a upgrade o compra de créditos.
- Periodo de gracia configurable por plan (típico: 24h para límites de almacenamiento; 0h para créditos; 30 días para downgrade de plan).

## 13. Bloqueos y upgrade

El bloqueo de acceso tiene dos caras: **backend gating** (ver sección 14) y **frontend visibility**. Ambas deben coordinarse: el frontend nunca muestra lo que el backend rechazaría, y el backend siempre es la última línea.

**Bloqueos en backend (canónicos):**

- `403 Forbidden`: permiso denegado. El usuario no tiene el `permission_key` requerido.
- `402 Payment Required`: sin saldo de créditos. El usuario tiene permiso pero no saldo.
- `429 Too Many Requests`: rate limit, concurrencia o cuota mensual excedida.
- `423 Locked`: módulo o plan suspendido por admin (fraude, impago, revisión legal).
- `451 Unavailable For Legal Reasons`: contenido bloqueado por política (derechos de autor, jurisdicción).

**Bloqueos en frontend (visibilidad):**

- Acciones no permitidas: botón deshabilitado, tooltip explicando el motivo.
- Acciones con coste: badge de créditos en el botón, click muestra estimación antes de confirmar.
- Módulos no incluidos en el plan: tarjeta del módulo con candado y CTA a upgrade o add-on.
- Cliente externo y revisor invitado: no ven créditos, no ven admin, no ven costos.

**Mensajes de bloqueo (principios):**

- Siempre en lenguaje del rol (no en jerga técnica SaaS).
- Incluyen qué se necesita para desbloquear (subir de plan, comprar add-on, comprar créditos, pedir permiso al admin).
- Nunca culpan al usuario; hablan de la configuración.
- Multiidioma (mínimo es-ES, en-GB, pt-BR en v1).

**Ejemplos de mensajes:**

- Permiso denegado: "Esta acción requiere el rol Productor. Pide a un administrador de tu organización que te asigne ese rol en el proyecto."
- Sin créditos: "Esta acción cuesta unos 30 créditos. Tu saldo actual es 12. Tienes dos opciones: comprar un paquete de 100 créditos (29 €) o subir a Pro para tener 10.000 créditos al mes."
- Cuota mensual: "Has llegado al límite de 100 hojas de storyboard de tu plan Pro este mes. El contador se reinicia el día 1. Si necesitas más, puedes comprar créditos extra o subir a Studio (500 hojas/mes)."
- Módulo no incluido: "El módulo Sound Ingest no está incluido en tu plan Pro. Puedes activarlo como add-on por 149 €/mes con 250 GB incluidos, o subir a Studio para incluirlo."

**Grace period y admin override:**

- Downgrade de plan: 30 días de gracia para que el cliente migre activos超额 o archive proyectos. Pasado el periodo, los activos超额 pasan a modo solo-lectura.
- Admin override: un `org_role=admin` puede, en Enterprise, forzar activación temporal de un módulo (auditada con motivo obligatorio).
- Soporte: staff CID puede aplicar `credit_adjustment` con motivo, pero no puede saltarse el gating de seguridad (por ejemplo, no puede dar acceso a un proyecto de otra organización).

## 14. Relacion con backend gating cerrado

Este contrato SaaS se apoya en el contrato de gating cerrado en `docs/architecture/backend_gating_contract_v1.md`. La división de responsabilidades es estricta:

- **Backend gating** decide **si** una acción se puede ejecutar. Lo hace en cada endpoint vía `Depends(require_write_permission)` o equivalente, evaluando `permission_key`, `organization_id`, `project_id`, `module_key`, `plan_key`, créditos, y estado del recurso. Es la última línea de defensa. Es código.
- **Contrato SaaS** decide **qué** se ofrece, **cuánto** cuesta, **cómo** se factura, **quién** lo puede usar y **qué** ve el cliente. Es la forma del producto. Es contrato (este documento) y, en su momento, datos (planes, matrices, pricing).

Donde el gating enforza:

- Tenant isolation: `organization_id` consistente entre token, query, body, job.
- Permission check: `permission_key` del usuario contra el endpoint.
- Module availability: `module_key` del endpoint contra los módulos habilitados del plan.
- Plan check: `plan_key` contra requisitos del endpoint.
- Credit pre-check: saldo contra `credit_estimate` antes de reservar.
- Resource state: estado del proyecto (archivado, suspendido) bloquea escrituras.

Donde el contrato SaaS define:

- Qué planes existen y qué cuestan.
- Qué módulos van en cada plan y con qué cuota.
- Qué roles existen y qué permisos por defecto tienen.
- Qué eventos se auditan.
- Qué mensajes ve el cliente cuando algo está bloqueado.
- Cómo se visualiza el crédito y el consumo.
- Qué límites concretos aplican a cada plan.

**Reglas de coherencia:**

- Cualquier acción permitida por el contrato SaaS debe ser ejecutable por el backend gating con un `permission_key` registrado. Si el contrato dice "puede", el gating tiene que poder enforzar "sí".
- Cualquier acción denegada por el contrato SaaS debe ser rechazada por el backend gating con el código HTTP canónico de la sección 13. No se permiten comportamientos divergentes.
- El frontend debe consumir la API de capabilities del backend para saber qué mostrar; no debe hardcodear la matriz planes x módulos.
- Cambios en el contrato SaaS sin cambios en el gating son incompletos. Cambios en el gating sin cambios en el contrato son invisibles para el cliente. Ambos se versionan juntos.

**Versionado conjunto:**

- `backend_gating_contract_v1.md` y `cid_saas_model_contract_v1.md` comparten número de versión mayor. Una subida de v1 a v2 de cualquiera exige revisión del otro.
- Cada `permission_key` nuevo en este contrato requiere un `P0` o `P1` de gating en el router correspondiente antes de ser usable en frontend.

## 15. Auditoria

CID audita toda acción que afecte a seguridad, billing, permisos, proyectos o IA. Los eventos son inmutables: se anexan, no se modifican ni se borran.

**Eventos canonicos (v1):**

| Evento | Cuando se registra | Campos clave |
|---|---|---|
| `user_login` | Inicio de sesion exitoso. | `user_id`, `organization_id`, `auth_provider`, `ip`, `user_agent`, `mfa_used`. |
| `user_logout` | Cierre de sesion. | `user_id`, `session_id`. |
| `user_invited` | Invitacion a unirse a org o proyecto. | `inviter_id`, `invitee_email`, `organization_id`, `project_id`, `role_key`. |
| `user_joined` | Aceptacion de invitacion. | `user_id`, `organization_id`, `project_id`, `role_key`. |
| `user_role_changed` | Cambio de rol de proyecto u org. | `actor_id`, `target_user_id`, `old_role`, `new_role`, `scope` (org/project). |
| `user_removed` | Baja de miembro. | `actor_id`, `target_user_id`, `organization_id`, `reason`. |
| `project_created` | Creacion de proyecto. | `project_id`, `organization_id`, `created_by`, `type`, `status`. |
| `project_state_changed` | Cambio de estado (pre-prod, prod, post, delivery, archivado). | `project_id`, `old_state`, `new_state`, `actor_id`. |
| `asset_uploaded` | Subida de archivo a proyecto. | `asset_id`, `project_id`, `uploader_id`, `size_bytes`, `kind`. |
| `asset_deleted` | Borrado de archivo. | `asset_id`, `project_id`, `actor_id`, `reason`. |
| `ai_job_started` | Inicio de job IA. | `job_id`, `permission_key`, `module_key`, `provider`, `model`, `credit_estimate`, `actor_id`, `project_id`. |
| `ai_job_completed` | Job IA terminado OK. | `job_id`, `credits_charged`, `duration_ms`, `output_asset_id`, `actor_id`. |
| `ai_job_failed` | Job IA terminado con error. | `job_id`, `error_code`, `error_message`, `credit_rollback`, `actor_id`. |
| `credit_reserved` | Reserva de creditos al inicio del job. | `credit_reservation_id`, `job_id`, `amount`, `actor_id`. |
| `credit_charged` | Consumo de creditos al cierre del job. | `credit_charge_id`, `job_id`, `amount`, `actor_id`. |
| `credit_rolled_back` | Liberacion de reserva por fallo recuperable. | `credit_rollback_id`, `job_id`, `amount`, `reason`. |
| `credit_purchased` | Compra de paquete adicional. | `purchase_id`, `package_key`, `credits`, `amount_eur`, `actor_id`. |
| `credit_adjusted` | Ajuste manual por soporte. | `adjustment_id`, `credits`, `reason`, `actor_id`, `support_user_id`. |
| `permission_denied` | Backend gating rechazo una accion. | `actor_id`, `permission_key`, `endpoint`, `reason`. |
| `module_blocked` | Modulo no disponible en el plan. | `actor_id`, `module_key`, `plan_key`, `reason`. |
| `plan_changed` | Cambio de plan contratado. | `organization_id`, `old_plan`, `new_plan`, `actor_id`. |
| `billing_change` | Cambio de metodo de pago, datos fiscales. | `organization_id`, `actor_id`, `change_type`. |
| `export_generated` | Export de deliverable (PDF, EDL, AAF, paquete). | `export_id`, `format`, `project_id`, `actor_id`, `size_bytes`. |
| `delivery_published` | Publicacion a cliente o plataforma. | `delivery_id`, `project_id`, `channel`, `actor_id`. |
| `integration_connected` | Conexion de integracion externa. | `integration_id`, `provider`, `actor_id`. |
| `integration_disconnected` | Desconexion. | `integration_id`, `provider`, `actor_id`. |
| `support_session_started` | Staff CID entra a una organizacion. | `support_user_id`, `organization_id`, `reason`, `justification`. |
| `support_session_ended` | Fin de la sesion de soporte. | `support_user_id`, `organization_id`, `duration_min`. |
| `admin_override_used` | Admin fuerza una accion fuera de politicas. | `actor_id`, `module_key`, `reason`, `organization_id`. |

**Reglas de auditoria:**

- Los eventos se escriben con un `event_id` (UUID), `occurred_at` y `actor_id` (o `system` si es automatico).
- El log es append-only. La modificacion de un evento se hace mediante un evento nuevo `audit_event_corrected` que referencia al anterior, no sobreescribiendo.
- Los eventos con datos personales (por ejemplo, `client_feedback` con texto) seudonimizan tras el periodo legal; el ID de usuario se mantiene.
- El cliente puede descargar su propio log de auditoria desde el panel de admin (`org_role=admin` o `org_role=billing`). Enterprise puede configurar retention mas larga.
- El log nunca expone secretos, claves de API, prompts crudos ni contenido de los inputs del cliente. Solo metadatos.

## 16. Roadmap

Este contrato es la base documental. Las fases de implementacion se ejecutan en orden, cada una con su propio spec, su propia implementacion backend/frontend y su propio cierre de validacion.

Fases inmediatas:

1. **CID.SAAS.ROLES.PERMISSIONS.MATRIX.1**: persistir los 22 roles de proyecto y los 25+ permisos base. Tabla `role`, `permission`, `role_permission`, `project_member`. Endpoints CRUD con gating.
2. **CID.SAAS.PLANS.MODULES.MATRIX.1**: persistir la matriz de la seccion 8. Tabla `plan_module` con `availability` y `monthly_quota`. Endpoint `GET /api/capabilities` que devuelve la matriz efectiva por organizacion.
3. **CID.SAAS.CREDITS.USAGE.MODEL.1**: implementar el modelo de la seccion 9. Tabla `credit_ledger`, `credit_reservation`, `credit_charge`, `credit_rollback`, `credit_purchase`. UI de saldo y consumo.
4. **CID.SAAS.AI.JOBS.AUDIT.MODEL.1**: implementar el job model de la seccion 10. Tabla `ai_job`. Catalogo de prompts versionado. Middleware que rechaza jobs sin campos obligatorios.
5. **CID.SAAS.LIMITS.ENFORCEMENT.1**: aplicar los limites de la seccion 12. Middleware de rate limit, middleware de cuota mensual, middleware de concurrencia.
6. **CID.SAAS.BACKEND.ENFORCEMENT.1**: extender el contrato de gating cerrado para que cada endpoint consulte `GET /api/capabilities` y aplique la matriz antes de ejecutar.
7. **CID.SAAS.FRONTEND.VISIBILITY.1**: consumir `/api/capabilities` en frontend. Esconder UI de modulos no disponibles, mostrar badges de creditos, tooltips de bloqueo.
8. **CID.SAAS.BILLING.STRIPE.SPEC.1**: integrar Stripe para suscripciones, add-ons, compra de creditos, prorrateo. Webhooks idempotentes. Eventos de auditoria conectados.
9. **CID.SAAS.AUDIT.LOGS.1**: persistencia de los eventos de la seccion 15. UI de admin para consultar y exportar.
10. **CID.SAAS.ONBOARDING.FLOW.1**: flujo de creacion de organizacion, invitacion, asignacion de roles, primer proyecto, trial.
11. **CID.SAAS.EXTERNAL.REVIEWERS.1**: soporte explicito para `cliente_externo` y `revisor_invitado` con vistas acotadas, sin acceso a creditos ni admin.
12. **CID.SAAS.ENTERPRISE.CUSTOM.1**: soporte de planes Enterprise custom: SSO, SAML, residencia de datos, soporte 24/7, account manager.
13. **CID.SAAS.MODULE.MATRIX.UPDATES.1**: mecanismo formal para actualizar la matriz modulo x plan sin redeploys. Versionado de capabilities.

Fases de soporte:

- **CID.SAAS.PRICING.CANONICALIZATION.1**: resolver la discrepancia entre pricing docs y `src/config/plans.yml` documentada en `cid_pricing_canonicalization_needed_v1.md`. Esta fase es prerrequisito de `CID.SAAS.BILLING.STRIPE.SPEC.1`.
- **CID.SAAS.DOCS.PUBLIC.PRICING.1**: pagina publica de pricing consistente con la matriz final. Sincronizada con backend, no hardcodeada en frontend.
- **CID.SAAS.COMPETITIVE.REFRESH.1`: refresco periodico del baseline competitivo (`cid_pricing_competitive_baseline_v1.md`).

## 17. Riesgos

Riesgos conocidos y aceptados, con mitigacion prevista o diferida:

1. **Confundir el producto con la landing publica**. Riesgo: que marketing venda CID como "una IA para hacer peliculas" y el cliente llegue esperando algo distinto. Mitigacion: pagina de pricing publica sincronizada con la matriz, onboarding que explica el modelo en el primer login, separacion clara de AILinkCinema landing vs CID SaaS (ver `cid_landing_vs_cid_saas_boundary_v1.md`).

2. **Roles audiovisual vs tecnicos**. Riesgo: que el equipo de desarrollo use jerga tecnica (admin, manager, viewer) y el cliente pida roles que no existen (Productor, Sonidista). Mitigacion: este contrato fija los 22 roles reales como canon; cualquier nuevo rol se anade aqui, no se improvisa.

3. **Modulos no disponibles no bien comunicados**. Riesgo: cliente de Starter espera tener `sound_ingest` y se encuentra un candado sin contexto. Mitigacion: mensajes de la seccion 13, badges de "no incluido" en la lista de modulos, CTA a upgrade o add-on, sin decepciones silenciosas.

4. **Creditos no trazables**. Riesgo: que un cargo de creditos se quede sin `job_id` o sin `output_asset_id`, rompiendo la trazabilidad. Mitigacion: rechazo de jobs sin campos obligatorios (seccion 10), auditoria exhaustiva (seccion 15), pruebas de regresion que verifiquen que todo cargo tiene su job y todo job exitoso tiene su asset.

5. **Costes IA no controlados**. Riesgo: que un proveedor externo suba precios o que un job se descontrole en tokens. Mitigacion: `credit_estimate` previo a la ejecucion, reserva de creditos, rollback en error, alertas automaticas cuando el coste real supere el estimado en mas de un margen configurable.

6. **Enterprise custom rompe la matriz**. Riesgo: que cada Enterprise negocie condiciones unicas y el sistema se llene de flags. Mitigacion: la columna Enterprise se modela como "custom" y se negocia fuera de la matriz estandar; las personalizaciones se modelan como overrides por organizacion, no como forks del plan base.

7. **Permisos duplicados backend/frontend**. Riesgo: frontend muestra una accion que el backend rechaza, o backend rechaza una accion que el frontend no mostraba (UX inutil). Mitigacion: fuente unica de verdad, `/api/capabilities`, pruebas de coherencia backend/frontend, contrato versionado junto (seccion 14).

8. **Pricing en docs no coincide con pricing en codigo**. Riesgo: que el cliente vea un precio en la web y otro en la factura, o que `src/config/plans.yml` siga con valores legacy. Mitigacion: fase dedicada `CID.SAAS.PRICING.CANONICALIZATION.1` antes de `CID.SAAS.BILLING.STRIPE.SPEC.1`. Hasta entonces, este contrato documenta la matriz objetivo y `cid_pricing_canonicalization_needed_v1.md` registra la discrepancia.

9. **Cliente externo ve informacion sensible**. Riesgo: que un `cliente_externo` o `revisor_invitado` vea creditos, billing o admin. Mitigacion: gating explicito en cada endpoint que devuelva datos sensibles, UI que oculta informacion por rol, auditoria de `permission_denied` para detectar fugas.

10. **Onboarding demasiado denso**. Riesgo: que el cliente se pierda en la primera sesion al ver 22 roles, 19 modulos, 5 planes, 25+ permisos. Mitigacion: wizard de onboarding que propone una configuracion inicial sensata segun tipo de organizacion (productora pequena, agencia, escuela, broadcaster) y la confirma; permite editar despues.

11. **Jobs de larga duracion fallan por timeout de sesion**. Riesgo: que un render de storyboard tarde 10 minutos y el token del usuario caduque a los 5. Mitigacion: tokens de servicio para jobs largos, refresco automatico, estado del job consultable sin sesion del usuario original.

12. **Sin versionado del modelo IA en el job**. Riesgo: que un trabajo antiguo no se pueda reproducir porque el modelo fue actualizado. Mitigacion: `model` y `prompt_version` obligatorios en el job, catalogo inmutable de prompts, posibilidad de re-ejecutar con el mismo `model` y `prompt_version` aunque ya no sean los actuales.

## 18. Criterio de GO

Este contrato v1 se considera **GO** para guiar las fases de implementacion cuando se cumplen todos los puntos siguientes:

1. Los 5 planes (Starter, Pro, Studio, Premium, Enterprise) estan definidos con precio, usuarios, proyectos, almacenamiento, creditos y upsell.
2. Los 19 modulos estan definidos con nombre canonico (`module_key`) y proposito.
3. La matriz modulos x plan (seccion 8) esta completa para los 5 planes y los 19 modulos, con valores `incluido`, `limitado`, `add-on`, `no incluido`.
4. Los 22 roles de proyecto (seccion 5) estan definidos con proposito, modulos donde operan, permisos por defecto y restricciones.
5. Los 25+ permisos base (seccion 6) estan definidos en notacion `domain.action`, con significado canonico.
6. El modelo de creditos (seccion 9) define saldo, reserva, cargo, rollback, expiracion y los 17 costes por accion.
7. El modelo de jobs de IA (seccion 10) define los 18 campos obligatorios, incluido `input_hash`, `prompt_version`, `provider`, `model`, `credits_charged`.
8. Los limites (seccion 12) estan definidos por organizacion, plan, proyecto, usuario y modulo, con soft y hard limit.
9. Los bloqueos y mensajes (seccion 13) estan definidos para los 5 codigos HTTP principales, con plantillas de mensaje en lenguaje del rol.
10. La relacion con el contrato de gating cerrado (seccion 14) es explicita: division de responsabilidades, reglas de coherencia, versionado conjunto.
11. La auditoria (seccion 15) define 28 eventos canonicos con sus campos clave.
12. El roadmap (seccion 16) enumera las fases en orden, con su prefijo CID.SAAS.*, su objetivo y su dependencia.
13. Los riesgos (seccion 17) enumeran al menos 8 riesgos con mitigacion prevista o diferida, incluida la canonicalizacion de pricing.
14. El documento es internamente consistente: ningun permiso de la seccion 6 rompe un rol de la seccion 5; ninguna cuota de la seccion 8 rompe un limite de la seccion 12; ningun evento de la seccion 15 rompe una accion de la seccion 10.

Cuando todos estos puntos se cumplen, el contrato sirve como base contractual y documental para:

- Disenar la primera iteracion del backend de capacidades (`/api/capabilities`).
- Disenar la UI de seleccion de plan y de modulos.
- Disenar los mensajes de bloqueo y los tooltips.
- Iniciar `CID.SAAS.ROLES.PERMISSIONS.MATRIX.1` y `CID.SAAS.PLANS.MODULES.MATRIX.1`.

El contrato no implementa nada. No es un GO de codigo. Es un GO de diseno, suficiente para que las fases 1, 2 y 3 del roadmap arranquen con un modelo de datos y de negocio estable, sin tener que revisarlo en cada sprint.
