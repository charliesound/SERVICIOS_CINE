# CID Billing Models v1

Version: 1.0
Status: SPEC / ARCHITECTURE
Date: 2026-06-05
Owners: CID Architecture / CID Product / CID Business
Scope: internal billing models, subscriptions, credits, invoices, provider references and future gates
Companion docs (no superseded, esta fase los respeta):
- `docs/business/cid_pricing_canonical_v1.md` (canon de pricing, D001-D010, 4 modos comerciales, 6 estados de credito, 17 audit events).
- `docs/architecture/cid_saas_model_contract_v1.md` (10 entidades canonicas, 22 roles, 31 permisos, modelo de creditos base).
- `docs/architecture/cid_plans_modules_matrix_v1.md` (21 modulos, 5 planes, 5 estados de modulo, 3 modos comerciales previos).
- `docs/architecture/cid_roles_permissions_matrix_v1.md` (matriz operativa rol x permiso x modulo, 8 roles especiales, pseudologica de 6 dimensiones).
- `docs/architecture/backend_gating_contract_v1.md` (P0=0, P1=0, P2=8, 5 dependencias, 8 patrones de router).

## 2. Metadata inicial

- **Version**: 1.0.
- **Status**: SPEC / ARCHITECTURE (documental, no implementation).
- **Date**: 2026-06-05.
- **Owners**: CID Architecture / CID Product / CID Business.
- **Scope**: modelos internos de billing, suscripciones, creditos, invoices, referencias de proveedor y gates futuros.
- **Idioma del canon**: espanol (es-ES).
- **Moneda del canon**: EUR.
- **Mercado inicial**: Espana/UE.
- **Versionado**: este documento se versiona con cada cambio mayor. Cambios menores se anotan al final.

## 3. Proposito

Este documento define los modelos internos de billing de CID SaaS. Su proposito es:

- Cerrar la forma de los datos de billing, suscripciones, creditos, invoices y referencias a proveedores externos antes de implementar nada.
- Evitar que Stripe (o cualquier otro proveedor de pagos) sea la fuente de verdad del producto. El canon afirma: CID decide, el proveedor ejecuta.
- Servir de base para fases tecnicas posteriores: `CID.SAAS.CREDIT.LEDGER.BACKEND.1`, `CID.SAAS.SUBSCRIPTION.STATE.BACKEND.1`, `CID.SAAS.PLAN.GATES.BACKEND.1`, `CID.SAAS.MODULE.GATES.BACKEND.1`, `CID.SAAS.CREDIT.GATES.BACKEND.1`, `CID.SAAS.STRIPE.PRODUCTS.PRICES.1`, `CID.SAAS.STRIPE.WEBHOOKS.1`, `CID.SAAS.BILLING.ADMIN.UI.1`.
- Mantener coherencia con `cid_pricing_canonical_v1.md`: precios, bolsas, modos comerciales, estados de credito, decisiones canonicas D001-D010.
- No implementar nada. Es arquitectura, no codigo.

Regla de oro: **CID es la fuente de verdad. El proveedor de pagos (Stripe u otro) es solo un ejecutor externo**. Los webhooks actualizan estado, nunca definen el producto.

## 4. Principio arquitectonico

CID SaaS se modela bajo una separacion estricta entre tres planos:

| Plano | Quien decide | Que decide | Donde vive |
|---|---|---|---|
| Producto | CID | Plan, modulo, limite, credito, modo comercial, override Enterprise. | Este documento, `cid_pricing_canonical_v1.md`, `cid_plans_modules_matrix_v1.md`. |
| Billing | CID | Suscripcion, estado de suscripcion, ledger de creditos, invoice canonica, prorrateo, override manual. | Este documento y los modelos de datos futuros. |
| Pago | Proveedor externo (Stripe, Adyen, etc.) | Cobro, reintento, fraude, metodo de pago, factura fiscal del proveedor. | Stripe (o el proveedor elegido), referenciado desde CID. |

Reglas derivadas:

- **Stripe (o el proveedor) no es la fuente de verdad del producto.** Un cambio de precio en Stripe sin un cambio versionado en `cid_pricing_canonical_v1.md` es un bug, no un comportamiento valido.
- **El billing backend recibe webhooks idempotentes** del proveedor y actualiza el estado interno. El proveedor no notifica al cliente final; CID lo hace, con sus plantillas y su multiidioma.
- **El ledger de creditos es interno.** Stripe no sabe cuantos creditos tiene una organizacion. Stripe solo refleja cobros y pagos. El saldo de creditos sale de CID.
- **Las facturas pueden tener dos caras**: la factura del proveedor (fiscal, con IVA/IGIC, numero legal) y la factura canonica de CID (interna, con detalle de plan, creditos, add-ons). Esta fase define la factura canonica; la factura del proveedor se mapea en `invoice_reference`.
- **El override Enterprise es CID-only.** Stripe no tiene visibilidad de los overrides Enterprise. El billing backend debe reflejar el override al cobrar, sin exponerlo como un plan publico.
- **El backend es la unica defensa.** El frontend no decide, solo muestra. Toda respuesta bloqueada lleva `code` canonico, `message` accionable y `cta`.

## 5. Entidades principales

Esta seccion define quince entidades internas del modelo de billing. Cada entidad tiene: proposito, campos recomendados, claves, relaciones, invariantes y riesgos. Los nombres usan `snake_case` y se usan tal cual en el codigo cuando se implemente.

Las entidades se modelan conceptualmente; esta fase no escribe migraciones ni SQL. El `id` de cada entidad es un UUID inmutable, salvo donde se indique lo contrario.

### 5.1 `billing_account`

- **Proposito**: representar la cuenta de facturacion de una organizacion. Es la unidad minima de billing: una organizacion tiene exactamente un `billing_account` activo. Enterprise puede tener varios `billing_account` si la organizacion tiene entidades legales separadas (multi-tenant legal); en ese caso, cada `billing_account` se factura aparte.
- **Campos recomendados**:
  - `billing_account_id` (UUID, PK, inmutable).
  - `organization_id` (UUID, FK a `organization`, unique cuando la organizacion tiene un solo `billing_account`).
  - `legal_name` (texto, razon social o nombre comercial).
  - `tax_id` (texto, NIF/CIF/VAT, validado por pais).
  - `billing_email` (email, validado; puede diferir del email del owner).
  - `country` (codigo ISO 3166-1 alpha-2).
  - `default_currency` (texto, por defecto `EUR`).
  - `language` (codigo BCP-47, por defecto `es-ES`).
  - `fiscal_address` (texto estructurado o jsonb: calle, ciudad, codigo postal, pais).
  - `status` (enum: `active`, `closed`).
  - `created_at`, `updated_at`, `closed_at` (si aplica).
- **Claves**:
  - PK: `billing_account_id`.
  - Unico: `(organization_id)` cuando la organizacion tiene un solo `billing_account`; en multi-tenant legal, la unicidad se reemplaza por una restriccion parcial.
- **Relaciones**:
  - `billing_account` 1..N `subscription` (una suscripcion historica, otra actual).
  - `billing_account` 1..N `invoice_reference`.
  - `billing_account` 1..N `payment_provider_reference`.
  - `billing_account` 1..N `credit_balance` (uno por moneda si se internacionaliza; por defecto uno en EUR).
- **Invariantes**:
  - Una organizacion self-service tiene exactamente un `billing_account` activo.
  - `tax_id` debe validarse contra el formato del pais declarado en `country`.
  - `closed_at` solo se permite si todas las suscripciones asociadas estan en `cancelled` o `expired`.
- **Riesgos**:
  - Multi-tenant legal: modelar varias cuentas para una sola organizacion complica los gates. Mitigacion: el `billing_account` es la unidad de decision; los gates futuros operan a nivel `billing_account_id`, no `organization_id`.
  - Cambio de pais fiscal: si la organizacion cambia de pais, se crea un nuevo `billing_account` o se cierra el viejo; no se reescribe el historial.
  - IVA/IGIC: cada pais tiene reglas distintas. Esta fase no las modela; el billing backend posterior debe soportar multiples regimenes fiscales.

### 5.2 `subscription`

- **Proposito**: representar el contrato comercial activo entre un `billing_account` y CID. Es el vinculo que dice "esta organizacion esta en el plan X, con la periodicidad Y, desde la fecha Z".
- **Campos recomendados**:
  - `subscription_id` (UUID, PK, inmutable).
  - `billing_account_id` (UUID, FK).
  - `plan_key` (enum: `starter`, `pro`, `studio`, `premium`, `enterprise`; viene de `cid_pricing_canonical_v1.md` seccion 6).
  - `billing_cycle` (enum: `monthly`, `annual`, `custom`).
  - `currency` (texto, por defecto `EUR`).
  - `current_status` (enum: enum de `subscription_status`; ver seccion 7).
  - `plan_snapshot_id` (UUID, FK a `plan_snapshot`; ver 5.4; congela el plan al contratar).
  - `start_at` (timestamp; inicio del primer ciclo).
  - `current_period_start` (timestamp).
  - `current_period_end` (timestamp; fin del ciclo de facturacion actual).
  - `next_renewal_at` (timestamp; puede ser null si la suscripcion no renueva).
  - `trial_end_at` (timestamp, nullable; presente solo si `current_status` es o fue `trialing`).
  - `cancelled_at` (timestamp, nullable).
  - `cancellation_effective_at` (timestamp, nullable; fin del periodo por el que el cliente ha pagado).
  - `auto_renew` (bool; por defecto `true`).
  - `grace_period_end_at` (timestamp, nullable; presente durante downgrade o suspension).
  - `enterprise_override_id` (UUID, FK a `enterprise_override`, nullable; presente solo si hay override activo).
  - `entitlement_flags` (jsonb: `is_demo`, `is_trial`, `is_beta`, `is_enterprise_manual`; usado por gates).
  - `metadata` (jsonb; notas internas, version de onboarding, fuente de captura).
  - `created_at`, `updated_at`.
- **Claves**:
  - PK: `subscription_id`.
  - Indice: `(billing_account_id, current_status)` para localizar suscripciones activas por cuenta.
  - Indice: `(next_renewal_at)` para jobs de renovacion.
- **Relaciones**:
  - `subscription` 1..N `plan_change_history` (historial de upgrades/downgrades).
  - `subscription` 1..N `billing_event` (eventos del ciclo de vida).
  - `subscription` 1..N `invoice_reference` (facturas asociadas).
  - `subscription` 1..1 `plan_snapshot` (plan congelado al contratar; ver 5.4).
  - `subscription` 0..1 `enterprise_override` (override activo, si aplica).
- **Invariantes**:
  - Una suscripcion `active` debe tener `current_period_end > now()`.
  - `trial_end_at <= current_period_end` cuando el trial aplica.
  - `cancelled_at <= cancellation_effective_at` (la cancelacion se programa, no se ejecuta al instante salvo que se pida asi).
  - Cambiar de `plan_key` no reescribe el `plan_snapshot_id`; crea un nuevo `plan_snapshot` y actualiza la referencia.
- **Riesgos**:
  - Plan cambiado a mitad de job IA: si el cliente cambia de plan mientras un job esta corriendo, el job sigue con el `plan_snapshot` que tenia al iniciar. El nuevo plan aplica al siguiente job.
  - Renovacion silenciosa: el sistema debe avisar antes de renovar. Mitigacion: emails T-7, T-1, T-0; evento `subscription_renewal_pending`.
  - Doble suscripcion activa: el modelo permite varias suscripciones historicas pero solo una `active` por `billing_account`. Mitigacion: indice unico parcial `(billing_account_id) WHERE current_status IN ('active', 'trialing', 'past_due')`.

### 5.3 `subscription_status`

- **Proposito**: modelar el campo `current_status` de la suscripcion. Es un enum de cadena con semantica canonica. La maquina de estados completa se define en la seccion 7; esta entidad describe el valor del campo.
- **Campos recomendados**:
  - `code` (string, PK; uno de: `trialing`, `active`, `past_due`, `suspended`, `cancelled`, `expired`, `enterprise_manual`, `beta`, `demo`).
  - `display_name` (texto, multiidioma).
  - `description` (texto, multiidioma).
  - `allows_write` (bool; puede el tenant ejecutar acciones mutantes?).
  - `allows_ai_jobs` (bool; puede lanzar jobs IA?).
  - `allows_billing_changes` (bool; puede cambiar de plan o comprar add-ons?).
  - `is_terminal` (bool; es un estado del que no se sale automaticamente?).
  - `grace_period_days` (int; periodo de gracia por defecto asociado al estado).
- **Claves**:
  - PK: `code`.
- **Relaciones**:
  - Referenciado por `subscription.current_status` y por `billing_event.to_status`.
- **Invariantes**:
  - El catalogo de `code` es estable; nuevos estados se introducen con una migracion versionada del canon.
  - `is_terminal=true` solo aplica a `cancelled` y `expired` (los datos sobreviven el periodo legal, pero la suscripcion no renueva).
- **Riesgos**:
  - Estado huerfano: si un webhook del proveedor actualiza el estado sin pasar por la maquina documentada, se rompe la coherencia. Mitigacion: el `billing_event` siempre registra `from_status`, `to_status`, `reason`, `actor_id`, `provider_event_id`.

### 5.4 `plan_snapshot`

- **Proposito**: congelar el plan contratado en el momento de la suscripcion. Esto es critico: el precio, los creditos incluidos, los limites y los modulos disponibles no pueden cambiar retroactivamente cuando el canon evoluciona. La suscripcion vive contra un `plan_snapshot`, no contra el `plan_key` canonico.
- **Campos recomendados**:
  - `plan_snapshot_id` (UUID, PK).
  - `plan_key` (string; referencia simbolica al canon; puede ser `starter`, `pro`, `studio`, `premium`, `enterprise`).
  - `display_name` (texto; nombre publico del plan en el momento del snapshot).
  - `price_amount` (decimal; precio del plan en el momento del snapshot, sin IVA).
  - `price_currency` (texto; por defecto `EUR`).
  - `billing_cycle` (enum: `monthly`, `annual`).
  - `credits_included_per_period` (int; cuota mensual de creditos; para planes con cuota anual, se mantiene el valor mensual prorrateado en facturacion).
  - `users_included` (int; limite de usuarios en el plan; `-1` significa `custom` para Enterprise).
  - `projects_active_max` (int; limite de proyectos activos; `-1` significa `custom`).
  - `storage_gb` (decimal; almacenamiento incluido en GB; `-1` significa `custom`).
  - `concurrent_ai_jobs` (int; jobs IA concurrentes; `-1` significa `custom`).
  - `modules_included` (array de `module_key`; modulos con estado `included` o `limited`; el detalle de cuotas de `limited` se modela aparte).
  - `modules_limited_quotas` (jsonb; `module_key -> monthly_quota`; para modulos con cuota mensual).
  - `exports_per_period` (int; exports/mes; `-1` significa `custom`).
  - `support_tier` (enum: `standard`, `priority_light`, `priority`, `priority_high`, `dedicated_24_7`).
  - `audit_retention_days` (int; retencion del log de auditoria; `-1` significa `custom`).
  - `data_retention_days_after_cancellation` (int; retencion de datos tras cancelacion).
  - `ai_traceability_level` (enum: `basic`, `standard`, `advanced`, `auditable`, `full`).
  - `canon_version` (string; version del canon de pricing al que se congela; permite auditar de que version se tomo el plan).
  - `effective_from` (timestamp; cuando empezo a aplicar este snapshot).
  - `effective_to` (timestamp, nullable; si el snapshot fue reemplazado por otro).
  - `created_at`.
- **Claves**:
  - PK: `plan_snapshot_id`.
  - Indice: `(plan_key, canon_version)`.
- **Relaciones**:
  - `plan_snapshot` 1..N `subscription` (varias suscripciones pueden compartir el mismo snapshot si se contrato el mismo plan en el mismo momento canonico).
  - `plan_snapshot` 0..N `plan_change_history` (cada cambio de plan crea un nuevo snapshot).
- **Invariantes**:
  - Un snapshot no se modifica despues de `effective_from`; cualquier cambio se refleja en un nuevo snapshot.
  - `canon_version` siempre presente; permite auditar.
  - `effective_to` se rellena cuando el snapshot es reemplazado; nunca se borra.
- **Riesgos**:
  - El canon evoluciona (precios, limites, modulos) y el snapshot lo bloquea. Esto es a proposito: protege al cliente contra cambios retroactivos. Pero exige mantener el canon versionado para que `canon_version` sea trazable.
  - Si el canon cambia, los snapshots antiguos siguen activos hasta que el cliente cambie de plan o cancele. Esto es lo correcto; el canon no reescribe la historia.

### 5.5 `plan_change_history`

- **Proposito**: registro inmutable de todos los cambios de plan de una suscripcion. Cada cambio crea una nueva entrada. La suscripcion siempre refleja el ultimo cambio; la historia queda en esta entidad.
- **Campos recomendados**:
  - `change_id` (UUID, PK).
  - `subscription_id` (UUID, FK).
  - `from_plan_snapshot_id` (UUID, FK; snapshot anterior).
  - `to_plan_snapshot_id` (UUID, FK; snapshot nuevo).
  - `change_type` (enum: `upgrade_immediate`, `downgrade_scheduled`, `downgrade_immediate`, `renewal`, `reactivation`, `enterprise_override_change`).
  - `effective_at` (timestamp; cuando aplica el nuevo plan).
  - `pro_rata_amount_eur` (decimal, nullable; importe prorrateado cobrado o acreditado, segun el tipo de cambio).
  - `credit_balance_carried_eur` (decimal, nullable; saldo acreditado por cancelacion anticipada del plan anterior).
  - `actor_id` (UUID, FK a `user`; quien solicita el cambio; `system` para cambios automaticos).
  - `reason` (texto, opcional; justificacion para Enterprise override).
  - `metadata` (jsonb; datos contextuales: id de la solicitud, IP, etc.).
  - `created_at`.
- **Claves**:
  - PK: `change_id`.
  - Indice: `(subscription_id, effective_at DESC)`.
- **Relaciones**:
  - `plan_change_history` N..1 `subscription`.
  - `plan_change_history` N..1 `plan_snapshot` (from, to).
- **Invariantes**:
  - Cada cambio es inmutable; correcciones se hacen con un nuevo cambio.
  - `downgrade_scheduled` deja el `from_plan_snapshot` activo hasta `effective_at`; el `to_plan_snapshot` no aplica hasta entonces.
- **Riesgos**:
  - Cambio de plan durante un job IA: el job en curso sigue con el plan anterior; el cargo se calcula con el `plan_snapshot` que tenia al reservar. Mitigacion: el cargo se evalua al final del job, no al reservar.
  - Downgrade con datos excedentes: el sistema avisa antes de aplicar el cambio y abre periodo de gracia (ver `cid_pricing_canonical_v1.md` seccion 16). Mitigacion: la suscripcion registra `grace_period_end_at`; los gates lo respetan.

### 5.6 `credit_balance`

- **Proposito**: representar el saldo actual de creditos de un `billing_account` o de una organizacion. Es un agregado: no es un contador entero simple, sino una composicion de varios saldos parciales que se actualizan por eventos del ledger.
- **Campos recomendados**:
  - `credit_balance_id` (UUID, PK).
  - `organization_id` (UUID, FK; el balance es de la organizacion, no del billing account, porque las bolsas y creditos sobreviven a cambios de billing account).
  - `currency_equivalent` (texto; por defecto `credits`, pero permite mapear a EUR para UI).
  - `included_monthly_remaining` (int; creditos del ciclo actual, no consumidos, no reservados).
  - `purchased_balance` (int; creditos comprados no consumidos, no reservados; suma de bolsas con su caducidad individual, gestionada en el ledger).
  - `promotional_balance` (int; creditos regalados o promocionales, con motivo registrado).
  - `trial_balance` (int; creditos de trial, si el tenant esta en trial o lo estuvo).
  - `enterprise_balance` (int; creditos Enterprise con prioridad y reglas custom; puede tener rollover contractual).
  - `reserved_active` (int; creditos bloqueados por jobs en curso, no consumidos todavia).
  - `consumed_period` (int; creditos consumidos en el ciclo actual; informativo, no afecta disponibilidad).
  - `expired_total` (int; creditos que llegaron a su fecha de expiracion, acumulado historico).
  - `refunded_total` (int; creditos devueltos al cliente, acumulado historico).
  - `adjusted_total` (int; creditos ajustados manualmente, acumulado historico).
  - `current_period_start` (timestamp; inicio del ciclo de facturacion actual, para `included_monthly_remaining`).
  - `current_period_end` (timestamp; fin del ciclo; al cerrarse, el remanente de `included_monthly_remaining` se pierde o rollovera segun el plan).
  - `last_updated_at` (timestamp).
  - `version` (int; control de concurrencia optimista).
- **Claves**:
  - PK: `credit_balance_id`.
  - Unico: `(organization_id)` (un balance por organizacion).
- **Relaciones**:
  - `credit_balance` 1..N `credit_ledger_entry` (cada evento del ledger actualiza el balance).
- **Invariantes**:
  - `available = included_monthly_remaining + purchased_balance + promotional_balance + trial_balance + enterprise_balance - reserved_active`.
  - `available >= 0` siempre (los gates rechazan antes de llegar a saldo negativo).
  - `consumed_period` es informativo; no bloquea, pero se usa para mostrar al cliente cuanto lleva gastado este ciclo.
  - Los saldos `expired_total`, `refunded_total`, `adjusted_total` son acumulativos y no decrementan nunca.
- **Riesgos**:
  - Concurrencia: dos jobs reservando a la vez pueden generar saldo negativo si no hay lock. Mitigacion: el ledger usa `SELECT FOR UPDATE` o equivalent, y los gates leen saldo dentro de transaccion.
  - Drift entre `credit_balance` y suma del ledger: si una entrada del ledger falla a medias, el balance y el ledger se desincronizan. Mitigacion: el balance se reconstruye en pruebas a partir del ledger, y hay un job de reconciliacion periodico.
  - Multi-moneda: si en el futuro se internacionaliza, la unidad interna sigue siendo `credits` (1 credito = X EUR segun plan), pero hay que dejar el `currency_equivalent` para conversiones en UI.

### 5.7 `credit_ledger_entry`

- **Proposito**: registro append-only de todos los movimientos de creditos. Es la fuente de verdad del saldo: el `credit_balance` es un cache derivado del ledger. Cualquier operacion que afecte a creditos debe crear una entrada en el ledger; el balance se actualiza dentro de la misma transaccion.
- **Campos recomendados**:
  - `entry_id` (UUID, PK).
  - `organization_id` (UUID, FK).
  - `entry_type` (enum: `credit_grant`, `credit_purchase`, `credit_reserve`, `credit_release`, `credit_consume`, `credit_refund`, `credit_expire`, `credit_adjustment`; ver seccion 10).
  - `saldo_origen` (enum: `trial`, `included`, `purchased`, `promotional`, `enterprise`; indica de que sub-saldo sale o entra el credito).
  - `amount` (int; cantidad de creditos; positivo para grant/purchase/refund, negativo para consume/expire, neutro para reserve/release que apuntan a una reserva).
  - `idempotency_key` (string, unique; protege contra duplicacion de eventos del proveedor o del sistema).
  - `reservation_id` (UUID, nullable, FK a reserva; presente en `credit_reserve`, `credit_release`, `credit_consume`).
  - `job_id` (UUID, nullable, FK a job IA; presente en `credit_reserve` y `credit_consume`).
  - `project_id` (UUID, nullable; proyecto asociado al consumo).
  - `user_id` (UUID, nullable; usuario que origino la operacion).
  - `billing_account_id` (UUID, nullable; cuenta de facturacion, para `credit_purchase`).
  - `invoice_reference_id` (UUID, nullable; factura asociada, para `credit_purchase`).
  - `package_key` (string, nullable; bolsa comprada, para `credit_purchase`).
  - `actor_id` (UUID o `system`; quien origino el evento).
  - `reason` (texto; motivo obligatorio para `credit_refund` y `credit_adjustment`).
  - `related_entry_id` (UUID, nullable; para enlazar refund con la operacion original, o ajuste con el cargo original).
  - `expires_at` (timestamp, nullable; presente en `credit_purchase` y `credit_grant` con caducidad).
  - `metadata` (jsonb; datos contextuales: parametros del job, hash de input, etc.).
  - `occurred_at` (timestamp inmutable; cuando ocurrio el evento).
  - `created_at` (timestamp de insercion en el ledger; puede diferir de `occurred_at` por latencia de webhook).
- **Claves**:
  - PK: `entry_id`.
  - Unico: `(idempotency_key)`; critico para webhooks del proveedor de pagos.
  - Indice: `(organization_id, occurred_at DESC)` para consultas del historial.
  - Indice: `(job_id)` para trazabilidad de jobs.
  - Indice: `(reservation_id)` para enlazar reserve/release/consume.
  - Indice: `(project_id)` para consultas por proyecto.
- **Relaciones**:
  - `credit_ledger_entry` N..1 `credit_balance` (organizacion).
  - `credit_ledger_entry` 0..1 `credit_ledger_entry` (`related_entry_id`, para refund/ajuste que apunta al original).
- **Invariantes**:
  - Append-only: las entradas no se modifican ni se borran. Las correcciones se hacen con una nueva entrada que apunta a la original via `related_entry_id`.
  - Cada job IA que consume creditos tiene al menos una entrada `credit_reserve` y una `credit_consume` (o `credit_release` si falla por causa tecnica).
  - `amount` siempre es entero (no se permiten creditos fraccionarios en v1).
- **Riesgos**:
  - Webhook duplicado: si el proveedor envia el mismo webhook dos veces, se duplicaria la entrada. Mitigacion: `idempotency_key` unico.
  - Job con `credit_consume` antes de tener `credit_reserve`: no debe ocurrir, pero si ocurre, el ledger lo registra y se audita. Mitigacion: el flujo canonico es reserve, ejecucion, consume/release.
  - Drift: la suma del ledger debe coincidir con el `credit_balance`. Si no coincide, hay un job de reconciliacion que reconstruye el balance a partir del ledger.

### 5.8 `credit_package_purchase`

- **Proposito**: representar la compra de una bolsa de creditos por parte de un cliente. Es un subtipo de operacion de billing; se modela aparte del `subscription` porque las bolsas son compras unicas, no recurrentes.
- **Campos recomendados**:
  - `purchase_id` (UUID, PK).
  - `organization_id` (UUID, FK).
  - `billing_account_id` (UUID, FK).
  - `subscription_id` (UUID, FK, nullable; presente si la compra esta vinculada a una suscripcion; null si es la unica operacion de billing, por ejemplo una organizacion en trial).
  - `package_key` (enum: `starter_500_pack`, `pro_1500_pack`, `pro_3000_pack`, `studio_10000_pack`, `premium_custom_pack`, `enterprise_custom_pack`; viene de `cid_pricing_canonical_v1.md` seccion 10).
  - `credits` (int; cantidad de creditos de la bolsa; canon: 500, 1500, 3000, 10000, contractual).
  - `price_amount_eur` (decimal; precio canon; canon: 49, 119, 229, 699, contractual).
  - `price_currency` (texto; por defecto `EUR`).
  - `purchased_at` (timestamp).
  - `expires_at` (timestamp; canon: 12 meses desde la compra, salvo override Enterprise).
  - `status` (enum: `pending`, `paid`, `failed`, `refunded`, `expired`).
  - `payment_provider_reference_id` (UUID, FK; el cargo en Stripe o el proveedor).
  - `invoice_reference_id` (UUID, FK; la factura canonica).
  - `credit_ledger_entry_id` (UUID, FK; entrada del ledger que refleja el alta de creditos).
  - `actor_id` (UUID, FK a user; quien realizo la compra).
  - `metadata` (jsonb; cupon aplicado, source de captura, etc.).
  - `created_at`, `updated_at`.
- **Claves**:
  - PK: `purchase_id`.
  - Indice: `(organization_id, status)`.
  - Indice: `(subscription_id)`.
- **Relaciones**:
  - `credit_package_purchase` N..1 `billing_account`.
  - `credit_package_purchase` 0..1 `subscription`.
  - `credit_package_purchase` 1..1 `payment_provider_reference`.
  - `credit_package_purchase` 1..1 `invoice_reference`.
  - `credit_package_purchase` 1..1 `credit_ledger_entry` (el alta de creditos).
- **Invariantes**:
  - `status='paid'` requiere un `payment_provider_reference_id` con estado terminal OK.
  - `expires_at = purchased_at + 12 meses` canon, salvo `premium_custom_pack` o `enterprise_custom_pack` que tienen expiracion contractual.
  - `status='refunded'` requiere un evento `credit_refund` en el ledger por la misma cantidad.
- **Riesgos**:
  - Doble cobro: el cliente puede hacer doble click; el backend debe idempotenciar por `idempotency_key` o por sesion.
  - Cambio de plan incompatible: si el cliente compra una bolsa y luego hace downgrade a un plan incompatible, los creditos siguen en su saldo pero no son utilizables. Ver `cid_pricing_canonical_v1.md` seccion 10 (regla: no desbloquean modulos).
  - Caducidad silenciosa: el sistema debe avisar 30, 15 y 1 dias antes de `expires_at`. Si la fecha pasa, los creditos se marcan `expired` y se emite el evento `credits_expired`.

### 5.9 `invoice_reference`

- **Proposito**: representar la factura canonica de CID. Es la factura que ve el cliente en su panel de billing: plan, add-ons, bolsas de creditos, prorrateos, descuentos. **No es necesariamente la factura fiscal del proveedor de pagos**. La factura del proveedor se mapea aqui como referencia externa.
- **Campos recomendados**:
  - `invoice_reference_id` (UUID, PK).
  - `billing_account_id` (UUID, FK).
  - `subscription_id` (UUID, FK, nullable; null si la factura es solo de una bolsa).
  - `invoice_number` (string, canonico CID; formato `CID-YYYY-NNNNNN`; unico por ejercicio).
  - `status` (enum: `draft`, `open`, `paid`, `past_due`, `void`, `uncollectible`).
  - `issue_date` (timestamp).
  - `due_date` (timestamp, nullable; ausente si no aplica, por ejemplo en cobros automaticos).
  - `period_start` (timestamp; inicio del periodo facturado).
  - `period_end` (timestamp; fin del periodo facturado).
  - `currency` (texto; por defecto `EUR`).
  - `subtotal_eur` (decimal; suma de lineas sin impuestos).
  - `tax_amount_eur` (decimal, nullable; IVA/IGIC si aplica).
  - `total_eur` (decimal; total a pagar).
  - `line_items` (jsonb; desglose: `plan_amount`, `addons_amount`, `credit_packages_amount`, `prorate_credit`, `prorate_debit`, `discount`).
  - `provider_invoice_id` (string, nullable; id de la factura en el proveedor externo, por ejemplo `in_xxx` en Stripe).
  - `provider_invoice_url` (string, nullable; URL al PDF en el portal del proveedor).
  - `pdf_storage_path` (string, nullable; ruta interna al PDF canonico CID; nunca expone datos sensibles de tarjeta).
  - `metadata` (jsonb; notas internas, idioma de la factura, etc.).
  - `created_at`, `updated_at`.
- **Claves**:
  - PK: `invoice_reference_id`.
  - Unico: `(invoice_number)`.
  - Unico: `(provider_invoice_id)` cuando el proveedor emite una.
  - Indice: `(billing_account_id, issue_date DESC)`.
- **Relaciones**:
  - `invoice_reference` N..1 `billing_account`.
  - `invoice_reference` 0..1 `subscription`.
  - `invoice_reference` 0..N `credit_package_purchase` (las bolsas cobradas en esa factura).
  - `invoice_reference` 0..1 `payment_provider_reference` (el cargo en el proveedor que paga esta factura).
- **Invariantes**:
  - `invoice_number` se asigna una sola vez; no se reutiliza aunque la factura se `void`.
  - `status='paid'` requiere un `payment_provider_reference` con estado terminal OK y un cargo por el `total_eur`.
  - `tax_amount_eur` se calcula al emitir; no se modifica despues (correcciones se hacen con `credit_note` separado).
  - La factura canonica no almacena nunca datos sensibles de tarjeta (PAN, CVV). Solo referencia el `payment_provider_reference`.
- **Riesgos**:
  - Doble emision: si el sistema reintenta la emision, se duplica la factura. Mitigacion: `idempotency_key` por emision.
  - Discrepancia de importes: el `total_eur` canonico puede diferir del cargo del proveedor si hay prorrateo manual. Mitigacion: el canon afirma el canonico como verdad; el cargo del proveedor se reconcilia periodicamente.
  - Multi-idioma de la factura: si el cliente pide factura en otro idioma, se reemite con el mismo `invoice_number` y `language` en metadata. El numero no cambia; se versiona el PDF.

### 5.10 `payment_provider_reference`

- **Proposito**: representar la relacion entre CID y un proveedor de pagos externo (Stripe, Adyen, etc.). Es la "puerta" entre el billing canonico y el proveedor; CID mantiene un puntero estable a los IDs del proveedor y un historial de webhooks.
- **Campos recomendados**:
  - `provider_reference_id` (UUID, PK).
  - `billing_account_id` (UUID, FK).
  - `provider_name` (enum: `stripe`, `adyen`, `manual`, `enterprise_invoice`; extensible).
  - `stripe_customer_id` (string, nullable; `cus_xxx`).
  - `stripe_subscription_id` (string, nullable; `sub_xxx`).
  - `stripe_price_id` (string, nullable; `price_xxx`).
  - `stripe_product_id` (string, nullable; `prod_xxx`).
  - `stripe_invoice_id` (string, nullable; `in_xxx`).
  - `stripe_payment_intent_id` (string, nullable; `pi_xxx`).
  - `provider_event_id` (string, nullable; id del ultimo webhook relevante; unico por proveedor y tipo de evento).
  - `provider_event_hash` (string, nullable; hash del payload del webhook para detectar replay).
  - `provider_metadata` (jsonb; campos especificos del proveedor no modelados).
  - `last_synced_at` (timestamp; ultima vez que CID consulto o recibio un evento del proveedor).
  - `sync_state` (enum: `synced`, `pending`, `out_of_sync`, `error`; permite detectar divergencias).
  - `created_at`, `updated_at`.
- **Claves**:
  - PK: `provider_reference_id`.
  - Unico: `(provider_name, stripe_customer_id)` cuando aplica.
  - Unico: `(provider_name, provider_event_id)`; idempotencia de webhooks.
- **Relaciones**:
  - `payment_provider_reference` N..1 `billing_account`.
  - `payment_provider_reference` 1..N `invoice_reference` (cada cargo se refleja como factura canonica).
- **Invariantes**:
  - **Esta fase no implementa Stripe.** Los campos `stripe_*` se documentan para preparar la integracion; en la fase actual, el `provider_name` para tenants existentes es `manual` o `enterprise_invoice` (Enterprise con contrato).
  - `provider_event_id` unico por proveedor; si llega un webhook duplicado, se ignora (idempotencia canonica).
  - `sync_state='out_of_sync'` requiere intervencion manual; el billing backend lo reporta en la consola de operaciones.
- **Riesgos**:
  - Webhook duplicado: el proveedor puede enviar el mismo evento varias veces. Mitigacion: `provider_event_id` unico + `provider_event_hash`.
  - Webhook fuera de orden: el evento `invoice.paid` puede llegar antes que `invoice.created`. Mitigacion: el billing backend reordena por `provider_event_id` o por timestamp; si no, espera y reconcilia.
  - Divergencia CID/proveedor: si el canon cambia y Stripe no se actualiza, los cargos pueden no coincidir. Mitigacion: el canon se versiona; cada cambio exige una fase de sincronizacion `CID.SAAS.STRIPE.PRODUCTS.PRICES.1`.

### 5.11 `enterprise_override`

- **Proposito**: modelar las condiciones especiales acordadas con un cliente Enterprise fuera del canon estandar. Es la unica entidad que admite "custom" en cualquier dimension. Cada override es auditable y limitado en alcance.
- **Campos recomendados**:
  - `enterprise_override_id` (UUID, PK).
  - `organization_id` (UUID, FK).
  - `subscription_id` (UUID, FK, nullable; presente si el override aplica a una suscripcion especifica).
  - `override_type` (enum: `price`, `credits`, `modules`, `storage`, `users`, `projects`, `support`, `retention`, `routing`, `multi_currency`; ver seccion 15).
  - `scope` (jsonb; sobre que aplica exactamente: por ejemplo, `{"module_key": "sound_ingest", "monthly_quota": 99999}`).
  - `effective_from` (timestamp).
  - `effective_to` (timestamp, nullable; null significa "hasta nuevo aviso").
  - `approver_id` (UUID, FK a `user` global_admin; quien aprobo el override).
  - `justification` (texto obligatorio; por que se concede el override).
  - `contract_reference` (string, nullable; referencia al contrato firmado; no se almacena el contrato en si).
  - `price_override_eur` (decimal, nullable; para `override_type='price'`).
  - `credit_override_amount` (int, nullable; para `override_type='credits'`).
  - `routing_overrides` (jsonb, nullable; para `override_type='routing'`; por ejemplo, GPU dedicada, region preferente, integracion a medida).
  - `is_active` (bool; permite desactivar sin borrar).
  - `metadata` (jsonb; notas internas).
  - `created_at`, `updated_at`.
- **Claves**:
  - PK: `enterprise_override_id`.
  - Indice: `(organization_id, is_active)`.
- **Relaciones**:
  - `enterprise_override` N..1 `organization`.
  - `enterprise_override` 0..1 `subscription`.
- **Invariantes**:
  - `approver_id` debe ser un `global_admin` (ver `cid_roles_permissions_matrix_v1.md` seccion 7.6).
  - `justification` obligatorio; longitud minima recomendada: 80 caracteres.
  - `effective_to` debe ser posterior a `effective_from` si esta presente.
  - Solo puede haber un override activo por `(organization_id, override_type)`; overrides adicionales desactivan al anterior.
- **Riesgos**:
  - Override abusivo: un `global_admin` podria aplicar overrides sin justificacion. Mitigacion: el override es auditable y la justificacion se revisa periodicamente; ademas, se notifica a otro `global_admin`.
  - Override con seguridad comprometida: si el aprobador cae en compromiso, los overrides aplicados se reauditan. Mitigacion: las sesiones de `global_admin` requieren MFA y se registran en `support_session_*`.
  - Multi-override: una organizacion Enterprise puede acumular multiples overrides (precio + creditos + modulos). El billing backend los aplica en composicion, con prioridad explicita.

### 5.12 `billing_event`

- **Proposito**: registro canonico de todos los eventos de billing que afectan a la suscripcion, al balance de creditos, a las facturas o a la relacion con el proveedor. Es append-only y auditable. **Es la fuente de verdad del historial de billing**, junto con el `credit_ledger_entry`.
- **Campos recomendados**:
  - `billing_event_id` (UUID, PK).
  - `organization_id` (UUID, FK).
  - `billing_account_id` (UUID, FK, nullable; cuando el evento aplica a una cuenta concreta).
  - `subscription_id` (UUID, FK, nullable).
  - `event_type` (enum: `billing_account_created`, `subscription_started`, `subscription_upgraded`, `subscription_downgraded`, `subscription_cancelled`, `subscription_past_due`, `subscription_suspended`, `payment_provider_synced`, `invoice_created`, `invoice_paid`, `invoice_failed`, `credit_package_purchased`, `credits_reserved`, `credits_consumed`, `credits_refunded`, `credits_expired`, `enterprise_override_applied`; ver seccion 20).
  - `from_status` (string, nullable; estado anterior cuando aplica).
  - `to_status` (string, nullable; estado nuevo cuando aplica).
  - `amount_eur` (decimal, nullable; importe afectado por el evento, si aplica).
  - `credit_amount` (int, nullable; creditos afectados por el evento, si aplica).
  - `actor_id` (UUID o `system`; quien origino el evento).
  - `actor_type` (enum: `user`, `admin`, `system`, `provider`; permite distinguir origen humano, admin, automatico, o externo).
  - `provider_event_id` (string, nullable; si el evento provino de un webhook, el id del evento en el proveedor).
  - `request_id` (string, nullable; id de correlacion HTTP).
  - `related_entity_id` (string, nullable; id de la entidad afectada: `credit_ledger_entry_id`, `invoice_reference_id`, etc.).
  - `reason` (texto, nullable; obligatorio para eventos manuales o sensibles).
  - `metadata` (jsonb; datos contextuales).
  - `occurred_at` (timestamp inmutable).
  - `created_at` (timestamp de insercion).
- **Claves**:
  - PK: `billing_event_id`.
  - Indice: `(organization_id, occurred_at DESC)`.
  - Indice: `(event_type, occurred_at DESC)` para consultas por tipo.
  - Indice: `(provider_event_id)`; idempotencia de webhooks.
- **Relaciones**:
  - `billing_event` N..1 `organization`.
  - `billing_event` 0..1 `subscription`.
  - `billing_event` 0..1 `billing_account`.
- **Invariantes**:
  - Append-only: las correcciones se hacen con un nuevo evento que referencia al anterior via `related_entity_id`.
  - `actor_type='provider'` requiere `provider_event_id` no nulo.
  - `reason` obligatorio para `credits_refunded`, `credits_adjusted`, `enterprise_override_applied`, `subscription_cancelled` (cuando lo solicita el cliente).
- **Riesgos**:
  - Volumen: una organizacion activa puede generar cientos de eventos al dia. Mitigacion: el sistema debe particionar por mes o por organizacion y archivar despues del periodo legal.
  - Datos personales: el evento puede incluir `user_id`, `email`, `ip`. Mitigacion: el storage de eventos cumple el periodo legal; tras el periodo, los campos personales se seudonimizan.

### 5.13 `trial_entitlement`

- **Proposito**: modelar la condicion especial de una organizacion en `current_status='trialing'` o `entitlement_flags.is_trial=true`. Define cuantos dias dura, cuantos creditos recibe, que plan activa y cuando se cobra.
- **Campos recomendados**:
  - `trial_entitlement_id` (UUID, PK).
  - `organization_id` (UUID, FK, unique; un trial activo por organizacion).
  - `subscription_id` (UUID, FK; suscripcion trial asociada).
  - `started_at` (timestamp; dia 1 del trial).
  - `ends_at` (timestamp; canon: 14 dias desde `started_at`; puede ser contractual para Enterprise).
  - `trial_plan_key` (enum: `pro` canon; contractual para Enterprise).
  - `trial_credits_granted` (int; canon: 2000 creditos de `trial_balance`).
  - `payment_method_required` (bool; canon: true; si falta, el trial no se inicia).
  - `card_collection_status` (enum: `pending`, `collected`, `failed`, `not_required`).
  - `anti_abuse_flags` (jsonb; resultado del check anti-abuso: `card_fingerprint`, `ip_risk_score`, `email_domain_risk`, `prepaid_card_blocked`).
  - `auto_convert_at_end` (bool; canon: true; si el cliente no cancela, se cobra al dia 15).
  - `target_plan_key` (enum; plan al que convierte si `auto_convert=true`; canon: `pro`).
  - `cancelled_at` (timestamp, nullable; si el cliente cancela durante el trial).
  - `converted_at` (timestamp, nullable; cuando se convirtio a plan de pago).
  - `metadata` (jsonb; cupon aplicado, fuente del trial, etc.).
  - `created_at`, `updated_at`.
- **Claves**:
  - PK: `trial_entitlement_id`.
  - Unico: `(organization_id)`.
- **Relaciones**:
  - `trial_entitlement` 1..1 `organization`.
  - `trial_entitlement` 1..1 `subscription`.
- **Invariantes**:
  - Un trial activo exige `card_collection_status='collected'` (o `not_required` para override Enterprise).
  - `ends_at - started_at <= 14 dias` canon, salvo override Enterprise con `ends_at` contractual documentado.
  - `trial_credits_granted` se asignan a `trial_balance`, separados de `included_monthly_remaining`.
  - `cancelled_at` durante el trial suprime la conversion automatica; los creditos trial no consumidos se pierden al `ends_at`.
- **Riesgos**:
  - Multi-cuenta: el mismo cliente abre varios trials con emails o tarjetas distintas. Mitigacion: `anti_abuse_flags` con `card_fingerprint`, IP, dominio, deteccion de tarjeta quemada; bloqueo de prepago de baja verificacion.
  - Cobro no deseado: si el cliente olvido cancelar, se cobra al dia 15. Mitigacion: emails T-3, T-1, T-0 antes de la conversion; opcion de cancelar en un click desde el email.
  - Trial largo: si el canon cambia y el trial se alarga, los trials antiguos siguen con la duracion original (snapshot de trial).

### 5.14 `beta_entitlement`

- **Proposito**: modelar la condicion especial de una organizacion en `private_beta` o `entitlement_flags.is_beta=true`. Define limites, plan activado, fecha de fin y override opcional sobre modulos experimentales.
- **Campos recomendados**:
  - `beta_entitlement_id` (UUID, PK).
  - `organization_id` (UUID, FK).
  - `subscription_id` (UUID, FK).
  - `beta_plan_key` (enum; plan al que tiene acceso durante el beta; canon: `pro` o `studio`).
  - `started_at` (timestamp).
  - `ends_at` (timestamp; fecha de fin del beta; configurable por invitacion).
  - `monthly_credits_grant` (int; canon: 1000 creditos/mes renovables durante el beta).
  - `feedback_required` (bool; canon: true; el beta tester debe reportar feedback al menos una vez al mes).
  - `last_feedback_at` (timestamp, nullable).
  - `experimental_modules` (array de `module_key`; modulos activados como override beta).
  - `price_lock_in_months` (int; canon: 3; si el beta tester convierte a plan de pago, se le respeta el precio del beta durante N meses).
  - `converted_at` (timestamp, nullable; cuando convirtio a plan de pago real).
  - `metadata` (jsonb; cohort del beta, programa, account manager).
  - `created_at`, `updated_at`.
- **Claves**:
  - PK: `beta_entitlement_id`.
  - Indice: `(organization_id, is_active)`.
- **Relaciones**:
  - `beta_entitlement` N..1 `organization`.
  - `beta_entitlement` 1..1 `subscription`.
- **Invariantes**:
  - `ends_at > started_at`.
  - `monthly_credits_grant` se asigna a `promotional_balance` o `enterprise_balance` (segun el contrato), no a `included_monthly_remaining`.
  - `feedback_required=true` exige un `last_feedback_at` reciente; si pasa el umbral sin feedback, se avisa y se puede cerrar el beta.
- **Riesgos**:
  - Churn al cierre: el beta tester deja el producto al cerrar el beta. Mitigacion: account manager dedicado, onboarding asistido, oferta de conversion.
  - Override sobre modulos experimentales: si el beta incluye modulos `enterprise_only` o `add_on` que no son publicos, se modela como `enterprise_override` adicional. Mitigacion: cada override es auditable.
  - Sobrecarga del cluster: si los beta testers lanzan jobs pesados, el cluster puede saturarse. Mitigacion: `concurrent_ai_jobs` configurado por tenant; rate limit por organizacion.

### 5.15 `demo_entitlement`

- **Proposito**: modelar la condicion especial de una organizacion en `demo_client` o `entitlement_flags.is_demo=true`. Define los limites one-shot, los modulos de preview y el criterio de conversion.
- **Campos recomendados**:
  - `demo_entitlement_id` (UUID, PK).
  - `organization_id` (UUID, FK, unique; un demo activo por organizacion).
  - `subscription_id` (UUID, FK; suscripcion demo asociada).
  - `started_at` (timestamp).
  - `ends_at` (timestamp, nullable; canon: 7 dias desde `started_at`; ampliable a peticion comercial).
  - `one_shot_credits` (int; canon: 50 creditos totales, no renovables).
  - `preview_modules` (array de `module_key`; canon: `project_hub`, `screenwriting` (analisis), `character_bible` (read), `budget` (read), `ai_traceability` (read)).
  - `sales_owner_user_id` (UUID, FK; comercial responsable; eventos `upgrade_prompt_shown` se notifican a este user).
  - `qualification_status` (enum: `cold`, `warm`, `hot`, `converted`; estado del lead).
  - `converted_at` (timestamp, nullable; cuando el demo se convirtio a `private_beta` o `trial` Pro).
  - `metadata` (jsonb; fuente del lead, motivo de la demo, pais, tamano de la productora).
  - `created_at`, `updated_at`.
- **Claves**:
  - PK: `demo_entitlement_id`.
  - Unico: `(organization_id)`.
- **Relaciones**:
  - `demo_entitlement` 1..1 `organization`.
  - `demo_entitlement` 1..1 `subscription`.
  - `demo_entitlement` 0..1 `user` (sales_owner).
- **Invariantes**:
  - `one_shot_credits` no se renueva; una vez consumidos, los jobs IA fallan con `credit_exhausted`.
  - `preview_modules` define los modulos visibles; el resto esta oculto o en candado.
  - El demo no tiene `payment_provider_reference` canonico; el cargo se hace al convertir a `private_beta` o `trial`.
- **Riesgos**:
  - Lead frio: si se regala el demo a leads frios, consume capacidad del cluster sin retorno. Mitigacion: `qualification_status` revisado por el sales owner; el demo se cierra si el lead no responde.
  - Conversion fallida: si el demo expira sin convertir, los datos se conservan 30 dias y luego se archivan frio. Mitigacion: el sales owner recibe eventos `demo_expiring_soon` (futuro).

## 6. Relacion con organization

La organizacion es el tenant de CID (ver `cid_saas_model_contract_v1.md` seccion 3). El billing cuelga de la organizacion de la siguiente forma:

| Nivel | Entidad | Cardinalidad | Notas |
|---|---|---|---|
| Organizacion | `organization` | 1 por tenant | Sujeto del multitenancy. |
| Billing account | `billing_account` | 1 (self-service) o N (Enterprise multi-entidad legal) | Unidad minima de facturacion. |
| Suscripcion | `subscription` | 1 activa por `billing_account` (o N historicas) | Vinculo con el plan contratado. |
| Saldo de creditos | `credit_balance` | 1 por organizacion | Sobrevive a cambios de billing account. |
| Ledger de creditos | `credit_ledger_entry` | N por organizacion | Append-only, fuente de verdad del saldo. |
| Facturas | `invoice_reference` | N por `billing_account` | Facturas canonicas CID; mapean a facturas del proveedor. |
| Override Enterprise | `enterprise_override` | 0..N por organizacion | Solo Enterprise; cada override es auditable. |
| Trial | `trial_entitlement` | 0..1 por organizacion | Solo si `is_trial=true`. |
| Beta | `beta_entitlement` | 0..1 por organizacion | Solo si `is_beta=true`. |
| Demo | `demo_entitlement` | 0..1 por organizacion | Solo si `is_demo=true`. |

Reglas:

- **Una organizacion self-service tiene exactamente un `billing_account` activo.** Enterprise puede tener varios si gestiona entidades legales separadas; en ese caso, cada `billing_account` se factura aparte y los gates futuros operan a nivel `billing_account_id`.
- **Una suscripcion activa por `billing_account`.** El modelo permite varias suscripciones historicas (renovaciones, cambios de plan), pero solo una `active` (o `trialing`, `past_due`) a la vez.
- **El `credit_balance` es de la organizacion, no del `billing_account`.** Esto permite que las bolsas compradas y los creditos incluidos sobrevivan a un eventual cambio de `billing_account` (por ejemplo, una escision de entidad legal).
- **Enterprise es contractual.** Los valores de plan, creditos, limites, soporte, retencion y residencia de datos se definen en el contrato y se modelan como `enterprise_override`. El canon afirma la disponibilidad del tier pero no los valores concretos.
- **Los usuarios, proyectos, almacenamiento y creditos cuelgan de la organizacion.** El `billing_account` solo agrega informacion fiscal; los gates futuros operan principalmente sobre `organization_id`, no `billing_account_id`.

## 7. Subscription status

La suscripcion tiene un campo `current_status` que evoluciona a lo largo del tiempo. Esta seccion define los nueve estados canonicos, que permite cada uno, que bloquea, que conserva, que eventos genera y que mensaje deberia ver el usuario. La maquina de estados es:

```
                  +-----------+
        +-------->|  trialing |--------+
        |         +-----------+        |
        |              |               |
        |              v               |
   +----+----+   +-----------+    +----+----+
   |  active |<--+ enterprise|<-->|  past_  |
   +----+----+   | _manual   |    |  due    |
        |        +-----------+    +----+----+
        |                             |
        v                             v
   +----+----+                  +----+----+
   | beta    |                  |suspend- |
   +----+----+                  |  ed     |
        |                       +----+----+
        v                             |
   +----+----+                        v
   | demo    |                  +----+----+
   +----+----+----------------->|cancelled|<---> expired
                                +---------+
```

Estados canonicos:

### 7.1 `trialing`

- **Que permite**: el tenant usa el plan `pro` canon durante 14 dias, con `trial_credits` en `trial_balance` (2000 creditos canon). Puede ejecutar modulos de la matriz Pro. Puede usar todas las funciones de lectura.
- **Que bloquea**: jobs IA por encima del `credit_estimate` del saldo trial; add-ons no incluidos en Pro trial; exportacion de paquetes no incluidos en Pro trial; cualquier cobro al proveedor antes del dia 15.
- **Que conserva**: datos del proyecto, modulos generados, historial de eventos. Los creditos trial no consumidos se pierden al expirar.
- **Que eventos genera**: `subscription_started` (cuando se inicia el trial), `credits_reserved`, `credits_consumed`, `credits_expired` (al final), `subscription_upgraded` (si convierte), `subscription_cancelled` (si cancela).
- **Mensaje al usuario**: "Estas en tu trial de CID Pro. Te quedan [N] dias y [M] creditos. Para continuar sin interruption, anade un metodo de pago antes del [fecha]."

### 7.2 `active`

- **Que permite**: el tenant usa el plan contratado al 100%. Creditos incluidos del ciclo se asignan. Modulos, limites, exports, integraciones, soporte, todo activo.
- **Que bloquea**: acciones que excedan los limites del plan; modulos no incluidos sin add-on.
- **Que conserva**: datos, creditos comprados, historial.
- **Que eventos genera**: `credits_reserved`, `credits_consumed`, `credits_refunded`, `credits_expired`, `credit_package_purchased`, `limit_reached` (cuando se agotan), `subscription_upgraded`, `subscription_downgraded`, `subscription_renewed` (al cierre del ciclo).
- **Mensaje al usuario**: ninguno especifico; el panel muestra el saldo y los limites normales.

### 7.3 `past_due`

- **Que permite**: el tenant sigue accediendo al producto durante el periodo de reintentos del proveedor (tipicamente 7 dias). Lectura y escritura siguen activas; jobs IA continuan con saldo normal.
- **Que bloquea**: el sistema intenta el cobro de nuevo segun la politica del proveedor; el cliente recibe emails de aviso. Si los reintentos fallan, la suscripcion pasa a `suspended`.
- **Que conserva**: datos, creditos, modulos. Si se reactiva con un nuevo metodo de pago, los creditos incluidos no consumidos del mes en curso se mantienen si el canon del plan lo permite; los creditos comprados nunca se pierden.
- **Que eventos genera**: `subscription_past_due`, `payment_provider_synced`, `invoice_failed`, `invoice_paid` (al recuperar), `subscription_suspended` (si se agotan los reintentos).
- **Mensaje al usuario**: "Tu ultimo pago no se proceso. Estamos reintentando. Actualiza tu metodo de pago desde [URL] para evitar la suspension."

### 7.4 `suspended`

- **Que permite**: lectura del proyecto, `ai_traceability`, exportacion de lo ya generado, descarga de masters historicos. Throttling reducido.
- **Que bloquea**: escritura en modulos (`423 Locked`); jobs IA (`402 Payment Required`); integraciones externas pausadas; nuevos exports premium; cambio de plan.
- **Que conserva**: datos durante el periodo legal (90-365 dias segun plan); el cliente puede solicitar export completo en cualquier momento.
- **Que eventos genera**: `subscription_suspended`, `subscription_reactivated` (al pagar), `data_archived` (al cierre del periodo), `data_purged` (al cierre del periodo legal).
- **Mensaje al usuario**: "Tu suscripcion esta suspendida. Para reactivar el acceso, actualiza el metodo de pago o contacta a soporte. Tus datos se conservan [N] dias."

### 7.5 `cancelled`

- **Que permite**: igual que `suspended` (lectura con throttling, descarga de historicos).
- **Que bloquea**: escritura, jobs IA, integraciones, cambios de plan.
- **Que conserva**: datos durante el periodo legal y, despues, en archivo frio. Pasado el periodo legal, se borran fisicamente.
- **Que eventos genera**: `subscription_cancelled`, `data_archived`, `data_purged`.
- **Mensaje al usuario**: "Tu suscripcion esta cancelada. Para reactivarla, contrata un nuevo plan desde [URL]. Tus datos se conservan [N] dias y se pueden exportar."

### 7.6 `expired`

- **Que permite**: lectura de lo ya generado; descarga de masters historicos; export completo.
- **Que bloquea**: todo lo demas. Es estado terminal desde el punto de vista de la suscripcion; reactivacion requiere nuevo contrato.
- **Que conserva**: datos durante el periodo legal + archivo frio.
- **Que eventos genera**: `subscription_cancelled` (automatico), `data_archived`, `data_purged`.
- **Mensaje al usuario**: "Tu periodo de prueba o suscripcion ha expirado. Para continuar, elige un plan. Tus datos se conservan [N] dias."

### 7.7 `enterprise_manual`

- **Que permite**: configuracion Enterprise con overrides activos. El plan, los creditos, los modulos y los limites siguen los `enterprise_override` activos.
- **Que bloquea**: lo definido por el contrato y los overrides. Si un override fija un limite, ese limite es el canon operativo.
- **Que conserva**: datos, creditos, modulos, limites custom.
- **Que eventos genera**: `enterprise_override_applied` (cuando se anade o cambia un override), `subscription_started`, `subscription_upgraded`, `subscription_downgraded`, eventos de creditos.
- **Mensaje al usuario**: ninguno especifico; la UI muestra el plan Enterprise con los limites y creditos del contrato.

### 7.8 `beta`

- **Que permite**: configuracion `private_beta` con `beta_plan_key`, `monthly_credits_grant` renovables, modulos experimentales activados via override.
- **Que bloquea**: modulos no incluidos en el `beta_plan_key`; cambios de plan automaticos; exportacion fuera de los formatos del beta.
- **Que conserva**: datos y creditos durante la beta; al cerrar, los creditos no consumidos se pierden o se transforman segun el contrato.
- **Que eventos genera**: `subscription_started`, `credits_reserved`, `credits_consumed`, `subscription_upgraded` (al convertir a plan de pago), `subscription_cancelled` (si el beta tester abandona).
- **Mensaje al usuario**: "Estas en el programa beta de CID. Tu acceso termina el [fecha]. Por favor, envia feedback al menos una vez al mes."

### 7.9 `demo`

- **Que permite**: preview limitado de los modulos definidos en `preview_modules` (5 modulos basicos canon). 50 creditos one-shot. 1 organizacion, 1 proyecto, 1 usuario, 5 GB.
- **Que bloquea**: modulos fuera de `preview_modules`; bolsas adicionales; exportacion fuera de lo basico; integraciones externas.
- **Que conserva**: datos del preview; al expirar (7 dias canon), el demo se archiva 30 dias y luego se elimina.
- **Que eventos genera**: `subscription_started`, `credits_reserved`, `credits_consumed` (hasta agotar los 50), `demo_expiring_soon` (futuro), `subscription_cancelled` (al expirar).
- **Mensaje al usuario**: "Estas en un demo de CID. Tienes [N] creditos y [M] dias. Para continuar con acceso completo, contacta a [sales_owner]."

### 7.10 Tabla resumen

| Estado | Lectura | Escritura | Jobs IA | Datos | Reactivacion |
|---|---|---|---|---|---|
| `trialing` | Si | Si | Si (saldo trial) | Mantenidos | Auto-cobro al dia 15 o conversion manual. |
| `active` | Si | Si | Si (saldo normal) | Mantenidos | n/a. |
| `past_due` | Si | Si (limitado) | Si (limitado) | Mantenidos | Actualizar pago. |
| `suspended` | Si (throttling) | No | No | Mantenidos 90-365d | Actualizar pago + meses atrasados. |
| `cancelled` | Si (throttling) | No | No | Mantenidos 90-365d + archivo frio | Nuevo contrato. |
| `expired` | Si (throttling) | No | No | Mantenidos 90-365d + archivo frio | Nuevo contrato. |
| `enterprise_manual` | Si | Si | Si (segun override) | Mantenidos | Segun contrato. |
| `beta` | Si | Si | Si (saldo beta) | Mantenidos durante beta | Conversion a plan de pago. |
| `demo` | Si (preview) | Limitado | Si (saldo one-shot) | Mantenidos 30d | Conversion a `beta` o `trial`. |

## 8. Plan snapshot

El `plan_snapshot` es un registro inmutable del plan que un `billing_account` tenia contratado en un instante dado. Cada vez que la suscripcion cambia de plan (up, down, lateral), se toma un nuevo snapshot y se cierra el anterior con `effective_to`.

### 8.1 Tabla canonica

| Campo | Tipo | Descripcion |
|---|---|---|
| `plan_snapshot_id` | UUID PK | Identificador unico. |
| `subscription_id` | UUID FK | Suscripcion a la que pertenece el snapshot. |
| `canon_version` | string | Version del canon de planes contra la que se genero el snapshot; `cid-plans-modules-matrix-v1` o superior. |
| `plan_key` | enum | `creator`, `pro`, `studio`, `enterprise` (canon); `trial`, `beta`, `demo` (modo). |
| `billing_period` | enum | `monthly`, `yearly`. |
| `price_eur` | decimal | Precio canonico del plan en este snapshot. TBD_PRICING. |
| `yearly_discount_pct` | decimal | Descuento anual canonico; canon: 16.67% (2 meses gratis). |
| `price_after_discount_eur` | decimal | Precio real despues del descuento. TBD_PRICING. |
| `currency` | text | `EUR` canon; extensible. |
| `included_credits_monthly` | int | Creditos incluidos en el plan. TBD_PRICING. |
| `included_storage_gb` | int | Almacenamiento canonico. TBD_PRICING. |
| `included_users` | int | Usuarios canonicos. TBD_PRICING. |
| `included_projects` | int | Proyectos canonicos. TBD_PRICING. |
| `module_keys` | jsonb | Modulos del plan; frozen en el snapshot para evitar reescrituras masivas. |
| `support_level` | enum | `community`, `email`, `priority`, `dedicated`. |
| `retention_days` | int | Retencion canonica; canon: 180d Pro, 365d Studio, contractual Enterprise. |
| `effective_from` | timestamp | Inicio de vigencia. |
| `effective_to` | timestamp, nullable | Fin de vigencia; null = vigente. |
| `change_reason` | text | `new`, `upgrade`, `downgrade`, `renewal`, `admin_correction`, `contract_revision`. |
| `created_at` | timestamp | Insercion; inmutable. |

### 8.2 Por que el snapshot es inmutable

- Un `billing_account` que tuvo plan `creator` el 1 de enero y migro a `pro` el 1 de junio tiene dos snapshots: uno con `effective_from=2026-01-01` y `effective_to=2026-06-01`, y otro con `effective_from=2026-06-01` y `effective_to=null`.
- Los modulos y limites del plan se congelan en el snapshot para que un cambio futuro del canon no altere contratos previos. Por ejemplo, si en 2027 el canon anade un modulo nuevo al plan `pro`, los tenants con `effective_to=2026-12-31` siguen con su catalogo antiguo.
- Los precios se congelan igual: un `plan_snapshot` con `price_eur=29.99` mantiene ese importe durante toda su vigencia, aunque el canon cambie a `price_eur=34.99` en el siguiente ciclo.

### 8.3 Estrategia de reescritura del canon

Cuando el canon de planes cambia, se siguen tres pasos:

1. **Versionar**: el canon de planes declara una nueva `canon_version` (`cid-plans-modules-matrix-v2`).
2. **Snapshot forzado**: al renovar la suscripcion de cada tenant, se cierra el snapshot actual y se crea uno nuevo con la nueva `canon_version`.
3. **No hay backfill**: los tenants con `effective_to` antiguo no se migran retroactivamente; su snapshot sigue valiendo.

Esta estrategia evita que un cambio del canon altere contratos existentes. Si el canon cambia un precio en sentido favorable (bajada), el tenant se beneficia en la siguiente renovacion; el ciclo actual mantiene el precio congelado.

### 8.4 Cambio de plan y prorateo

El prorateo del cambio de plan se modela en el `credit_ledger_entry` con `entry_type='credit_grant'` (cuando el tenant tiene creditos no consumidos del plan anterior) o `entry_type='credit_adjustment'` (cuando hay compensacion manual). Ver seccion 10.

Ejemplo: un tenant en plan `creator` a mitad de mes actualiza a `pro`. Los creditos incluidos del mes en curso se recalculan: se devuelven los del plan anterior como `credit_refund` y se conceden los del plan nuevo como `credit_grant`. El `credit_balance.included_monthly_remaining` refleja el nuevo saldo. Los creditos comprados (`purchased_balance`) no se tocan; siguen siendo del tenant.

## 9. Credit balance

El `credit_balance` es el saldo agregado de creditos de una organizacion. Aunque se desglosa en sub-saldos por origen, **se consulta y se opera como un numero unico desde el billing backend**. La UI puede desglosarlo, pero la fuente de verdad es el `credit_balance`.

### 9.1 Estados del credito

Canon (ver `cid_pricing_canonical_v1.md` seccion 9):

| Estado | Significado |
|---|---|
| `available` | Credito activo y consumible. |
| `reserved` | Credito bloqueado por una reserva en curso (job IA en ejecucion). |
| `consumed` | Credito ya gastado; ya no esta disponible. |
| `expired` | Credito que vencio por su `expires_at`; ya no esta disponible. |
| `refunded` | Credito devuelto al tenant por una anulacion o downgrade. |
| `adjusted` | Credito modificado manualmente por un admin (compensacion, error, regalo). |

### 9.2 Sub-saldos canonicos

| Sub-saldo | Origen | Renovacion | Caducidad canonica |
|---|---|---|---|
| `included_monthly_remaining` | Plan contratado | Mensual; se resetea cada ciclo | Fin del ciclo; no consumido se pierde. |
| `purchased_balance` | Bolsas de creditos compradas | No se renueva | Por bolsa; canon: 12 meses desde la compra. |
| `promotional_balance` | Promociones, beta, regalos | Segun campana | Segun campana; canon: 6 meses. |
| `trial_balance` | Trial | No se renueva | Fin del trial + 7d. |
| `enterprise_balance` | Override Enterprise o contrato | Segun contrato | Segun contrato; canon: anual. |
| `reserved_active` | Reservas en curso (jobs IA) | n/a | Liberadas al cerrar el job. |
| `consumed_period` | Creditos consumidos en el ciclo | n/a | Metrica; no se usa para gates. |
| `expired_total` | Creditos caducados historicos | n/a | Metrica; auditable. |
| `refunded_total` | Creditos devueltos historicos | n/a | Metrica; auditable. |
| `adjusted_total` | Creditos ajustados historicos | n/a | Metrica; auditable. |

### 9.3 Orden de consumo canonico

El `credit_balance` se consume siempre en el mismo orden, independientemente del modulo o del job. Esto asegura que el tenant siempre use primero lo mas volatil y conserve lo mas estable:

1. **`trial_balance`** y **`promotional_balance`** (los mas volatiles; caducan pronto).
2. **`included_monthly_remaining`** (los incluidos del plan; caducan al fin del ciclo).
3. **`purchased_balance`** en orden FIFO por `expires_at` (los mas proximos a caducar primero).
4. **`enterprise_balance`** (los mas estables; bajo contrato).

Reglas adicionales:

- Si un `enterprise_override` fija un orden distinto, se respeta el override como una excepcion documentada.
- Si un sub-saldo llega a cero, se pasa al siguiente en el orden.
- El ledger registra cada consumo con `entry_type='credit_consume'` y desglosa cuantos creditos se tomaron de cada sub-saldo.

### 9.4 Renovacion mensual

Al inicio de cada ciclo:

- `included_monthly_remaining` se resetea al valor del `plan_snapshot.included_credits_monthly` activo.
- `consumed_period` se cierra y se archiva en `consumed_history` (futuro).
- `expired_total` se incrementa por la cantidad de creditos incluidos no consumidos del ciclo anterior.
- `reserved_active` se cierra; las reservas huerfanas se reconcilian con un job batch.

Los creditos comprados (`purchased_balance`) no se tocan. Los trial, beta, demo y Enterprise se rigen por sus propias reglas (ver secciones 7.1, 7.7, 7.8, 7.9).

### 9.5 Caducidad

Las bolsas compradas caducan a los 12 meses desde la compra (canon). El sistema corre un job batch diario que:

- Detecta bolsas con `expires_at < now()`.
- Genera `credit_ledger_entry` con `entry_type='credit_expire'` por el saldo restante.
- Decrementa `purchased_balance` e incrementa `expired_total`.
- Emite `billing_event` con `event_type='credits_expired'`.

El tenant recibe notificaciones T-30, T-7 y T-1 antes de la caducidad de cada bolsa.

## 10. Credit ledger entry

El `credit_ledger_entry` es el registro append-only de todos los movimientos de creditos de una organizacion. Es la fuente de verdad del saldo: el `credit_balance` se puede reconstruir a partir del ledger. Si hay divergencia, el ledger gana.

### 10.1 Tipos de movimiento

| `entry_type` | Cuando se usa | Impacto en sub-saldos |
|---|---|---|
| `credit_grant` | Concesion de creditos: included mensual, trial, beta, override. | Incrementa el sub-saldo correspondiente. |
| `credit_purchase` | Compra de una bolsa. | Incrementa `purchased_balance`. |
| `credit_reserve` | Reserva al iniciar un job IA. | Mueve de sub-saldo origen a `reserved_active`. |
| `credit_release` | Liberacion de reserva (job fallo tecnico o cancelado por el usuario). | Mueve de `reserved_active` al sub-saldo origen. |
| `credit_consume` | Consumo definitivo al terminar el job. | Decrementa `reserved_active`; incrementa `consumed_period`. |
| `credit_refund` | Devolucion (downgrade, cancelacion, error). | Incrementa el sub-saldo configurado (puede ser `purchased_balance` o `promotional_balance`). |
| `credit_expire` | Caducidad de bolsa o included no consumido. | Decrementa el sub-saldo; incrementa `expired_total`. |
| `credit_adjustment` | Modificacion manual por admin. | Incrementa o decrementa el sub-saldo correspondiente; incrementa `adjusted_total`. |

### 10.2 Campos canonicos

| Campo | Tipo | Descripcion |
|---|---|---|
| `credit_ledger_entry_id` | UUID PK | Identificador unico. |
| `organization_id` | UUID FK | Organizacion afectada. |
| `credit_balance_id` | UUID FK | Saldo afectado. |
| `credit_package_purchase_id` | UUID FK, nullable | Si es de una bolsa, referencia. |
| `subscription_id` | UUID FK, nullable | Si aplica a un ciclo de suscripcion. |
| `entry_type` | enum | Uno de los 8 tipos de la seccion 10.1. |
| `credit_amount` | int | Cantidad de creditos del movimiento (positivo o negativo). |
| `sub_balance_from` | enum, nullable | Sub-saldo origen (para `credit_reserve`, `credit_release`, `credit_consume`, `credit_refund`, `credit_expire`). |
| `sub_balance_to` | enum, nullable | Sub-saldo destino. |
| `idempotency_key` | string, unique | Clave unica de operacion; permite reintentar sin duplicar. |
| `provider_event_id` | string, nullable | Id del webhook del proveedor si el movimiento lo origino. |
| `actor_id` | UUID o `system` | Quien origino el movimiento. |
| `actor_type` | enum | `user`, `admin`, `system`, `provider`. |
| `related_entity_type` | string, nullable | `project`, `storyboard`, `sound_ingest`, etc. |
| `related_entity_id` | UUID, nullable | Id de la entidad que origino el movimiento. |
| `reason` | text, nullable | Obligatorio para `credit_adjustment`, `credit_refund` no automatico. |
| `metadata` | jsonb | Datos contextuales; por ejemplo, desglose por sub-saldo. |
| `occurred_at` | timestamp | Inmutable. |
| `created_at` | timestamp | Insercion; inmutable. |

### 10.3 Idempotencia

Cada movimiento lleva un `idempotency_key` unico. Esto permite reintentar operaciones de billing (cobro, devolucion, ajuste) sin duplicar efectos. Si dos requests llegan con el mismo `idempotency_key`, el segundo se rechaza o se ignora segun el caso.

Las claves se construyen como:

- `credit_grant`: hash de `(subscription_id, plan_snapshot_id, period_start)`.
- `credit_purchase`: hash de `(billing_account_id, credit_package_id, provider_invoice_id)`.
- `credit_reserve`: hash de `(job_id, sub_balance_from, credit_amount)`.
- `credit_consume`: id del `credit_reserve` correspondiente.
- `credit_refund`: hash de `(credit_ledger_entry_id_origen, request_id)`.
- `credit_expire`: hash de `(credit_package_purchase_id, expires_at)`.
- `credit_adjustment`: generado por el admin, unico por operacion.

### 10.4 Reconciliacion

El sistema corre un job batch diario que:

- Compara `credit_balance.included_monthly_remaining + purchased_balance + ...` con la suma del ledger por sub-saldo.
- Si hay divergencia, genera una alerta `billing_event` con `event_type='balance_drift_detected'` y congela nuevas reservas hasta resolver.
- La resolucion exige un admin con permisos; se documenta en `credit_adjustment`.

## 11. Credit reservation

La reserva de creditos es el mecanismo por el cual el billing backend autoriza un job IA, bloquea el `credit_estimate` del sub-saldo correspondiente y, al terminar el job, ejecuta `credit_consume` o `credit_release` segun el resultado.

### 11.1 Flujo canonico

```
job_start                   estimate_evaluated                job_done
   |                              |                                |
   v                              v                                v
[estimate=300]  --->  [reserve 300, status='reserved']  --->  [consume 250, release 50]
                                                   \           /
                                                    \         /
                                              [fail tecnico]
                                                     |
                                                     v
                                          [release 300, status='available']
                                                     |
                                                     v
                                          [fail por error de usuario]
                                                     |
                                                     v
                                          [consume 300, no release]
```

### 11.2 Estados de la reserva

| Estado | Significado |
|---|---|
| `pending` | Reserva creada, todavia no movio creditos a `reserved_active`. |
| `reserved` | Reserva activa; creditos en `reserved_active`. |
| `consumed_ok` | Job termino OK; consumo parcial o total. |
| `consumed_full` | Job termino en error de usuario; consumo total del `credit_estimate`. |
| `released_tech` | Job fallo tecnico; reserva liberada. |
| `released_admin` | Admin libero la reserva manualmente. |
| `released_orphan` | Job nunca cerro la reserva; reaper la libero. |

### 11.3 Reaper de reservas huerfanas

Una reserva queda huerfana si el job termina sin cerrar la reserva (crash del worker, error de red, etc.). El sistema corre un reaper cada 6 horas que:

- Detecta reservas con `status='reserved'` y `reserved_at < now() - 24h`.
- Verifica que el job no este activo en el cluster.
- Si el job esta activo, lo deja en `reserved` y escala el caso.
- Si el job esta cerrado o no existe, libera la reserva con `status='released_orphan'` y devuelve los creditos al sub-saldo origen.

Esto evita que los tenants pierdan creditos por errores tecnicos.

### 11.4 Estimacion vs consumo real

El `credit_estimate` se calcula al inicio del job con un margen (canon: 10% sobre el coste medio). El `credit_consume` final es el consumo real. Si el consumo real es menor, la diferencia se libera como `credit_release` y vuelve al sub-saldo origen. Esto es un beneficio para el tenant: paga solo por lo que consume.

Si el consumo real es mayor, el job falla con `credit_exhausted` antes de agotar la reserva. Esto es un caso raro; el canon actual considera esto un bug, no un feature.

## 12. Credit package purchase

La compra de una bolsa de creditos genera una `credit_package_purchase` y un `credit_ledger_entry` con `entry_type='credit_purchase'`. Las bolsas se modelan como entidades de primera clase para que el saldo de creditos comprados sea siempre trazable a una factura y un cargo en el proveedor.

### 12.1 Bolsas canonicas

Del canon (ver `cid_pricing_canonical_v1.md` seccion 10):

| Bolsa | Creditos | Precio | Precio por 1k cr | Validez | `credit_package_id` canonico |
|---|---|---|---|---|---|
| Starter 500 | 500 | 49€ | 98€ | 12 meses | `starter_500_pack` |
| Pro 1500 | 1500 | 119€ | 79.3€ | 12 meses | `pro_1500_pack` |
| Pro 3000 | 3000 | 229€ | 76.3€ | 12 meses | `pro_3000_pack` |
| Studio 10000 | 10000 | 699€ | 69.9€ | 12 meses | `studio_10000_pack` |
| Premium custom | 5000-50000 | contractual | 65-79€ | 12 meses o anual | `premium_custom_pack` |
| Enterprise custom | 50000+ | contractual | 30-50€ | anual o plurianual | `enterprise_custom_pack` |

**Nota**: los precios y los ratios precio/1000 creditos son TBD_PRICING hasta que se cierre la fase de canon. Los nombres de las bolsas y la cardinalidad de creditos son canon v1; los importes pueden ajustarse en la fase `CID.SAAS.PRICING.CANONICALIZATION.2` sin tocar el modelo de datos.

### 12.2 Campos de la compra

| Campo | Tipo | Descripcion |
|---|---|---|
| `credit_package_purchase_id` | UUID PK | Identificador unico. |
| `organization_id` | UUID FK | Organizacion compradora. |
| `billing_account_id` | UUID FK | Billing account. |
| `credit_package_id` | string | Codigo canonico de la bolsa (`starter_500_pack`, etc.). |
| `credits_granted` | int | Creditos concedidos. |
| `price_eur` | decimal | Precio pagado. TBD_PRICING. |
| `currency` | text | `EUR` canon. |
| `purchased_at` | timestamp | Fecha de compra. |
| `expires_at` | timestamp | Caducidad; canon: 12 meses desde `purchased_at`. |
| `status` | enum | `active`, `fully_consumed`, `partially_consumed`, `expired`, `refunded`. |
| `invoice_reference_id` | UUID FK | Factura en la que se cobro la bolsa. |
| `payment_provider_reference_id` | UUID FK | Cargo en el proveedor. |
| `provider_charge_id` | string, nullable | Id del cargo en Stripe (futuro). |
| `is_gift` | bool | Si la bolsa fue un regalo. |
| `gifted_by_org_id` | UUID, nullable | Si es regalo, organizacion que lo concedio. |
| `metadata` | jsonb | Cupon, campana, motivo. |
| `created_at`, `updated_at` | timestamps | Auditoria. |

### 12.3 Trazabilidad

Cada `credit_package_purchase` referencia:

- El `invoice_reference` que la facturo.
- El `payment_provider_reference` que la cobro.
- El `credit_ledger_entry` con `entry_type='credit_purchase'` que registro la entrada de creditos.

Esta trazabilidad permite responder preguntas como: "De donde vienen estos 800 creditos que me quedan?" mostrando la bolsa, la factura, el cargo y la fecha. Tambien permite auditoria contable: el importe pagado por bolsas y los creditos concedidos coinciden siempre con la factura y el cargo del proveedor.

### 12.4 Regalos y promociones

Las bolsas pueden ser regalos (`is_gift=true`). En ese caso, `gifted_by_org_id` apunta a la organizacion que las concedio (un partner, un account manager, un evangelista). El cargo lo paga quien regala; el credito se concede al destinatario. Esto permite flujos B2B2C (por ejemplo, una escuela regalando CID Pro a sus alumnos) sin alterar el modelo canonico.

Las promociones (campanas de marketing) usan el mismo flujo pero con `payment_provider_reference` ausente (no hay cargo real) y `metadata.promotion_id` presente. Los creditos se conceden a `promotional_balance` en lugar de `purchased_balance`, y caducan a los 6 meses canon (o lo que diga la campana).

## 13. Invoice reference behavior

La `invoice_reference` representa la factura canonica CID. Esta seccion describe su ciclo de vida, su mapeo con el proveedor externo y sus invariantes operativas.

### 13.1 Ciclo de vida

```
[draft]  --emit-->  [open]  --pay-->  [paid]
                         |             |
                         |             +-->  [past_due] (parcial)  -->  [uncollectible]
                         |
                         +-->  [void] (anulacion)
```

- **`draft`**: la factura se esta generando. Es modificable; aun no se ha emitido al cliente ni al proveedor.
- **`open`**: la factura se emitio. El cliente la ve en su panel; el proveedor tiene una sesion de cobro activa. Es inmutable salvo para `void`.
- **`paid`**: el cargo del proveedor se completo. La factura esta saldada. Es inmutable.
- **`past_due`**: el cargo del proveedor fallo parcialmente; el sistema reintenta. La factura sigue abierta y el tenant sigue con acceso `past_due`.
- **`void`**: la factura se anulo (error de emision, devolucion total). Los creditos asociados se devuelven via `credit_refund`. La factura sigue en el historial pero no se contabiliza.
- **`uncollectible`**: el sistema agoto los reintentos y la factura se marca como incobrable. La suscripcion pasa a `suspended`.

### 13.2 Emision idempotente

La emision de la factura lleva un `idempotency_key` por intento. Esto permite reintentos seguros: si el billing backend falla a mitad de emision, el reintento no genera una factura duplicada. El `idempotency_key` se construye como `hash(credit_package_purchase_ids + subscription_id + period_start + attempt_number)`.

### 13.3 Mapeo con el proveedor

Cuando hay `payment_provider_reference.provider_name='stripe'`, la factura canonica CID se mapea con la factura del proveedor via `provider_invoice_id`. El mapeo es:

- **Emision CID**: se crea `invoice_reference` con `status='open'` y `provider_invoice_id=null`. Se inicia el cargo en el proveedor; el proveedor emite su propia factura con un `in_xxx` id.
- **Webhook `invoice.created` del proveedor**: se actualiza `invoice_reference` con `provider_invoice_id` y `provider_invoice_url`.
- **Webhook `invoice.paid` del proveedor**: se actualiza `invoice_reference.status='paid'`.
- **Webhook `invoice.payment_failed` del proveedor**: se actualiza `invoice_reference.status='past_due'` y `subscription.current_status='past_due'`.

Esta fase documenta el mapeo pero **no implementa Stripe**. La integracion se hara en `CID.SAAS.STRIPE.PRODUCTS.PRICES.1` y `CID.SAAS.STRIPE.WEBHOOKS.1`.

### 13.4 Discrepancias CID vs proveedor

Si el canon CID y el canon del proveedor divergen (por ejemplo, CID cobra 49€ y el cargo en el proveedor es 50€ por una fluctuacion de moneda), el canon CID es la verdad para el tenant: el cliente ve 49€ en su panel y paga 49€. La diferencia de 1€ se reconcilia con un `credit_adjustment` a favor del tenant o del proveedor segun el caso. Esta politica se aplica tambien a discrepancias de redondeo, IVA y comisiones del proveedor.

### 13.5 Multi-idioma

La factura canonica CID puede emitirse en multiples idiomas. La primera emision se hace en el idioma del tenant (detectado por `organization.country` y `organization.preferred_language`). Si el tenant pide otra emision en otro idioma, se genera una `invoice_reference` adicional con el mismo `invoice_number` pero `metadata.language` distinto. El numero no cambia para evitar duplicidad contable.

## 14. Payment provider reference behavior

La `payment_provider_reference` es la "puerta" entre CID y el proveedor de pagos. Esta seccion describe su ciclo de vida, su sincronizacion con el proveedor y su manejo de webhooks.

### 14.1 Estados de sincronizacion

| Estado | Significado |
|---|---|
| `synced` | CID y el proveedor estan alineados; el ultimo webhook o consulta confirma coincidencia. |
| `pending` | CID envio una operacion al proveedor y espera confirmacion. |
| `out_of_sync` | CID y el proveedor divergen; requiere intervencion. |
| `error` | La operacion con el proveedor fallo de manera irrecuperable. |

### 14.2 Reintentos y backoff

Cuando una operacion con el proveedor falla por error transitorio (timeout, 5xx), el sistema reintenta con backoff exponencial: 1s, 2s, 4s, 8s, 16s, 32s, 64s, 128s, 256s, 512s. Tras 10 reintentos, la operacion se marca como `error` y se notifica a operaciones. Esto se aplica a:

- Crear customer en el proveedor.
- Crear suscripcion.
- Actualizar suscripcion (cambio de plan).
- Cancelar suscripcion.
- Crear cargo (compra de bolsa).
- Crear reembolso.

### 14.3 Webhooks idempotentes

Cada webhook del proveedor lleva un `provider_event_id` unico. El billing backend lo registra en `payment_provider_reference.provider_event_id` con una `idempotency_key` unica. Si llega el mismo evento dos veces, el segundo se ignora. Esto cubre el caso comun de webhooks duplicados por reintentos del proveedor.

El orden de los webhooks no se garantiza. El sistema maneja el caso de un evento fuera de orden (`invoice.paid` llega antes que `invoice.created`) con las siguientes reglas:

- Si el evento recibido es de un id que CID ya conoce y cuyo `occurred_at` es anterior al ultimo procesado, se ignora.
- Si el evento es de un id desconocido pero hay un evento posterior ya procesado, se intenta reprocesar en orden. Si no es posible, se encola para reconciliacion.

### 14.4 Reconciliacion periodica

Ademas de webhooks, el sistema corre una reconciliacion periodica (canon: cada 6 horas) que:

- Lista las suscripciones activas en CID.
- Para cada una, consulta el estado en el proveedor.
- Compara `subscription.current_status`, `subscription.plan_key`, `subscription.renews_at` con la respuesta del proveedor.
- Si hay divergencia, genera un `billing_event` con `event_type='provider_sync_drift'` y notifica a operaciones.

La reconciliacion es esencial para detectar divergencias cuando un webhook se perdio o se proceso mal.

### 14.5 Multi-proveedor

El modelo admite multiples proveedores (`provider_name='stripe'`, `provider_name='adyen'`, etc.) pero la fase actual no los implementa. La idea es que un tenant pueda migrar de proveedor sin perder su historial: el `billing_account` se mantiene, la suscripcion se cierra en el proveedor antiguo y se crea una nueva en el nuevo. El `credit_balance` y el `credit_ledger_entry` no se tocan.

## 15. Enterprise override semantics

Los `enterprise_override` son la unica via para personalizar el canon fuera de los parametros estandar. Esta seccion describe los tipos, su composicion, su aprobacion y su auditoria.

### 15.1 Tipos de override

| Tipo | Que afecta | Ejemplo |
|---|---|---|
| `price` | Precio del plan | Plan Studio a 599€/mes en lugar de 699€/mes. |
| `credits` | Creditos incluidos | 5000 creditos/mes en lugar de 2000 canon. |
| `modules` | Modulos activados | Acceso a `enterprise_only` sin ser Enterprise publico. |
| `storage` | Almacenamiento | 5 TB en lugar de 1 TB canon. |
| `users` | Usuarios incluidos | 50 usuarios en lugar de 10 canon. |
| `projects` | Proyectos incluidos | 200 proyectos en lugar de 50 canon. |
| `support` | Nivel de soporte | `dedicated` con account manager. |
| `retention` | Retencion de datos | 5 anos en lugar de 365d canon. |
| `routing` | Routing de jobs | GPU dedicada, region preferente, integracion a medida. |
| `multi_currency` | Moneda de cobro | USD o MXN en lugar de EUR canon. |

### 15.2 Composicion de overrides

Una organizacion Enterprise puede tener varios overrides activos. El billing backend los compone siguiendo el orden:

1. **Overrides de plan** (modulos, creditos, storage, users, projects): suman al plan canon. Por ejemplo, `plan_key='studio'` + override `credits=5000` resulta en un Studio con 5000 creditos.
2. **Overrides de precio**: se aplican despues de los anteriores, sobre el plan modificado. Por ejemplo, override `price=599` sobre Studio canon (699) + 5000 creditos (canon 2000) resulta en 599€ con 5000 creditos.
3. **Overrides de soporte, retencion, routing, multi_currency**: ortogonales; se aplican al final.
4. **Overrides contradictorios**: si dos overrides activos contradicen un campo, gana el mas reciente (`created_at` mayor). El override perdedor se desactiva automaticamente.

### 15.3 Aprobacion

Todos los overrides requieren aprobacion por un `global_admin`. El flujo canonico:

1. Account manager comercial identifica la necesidad del cliente.
2. Account manager redacta propuesta y la envia a un `global_admin` con `permissions.global_admin.global_admin_override_billing`.
3. `global_admin` revisa, aprueba o rechaza. Si aprueba, crea el `enterprise_override` con `actor_id=global_admin_user_id` y `justification`.
4. El sistema genera `billing_event` con `event_type='enterprise_override_applied'`.
5. El `credit_balance` y los gates reflejan el override desde ese momento.

Los overrides no son inmutables: se pueden modificar o desactivar con un nuevo evento y una nueva justificacion. El historial se conserva.

### 15.4 Auditoria

El sistema audita todos los overrides con:

- `approver_id` (quien aprobo).
- `justification` (por que se aprobo).
- `effective_from` y `effective_to` (cuando aplica).
- `created_at` y `updated_at`.
- `billing_event` asociado (trazabilidad).

Una revision periodica (canon: trimestral) reaudita los overrides activos. Los overrides sin uso o con justificacion obsoleta se desactivan o renuevan.

## 16. Trial, demo y beta

Los modos `trialing`, `demo` y `beta` se modelan como entidades separadas (`trial_entitlement`, `beta_entitlement`, `demo_entitlement`) con su propio estado, sus propios limites y su propia conversion. Esta seccion describe la semantica de cada uno y las reglas de conversion.

### 16.1 Trial

- **Duracion canonica**: 14 dias.
- **Plan canonico**: `pro`.
- **Creditos canonicos**: 2000 creditos en `trial_balance` (sub-saldo separado).
- **Metodo de pago**: obligatorio. Sin tarjeta, el trial no se inicia. La tarjeta se valida con un cargo simbolico canon (canon: 1€) que se reembolsa de inmediato.
- **Conversion automatica**: al dia 15, si el trial no se cancelo, la suscripcion se convierte en `pro` canonico y se cobra el plan completo.
- **Conversion manual**: el usuario puede convertir el trial en `pro` o `studio` en cualquier momento del periodo.
- **Cancelacion**: durante el trial, el usuario puede cancelar. Los creditos trial no consumidos se pierden al `ends_at`.
- **Anti-abuso**: `anti_abuse_flags` con `card_fingerprint`, IP, dominio de email, tarjeta quemada. Bloqueo de tarjetas prepago de baja verificacion. Limite canon: 1 trial por huella de tarjeta y 1 trial por huella de email.

### 16.2 Demo

- **Duracion canonica**: 7 dias.
- **Plan canonico**: ninguno; `preview_modules` definen que se ve.
- **Creditos canonicos**: 50 creditos one-shot en `promotional_balance`.
- **Metodo de pago**: no se requiere.
- **Limites canonicos**: 1 organizacion, 1 proyecto, 1 usuario, 5 GB.
- **Conversion**: al convertir, la suscripcion pasa a `beta` (recomendado) o a `trial` Pro. La conversion no es automatica; requiere un sales owner con `qualification_status='warm'` o `'hot'`.
- **Caducidad**: 7 dias canon. Ampliable manualmente por el sales owner.
- **Datos**: al expirar, los datos se conservan 30 dias y luego se archivan frio.

### 16.3 Beta

- **Duracion canonica**: abierta; configurable por el programa.
- **Plan canonico**: `pro` o `studio` segun el beta.
- **Creditos canonicos**: 1000 creditos/mes renovables en `promotional_balance` o `enterprise_balance`.
- **Metodo de pago**: requerido para convertir; no requerido durante el beta.
- **Feedback obligatorio**: el beta tester debe reportar feedback al menos una vez al mes. Si pasa el umbral, se avisa al account manager.
- **Modulos experimentales**: el beta puede incluir modulos activados como override. Estos modulos pueden ser `enterprise_only` o `add_on` que no son publicos.
- **Conversion**: al cerrar el beta, el beta tester puede convertir a plan de pago con `price_lock_in_months` canon (3 meses) durante los cuales se le respeta el precio del beta.
- **Salida**: si el beta tester abandona, los creditos no consumidos se pierden. Los datos del proyecto se conservan 90 dias.

### 16.4 Conversion entre modos

```
   +-----------+   convertir    +--------+
   |   demo    | -------------> |  beta  |
   +-----------+                +--------+
        |                            |
        | convertir a trial          | convertir a trial o plan de pago
        v                            v
   +-----------+                +--------+
   |  trial    | -------------> |  plan  |  (creator / pro / studio / enterprise)
   +-----------+                +--------+
```

La conversion entre modos no es automatica; cada una exige una decision humana (sales owner, account manager, o el propio usuario) y genera los `billing_event` correspondientes (`subscription_started`, `subscription_upgraded`, etc.).

### 16.5 Coexistencia con billing canon

- `trial_entitlement` y `demo_entitlement` son entidades de primera clase. **No usan `subscription.current_status='active'`** durante el trial/demo. Usan `current_status='trialing'` o `'demo'` con la entidad de modo adjunta.
- `beta_entitlement` puede coexistir con `subscription.current_status='active'` o `='enterprise_manual'`. El beta es un overlay; la suscripcion real es la que esta debajo.
- El canon afirma que **una organizacion solo puede estar en un modo a la vez**. No se puede ser trial y beta simultaneamente; no se puede ser demo y plan de pago simultaneamente. La conversion cierra el modo origen antes de abrir el destino.

## 17. Gates derivados

Los gates son las reglas que el billing backend aplica para permitir, throttlear o bloquear operaciones del tenant en funcion de su estado de suscripcion, su saldo de creditos, su plan, sus overrides Enterprise y sus modulos contratados. Esta seccion describe los gates canonicos.

### 17.1 Dimensiones de gate

| Dimension | Que se chequea | Bloquea |
|---|---|---|
| Suscripcion | `subscription.current_status` en `{active, trialing, past_due, enterprise_manual, beta, demo}` | Bloquea escritura, jobs IA, integraciones si no esta en ese set. |
| Plan | `plan_snapshot.module_keys` y `plan_snapshot.included_*` | Bloquea modulos no incluidos, limites excedidos. |
| Creditos | `credit_balance.included_monthly_remaining + purchased_balance + ...` y `reserved_active` | Bloquea jobs IA si `available - reserved_active < credit_estimate`. |
| Modulos | Override explicito del plan o `enterprise_override` | Modulos `enterprise_only` requieren override; modulos `add_on` requieren compra. |
| Almacenamiento | Suma del tamano de uploads y outputs contra `plan_snapshot.included_storage_gb + storage_override` | Bloquea uploads si excede. |
| Usuarios | Conteo de usuarios activos contra `plan_snapshot.included_users + users_override` | Bloquea invitaciones si excede. |
| Proyectos | Conteo de proyectos activos contra `plan_snapshot.included_projects + projects_override` | Bloquea creacion de proyectos si excede. |
| Override | `enterprise_override.is_active=true` con el `override_type` correspondiente | Modifica el resultado del gate. |

### 17.2 Jerarquia de gates

Los gates se aplican en el siguiente orden:

1. **Gate de suscripcion**: si la suscripcion no esta en estado activo, se bloquea todo lo no leible. El codigo canonico de bloqueo es `subscription_not_active` (HTTP 402).
2. **Gate de plan**: si el modulo solicitado no esta en `plan_snapshot.module_keys` y no hay `enterprise_override` que lo autorice, se bloquea. El codigo canonico es `module_not_included` (HTTP 402).
3. **Gate de creditos**: si el saldo disponible (incluido + comprado + trial + beta + enterprise - reserved_active) es menor que el `credit_estimate`, se bloquea. El codigo canonico es `credits_exhausted` (HTTP 402).
4. **Gate de almacenamiento**: si el upload excede el almacenamiento disponible, se bloquea. El codigo canonico es `storage_exhausted` (HTTP 402).
5. **Gate de usuarios**: si la invitacion excede el limite, se bloquea. El codigo canonico es `seat_limit_reached` (HTTP 402).
6. **Gate de proyectos**: si la creacion excede el limite, se bloquea. El codigo canonico es `project_limit_reached` (HTTP 402).
7. **Gate de add-ons**: si el modulo es `add_on` y no esta comprado, se bloquea con un CTA para comprar. El codigo canonico es `add_on_required` (HTTP 402).
8. **Gate Enterprise**: si el modulo es `enterprise_only` y no hay override, se bloquea con un CTA para contactar a ventas. El codigo canonico es `enterprise_only` (HTTP 402).

### 17.3 Evaluacion de gates

Cada operacion del tenant pasa por una evaluacion de gates. La evaluacion es sincrona para operaciones de escritura y asincrona para operaciones de lectura (los lectores reciben una vista `best_effort` con campos de limite visibles pero no bloqueantes).

La evaluacion sincrona se hace con un servicio `BillingGateService` que recibe:

- `organization_id`.
- `operation_type` (`create_project`, `submit_ai_job`, `upload_master`, `invite_user`, `export_package`, etc.).
- `module_key` (cuando aplica).
- `credit_estimate` (cuando aplica).
- `actor_id` y `actor_type` (para el evento de auditoria).

El servicio devuelve:

- `allow`: bool.
- `reason`: codigo canonico del bloqueo, si aplica.
- `message`: mensaje canonico.
- `cta`: accion sugerida (comprar bolsa, actualizar plan, contactar a ventas).
- `metadata`: contexto adicional (saldo disponible, plan actual, modulo solicitado).

El backend que origina la operacion traduce `allow=false` en una excepcion HTTP 402 con el codigo canonico y el mensaje. La UI lee el codigo canonico y muestra el CTA correspondiente.

### 17.4 Throttling vs bloqueo

No todos los estados de la suscripcion bloquean por completo:

- `active`: sin throttling.
- `trialing`: throttling leve; avisos de "trial acaba pronto".
- `past_due`: throttling medio; avisos de "actualiza tu pago".
- `suspended`: throttling fuerte; lectura con limites, escritura bloqueada.
- `cancelled` y `expired`: throttling fuerte; lectura con limites largos, escritura bloqueada.
- `enterprise_manual`: sin throttling si los overrides son suficientes; throttling si el override no cubre la operacion.
- `beta`: throttling leve; avisos de "cierre del beta".
- `demo`: throttling fuerte; solo `preview_modules`.

El throttling se aplica a la latencia de las respuestas y al rate limit por minuto, no al resultado de las operaciones individuales.

## 18. Backend behavior

El billing backend expone servicios a los routers del backend principal. Esta seccion describe los servicios, sus contratos y su composicion con los gates.

### 18.1 Servicios canonicos

| Servicio | Responsabilidad | Endpoints internos |
|---|---|---|
| `BillingAccountService` | CRUD de `billing_account` y emision del primer cargo. | `create_billing_account`, `get_billing_account`, `list_billing_accounts_for_org`, `update_billing_account`. |
| `SubscriptionService` | Gestion del ciclo de vida de la suscripcion. | `start_subscription`, `change_plan`, `cancel_subscription`, `suspend_subscription`, `reactivate_subscription`, `expire_subscription`. |
| `CreditLedgerService` | Registro append-only de movimientos. | `grant_credits`, `purchase_credits`, `reserve_credits`, `release_credits`, `consume_credits`, `refund_credits`, `expire_credits`, `adjust_credits`. |
| `CreditBalanceService` | Lectura agregada del saldo y reconciliacion. | `get_balance`, `reconcile_balance`, `get_balance_breakdown`. |
| `InvoiceService` | Emision, gestion y mapeo de facturas. | `emit_invoice`, `get_invoice`, `list_invoices`, `void_invoice`, `mark_paid`, `mark_uncollectible`. |
| `PaymentProviderService` | Integracion con proveedores externos. | `sync_with_provider`, `handle_webhook`, `create_charge`, `refund_charge`. |
| `EnterpriseOverrideService` | Gestion de overrides Enterprise. | `apply_override`, `deactivate_override`, `list_overrides_for_org`, `audit_overrides`. |
| `TrialService` | Gestion del ciclo del trial. | `start_trial`, `cancel_trial`, `convert_trial`, `expire_trial`. |
| `BetaService` | Gestion del ciclo del beta. | `start_beta`, `convert_beta`, `close_beta`, `record_feedback`. |
| `DemoService` | Gestion del ciclo del demo. | `start_demo`, `expire_demo`, `convert_demo`. |
| `BillingEventService` | Append-only de eventos de billing. | `emit_event`, `list_events`, `export_events`. |
| `BillingGateService` | Evaluacion de gates para operaciones del tenant. | `evaluate_gate`, `explain_gate`, `bulk_evaluate`. |

### 18.2 Contratos de entrada

Todos los servicios exponen contratos Pydantic en `src/services/billing/contracts.py`. Cada contrato lleva:

- `request_id` (string; correlacion HTTP).
- `actor_id` y `actor_type`.
- `organization_id` (cuando aplica).
- `idempotency_key` (cuando la operacion es idempotente).

Los servicios son stateless salvo por la conexion a la base de datos. Toda la informacion de estado se persiste.

### 18.3 Composicion con dependencias

El billing backend depende de las 5 dependencias del canon (ver `backend_gating_contract_v1.md` seccion 4):

- `get_tenant_context`: para resolver `organization_id` desde la sesion.
- `require_organization`: para asegurar que el actor pertenece a la organizacion.
- `validate_project_access`: para asegurar que el actor tiene acceso al proyecto afectado.
- `require_write_permission`: para asegurar que el actor puede ejecutar la operacion.
- `require_module_access`: para asegurar que el actor tiene acceso al modulo.

Las dependencias de billing extienden estas con `BillingGateService` y `BillingEventService` para emitir los eventos canonicos y aplicar los gates.

### 18.4 Patrones de router

Los routers que exponen endpoints de billing siguen los 8 patrones del canon (ver `backend_gating_contract_v1.md` seccion 5):

- **P2-1**: endpoint `GET /billing/balance` con `require_organization` y `BillingGateService` para exponer el saldo.
- **P2-2**: endpoint `POST /billing/credit-packages/purchase` con `require_module_access` y `CreditLedgerService.purchase_credits`.
- **P2-3**: endpoint `GET /billing/invoices` con `require_organization` y `InvoiceService.list_invoices`.
- **P2-4**: endpoint `POST /billing/subscription/change-plan` con `require_write_permission` y `SubscriptionService.change_plan`.
- **P2-5**: endpoint `POST /billing/webhooks/stripe` con validacion de firma y `PaymentProviderService.handle_webhook` (futuro).
- **P2-6**: endpoint `POST /billing/enterprise-overrides` con `require_module_access` y `EnterpriseOverrideService.apply_override`.
- **P2-7**: endpoint `GET /billing/events` con `require_organization` y `BillingEventService.list_events`.
- **P2-8**: endpoint `POST /billing/admin/adjust-credits` con `require_module_access` y `CreditLedgerService.adjust_credits`.

### 18.5 Auditoria de operaciones

Todas las operaciones de billing emiten `billing_event`. La emision es sincrona con la operacion; si falla, la operacion se aborta. Esto garantiza que el historial de billing refleje exactamente lo que se hizo y cuando.

Los `credit_ledger_entry` siguen la misma regla: se emiten antes de que la operacion tenga efecto, y si el efecto falla, el ledger se compensa con un movimiento inverso.

## 19. Estados de bloqueo

Los estados de bloqueo son la respuesta canonica del billing backend cuando un gate falla. Esta seccion define los 12 codigos canonicos, su HTTP code, su mensaje canonico y su CTA.

### 19.1 Catalogo canonico

| Codigo canonico | HTTP | Mensaje canonico | CTA | Cuando se emite |
|---|---|---|---|---|
| `billing_inactive` | 402 | "El billing de tu organizacion no esta activo. Para reactivarlo, contacta a soporte." | "Contactar a soporte" | `subscription.current_status` no esta en `{active, trialing, past_due, enterprise_manual, beta, demo}`. |
| `subscription_past_due` | 402 | "Tu ultimo pago no se proceso. Estamos reintentando. Para evitar la suspension, actualiza tu metodo de pago." | "Actualizar metodo de pago" | `subscription.current_status='past_due'` y se intenta una operacion critica. |
| `subscription_suspended` | 423 | "Tu suscripcion esta suspendida. Para reactivar el acceso, actualiza el metodo de pago o contacta a soporte." | "Actualizar metodo de pago" | `subscription.current_status='suspended'`. |
| `plan_not_active` | 402 | "Tu plan no esta activo. Para continuar, elige un plan." | "Elegir plan" | Plan `creator/pro/studio/enterprise` con `effective_to` ya cerrado. |
| `module_not_included` | 402 | "El modulo [X] no esta incluido en tu plan [Y]. Para acceder, actualiza tu plan o compra un add-on." | "Actualizar plan" | Modulo solicitado no esta en `plan_snapshot.module_keys` y no hay `enterprise_override`. |
| `add_on_required` | 402 | "El modulo [X] requiere un add-on. Para comprarlo, ve a la seccion de add-ons." | "Comprar add-on" | Modulo solicitado es `add_on` y no esta comprado. |
| `credits_exhausted` | 402 | "No tienes creditos suficientes para este job. Compra una bolsa o actualiza tu plan." | "Comprar bolsa" | Saldo disponible menor que `credit_estimate`. |
| `storage_exhausted` | 402 | "Has alcanzado el limite de almacenamiento de tu plan. Libera espacio o actualiza tu plan." | "Actualizar plan" | Upload excede `included_storage_gb + storage_override`. |
| `seat_limit_reached` | 402 | "Has alcanzado el limite de usuarios de tu plan. Libera un usuario o actualiza tu plan." | "Actualizar plan" | Invitacion excede `included_users + users_override`. |
| `project_limit_reached` | 402 | "Has alcanzado el limite de proyectos de tu plan. Cierra un proyecto o actualiza tu plan." | "Actualizar plan" | Creacion excede `included_projects + projects_override`. |
| `enterprise_only` | 402 | "El modulo [X] solo esta disponible para clientes Enterprise. Para acceder, contacta a ventas." | "Contactar a ventas" | Modulo es `enterprise_only` y no hay override. |
| `provider_sync_pending` | 503 | "Estamos sincronizando con tu proveedor de pagos. Intentalo de nuevo en unos minutos." | "Reintentar" | `payment_provider_reference.sync_state='pending'` o `='out_of_sync'`. |

### 19.2 Estructura de la respuesta

Las respuestas de bloqueo siguen la estructura canonica:

```json
{
  "error": {
    "code": "credits_exhausted",
    "http_status": 402,
    "message": "No tienes creditos suficientes para este job. Compra una bolsa o actualiza tu plan.",
    "cta": {
      "label": "Comprar bolsa",
      "url": "/billing/credit-packages",
      "action": "open_credit_packages"
    },
    "context": {
      "credit_estimate": 300,
      "available_balance": 50,
      "current_plan": "pro"
    },
    "request_id": "req_01HXY...",
    "billing_event_id": "01HXY..."
  }
}
```

La UI lee el `code`, muestra el `message` canonico y el `cta` con su URL. El `context` permite construir la explicacion detallada (por ejemplo, "Te faltan 250 creditos").

### 19.3 Localizacion

Los mensajes canonicos estan en espanol. La UI los traduce segun el locale del usuario. Los codigos canonicos son inmutables; solo los mensajes se localizan.

### 19.4 Versionado

Si en una version futura se anade un codigo nuevo, la UI trata los codigos desconocidos como `billing_inactive` y muestra un mensaje generico. Esto evita que la UI rompa cuando se despliega el backend con un codigo nuevo antes que la UI lo reconozca.

## 20. Eventos de auditoria

Los `billing_event` son el registro canonico de los eventos de billing. Esta seccion lista los 17 eventos canonicos, su payload minimo y cuando se emiten.

### 20.1 Catalogo canonico

| `event_type` | Payload minimo | Cuando se emite |
|---|---|---|
| `billing_account_created` | `billing_account_id`, `organization_id`, `actor_id`, `actor_type='user'` | Cuando se crea un `billing_account`. |
| `subscription_started` | `subscription_id`, `billing_account_id`, `plan_key`, `from_status=null`, `to_status` | Cuando una suscripcion pasa de `null` a `trialing`, `active`, `enterprise_manual`, `beta` o `demo`. |
| `subscription_upgraded` | `subscription_id`, `from_plan_key`, `to_plan_key`, `from_status`, `to_status` | Cuando una suscripcion cambia de un plan a otro de mayor nivel (pro a studio, demo a trial). |
| `subscription_downgraded` | `subscription_id`, `from_plan_key`, `to_plan_key`, `from_status`, `to_status` | Cuando una suscripcion cambia de un plan a otro de menor nivel (studio a pro). |
| `subscription_cancelled` | `subscription_id`, `actor_id`, `actor_type`, `reason` | Cuando el usuario o un admin cancela la suscripcion. `actor_type='user'` o `'admin'`. |
| `subscription_past_due` | `subscription_id`, `from_status='active'`, `to_status='past_due'`, `provider_event_id` | Cuando el cargo del proveedor falla y la suscripcion entra en reintentos. |
| `subscription_suspended` | `subscription_id`, `from_status`, `to_status='suspended'`, `reason` | Cuando los reintentos del proveedor se agotan. |
| `payment_provider_synced` | `payment_provider_reference_id`, `provider_name`, `provider_event_id`, `sync_state` | Cuando se recibe un webhook o se completa una consulta de sincronizacion. |
| `invoice_created` | `invoice_reference_id`, `billing_account_id`, `total_eur`, `actor_id`, `actor_type='system'` | Cuando se emite una factura. |
| `invoice_paid` | `invoice_reference_id`, `total_eur`, `provider_event_id` | Cuando el cargo del proveedor completa el pago. |
| `invoice_failed` | `invoice_reference_id`, `total_eur`, `provider_event_id`, `reason` | Cuando el cargo del proveedor falla. |
| `credit_package_purchased` | `credit_package_purchase_id`, `credit_package_id`, `credits_granted`, `price_eur`, `actor_id`, `actor_type='user'` | Cuando se completa la compra de una bolsa. |
| `credits_reserved` | `credit_ledger_entry_id`, `credit_amount`, `sub_balance_from`, `related_entity_id` | Cuando un job IA reserva creditos. |
| `credits_consumed` | `credit_ledger_entry_id`, `credit_amount`, `related_entity_id` | Cuando un job IA consume los creditos reservados. |
| `credits_refunded` | `credit_ledger_entry_id`, `credit_amount`, `reason` | Cuando se devuelven creditos al tenant (downgrade, cancelacion, error). |
| `credits_expired` | `credit_ledger_entry_id`, `credit_amount`, `sub_balance` | Cuando una bolsa caduca o se pierden creditos incluidos no consumidos. |
| `enterprise_override_applied` | `enterprise_override_id`, `override_type`, `scope`, `actor_id`, `actor_type='admin'` | Cuando se anade, modifica o desactiva un override. |

### 20.2 Garantias

- **Append-only**: los eventos nunca se borran. Las correcciones se hacen con un evento nuevo que referencia al anterior.
- **Idempotencia**: el `idempotency_key` del evento es unico por emision. Si dos requests generan el mismo evento, solo se registra uno.
- **Trazabilidad**: cada evento lleva `actor_id`, `actor_type`, `request_id` (cuando aplica), `provider_event_id` (cuando aplica) y `related_entity_id` (cuando aplica). Esto permite reconstruir cualquier accion de billing.
- **Retencion**: el canon retiene los eventos durante el periodo legal + 1 ano. Despues, los campos personales se seudonimizan.

### 20.3 Consumidores

Los `billing_event` se consumen desde:

- **Panel de billing del tenant**: el usuario ve su historial de eventos de billing con filtros por tipo, fecha y monto.
- **Consola de operaciones**: los operadores ven eventos en tiempo real con alertas configurables (por ejemplo, "mas de 3 `invoice_failed` en 24h").
- **Auditoria contable**: el sistema contable lee los eventos para conciliacion contable.
- **Anti-fraude**: el sistema anti-fraude lee los eventos para detectar patrones anormales (multiples reembolsos, cambios de tarjeta, etc.).

## 21. Modelo relacional propuesto

Esta seccion presenta el modelo relacional propuesto para implementar las 15 entidades de billing. Es una propuesta de nivel arquitectonico; la implementacion concreta (DDL, ORM, migraciones) se hara en fases posteriores.

### 21.1 Convenciones

- **Nombres de tabla**: `billing_<entity>` en snake_case, plural cuando aplica (`billing_accounts`, `subscriptions`, etc.).
- **PKs**: `id` UUID v7; el canon prefiere v7 por su ordenamiento temporal y su unicidad.
- **FKs**: `<entity>_id` siguiendo el nombre canonico (`organization_id`, `subscription_id`, etc.).
- **Timestamps**: `created_at`, `updated_at` en UTC; `occurred_at` o `effective_*` para eventos con semantica temporal canonica.
- **Soft delete**: el canon no usa soft delete. Las entidades se borran fisicamente al final del periodo legal, salvo el `billing_event` y el `credit_ledger_entry` que son append-only.
- **Audit columns**: `actor_id`, `actor_type`, `request_id` cuando aplica.

### 21.2 Tablas

#### 21.2.1 `billing_accounts`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK |
| `legal_name` | TEXT | NOT NULL |
| `tax_id` | TEXT | nullable |
| `country` | TEXT | NOT NULL, ISO 3166-1 alpha-2 |
| `preferred_language` | TEXT | NOT NULL, ISO 639-1 |
| `currency` | TEXT | NOT NULL, default `EUR` |
| `is_default` | BOOLEAN | NOT NULL, default `false` |
| `status` | ENUM | NOT NULL, default `active` |
| `metadata` | JSONB | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.2 `subscriptions`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK |
| `billing_account_id` | UUID | NOT NULL, FK |
| `current_status` | ENUM | NOT NULL, default `active` |
| `current_plan_snapshot_id` | UUID | nullable, FK |
| `started_at` | TIMESTAMPTZ | NOT NULL |
| `current_period_start` | TIMESTAMPTZ | nullable |
| `current_period_end` | TIMESTAMPTZ | nullable |
| `renews_at` | TIMESTAMPTZ | nullable |
| `cancelled_at` | TIMESTAMPTZ | nullable |
| `ended_at` | TIMESTAMPTZ | nullable |
| `cancellation_reason` | TEXT | nullable |
| `metadata` | JSONB | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.3 `subscription_status_history`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `subscription_id` | UUID | NOT NULL, FK |
| `from_status` | ENUM | nullable |
| `to_status` | ENUM | NOT NULL |
| `changed_at` | TIMESTAMPTZ | NOT NULL |
| `actor_id` | UUID o `system` | NOT NULL |
| `actor_type` | ENUM | NOT NULL |
| `reason` | TEXT | nullable |
| `billing_event_id` | UUID | nullable, FK |
| `request_id` | TEXT | nullable |
| `metadata` | JSONB | nullable |

#### 21.2.4 `plan_snapshots`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `subscription_id` | UUID | NOT NULL, FK |
| `canon_version` | TEXT | NOT NULL |
| `plan_key` | ENUM | NOT NULL |
| `billing_period` | ENUM | NOT NULL |
| `price_eur` | NUMERIC(10,2) | NOT NULL, TBD_PRICING |
| `yearly_discount_pct` | NUMERIC(5,2) | NOT NULL, default 16.67 |
| `price_after_discount_eur` | NUMERIC(10,2) | NOT NULL, TBD_PRICING |
| `currency` | TEXT | NOT NULL, default `EUR` |
| `included_credits_monthly` | INT | NOT NULL, TBD_PRICING |
| `included_storage_gb` | INT | NOT NULL, TBD_PRICING |
| `included_users` | INT | NOT NULL, TBD_PRICING |
| `included_projects` | INT | NOT NULL, TBD_PRICING |
| `module_keys` | JSONB | NOT NULL |
| `support_level` | ENUM | NOT NULL |
| `retention_days` | INT | NOT NULL |
| `effective_from` | TIMESTAMPTZ | NOT NULL |
| `effective_to` | TIMESTAMPTZ | nullable |
| `change_reason` | ENUM | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL, inmutable |

#### 21.2.5 `plan_change_history`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `subscription_id` | UUID | NOT NULL, FK |
| `from_plan_snapshot_id` | UUID | nullable, FK |
| `to_plan_snapshot_id` | UUID | NOT NULL, FK |
| `changed_at` | TIMESTAMPTZ | NOT NULL |
| `change_reason` | ENUM | NOT NULL |
| `prorate_credit_eur` | NUMERIC(10,2) | nullable |
| `prorate_debit_eur` | NUMERIC(10,2) | nullable |
| `actor_id` | UUID o `system` | NOT NULL |
| `actor_type` | ENUM | NOT NULL |
| `request_id` | TEXT | nullable |
| `billing_event_id` | UUID | nullable, FK |
| `created_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.6 `credit_balances`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK, unique |
| `included_monthly_remaining` | INT | NOT NULL, default 0 |
| `purchased_balance` | INT | NOT NULL, default 0 |
| `promotional_balance` | INT | NOT NULL, default 0 |
| `trial_balance` | INT | NOT NULL, default 0 |
| `enterprise_balance` | INT | NOT NULL, default 0 |
| `reserved_active` | INT | NOT NULL, default 0 |
| `consumed_period` | INT | NOT NULL, default 0 |
| `expired_total` | INT | NOT NULL, default 0 |
| `refunded_total` | INT | NOT NULL, default 0 |
| `adjusted_total` | INT | NOT NULL, default 0 |
| `version` | INT | NOT NULL, default 1; control de concurrencia optimista |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.7 `credit_ledger_entries`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK |
| `credit_balance_id` | UUID | NOT NULL, FK |
| `credit_package_purchase_id` | UUID | nullable, FK |
| `subscription_id` | UUID | nullable, FK |
| `entry_type` | ENUM | NOT NULL |
| `credit_amount` | INT | NOT NULL |
| `sub_balance_from` | ENUM | nullable |
| `sub_balance_to` | ENUM | nullable |
| `idempotency_key` | TEXT | NOT NULL, unique |
| `provider_event_id` | TEXT | nullable |
| `actor_id` | UUID o `system` | NOT NULL |
| `actor_type` | ENUM | NOT NULL |
| `related_entity_type` | TEXT | nullable |
| `related_entity_id` | UUID | nullable |
| `reason` | TEXT | nullable |
| `metadata` | JSONB | nullable |
| `occurred_at` | TIMESTAMPTZ | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.8 `credit_package_purchases`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK |
| `billing_account_id` | UUID | NOT NULL, FK |
| `credit_package_id` | TEXT | NOT NULL |
| `credits_granted` | INT | NOT NULL |
| `price_eur` | NUMERIC(10,2) | NOT NULL |
| `currency` | TEXT | NOT NULL, default `EUR` |
| `purchased_at` | TIMESTAMPTZ | NOT NULL |
| `expires_at` | TIMESTAMPTZ | NOT NULL |
| `status` | ENUM | NOT NULL |
| `invoice_reference_id` | UUID | nullable, FK |
| `payment_provider_reference_id` | UUID | nullable, FK |
| `provider_charge_id` | TEXT | nullable |
| `is_gift` | BOOLEAN | NOT NULL, default `false` |
| `gifted_by_org_id` | UUID | nullable, FK |
| `metadata` | JSONB | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.9 `invoice_references`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `billing_account_id` | UUID | NOT NULL, FK |
| `subscription_id` | UUID | nullable, FK |
| `invoice_number` | TEXT | NOT NULL, unique |
| `status` | ENUM | NOT NULL |
| `issue_date` | TIMESTAMPTZ | NOT NULL |
| `due_date` | TIMESTAMPTZ | nullable |
| `period_start` | TIMESTAMPTZ | NOT NULL |
| `period_end` | TIMESTAMPTZ | NOT NULL |
| `currency` | TEXT | NOT NULL, default `EUR` |
| `subtotal_eur` | NUMERIC(10,2) | NOT NULL |
| `tax_amount_eur` | NUMERIC(10,2) | nullable |
| `total_eur` | NUMERIC(10,2) | NOT NULL |
| `line_items` | JSONB | NOT NULL |
| `provider_invoice_id` | TEXT | nullable, unique |
| `provider_invoice_url` | TEXT | nullable |
| `pdf_storage_path` | TEXT | nullable |
| `metadata` | JSONB | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.10 `payment_provider_references`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `billing_account_id` | UUID | NOT NULL, FK |
| `provider_name` | ENUM | NOT NULL |
| `stripe_customer_id` | TEXT | nullable |
| `stripe_subscription_id` | TEXT | nullable |
| `stripe_price_id` | TEXT | nullable |
| `stripe_product_id` | TEXT | nullable |
| `stripe_invoice_id` | TEXT | nullable |
| `stripe_payment_intent_id` | TEXT | nullable |
| `provider_event_id` | TEXT | nullable |
| `provider_event_hash` | TEXT | nullable |
| `provider_metadata` | JSONB | nullable |
| `last_synced_at` | TIMESTAMPTZ | nullable |
| `sync_state` | ENUM | NOT NULL, default `pending` |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.11 `enterprise_overrides`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK |
| `subscription_id` | UUID | nullable, FK |
| `override_type` | ENUM | NOT NULL |
| `scope` | JSONB | nullable |
| `effective_from` | TIMESTAMPTZ | NOT NULL |
| `effective_to` | TIMESTAMPTZ | nullable |
| `approver_id` | UUID | NOT NULL, FK |
| `justification` | TEXT | NOT NULL |
| `contract_reference` | TEXT | nullable |
| `price_override_eur` | NUMERIC(10,2) | nullable |
| `credit_override_amount` | INT | nullable |
| `routing_overrides` | JSONB | nullable |
| `is_active` | BOOLEAN | NOT NULL, default `true` |
| `metadata` | JSONB | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.12 `billing_events`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK |
| `billing_account_id` | UUID | nullable, FK |
| `subscription_id` | UUID | nullable, FK |
| `event_type` | ENUM | NOT NULL |
| `from_status` | TEXT | nullable |
| `to_status` | TEXT | nullable |
| `amount_eur` | NUMERIC(10,2) | nullable |
| `credit_amount` | INT | nullable |
| `actor_id` | UUID o `system` | NOT NULL |
| `actor_type` | ENUM | NOT NULL |
| `provider_event_id` | TEXT | nullable |
| `request_id` | TEXT | nullable |
| `related_entity_id` | UUID | nullable |
| `reason` | TEXT | nullable |
| `metadata` | JSONB | nullable |
| `occurred_at` | TIMESTAMPTZ | NOT NULL |
| `created_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.13 `trial_entitlements`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK, unique |
| `subscription_id` | UUID | NOT NULL, FK |
| `started_at` | TIMESTAMPTZ | NOT NULL |
| `ends_at` | TIMESTAMPTZ | NOT NULL |
| `trial_plan_key` | ENUM | NOT NULL, default `pro` |
| `trial_credits_granted` | INT | NOT NULL, default 2000 |
| `payment_method_required` | BOOLEAN | NOT NULL, default `true` |
| `card_collection_status` | ENUM | NOT NULL |
| `anti_abuse_flags` | JSONB | nullable |
| `auto_convert_at_end` | BOOLEAN | NOT NULL, default `true` |
| `target_plan_key` | ENUM | NOT NULL, default `pro` |
| `cancelled_at` | TIMESTAMPTZ | nullable |
| `converted_at` | TIMESTAMPTZ | nullable |
| `metadata` | JSONB | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.14 `beta_entitlements`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK |
| `subscription_id` | UUID | NOT NULL, FK |
| `beta_plan_key` | ENUM | NOT NULL |
| `started_at` | TIMESTAMPTZ | NOT NULL |
| `ends_at` | TIMESTAMPTZ | NOT NULL |
| `monthly_credits_grant` | INT | NOT NULL, default 1000 |
| `feedback_required` | BOOLEAN | NOT NULL, default `true` |
| `last_feedback_at` | TIMESTAMPTZ | nullable |
| `experimental_modules` | JSONB | nullable |
| `price_lock_in_months` | INT | NOT NULL, default 3 |
| `converted_at` | TIMESTAMPTZ | nullable |
| `metadata` | JSONB | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

#### 21.2.15 `demo_entitlements`

| Columna | Tipo | Constraints |
|---|---|---|
| `id` | UUID | PK |
| `organization_id` | UUID | NOT NULL, FK, unique |
| `subscription_id` | UUID | NOT NULL, FK |
| `started_at` | TIMESTAMPTZ | NOT NULL |
| `ends_at` | TIMESTAMPTZ | nullable |
| `one_shot_credits` | INT | NOT NULL, default 50 |
| `preview_modules` | JSONB | NOT NULL |
| `sales_owner_user_id` | UUID | nullable, FK |
| `qualification_status` | ENUM | NOT NULL, default `cold` |
| `converted_at` | TIMESTAMPTZ | nullable |
| `metadata` | JSONB | nullable |
| `created_at` | TIMESTAMPTZ | NOT NULL |
| `updated_at` | TIMESTAMPTZ | NOT NULL |

### 21.3 Cardinalidad y dependencias

- `billing_accounts` 1..N `subscriptions`.
- `subscriptions` 1..N `plan_snapshots` (1 activo, N historicos).
- `subscriptions` 1..N `subscription_status_history`.
- `subscriptions` 1..N `plan_change_history`.
- `organizations` 1..1 `credit_balances` (unique).
- `credit_balances` 1..N `credit_ledger_entries`.
- `credit_package_purchases` 1..N `credit_ledger_entries` (los `credit_purchase`).
- `billing_accounts` 1..N `credit_package_purchases`.
- `billing_accounts` 1..N `invoice_references`.
- `billing_accounts` 1..N `payment_provider_references`.
- `organizations` 0..N `enterprise_overrides`.
- `organizations` 0..1 `trial_entitlements`.
- `organizations` 0..1 `beta_entitlements`.
- `organizations` 0..1 `demo_entitlements`.
- `billing_events` referencia N..1 cualquier entidad por `related_entity_id`.

## 22. Indices y constraints

### 22.1 Indices canonicos

| Tabla | Indice | Justificacion |
|---|---|---|
| `billing_accounts` | `(organization_id, is_default)` | Resolver cuenta default. |
| `billing_accounts` | `(country)` | Reportes por pais. |
| `subscriptions` | `(organization_id, current_status)` | Resolver suscripcion activa. |
| `subscriptions` | `(billing_account_id, current_status)` | Resolver suscripcion por cuenta. |
| `subscriptions` | `(current_status, renews_at)` | Cierre de ciclos, gestion de past_due. |
| `subscription_status_history` | `(subscription_id, changed_at DESC)` | Historial de la suscripcion. |
| `plan_snapshots` | `(subscription_id, effective_from DESC)` | Snapshot actual e historico. |
| `plan_snapshots` | `(subscription_id) WHERE effective_to IS NULL` | Snapshot activo (parcial). |
| `plan_change_history` | `(subscription_id, changed_at DESC)` | Historial de cambios. |
| `credit_ledger_entries` | `(organization_id, occurred_at DESC)` | Historial por org. |
| `credit_ledger_entries` | `(idempotency_key)` | Unico, idempotencia. |
| `credit_ledger_entries` | `(credit_balance_id, occurred_at DESC)` | Reconciliacion. |
| `credit_ledger_entries` | `(related_entity_type, related_entity_id)` | Trazabilidad por entidad. |
| `credit_package_purchases` | `(organization_id, status)` | Saldo comprado. |
| `credit_package_purchases` | `(status, expires_at)` | Caducidad. |
| `invoice_references` | `(billing_account_id, issue_date DESC)` | Historial de facturas. |
| `invoice_references` | `(invoice_number)` | Unico. |
| `invoice_references` | `(provider_invoice_id)` | Unico parcial; mapeo con proveedor. |
| `invoice_references` | `(status, due_date)` | Gestion de past_due. |
| `payment_provider_references` | `(billing_account_id, provider_name)` | Resolver por proveedor. |
| `payment_provider_references` | `(provider_name, provider_event_id)` | Idempotencia de webhooks. |
| `enterprise_overrides` | `(organization_id, is_active)` | Overrides activos. |
| `enterprise_overrides` | `(organization_id, override_type) WHERE is_active=true` | Un override activo por tipo. |
| `billing_events` | `(organization_id, occurred_at DESC)` | Historial de eventos. |
| `billing_events` | `(event_type, occurred_at DESC)` | Consultas por tipo. |
| `billing_events` | `(provider_event_id)` | Idempotencia de webhooks. |
| `trial_entitlements` | `(organization_id)` | Unico; trial activo. |
| `trial_entitlements` | `(ends_at) WHERE cancelled_at IS NULL AND converted_at IS NULL` | Trials activos. |
| `beta_entitlements` | `(organization_id, is_active)` | Beta activo. |
| `demo_entitlements` | `(organization_id)` | Unico. |
| `demo_entitlements` | `(ends_at) WHERE converted_at IS NULL` | Demos activos. |

### 22.2 Constraints canonicas

- `billing_accounts.is_default=true` debe ser unico por `organization_id`. Si hay varias cuentas, solo una es `is_default=true`.
- `subscriptions` solo puede tener una suscripcion activa por `billing_account` (`current_status IN ('active', 'trialing', 'past_due', 'enterprise_manual', 'beta', 'demo')`). Las historicas con `current_status IN ('cancelled', 'expired', 'suspended')` se permiten.
- `plan_snapshots.effective_to > effective_from` si `effective_to IS NOT NULL`.
- `plan_snapshots` solo puede haber uno con `effective_to IS NULL` por `subscription_id`.
- `credit_balances.included_monthly_remaining + purchased_balance + promotional_balance + trial_balance + enterprise_balance - reserved_active >= 0` (constraint de no-negatividad).
- `credit_ledger_entries.idempotency_key` unico.
- `invoice_references.invoice_number` unico.
- `enterprise_overrides` solo puede haber uno activo por `(organization_id, override_type)`.
- `trial_entitlements` unico por `organization_id`.
- `demo_entitlements` unico por `organization_id`.

### 22.3 Concurrencia

- `credit_balances` usa control de concurrencia optimista (`version`); cada `UPDATE` incrementa `version` y rechaza con error si la version no coincide.
- `plan_snapshots` son inmutables; no requieren lock.
- `credit_ledger_entries` son append-only; el unico lock es sobre la insercion (UNIQUE en `idempotency_key`).
- `billing_events` son append-only; mismo tratamiento que el ledger.

## 23. Riesgos

Esta seccion lista los riesgos identificados en el modelo de billing, su severidad, su probabilidad, su mitigacion propuesta y su estado. El estado actual es "documentado, pendiente de mitigacion concreta en fases posteriores".

### 23.1 Tabla de riesgos

| # | Riesgo | Severidad | Probabilidad | Mitigacion | Estado |
|---|---|---|---|---|---|
| R1 | Cobro duplicado por webhook del proveedor repetido. | Alta | Media | `idempotency_key` en `billing_events` y `payment_provider_references.provider_event_id` unico. | Documentado, implementado en fase `CID.SAAS.STRIPE.WEBHOOKS.1`. |
| R2 | Discrepancia de importes entre CID canon y el cargo del proveedor. | Media | Media | Canon CID como verdad; reconciliacion periodica; `credit_adjustment` automatico para diferencias pequenas. | Documentado, pendiente. |
| R3 | Webhook fuera de orden (paid antes de created). | Media | Baja | Reorden por `provider_event_id` y `occurred_at`; encolado a reconciliacion si no se puede. | Documentado, implementado en `CID.SAAS.STRIPE.WEBHOOKS.1`. |
| R4 | Drift de saldo (`credit_balance` no coincide con ledger). | Alta | Baja | Job batch de reconciliacion diaria; congelacion de reservas si hay drift. | Documentado, pendiente de implementacion. |
| R5 | Multi-cuenta de trial con misma tarjeta. | Media | Alta | `anti_abuse_flags` con `card_fingerprint`, IP, dominio, tarjeta quemada. | Documentado, pendiente. |
| R6 | Cobro no deseado al convertir trial. | Alta | Media | Emails T-3, T-1, T-0; opcion de cancelar en un click desde el email. | Documentado, pendiente. |
| R7 | Reserva huerfana (job no cierra la reserva). | Media | Baja | Reaper cada 6h; libera reservas >24h. | Documentado, pendiente. |
| R8 | Override Enterprise abusivo. | Alta | Baja | `approver_id` obligatorio; `justification` obligatorio; revision trimestral; notificacion a otro `global_admin`. | Documentado, pendiente. |
| R9 | Volumen de `billing_events` supera el rendimiento de la BD. | Media | Media | Particion por mes; archivo frio despues del periodo legal; indice en `(organization_id, occurred_at DESC)`. | Documentado, pendiente. |
| R10 | Datos personales en `billing_events` violan GDPR mas alla del periodo legal. | Alta | Baja | Seudonimizacion de campos personales tras periodo legal; retencion maxima de 7 anos. | Documentado, pendiente. |
| R11 | Plan canon cambia a mitad de ciclo y rompe precios congelados. | Media | Baja | `plan_snapshot` inmutable; nuevo canon no afecta a `effective_to` antiguos. | Mitigado por diseno. |
| R12 | Conversion entre modos (demo, trial, beta) genera doble suscripcion. | Media | Baja | `billing_event` con `related_entity_id` enlazando origen y destino; un solo modo activo por org. | Documentado, pendiente. |
| R13 | Multi-moneda no soportada rompe la suposicion de EUR canon. | Media | Media | `currency` por `billing_account`; `multi_currency` como override Enterprise; conversion FX en factura canon. | Documentado, pendiente. |
| R14 | Proveedor caido (Stripe fuera de servicio). | Alta | Baja | Reintentos con backoff exponencial; modo degradado que permite lectura; reconciliacion al volver. | Documentado, pendiente. |
| R15 | Refund mal calculado. | Alta | Baja | `credit_refund` idempotente; doble validacion contra factura original; logica en `RefundService` revisada. | Documentado, pendiente. |
| R16 | Plan_snapshot con precios TBD_PRICING entra a produccion prematuramente. | Alta | Media | Bloqueo en `CID.SAAS.PRICING.CANONICALIZATION.2` antes de migrar a DDL real; canon afirma TBD_PRICING en todos los `price_eur`. | Bloqueado por diseno. |
| R17 | Organizacion Enterprise multi-entidad legal con varias `billing_account` y gates divididos. | Media | Media | Gates operan sobre `organization_id` para limites principales; `billing_account_id` solo para emitir factura. | Documentado, pendiente. |
| R18 | Conversion Enterprise con `multi_currency` no contemplada en el modelo de saldo canon. | Media | Baja | `credit_balance` no tiene `currency` (canon: 1 credito = 1 unidad abstracta); el canon monetario vive en `invoice_reference`. | Mitigado por diseno. |
| R19 | Refactor del canon de planes sin fase de migracion para `plan_snapshots` historicos. | Media | Baja | Plan canon versionado; `plan_snapshots` se cierran con `effective_to` y se reemplazan en renovacion. | Mitigado por diseno. |
| R20 | Auditoria incompleta por actor_id faltante. | Alta | Baja | Todos los servicios exigen `actor_id` y `actor_type`; `system` permitido para eventos automaticos. | Documentado, pendiente. |

## 24. Roadmap derivado

Las fases derivadas de este documento son las siguientes. Cada fase declara su objetivo, sus criterios de aceptacion, su alcance y sus dependencias. Las fases siguen la politica de versionado canonico y se ejecutan en orden secuencial salvo paralelismos explicitos.

### 24.1 Catalogo de fases

#### `CID.SAAS.BILLING.MODELS.1`

- **Objetivo**: aterrizar el modelo de este documento a DDL real en `alembic/versions/` y a ORM en `src/models/billing/`.
- **Criterios de aceptacion**: las 15 tablas existen; los indices canonicos estan creados; los constraints canonicos estan aplicados; las migraciones suben y bajan sin errores en CI.
- **Alcance**: solo DDL y modelos ORM. Sin servicios, sin routers, sin UI.
- **Dependencias**: este documento aprobado.

#### `CID.SAAS.CREDIT.LEDGER.BACKEND.1`

- **Objetivo**: implementar `CreditLedgerService` con los 8 tipos de movimiento (`credit_grant`, `credit_purchase`, `credit_reserve`, `credit_release`, `credit_consume`, `credit_refund`, `credit_expire`, `credit_adjustment`).
- **Criterios de aceptacion**: tests unitarios cubren los 8 tipos; `credit_balance` se actualiza en orden canonico; idempotencia verificada con reintentos.
- **Alcance**: servicios + tests; sin routers; sin UI.
- **Dependencias**: `CID.SAAS.BILLING.MODELS.1`.

#### `CID.SAAS.SUBSCRIPTION.STATE.BACKEND.1`

- **Objetivo**: implementar `SubscriptionService` con la maquina de 9 estados.
- **Criterios de aceptacion**: transiciones validas y no validas cubiertas; eventos `billing_event` emitidos en cada cambio; pruebas con happy path y edge cases (trialing past_due, past_due suspended, suspended reactivated, cancelled expired).
- **Alcance**: servicios + tests.
- **Dependencias**: `CID.SAAS.CREDIT.LEDGER.BACKEND.1`.

#### `CID.SAAS.PLAN.GATES.BACKEND.1`

- **Objetivo**: implementar los gates de plan y modulos en `BillingGateService`.
- **Criterios de aceptacion**: las 8 dimensiones de gate evaluadas; respuesta canonica con codigo canonico y CTA; cobertura de todos los `plan_key` y `module_key`.
- **Alcance**: servicios + tests.
- **Dependencias**: `CID.SAAS.SUBSCRIPTION.STATE.BACKEND.1`.

#### `CID.SAAS.MODULE.GATES.BACKEND.1`

- **Objetivo**: extender `BillingGateService` con gates especificos de modulos (lectura, escritura, exportacion).
- **Criterios de aceptacion**: cada `module_key` conoce su nivel (`free`, `plan_included`, `add_on`, `enterprise_only`); la UI de cada modulo muestra el CTA canonico.
- **Alcance**: servicios + tests.
- **Dependencias**: `CID.SAAS.PLAN.GATES.BACKEND.1`.

#### `CID.SAAS.CREDIT.GATES.BACKEND.1`

- **Objetivo**: implementar el flujo completo de reserva de creditos con `CreditLedgerService.reserve_credits`, `release_credits`, `consume_credits` y el reaper.
- **Criterios de aceptacion**: jobs IA prueban el flujo; el reaper libera reservas huerfanas >24h; cobertura de los 6 estados de reserva.
- **Alcance**: servicios + tests + reaper.
- **Dependencias**: `CID.SAAS.MODULE.GATES.BACKEND.1`.

#### `CID.SAAS.STRIPE.PRODUCTS.PRICES.1`

- **Objetivo**: configurar productos y precios en Stripe para que coincidan con el canon (planes, add-ons, bolsas).
- **Criterios de aceptacion**: todos los `plan_key`, `credit_package_id` y add-ons tienen su contraparte en Stripe con `price_id` registrado; reconciliation periodica confirma igualdad.
- **Alcance**: configuracion de Stripe + tests de reconciliacion.
- **Dependencias**: `CID.SAAS.CREDIT.GATES.BACKEND.1`.

#### `CID.SAAS.STRIPE.WEBHOOKS.1`

- **Objetivo**: implementar el endpoint `POST /billing/webhooks/stripe` con validacion de firma, idempotencia y manejo de los eventos clave (`invoice.created`, `invoice.paid`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`).
- **Criterios de aceptacion**: webhook firmado valido se procesa; webhook con firma invalida se rechaza (401); webhook duplicado se ignora; reorden de eventos funciona.
- **Alcance**: routers + servicios + tests.
- **Dependencias**: `CID.SAAS.STRIPE.PRODUCTS.PRICES.1`.

#### `CID.SAAS.BILLING.ADMIN.UI.1`

- **Objetivo**: panel de billing en `src_frontend` con saldo, facturas, eventos, planes y overrides.
- **Criterios de aceptacion**: UI carga datos via los 8 routers canonicos; muestra el `cta` canonico para cada error; i18n en espanol e ingles.
- **Alcance**: frontend.
- **Dependencias**: `CID.SAAS.STRIPE.WEBHOOKS.1`.

### 24.2 Dependencias graficas

```
MODELS.1
   |
   v
LEDGER.BACKEND.1
   |
   v
SUBSCRIPTION.STATE.BACKEND.1
   |
   v
PLAN.GATES.BACKEND.1
   |
   v
MODULE.GATES.BACKEND.1
   |
   v
CREDIT.GATES.BACKEND.1
   |
   v
STRIPE.PRODUCTS.PRICES.1
   |
   v
STRIPE.WEBHOOKS.1
   |
   v
BILLING.ADMIN.UI.1
```

No hay paralelismos: cada fase depende de la anterior. Esto simplifica la planificacion y reduce el riesgo de regresiones.

## 25. Criterio GO

Esta seccion define los criterios GO/NO-GO para que el modelo de billing pase de la fase de diseno a la fase de implementacion (`CID.SAAS.BILLING.MODELS.1`).

### 25.1 Criterios de aprobacion

- [ ] **C1**: el documento actual esta aprobado por el equipo de arquitectura y el equipo de producto.
- [ ] **C2**: el canon de precios (`cid_pricing_canonical_v1.md`) esta cerrado y validado, con `TBD_PRICING` solo en campos que la implementacion pueda tolerar (placeholder explicito).
- [ ] **C3**: el canon de planes y modulos (`cid_plans_modules_matrix_v1.md`) esta cerrado y validado.
- [ ] **C4**: el canon de roles y permisos (`cid_roles_permissions_matrix_v1.md`) confirma que existen `global_admin` y `support_specialist` con los permisos necesarios para aprobar overrides.
- [ ] **C5**: el `backend_gating_contract_v1.md` confirma las 5 dependencias y los 8 patrones de router.
- [ ] **C6**: el `cid_saas_model_contract_v1.md` confirma que `organization`, `project`, `user`, `role`, `permission` y `audit_event` existen en el modelo canonico.
- [ ] **C7**: las 9 fases del roadmap derivado tienen asignadas estimacion, equipo y fecha objetivo.
- [ ] **C8**: la auditoria tecnica (revisiones cruzadas) ha marcado este documento como "listo para implementacion".
- [ ] **C9**: las 20 filas de riesgos tienen plan de mitigacion concreto o aceptacion explicita del riesgo.
- [ ] **C10**: la decision sobre Stripe (implementar en esta fase o mas adelante) esta tomada y documentada.

### 25.2 Criterios de bloqueo (NO-GO automaticos)

- **N1**: cualquier campo `TBD_PRICING` que no pueda ser tolerado como placeholder esta presente sin valor canon.
- **N2**: el canon de planes o el canon de precios no estan validados.
- **N3**: hay desacuerdo entre el documento actual y cualquiera de los 5 documentos canon referenciados.
- **N4**: una nueva entidad de billing (16 o 17) se ha anadido sin actualizar las 9 fases del roadmap.
- **N5**: los criterios C1-C10 no estan todos cumplidos.

### 25.3 Estado actual

- C1: pendiente de revision.
- C2: cerrado en `cid_pricing_canonical_v1.md` (commit `90756ad`).
- C3: cerrado en `cid_plans_modules_matrix_v1.md`.
- C4: cerrado en `cid_roles_permissions_matrix_v1.md`.
- C5: cerrado en `backend_gating_contract_v1.md`.
- C6: cerrado en `cid_saas_model_contract_v1.md`.
- C7: pendiente de asignacion de equipo y fechas.
- C8: pendiente de auditoria tecnica.
- C9: abierto; este documento lista 20 riesgos y propone mitigaciones; algunas mitigaciones son "pendiente".
- C10: pendiente; el canon afirma que Stripe NO se implementa en esta fase; la decision debe confirmarse.

Estado actual: **NO-GO hasta que C1, C7, C8, C9 y C10 se cierren**. Esto es compatible con la politica de implementacion incremental: la fase actual es de diseno, no de implementacion.

## Estilo y forma

- **Encabezados**: el documento usa `##` para secciones numeradas (2-25) y `###` para sub-secciones dentro de las entidades (5.1-5.15) y dentro de las secciones descriptivas (7.1-7.10, 13.1-13.5, etc.).
- **Tablas**: todas las definiciones de campos y de catalogos se presentan en tablas Markdown con columnas `Campo`, `Tipo`, `Descripcion` (o equivalente). Esto permite busqueda rapida y consistencia visual.
- **Codigos canonicos**: los codigos de bloqueo, los `event_type`, los `entry_type`, los `override_type`, los `plan_key`, los `module_key` y los `current_status` se escriben en `snake_case` y se rodean con `` ` `` en el texto.
- **TBD_PRICING**: cualquier valor de precio pendiente se marca explicitamente con `TBD_PRICING` para distinguir de un valor canonico.
- **CONTRACTUAL**: cualquier valor definido por contrato Enterprise se marca explicitamente con `CONTRACTUAL` para distinguir de un valor canonico.
- **Referencias a otros documentos**: las referencias al canon o a directivas usan la ruta relativa al archivo (`cid_pricing_canonical_v1.md`, `cid_saas_model_contract_v1.md`).
- **Numeros y unidades**: los precios en EUR se escriben con el simbolo (`29.99€`); los creditos en enteros sin unidad; el almacenamiento en GB o TB; el tiempo en dias, meses o anos con la unidad explicita.
- **Idioma**: el documento esta en espanol, salvo terminos tecnicos en ingles (`append-only`, `idempotency_key`, `webhook`, `snapshot`, etc.).
- **Versionado**: este documento es `v1` y se versionara en el directorio `docs/architecture/` siguiendo la politica de canon. Las fases `CID.SAAS.BILLING.*` daran lugar a revisiones `v1.x` o `v2` segun la magnitud del cambio.
