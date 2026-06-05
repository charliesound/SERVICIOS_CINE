# CID Pricing Canonical v1

Version: 1.0
Status: SPEC / CANONICAL BUSINESS SOURCE
Date: 2026-06-05
Owners: CID Product / CID Business / CID Architecture
Scope: CID SaaS pricing, credits, packages, limits and billing rules
Supersedes (parcialmente, en lo concerniente a precios y creditos):
- `docs/business/cid_pricing_canonicalization_needed_v1.md` (discrepancia documentada, valores resueltos aqui).
- `docs/business/cid_pricing_competitive_baseline_v1.md` (hipotesis v1.0; tabla de hipotesis 10.1 reemplazada).
- `docs/business/cid_credits_business_model_v1.md` (hipotesis v1.0/1.1; tabla de creditos incluidos §20 reemplazada).
- `docs/architecture/cid_saas_model_contract_v1.md` (tabla de planes §7 y matriz de creditos §9 reemplazadas en sus valores top-level; el resto del contrato permanece).
Companion docs (no superseded):
- `docs/architecture/cid_plans_modules_matrix_v1.md` (matriz de modulos por plan y limites por plan; consistente con este canon).
- `docs/architecture/cid_roles_permissions_matrix_v1.md` (matriz operativa de roles, permisos, modulos).
- `docs/architecture/backend_gating_contract_v1.md` (cierre P0/P1 de backend gating).
- `src/config/plans.yml` (codigo legacy, NO canonico; pendiente de migracion).

## 2. Metadata inicial

- **Version**: 1.0.
- **Status**: SPEC / CANONICAL BUSINESS SOURCE.
- **Date**: 2026-06-05.
- **Owners**: CID Product / CID Business / CID Architecture.
- **Scope**: CID SaaS pricing, credits, packages, limits and billing rules.
- **Idioma del canon**: espanol (es-ES).
- **Moneda del canon**: EUR.
- **Mercado inicial**: Espana/UE.
- **Versionado**: este canon se versiona con cada cambio mayor. Cambios menores se anotan en el historial al final del documento.

## 3. Proposito

Este documento es la verdad canonica de pricing, creditos, paquetes, limites y reglas comerciales de CID SaaS. Su proposito es:

- Cerrar la verdad canonica de pricing. Cualquier documento, presentacion, calculadora, propuesta comercial o implementacion que use valores de pricing debe usar los de este documento o marcarlos explicitamente como `TBD_PRICING` / `CONTRACTUAL`.
- Resolver las discrepancias entre documentos previos. Las fases `CID.SAAS.PRICING.CANONICALIZATION.1` (esta), `CID.SAAS.PRICING.PUBLIC.LANDING.1` y `CID.SAAS.BILLING.MODELS.1` las cierran.
- Servir de base futura para Stripe (`CID.SAAS.STRIPE.PRODUCTS.PRICES.1`).
- Servir de base futura para Billing UI (`CID.SAAS.BILLING.ADMIN.UI.1`).
- Servir de base futura para plan gates, module gates y credit gates (`CID.SAAS.PLAN.GATES.BACKEND.1`, `CID.SAAS.MODULE.GATES.BACKEND.1`, `CID.SAAS.CREDIT.GATES.BACKEND.1`).
- Separar pricing publico, pricing interno y condiciones Enterprise. Pricing publico es el que aparece en la landing y la UI. Pricing interno es el que usa operaciones y soporte. Enterprise es contractual.

Regla de oro: **un solo canon, una sola moneda, un solo set de limites**. Si un valor nuevo contradice este documento sin una actualizacion versionada, el canon gana.

## 4. Alcance

- **CID como SaaS integral.** Este documento define el pricing del producto autenticado, no de la landing publica ni de servicios sueltos.
- **AILinkCinema como canal comercial/landing.** AILinkCinema vende modulos o capta leads, pero no redefine el contrato de producto. Si AILinkCinema vende algo, debe existir en CID bajo un plan compatible.
- **Esta fase no implementa Stripe.** Solo define los nombres futuros de productos, precios y paquetes para que la integracion sea directa.
- **Esta fase no implementa billing backend.** El modelo de datos de suscripciones, webhooks y ledger es objeto de fases posteriores.
- **Esta fase no cambia permisos.** La matriz de roles/permisos y el contrato de gating cerrado no se tocan.
- **Esta fase no cambia frontend.** Las decisiones de UI para mostrar precios y CTAs de upgrade se derivan, no se aplican.
- **Esta fase no cambia modelos de datos.** El schema vendra en fases posteriores.
- **Esta fase no cambia planes en codigo.** `src/config/plans.yml` sigue siendo legacy y se migrara en `CID.SAAS.PRICING.CANONICALIZATION.1` (fase de implementacion) o en `CID.SAAS.STRIPE.PRODUCTS.PRICES.1`, lo que llegue antes. No se modifica en esta fase.

## 5. Fuentes reconciliadas

Este canon reconcilia seis fuentes. La columna "Decision canonica" indica que valor de este documento aplica; la columna "Estado" indica que se hace con la fuente original.

| Documento fuente | Que aporta | Conflictos detectados | Decision canonica | Estado |
|---|---|---|---|---|
| `cid_saas_model_contract_v1.md` | Modelo SaaS: 22 roles, 31 permisos, planes 5/5, matriz 19 modulos. | Creditos incluidos antiguos (2.000/10.000/40.000/150.000) y modulos 19 (vs 21 actuales). | Creditos: 500/2.000/7.500/20.000/contractual. Modulos: 21 (segun `cid_plans_modules_matrix_v1.md`). Precios: 99/299/799/1.490/3.500+ €. | Parcialmente superseded en pricing y creditos. |
| `cid_plans_modules_matrix_v1.md` | Matriz de 21 modulos x 5 planes con 5 estados; limites por plan cuantitativos; bolsas. | Ninguno significativo; consistente con el canon. | Coherente. Se respeta. | Vigente, companiero. |
| `cid_roles_permissions_matrix_v1.md` | Matriz operativa de roles, permisos, modulos. | Ninguno. | Coherente. Se respeta. | Vigente, companiero. |
| `cid_pricing_canonicalization_needed_v1.md` | Documenta la discrepancia entre docs y codigo. | Doc dice 8.000 creditos/mes para Studio; canon dice 7.500. | Creditos Studio: 7.500 (canon gana). | Discrepancia resuelta en §26 de este documento. |
| `cid_pricing_competitive_baseline_v1.md` | Analisis competitivo de 12 productos; hipotesis de precios. | Hipotesis §10.1 dice 100/300/1.000/3.000 creditos; canon dice 500/2.000/7.500/20.000. | Canon gana. La hipotesis v1.0 queda como referencia competitiva, no como tabla de precios. | Parcialmente superseded en tabla de hipotesis. |
| `cid_credits_business_model_v1.md` | Modelo de creditos por operacion; coste por uso. | §20 dice 100/300/1.000/3.000 creditos; canon dice 500/2.000/7.500/20.000. | Canon gana. La tabla de coste por operacion §19 se mantiene como referencia provisional; se cierra en `CID.SAAS.CREDITS.USAGE.MODEL.1`. | Parcialmente superseded en creditos incluidos. |
| `src/config/plans.yml` (legacy code) | Configuracion de planes en codigo (Demo/Free/Creator/Producer/Studio/Enterprise a 0/0/9.99/19.99/29.99/99.99). | Planes, nombres y precios totalmente divergentes. | NO canonico. Se migra en fase de implementacion. | Legacy, pendiente de migracion. |

Regla de precedencia:

1. Si un valor aparece en este documento, este documento gana.
2. Si un valor no aparece en este documento pero aparece en `cid_plans_modules_matrix_v1.md` o `cid_roles_permissions_matrix_v1.md`, gana el companiero (es coherente con el canon).
3. Si un valor aparece solo en `cid_pricing_competitive_baseline_v1.md` o `cid_credits_business_model_v1.md`, gana este canon.
4. Si un valor aparece solo en `src/config/plans.yml`, se ignora; ese archivo es legacy.

## 6. Tabla canonica de planes

| `plan_key` | Nombre publico | Precio mensual | Precio anual efectivo | Creditos incluidos/mes | Usuarios incluidos | Proyectos activos | Almacenamiento incluido | Jobs IA concurrentes | Soporte | Target customer |
|---|---|---|---|---|---|---|---|---|---|---|
| `starter` | Starter | 99 €/mes | 990 €/ano | 500 | 2 | 1 | 10 GB | 1 | Estandar (email, 48h laborables) | Productor independiente, cortometraje, freelance. |
| `pro` | Pro | 299 €/mes | 2.990 €/ano | 2.000 | 5 | 3 | 50 GB | 2 | Prioritario ligero (email + chat, 24h) | Productora pequena-mediana, agencia. |
| `studio` | Studio | 799 €/mes | 7.990 €/ano | 7.500 | 15 | 10 | 250 GB | 4 | Prioritario (email + chat + telefono, 8h) | Productora mediana, estudio, broadcaster. |
| `premium` | Premium | 1.490 €/mes | 14.900 €/ano | 20.000 | 30 | 25 | 1 TB | 8 | Prioritario alto (email + chat + telefono 12x5, 4h) | Productora grande, agencia internacional, broadcaster. |
| `enterprise` | Enterprise | Desde 3.500 €/mes (contractual) | Contractual | Contractual (min. recomendado 50.000) | Contractual | Contractual | Contractual | Contractual | Dedicado 24/7, SLA contractual | Major studio, broadcaster, plataforma de distribucion, institucion publica. |

Notas:

- Los precios sin IVA salvo que se indique lo contrario.
- Moneda principal: EUR.
- Mercado inicial: Espana/UE.
- El precio anual se calcula como 10 meses pagados por 12 meses de servicio (ver seccion 8).
- "Usuarios incluidos" y "Proyectos activos" son limites del plan, no capacidades extras.
- "Almacenamiento incluido" es la cuota de la organizacion, no por proyecto.
- "Jobs IA concurrentes" es el limite de jobs ejecutandose simultaneamente en la organizacion.
- Los limites detallados (exports, integraciones, API, auditoria, retencion, trazabilidad) estan en `cid_plans_modules_matrix_v1.md` y se referencian aqui por consistencia.

## 7. Precios mensuales

Fijados en este canon:

- `starter`: 99 €/mes.
- `pro`: 299 €/mes.
- `studio`: 799 €/mes.
- `premium`: 1.490 €/mes.
- `enterprise`: desde 3.500 €/mes, contractual.

Reglas:

- **Precios sin IVA** salvo que se indique lo contrario. El IVA/IGIC u otros impuestos se aplican en factura segun la jurisdiccion del cliente.
- **Moneda principal EUR.** El precio publico se publica en EUR. Para mercados no-EUR, el precio se calcula al tipo de cambio del dia de facturacion; los planes Enterprise pueden fijar precio en otra moneda.
- **Mercado inicial**: Espana/UE. Otros mercados se abordan en fases de internacionalizacion posteriores.
- **Enterprise** puede tener pricing anual, plurianual o por volumen. Se negocia caso por caso.
- **Cambio de plan** dentro de Starter/Pro/Studio/Premium: prorrateo al dia con efecto inmediato (ver seccion 15).
- **Promociones temporales**: permitidas con fecha de fin y `code` interno. No alteran el canon.

## 8. Precios anuales

Calculo: pago de 10 meses por 12 meses de servicio. Equivale a un descuento del ~16,67 % sobre el mensual (2 meses bonificados).

| `plan_key` | Precio mensual | Precio anual canonico | Ahorro frente a mensual | Equivalencia EUR/mes |
|---|---|---|---|---|
| `starter` | 99 €/mes | 990 €/ano | 198 € (2 meses) | 82,50 €/mes efectivos |
| `pro` | 299 €/mes | 2.990 €/ano | 598 € (2 meses) | 249,17 €/mes efectivos |
| `studio` | 799 €/mes | 7.990 €/ano | 1.598 € (2 meses) | 665,83 €/mes efectivos |
| `premium` | 1.490 €/mes | 14.900 €/ano | 2.980 € (2 meses) | 1.241,67 €/mes efectivos |
| `enterprise` | Desde 3.500 €/mes | Contractual | Contractual | Contractual |

Reglas:

- **Ahorro frente a mensual**: el canon afirma 2 meses bonificados; no aplicar otro descuento anual salvo promocion explicita con fecha de fin.
- **Prorrateo en cambio de plan anual**: si el cliente cambia de plan anual a mitad de ciclo, se calcula el credito proporcional sobre el precio anual del plan original y se aplica al nuevo plan. El sistema no devuelve dinero; acredita el saldo.
- **Upgrade anual**: el cliente puede subir de plan anual en cualquier momento. Se aplica el canon del plan nuevo, se acredita el saldo no consumido del plan anterior, y se renueva el ciclo en la fecha original.
- **Downgrade anual**: el downgrade desde un plan anual se aplica al final del ciclo de facturacion, no de forma inmediata. Excepcion: el cliente acepta perder el descuento anual y paga el prorrateo del nuevo plan desde el dia del cambio.
- **Cancelacion anual**: si el cliente cancela dentro de los 14 dias posteriores al cobro anual, se devuelve el importe integro. Pasados los 14 dias, no hay reembolso; el servicio sigue hasta el final del periodo anual pagado.
- **Enterprise**: el ciclo y las condiciones se negocian en el contrato.

## 9. Creditos incluidos

Tabla canonica:

| `plan_key` | Creditos incluidos / mes |
|---|---|
| `starter` | 500 |
| `pro` | 2.000 |
| `studio` | 7.500 |
| `premium` | 20.000 |
| `enterprise` | Contractual (minimo recomendado: 50.000) |

Reglas:

- Los creditos incluidos se resetean cada ciclo mensual. Si el cliente paga anual, los creditos se asignan mensualmente dentro del ciclo anual; no se anticipa el año entero.
- No hacen rollover por defecto. Los creditos no consumidos al cierre del ciclo se pierden.
- Enterprise puede tener rollover contractual, segun el acuerdo. Por defecto contractual: 100 % de los incluidos pueden hacer rollover hasta un maximo de 2 ciclos. Detalles en el contrato.
- Creditos incluidos y creditos comprados deben separarse contablemente. El sistema mantiene dos saldos: `included_monthly_remaining` y `purchased_balance`. La suma es el saldo disponible.
- Los creditos incluidos se consumen antes que los comprados, salvo decision contraria justificada (Enterprise con prioridad custom).
- Los creditos de trial y los creditos promocionales son un tercer saldo, `adjustment_credits`, y se consumen primero que los incluidos.

## 10. Bolsas adicionales

CREDITO EXTRA que el cliente compra sin cambiar de plan. Se aplican al saldo `purchased_balance` y tienen caducidad a 12 meses.

| `package_key` | Plan compatible | Creditos | Precio | Ratio €/credito | Caducidad | Notas |
|---|---|---|---|---|---|---|
| `starter_500_pack` | starter | 500 | 49 € | 0,098 €/cr | 12 meses | Bolsa pequena para escalar. |
| `pro_1500_pack` | pro | 1.500 | 119 € | 0,0793 €/cr | 12 meses | Estandar. |
| `pro_3000_pack` | pro | 3.000 | 229 € | 0,0763 €/cr | 12 meses | Bono por volumen. |
| `studio_10000_pack` | studio | 10.000 | 699 € | 0,0699 €/cr | 12 meses | Produccion a escala. |
| `premium_custom_pack` | premium | Contractual | Contractual | Contractual | Contractual | Negociado caso por caso. |
| `enterprise_custom_pack` | enterprise | Contractual | Contractual | Contractual | Contractual | Incluido en pool mensual o bolsa extra. |

Reglas:

- Las bolsas caducan a 12 meses desde la compra. El sistema avisa 30, 15 y 1 dias antes.
- No son recurrentes; se facturan al momento de la compra.
- Pueden comprarse varias veces; cada compra es independiente y su caducidad empieza desde la fecha de compra.
- No deben permitir acceso a modulos no incluidos en el plan. Si el usuario compra creditos pero su plan no incluye el modulo, el modulo sigue bloqueado (los creditos quedan en su saldo pero no son utilizables para ese modulo).
- Si el usuario hace downgrade a un plan incompatible, las bolsas no consumidas se mantienen durante 30 dias (periodo de gracia) y caducan al cambiar.
- Las bolsas son transferibles dentro de la misma organizacion entre proyectos; la transferencia la realiza un `organization_admin` o `project_admin`.

## 11. Limites canonicos por plan

Limites cuantitativos por plan. Coherentes con `cid_plans_modules_matrix_v1.md` (seccion 9). Cualquier ajuste a estos valores requiere una actualizacion versionada de este canon.

| Limite | starter | pro | studio | premium | enterprise |
|---|---|---|---|---|---|
| Organizaciones incluidas | 1 | 1 | 1 | 1 | Contractual (1+) |
| Usuarios incluidos | 2 | 5 | 15 | 30 | Contractual |
| Usuarios adicionales | No disponibles (upgrade a Pro) | TBD_PRICING (ver §12) | TBD_PRICING (ver §12) | TBD_PRICING (ver §12) | Contractual |
| Proyectos activos | 1 | 3 | 10 | 25 | Contractual |
| Almacenamiento incluido | 10 GB | 50 GB | 250 GB | 1 TB | Contractual |
| Almacenamiento adicional | No disponible (upgrade) | TBD_PRICING (ver §13) | TBD_PRICING (ver §13) | TBD_PRICING (ver §13) | Contractual |
| Jobs IA concurrentes | 1 | 2 | 4 | 8 | Contractual |
| Exports / mes | 10 (basicos) | 50 (profesionales) | 200 (profesionales avanzados) | 1.000 (completos) | Contractual |
| Integraciones externas | 1 | 3 | 10 | Ilimitadas | Contractual |
| API publica | No | Lectura (1.000 req/dia) | Lectura/escritura (10.000 req/dia) | Completa (100.000 req/dia) | Contractual |
| Soporte | Estandar | Prioritario ligero | Prioritario | Prioritario alto | Dedicado 24/7 SLA |
| Auditoria | 30 dias, sin export | 90 dias, export CSV | 180 dias, export CSV/JSON | 365 dias, export + alertas + dashboard | Contractual (1-7 anos) |
| Retencion de datos post-baja | 90 dias | 180 dias | 365 dias | 730 dias | Contractual |
| Trazabilidad IA | Basica (job_id, provider, model, output_asset) | Estandar (+input_hash, prompt_version, credit_estimate, credits_charged) | Avanzada (+parametros, parent_job_id, trace_id, replay) | Auditable + export CSV/JSON | Full + cross-organization + export a SIEM |

Notas:

- Los limites `TBD_PRICING` se cierran en las fases `CID.SAAS.USER_SEATS.PRICING.1` y `CID.SAAS.STORAGE.PRICING.1` (ver roadmap seccion 27).
- Los modulos disponibles por plan y sus estados (`included`, `limited`, `add_on`, `not_included`, `enterprise_only`) estan en `cid_plans_modules_matrix_v1.md` seccion 5.3. Este canon no redefine la matriz de modulos.

## 12. Usuarios adicionales

Regla canonica:

- **Starter**: no permite usuarios extra. El limite es 2 usuarios incluidos. Cualquier invite que supere el limite devuelve `seat_limit_reached`. El usuario debe upgrade a Pro.
- **Pro**: usuarios extra disponibles como add-on. Precio por definir.
- **Studio**: usuarios extra disponibles como add-on. Precio por definir.
- **Premium**: usuarios extra disponibles como add-on. Precio por definir.
- **Enterprise**: contractual.

`TBD_PRICING`: hasta que se cierre la fase `CID.SAAS.USER_SEATS.PRICING.1`, el canon afirma la disponibilidad del add-on pero no el precio. El sistema mostrara el CTA "Upgrade to add seats" sin importe hasta que se cierre la fase.

Referencia provisional (no canon): `cid_plans_modules_matrix_v1.md` propuso Pro +1/19 €/mes, Studio +1/15 €/mes, Premium +1/12 €/mes. Esos valores son orientativos hasta que `CID.SAAS.USER_SEATS.PRICING.1` los cierre.

Reglas:

- La compra de usuarios adicionales se factura mensualmente, prorrateada al dia en el ciclo de compra.
- Cancelar un usuario adicional: el cupo se libera al final del ciclo. El usuario no se ve afectado inmediatamente; el siguiente ciclo ya no factura ese asiento.
- Los usuarios `cliente_externo` y `revisor_invitado` no cuentan para la cuota de asientos del plan. Esto es valido en todos los planes y se respeta independientemente del addon de asientos.

## 13. Almacenamiento adicional

Regla canonica:

- **Starter**: no permite almacenamiento adicional. Cualquier subida que exceda el limite devuelve `storage_limit_reached`. El usuario debe upgrade a Pro.
- **Pro**: almacenamiento adicional disponible como add-on. Precio por definir.
- **Studio**: almacenamiento adicional disponible como add-on. Precio por definir.
- **Premium**: almacenamiento adicional disponible como add-on. Precio por definir.
- **Enterprise**: contractual.

`TBD_PRICING`: hasta que se cierre la fase `CID.SAAS.STORAGE.PRICING.1`, el canon afirma la disponibilidad del add-on pero no el precio. El sistema mostrara el CTA "Need more storage?" sin importe hasta que se cierre la fase.

Reglas:

- La compra de almacenamiento adicional se factura mensualmente, prorrateada al dia.
- El almacenamiento es a nivel de organizacion, no de proyecto. Un proyecto no puede tener su propio limite; hereda el de la organizacion.
- Periodo de gracia: 7 dias para que el cliente libere espacio o upgrade. Pasado el periodo, el sistema no borra nada (no destructivo) pero no permite nuevas subidas.

## 14. Reglas de trial / demo / beta / public SaaS

Cuatro modos comerciales diferenciados. Cada uno tiene objetivo, limites, creditos, acceso a modulos, riesgo y criterio de conversion propios.

### 12.1 demo_client

- **Objetivo**: mostrar el producto a un prospecto cualificado, sin compromiso, durante un periodo corto.
- **Limites**: 1 organizacion, 1 proyecto activo, 1 usuario, 5 GB de almacenamiento, 1 job IA concurrente, 50 exports totales, 0 integraciones.
- **Creditos**: 50 creditos one-shot, no renovables, sin bolsas.
- **Acceso a modulos**: solo lectura o ejecucion limitada en `project_hub`, `screenwriting` (analisis), `character_bible` (read), `budget` (read), `ai_traceability` (read). El resto esta oculto o en candado.
- **Riesgo comercial**: bajo si el prospecto es cualificado; medio si se regala a leads frios porque consume capacidad del cluster.
- **Criterio de conversion**: a `private_beta` si el prospecto pasa a evaluacion, o a `public_saas` trial Pro si el prospecto es self-service.

### 12.2 private_beta

- **Objetivo**: evaluar el producto con un conjunto cerrado de clientes pioneros, recoger feedback, validar pricing y comportamiento bajo carga real. Acceso gratuito o bonificado.
- **Limites**: configurables por invitacion. Tipico: 1 organizacion, 3 proyectos activos, 5 usuarios, 50 GB, 2 jobs IA concurrentes, 50 exports/mes, 3 integraciones.
- **Creditos**: cuota mensual renovable mientras la beta este activa. Sin bolsas; si se agotan, se reactiva la cuota (politica de no-spam).
- **Acceso a modulos**: modulos completos del plan Pro o Studio segun el beta. Modulos experimentales pueden activarse como `enterprise_only` o `add_on` con override beta.
- **Riesgo comercial**: medio. El beta tester recibe capacidad real; si se va, hay churn potencial. Si se queda, hay conversion a plan de pago. Hay que gestionar bien la transicion.
- **Criterio de conversion**: a `public_saas` plan Pro o superior al cierre del beta, con onboarding asistido y posible lock-in de precio durante 3 meses.

### 12.3 public_saas

- **Objetivo**: producto comercial general, disponible para cualquier cliente que pague o este en trial.
- **Limites**: los de la seccion 9 por plan. Trial 14 dias con plan Pro activado (ver §12.4).
- **Creditos**: cuota del plan + bolsas adicionales.
- **Acceso a modulos**: la matriz principal de `cid_plans_modules_matrix_v1.md` seccion 5.3 segun plan contratado.
- **Riesgo comercial**: bajo en ingresos pero alto en soporte si la documentacion es insuficiente. El reto es el ratio conversion trial -> pago.
- **Criterio de conversion**: trial -> pago a Pro, Studio, Premium o Enterprise segun el tamano del proyecto del cliente. Si el trial expira sin conversion, el tenant pasa a estado `expired` y los datos se conservan 30 dias antes de archivar.

### 12.4 trial

- **Objetivo**: prueba gratuita del producto en modo `public_saas` con plan Pro activado, durante 14 dias, con tarjeta requerida.
- **Duracion**: 14 dias desde la primera activacion. Renovable una vez por cuenta; no mas.
- **Plan activado**: Pro canonico (299 €/mes, 2.000 creditos, 5 usuarios, 3 proyectos, 50 GB, 2 jobs concurrentes).
- **Creditos**: 2.000/mes Pro canonicos. NO se mezclan con creditos de pago: se asignan a `trial_credits` (subtipo de `adjustment_credits`). Al expirar el trial, los creditos trial no consumidos se pierden.
- **Tarjeta requerida**: para activar el trial. Si el cliente no convierte al dia 15, se cobra el primer mes Pro canonico (o se cancela, segun la opcion del cliente).
- **Sin cargo hasta dia 15**: la suscripcion existe desde el dia 1 pero la primera factura se emite el dia 15 si el cliente no ha cancelado.
- **Limites anti-abuso**: 1 trial por organizacion; 1 trial por tarjeta; deteccion de patrones de tarjeta quemada; bloqueo de tarjetas prepago de baja verificacion.
- **Modulos disponibles**: la matriz Pro completa.
- **Riesgo comercial**: bajo si los limites anti-abuso estan activos; medio si se abusa (multi-cuentas, tarjetas rotadas).
- **Criterio de conversion**: cobro automatico al dia 15 si el cliente no cancela; conversion a plan de pago (Pro, Studio, Premium, Enterprise) en cualquier momento del trial.

### 12.5 Tabla resumen

| Dimension | demo_client | private_beta | public_saas | trial |
|---|---|---|---|---|
| Organizaciones | 1 | 1 | 1 (Enterprise: varias) | 1 |
| Usuarios | 1 | 5 (tipico) | 2/5/15/30/custom | 5 (Pro) |
| Proyectos | 1 | 3 | 1/3/10/25/custom | 3 (Pro) |
| Almacenamiento | 5 GB | 50 GB | Por plan | 50 GB (Pro) |
| Creditos | 50 one-shot | 1.000/mes renovables | Por plan + bolsas | 2.000/mes (Pro, trial_credits) |
| Modulos | 5 basicos | Plan Pro/Studio + experimentales | Por plan (matriz) | Matriz Pro completa |
| Soporte | Email | Email + onboarding | Por plan | Email (Pro trial) |
| Facturacion | No | No / bonificada | Real | Real desde dia 15 |
| Riesgo comercial | Bajo | Medio | Bajo/alto segun conversion | Bajo con anti-abuso |
| Conversion tipica | -> beta o trial | -> plan pago | (es el destino) | -> plan pago |

## 15. Reglas de upgrade

Comportamiento canonico cuando el cliente sube de plan.

- **Upgrade inmediato**: el nuevo plan aplica desde el momento del upgrade. No se espera al cierre del ciclo.
- **Prorrateo al dia**: el cliente paga la diferencia entre el plan actual y el nuevo, prorrateada por los dias restantes del ciclo. El calculo lo hace el sistema, no el cliente.
- **Conservacion de creditos comprados**: las bolsas compradas (saldo `purchased_balance`) se conservan integramente y mantienen su caducidad original.
- **Reinicio de creditos incluidos**: los creditos incluidos del nuevo plan se asignan al momento del upgrade, prorrateados por los dias restantes del ciclo. Ejemplo: el cliente Pro upgrade a Studio el dia 15 de un ciclo de 30 dias; recibe 7.500/2 = 3.750 creditos Studio para los 15 dias restantes; el dia 1 del siguiente ciclo recibe los 7.500 completos.
- **Ampliacion inmediata de limites**: los limites del nuevo plan (usuarios, proyectos, almacenamiento, jobs concurrentes, exports, integraciones, API) se aplican al momento del upgrade.
- **Desbloqueo de modulos**: los modulos `not_included` en el plan anterior y `included`/`limited`/`add_on` en el nuevo quedan disponibles al instante.
- **Cambio de concurrencia de jobs**: si el nuevo plan permite mas jobs concurrentes, el sistema aumenta el limite de inmediato. Los jobs en curso no se cancelan.
- **Cambio de almacenamiento**: el almacenamiento disponible aumenta al instante. Si el cliente estaba cerca del limite, el espacio nuevo es utilizable sin intervencion manual.
- **Auditoria del cambio**: evento `subscription_upgraded` con `old_plan`, `new_plan`, `pro_rata_amount`, `effective_at`, `actor_id`.

## 16. Reglas de downgrade

Comportamiento canonico cuando el cliente baja de plan.

- **Downgrade al final del ciclo**: por defecto, el downgrade aplica al cierre del ciclo de facturacion, no inmediatamente. Esto evita perder el pago del mes en curso.
- **Excepcion inmediata**: el cliente puede solicitar downgrade inmediato. En ese caso, se aplica al momento pero no hay reembolso del periodo ya pagado.
- **Periodo de gracia de 30 dias**: si el cliente excede los limites del nuevo plan al momento del downgrade (por ejemplo, tiene 5 usuarios y baja de Studio con 15 a Pro con 5), el sistema activa un periodo de gracia de 30 dias.
- **Bloqueo de nuevos jobs si excede limites**: durante el periodo de gracia, los nuevos jobs que excedan los limites se rechazan con el codigo canonico (`user_limit_reached`, `project_limit_reached`, `storage_limit_reached`, etc.). Los jobs en curso no se cancelan.
- **No borrar datos automaticamente**: el sistema no destruye datos excedentes. Los proyectos, usuarios, assets y creditos comprados se conservan.
- **Congelar exports premium**: si el nuevo plan no incluye el formato de export que el cliente usaba, los exports premium fallan durante el periodo de gracia. El sistema sugiere re-exportar antes del fin del periodo.
- **Mantener acceso lectura a material historico**: el cliente siempre puede leer y descargar material historico, incluso si el plan nuevo no permite escritura. Esto aplica a `project_hub`, `ai_traceability` y al modulo que sea.
- **Modulos en estado `graced`**: los modulos `not_included` en el nuevo plan pasan a estado `graced` durante 30 dias. En `graced`, los assets son visibles pero no editables; los jobs IA fallan; los exports se bloquean para formatos no incluidos.
- **Avisos durante el periodo de gracia**: el sistema avisa al cliente en T-7, T-1 y T-0.
- **Al expirar el periodo de gracia**: los modulos `graced` pasan a no disponibles; los datos excedentes se mueven a archivo frio. No se borra nada; el cliente puede restaurar pagando un plan compatible.
- **Auditoria del cambio**: evento `subscription_downgraded` con `old_plan`, `new_plan`, `effective_at`, `grace_period_end`, `exceeded_limits` (lista), `actor_id`.

## 17. Cancelacion y impago

Estados de suscripcion y comportamiento en cada uno.

### 15.1 active

- Estado normal. El cliente usa el plan, los creditos fluyen, el soporte responde.
- Eventos normales: `subscription_started`, `subscription_upgraded`, `subscription_downgraded`, `credit_package_purchased`, `credits_reserved`, `credits_consumed`.

### 15.2 past_due

- El pago ha fallado (tarjeta rechazada, fondos insuficientes, fraude detectado).
- Comportamiento: el sistema intenta el cobro de nuevo segun la politica del proveedor de pagos (tipico: 3 intentos en 7 dias). El cliente recibe emails de aviso.
- Acceso: el sistema mantiene el acceso durante el periodo de reintentos para no impactar al cliente por un fallo tecnico.
- Si tras los reintentos el pago sigue fallando, el sistema mueve la suscripcion a `suspended`.

### 15.3 suspended

- Suspension por impago prolongado o por accion administrativa.
- Acceso: lectura permitida con throttling reducido; escritura bloqueada con `423 Locked`; jobs IA rechazados con `402 Payment Required`; integraciones externas pausadas.
- Datos: se conservan durante el periodo legal (90-365 dias segun plan); el cliente puede solicitar export.
- Reactivacion: actualizar metodo de pago. El sistema cobra los meses atrasados, limpia el flag `suspended_at` y restaura el plan con prorrateo. Los creditos incluidos no consumidos se pierden; los creditos comprados se mantienen.
- Auditoria: `subscription_past_due`, `subscription_suspended`, `subscription_reactivated`.

### 15.4 cancelled

- El `organization_owner` cancela la suscripcion. La cancelacion es definitiva; reactivacion requiere nuevo contrato.
- Acceso: igual que `suspended`.
- Datos: se conservan durante el periodo legal; el cliente puede solicitar export en cualquier momento. Pasado el periodo, los datos se mueven a archivo frio; pasado el periodo legal, se borran fisicamente.
- Reactivacion: requiere nuevo pago y, opcionalmente, cambio de plan. El sistema trata la reactivacion como una nueva suscripcion.
- Auditoria: `subscription_cancelled`, `subscription_reactivated` (si aplica), `data_archived` (al cierre del periodo), `data_purged` (al cierre del periodo legal).

### 15.5 Tabla resumen

| Estado | Acceso lectura | Acceso escritura | Jobs IA | Datos | Reactivacion |
|---|---|---|---|---|---|
| active | Si | Si | Si | Mantenidos | n/a |
| past_due | Si | Si (limitado) | Si (limitado) | Mantenidos | Actualizar pago |
| suspended | Si (throttling) | No | No | Mantenidos 90-365d | Actualizar pago + meses atrasados |
| cancelled | Si (throttling) | No | No | Mantenidos 90-365d + archivo frio | Nuevo contrato |

## 18. Regla de consumo de creditos

Orden canonico de consumo cuando se ejecuta un job IA:

1. **Creditos promocionales / trial** (`adjustment_credits`): se consumen primero. Incluyen creditos trial, regalos de soporte, promos, compensaciones. Su caducidad es independiente.
2. **Creditos incluidos del ciclo** (`included_monthly_remaining`): se consumen en segundo lugar, hasta agotar la cuota del mes. No tienen caducidad dentro del mes; al cierre del ciclo, el remanente se pierde.
3. **Creditos comprados** (`purchased_balance`): se consumen en tercer lugar, priorizando los de caducidad mas proxima (FIFO por expiracion). Caducan a 12 meses.
4. **Creditos enterprise / ajustes manuales** (`enterprise_credits` o equivalentes): se consumen en ultimo lugar. Aplican solo a planes Enterprise con configuracion custom; pueden tener rollover, prioridad custom o reglas de consumo especificas del contrato.

Estados de un credito (ciclo de vida):

- **available**: parte de cualquier saldo. Puede ser reservado por un job.
- **reserved**: bloqueado por un job en curso. Si el job termina OK, pasa a `consumed`. Si falla por causa tecnica, vuelve a `available`. Si falla por error del usuario, pasa a `consumed` (politica de no-spam).
- **consumed**: gastado. No se recupera salvo rollback explicito.
- **expired**: llego a su fecha de expiracion (bolsas a 12 meses, incluidos al cierre del ciclo). No puede ser reservado.
- **refunded**: devuelto al cliente por motivo documentado (soporte, error de plataforma, cancelacion). Vuelve a `available` o se anota como `adjustment_credits`.
- **adjusted**: modificado manualmente por soporte con motivo obligatorio (compensacion, correccion). Queda registrado en auditoria.

Reglas de reserva:

- La reserva se hace **antes de iniciar un job IA pesado**. El sistema calcula `credit_estimate` con la tabla de coste por operacion (seccion 17) y bloquea esa cantidad del saldo disponible.
- **Liberacion si el job falla por causa tecnica**: timeout, error de proveedor, validacion de plataforma, error de orquestacion. El `credit_estimate` se libera y el evento `credits_refunded` se registra.
- **Consumo si el job se completa**: al cerrar el job como `succeeded`, la reserva pasa a `consumed` y el evento `credits_consumed` se registra.
- **Consumo parcial si el job produjo resultado parcial util**: si el job falla a mitad pero produjo un asset utilisable (ej. un storyboard con 8 de 10 planos), se cobra la fraccion correspondiente segun la politica de la operacion; el resto se libera.
- **No consumir si falla por error interno antes de ejecutar IA**: si la plataforma rechaza el job por configuracion, validacion de payload, o error interno antes de invocar el motor IA, no se consume credito. Se registra el rechazo sin cargo.
- **Politica de no-spam para errores del usuario**: input invalido, cancelacion voluntaria, parametros mal configurados. El credito reservado se consume para evitar que un usuario abuse lanzando jobs sin pagar coste.

## 19. Taxonomia de consumo

Cuatro rangos segun el coste computacional y operativo de la accion. Esta taxonomia guia la documentacion de precios y la explicacion al cliente.

| Rango | Coste (creditos) | Descripcion |
|---|---|---|
| `low_cost` | 1-10 | Operaciones ligeras, baja latencia, modelos pequenos. |
| `medium_cost` | 10-100 | Operaciones medias, varios segundos, modelos medianos. |
| `high_cost` | 100-1.000 | Operaciones pesadas, minutos, modelos grandes o GPU dedicada. |
| `enterprise_cost` | Contractual | Operaciones a medida, GPU dedicada, integraciones custom. |

Mapeo provisional de operaciones a rangos. Se cierra en `CID.SAAS.CREDITS.USAGE.MODEL.1`.

| Operacion | Rango | Coste orientativo (creditos) | Notas |
|---|---|---|---|
| Analisis textual (resumen, extraccion) | `low_cost` | 1-5 | Bajo coste, alta frecuencia. |
| Resumen de guion | `low_cost` | 3-5 | Por guion o por bloque. |
| Character bible (crear entrada) | `low_cost` | 2-3 | Por personaje. |
| Presupuesto (generacion inicial) | `low_cost` | 5-10 | Por presupuesto. |
| RAG avanzado (con citacion) | `medium_cost` | 15-30 | Por consulta con contexto amplio. |
| Storyboard image generation (estandar) | `medium_cost` | 30-60 | Por hoja. |
| Storyboard image generation (alta calidad) | `high_cost` | 60-120 | Por hoja, con calidad maxima. |
| Concept art (estandar) | `medium_cost` | 40-90 | Por lamina. |
| Video generation (5-15 s) | `high_cost` | 150-300 | Por clip. |
| Dubbing / localization (1 min) | `medium_cost` | 50-80 | Por minuto, por idioma. |
| Restoration (1 min completa) | `high_cost` | 100-200 | Por minuto. |
| Delivery QC | `low_cost` | 5-15 | Por master. |
| Integrations / API heavy use | `high_cost` | 100-500 | Por operacion batch. |
| Entrenamiento personalizado | `enterprise_cost` | Contractual | Solo Enterprise. |
| GPU dedicada | `enterprise_cost` | Contractual | Solo Enterprise. |

## 20. Stripe readiness

Nombres futuros de productos, precios y paquetes en Stripe. Esta fase no implementa Stripe; solo define la nomenclatura para que la integracion sea directa.

### 18.1 Claves de productos (Stripe Products)

| Plan / paquete | `stripe_product_key` propuesto |
|---|---|
| Starter | `cid_starter_product` |
| Pro | `cid_pro_product` |
| Studio | `cid_studio_product` |
| Premium | `cid_premium_product` |
| Enterprise | `cid_enterprise_product` (configurable) |
| starter_500_pack | `cid_credit_pack_starter_500` |
| pro_1500_pack | `cid_credit_pack_pro_1500` |
| pro_3000_pack | `cid_credit_pack_pro_3000` |
| studio_10000_pack | `cid_credit_pack_studio_10000` |
| premium_custom_pack | `cid_credit_pack_premium_custom` |
| enterprise_custom_pack | `cid_credit_pack_enterprise_custom` |

### 18.2 Claves de precios (Stripe Prices)

| Plan | Mensual | Anual |
|---|---|---|
| Starter | `cid_starter_monthly_eur` | `cid_starter_annual_eur` |
| Pro | `cid_pro_monthly_eur` | `cid_pro_annual_eur` |
| Studio | `cid_studio_monthly_eur` | `cid_studio_annual_eur` |
| Premium | `cid_premium_monthly_eur` | `cid_premium_annual_eur` |
| Enterprise | Contractual | Contractual |

| Bolsa | Clave |
|---|---|
| `starter_500_pack` | `cid_credit_pack_starter_500_eur` |
| `pro_1500_pack` | `cid_credit_pack_pro_1500_eur` |
| `pro_3000_pack` | `cid_credit_pack_pro_3000_eur` |
| `studio_10000_pack` | `cid_credit_pack_studio_10000_eur` |

Convencion de naming:

- Prefijo `cid_` para todos los productos y precios.
- Sufijo `_monthly_eur` o `_annual_eur` para precios recurrentes.
- Sufijo `_eur` para pagos unicos (bolsas).
- Sufijo `_usd`, `_gbp` etc. se anade si se internacionaliza (no en v1).
- Enterprise usa identificadores custom negociados caso por caso.

Reglas:

- Los IDs de Stripe se crean en una sola vez durante `CID.SAAS.STRIPE.PRODUCTS.PRICES.1` y se mantienen estables.
- El billing backend mapea `plan_key` a `stripe_product_key` y `stripe_price_key` sin hardcodear precios.
- Los webhooks de Stripe (suscripcion creada, actualizada, cancelada, pago fallido) se traducen a eventos del canon de auditoria (seccion 20).

## 21. Backend gates derivados

Decisiones futuras que el backend deberia tomar al evaluar una peticion. Cada decision tiene una clave y se conecta con una o varias dependencias de gating existentes o futuras.

| Decision | Clave | Conexion |
|---|---|---|
| El plan del tenant esta activo y no suspendido | `plan_active` | `get_tenant_context` (futuro: `require_plan`). |
| El modulo esta habilitado en el plan del tenant | `module_enabled` | `require_module_access` (existente). |
| El usuario tiene el permiso para la accion | `role_permission` | (futuro) `require_permission`. |
| El usuario tiene acceso al proyecto | `project_access` | `validate_project_access` (existente). |
| El usuario puede escribir en el proyecto | `write_permission` | `require_write_permission` (existente). |
| Hay creditos disponibles para la accion | `credit_available` | (futuro) `require_credit`. |
| Hay almacenamiento disponible para la accion | `storage_available` | (futuro) `require_storage`. |
| Hay un asiento disponible para un nuevo usuario | `seat_available` | (futuro) `require_seat`. |
| Hay cupo de proyecto activo | `project_limit_available` | (futuro) `require_project_limit`. |
| Hay cupo de export mensual | `export_limit_available` | (futuro) `require_export_limit`. |
| La API publica esta habilitada en el plan y scope | `api_access_available` | (futuro) `require_api_access`. |

Reglas:

- Cada decision se evalua en el orden definido por `cid_roles_permissions_matrix_v1.md` seccion 8. Si una falla, las siguientes no se ejecutan.
- El frontend consume `/api/capabilities` (futuro) para saber que decisiones ya estan evaluadas como true/false y mostrar UI coherente.
- Las dependencias futuras se introducen en fases dedicadas, no se acoplan al gating cerrado v1.

## 22. Frontend visibility

Reglas canonicas de como el frontend debe presentar el pricing, los limites y los bloqueos.

- **Frontend nunca es fuente de verdad.** Cualquier decision de plan, modulo, credito, limite, export, integracion, billing, etc. se enforza en el backend. El frontend puede mentir; el backend no.
- **Frontend solo explica, muestra, oculta y guia upgrades.** Su funcion es evitar friccion: no muestra acciones que el backend rechazaria, y muestra mensajes contextuales cuando una accion no esta disponible.
- **Todo bloqueo real viene del backend.** El frontend puede esconder un boton, pero si el usuario conoce la URL y la escribe, el backend responde con el codigo canonico.
- **UI debe mostrar motivo de bloqueo.** Cuando una accion no esta disponible, el tooltip o mensaje debe decir por que (modulo no incluido, limite agotado, creditos insuficientes, etc.).
- **UI debe mostrar accion posible.** El mensaje de bloqueo debe acompanarse de la accion que el usuario puede tomar para desbloquear.
- **CTAs canonicos** (orden de prioridad):
  - `buy_credits`: si la causa es `credit_exhausted`.
  - `upgrade_plan`: si la causa es `module_not_included`, `module_add_on_required`, `seat_limit_reached`, `project_limit_reached`, `storage_limit_reached`, `export_limit_reached`, `api_not_available`.
  - `contact_sales`: si la causa es `enterprise_only` o cualquier condicion Enterprise.
  - `wait_next_cycle`: si la causa es cuota mensual y el cliente no quiere comprar nada.
  - `ask_admin`: si el usuario no es admin de la organizacion.

## 23. Mensajes de bloqueo

Tabla canonica de mensajes para los 10 bloqueos mas comunes. Cada mensaje sigue el formato: "Esta accion requiere [X]. Tu [Y] es [Z]. [CTA]". El backend devuelve `code` y `message`; el frontend muestra el mensaje tal cual (sin reformatear) y anade el CTA del backend.

| Bloqueo | HTTP status | Codigo interno | Mensaje usuario | Accion recomendada |
|---|---|---|---|---|
| `plan_inactive` | 402 | `plan_inactive` | "Tu suscripcion no esta activa. Para continuar, actualiza el metodo de pago o contrata un plan." | Actualizar pago, contactar soporte. |
| `module_not_included` | 403 | `module_not_included` | "El modulo [nombre] no esta disponible en tu plan [plan]. Sube a [plan superior] o activalo como add-on." | Upgrade plan, add-on. |
| `module_add_on_required` | 403 | `module_add_on_required` | "El modulo [nombre] requiere el add-on [add_on]. Activar por [precio]/mes o sube a [plan]." | Activar add-on, upgrade. |
| `credit_exhausted` | 402 | `credit_exhausted` | "Esta accion cuesta unos [N] creditos. Tu saldo actual es [M]. Compra un paquete de [paquete] creditos ([precio]) o sube a [plan] para [cuota] creditos/mes." | Buy credits, upgrade. |
| `storage_limit_reached` | 507 | `storage_limit_reached` | "Has llegado al limite de [N] GB de almacenamiento. Libera espacio o sube a [plan]." | Delete assets, upgrade. |
| `seat_limit_reached` | 403 | `seat_limit_reached` | "Tu plan [plan] incluye [N] usuarios. Tienes [M] usuarios adicionales disponibles contratandolos por [precio]/mes, o sube a [plan]." | Add seats, upgrade. |
| `project_limit_reached` | 403 | `project_limit_reached` | "Tu plan [plan] incluye [N] proyectos activos. Archiva proyectos finalizados o sube a [plan]." | Archive projects, upgrade. |
| `export_limit_reached` | 429 | `export_limit_reached` | "Has llegado al limite de [N] exports/mes de tu plan [plan]. Espera al reset, compra un paquete o sube a [plan]." | Wait, buy, upgrade. |
| `api_not_available` | 403 | `api_not_available` | "La API publica no esta disponible en tu plan [plan]. Sube a Pro para acceso de lectura o Studio para lectura/escritura." | Upgrade. |
| `enterprise_only` | 403 | `enterprise_only` | "La funcionalidad [nombre] esta reservada al plan Enterprise. Contacta a ventas para una propuesta." | Contact sales. |

Reglas:

- El mensaje nunca culpabiliza al usuario; describe la configuracion.
- El mensaje siempre incluye una accion posible.
- El mensaje esta en lenguaje del rol, no en jerga tecnica.
- Multiidioma (minimo es-ES, en-GB, pt-BR en v1).

## 24. Auditoria

Eventos canonicos que el sistema deberia registrar cuando se implemente el canon. Se anexan a los 28 del contrato SaaS, los 9 de la matriz de roles y los 10 de la matriz de planes/modulos. La union de los cuatro conjuntos forma el catalogo completo de eventos auditables de CID.

| Evento | Cuando se registra | Campos clave |
|---|---|---|
| `pricing_plan_created` | Se crea un plan canonico en el sistema. | `actor_id`, `plan_key`, `effective_at`. |
| `pricing_plan_changed` | Se modifica un plan canonico (precio, creditos, limites). | `actor_id`, `plan_key`, `field`, `old_value`, `new_value`, `effective_at`. |
| `subscription_started` | Nueva suscripcion activa. | `actor_id`, `organization_id`, `plan_key`, `billing_cycle` (monthly/annual), `price_paid`, `payment_id`. |
| `subscription_upgraded` | Upgrade inmediato o al final de ciclo. | `actor_id`, `organization_id`, `old_plan`, `new_plan`, `pro_rata_amount`, `effective_at`. |
| `subscription_downgraded` | Downgrade inmediato o al final de ciclo. | `actor_id`, `organization_id`, `old_plan`, `new_plan`, `effective_at`, `grace_period_end`, `exceeded_limits`. |
| `subscription_cancelled` | Cancelacion definitiva. | `actor_id`, `organization_id`, `plan_key`, `cancellation_date`, `data_retention_end`. |
| `subscription_past_due` | Pago fallido tras los reintentos del proveedor. | `actor_id` (system), `organization_id`, `plan_key`, `failed_amount`, `retry_count`. |
| `credit_package_purchased` | Compra de una bolsa de creditos. | `actor_id`, `organization_id`, `package_key`, `credits`, `amount_eur`, `payment_id`, `expires_at`. |
| `credits_reserved` | Reserva al iniciar un job IA. | `actor_id`, `organization_id`, `job_id`, `credit_estimate`, `saldo_origen` (trial/included/purchased/enterprise). |
| `credits_consumed` | Consumo al cerrar un job OK. | `actor_id`, `organization_id`, `job_id`, `credits_charged`, `saldo_origen`. |
| `credits_refunded` | Devolucion tras fallo tecnico o ajuste manual. | `actor_id` (system o support), `organization_id`, `job_id` o `credit_id`, `amount`, `reason`. |
| `credits_expired` | Creditos que llegaron a su fecha de expiracion. | `actor_id` (system), `organization_id`, `amount`, `saldo_origen`, `expired_at`. |
| `limit_reached` | Cualquier limite de plan agotado (usuarios, proyectos, almacenamiento, exports, integraciones, API). | `actor_id`, `organization_id`, `limit_type`, `current_value`, `max_value`, `plan_key`. |
| `module_blocked` | Modulo no disponible en el plan. | `actor_id`, `organization_id`, `module_key`, `plan_key`, `reason` (not_included, add_on_required, enterprise_only, graced). |
| `upgrade_prompt_shown` | El frontend muestra un mensaje de upgrade. | `actor_id`, `organization_id`, `trigger` (module_blocked, limit_reached, credit_exhausted), `shown_at`. |
| `enterprise_override_applied` | Override Enterprise aplicado (modulo, permiso, quota custom). | `actor_id` (preferiblemente global_admin), `organization_id`, `override_type`, `justification`, `scope`. |

Reglas comunes:

- Append-only. Las correcciones se hacen con un evento `audit_event_corrected` que referencia al anterior, no sobreescribiendo.
- Datos personales se seudonimizan tras el periodo legal; el `user_id` y `organization_id` se mantienen.
- El log nunca expone secretos, claves de API, prompts crudos ni contenido de los inputs del cliente.
- El cliente puede descargar su propio log desde el panel de admin (`org_role=admin` o `org_role=billing`). Enterprise puede configurar retention mas larga.
- Los eventos `limit_reached`, `credit_exhausted` y `upgrade_prompt_shown` son senales comerciales: el sistema puede disparar outreach proactivo al account manager.

## 25. Decisiones canonicas

Diez decisiones que el canon afirma y que sirven como referencia rapida.

- **D001**: EUR como moneda inicial del canon. Mercado inicial Espana/UE. Internacionalizacion posterior.
- **D002**: Precios sin IVA. El IVA/IGIC u otros impuestos se aplican en factura segun la jurisdiccion del cliente.
- **D003**: Pago anual con 2 meses bonificados (10 meses pagados por 12 de servicio). No aplicar otro descuento anual salvo promocion explicita con fecha de fin. Enterprise se negocia por contrato.
- **D004**: Creditos incluidos no hacen rollover por defecto. Enterprise puede tener rollover contractual.
- **D005**: Las bolsas de creditos caducan a 12 meses desde la compra. Se factura al momento; no son recurrentes.
- **D006**: Enterprise es contractual en precio, creditos, limites, soporte, SLA, residencia de datos. El canon afirma la disponibilidad del tier pero no los valores concretos.
- **D007**: Los creditos no desbloquean modulos. Si el plan no incluye un modulo, los creditos comprados no permiten acceder a ese modulo.
- **D008**: El backend es la fuente de verdad de todas las decisiones de plan, modulo, credito, limite, export, integracion, billing. El frontend puede mentir; el backend no.
- **D009**: El frontend solo explica, muestra, oculta y guia upgrades. Nunca es la primera ni la ultima linea de defensa.
- **D010**: Este documento reemplaza los valores conflictivos de `cid_pricing_canonicalization_needed_v1.md`, `cid_pricing_competitive_baseline_v1.md` (tabla §10.1) y `cid_credits_business_model_v1.md` (tabla §20). Los companieros (`cid_plans_modules_matrix_v1.md`, `cid_roles_permissions_matrix_v1.md`) son coherentes y se mantienen.

## 26. Conflictos resueltos

Tabla de discrepancias identificadas y resueltas por este canon. La columna "Impacto" describe el efecto practico; la columna "Fase futura" indica donde se cierra la implementacion.

| # | Discrepancia | Valor anterior | Valor nuevo (canon) | Decision | Impacto | Fase futura |
|---|---|---|---|---|---|---|
| C1 | Creditos Starter | 100/mes (hipotesis v1) | 500/mes | Canon | Documentos de hipotesis y competencia quedan como referencia, no como tabla de precios. | `CID.SAAS.STRIPE.PRODUCTS.PRICES.1`. |
| C2 | Creditos Pro | 300/mes (hipotesis v1) | 2.000/mes | Canon | Idem. | Idem. |
| C3 | Creditos Studio | 1.000/mes (hipotesis v1) y 8.000/mes (canonicalization v1) | 7.500/mes | Canon | Resuelve la doble discrepancia: baja de 8.000 a 7.500 respecto a canonicalization, sube de 1.000 a 7.500 respecto a hipotesis. | Idem. |
| C4 | Creditos Premium | 3.000/mes (hipotesis v1) y 20.000/mes (canonicalization v1) | 20.000/mes | Canon | Resuelve la doble discrepancia. | Idem. |
| C5 | Modulos por plan | 19 (contrato SaaS v1) | 21 (plans/modules matrix v1) | Canon | El canon no redefine la matriz de modulos; respeta la de plans/modules matrix. El contrato SaaS v2 debera alinear el numero. | `CID.SAAS.MODULE.GATES.BACKEND.1`. |
| C6 | Pricing provisional vs canonico | 6 planes legacy en `plans.yml` (Demo/Free/Creator/Producer/Studio/Enterprise a 0/0/9.99/19.99/29.99/99.99) | 5 planes canonicos (Starter/Pro/Studio/Premium/Enterprise a 99/299/799/1.490/3.500+) | Canon | `plans.yml` queda como legacy; se migra en fase de implementacion. | `CID.SAAS.STRIPE.PRODUCTS.PRICES.1` o migracion previa. |
| C7 | Trial/demo/beta/public SaaS | Mezclados en algunas secciones; trial no diferenciado | 4 modos separados (demo_client, private_beta, public_saas, trial) con reglas propias | Canon | La matriz de planes/modulos y el contrato SaaS se actualizan implicitamente al usar este canon como referencia. | `CID.SAAS.DEMO.CLIENT.1`, `CID.SAAS.PRIVATE.BETA.1`. |
| C8 | Paquetes de credito | Hipotesis v1: "Recarga pequena 100, mediana 500, grande 2.000, enterprise 10.000" (precios no cerrados) | 5 paquetes canonicos con `package_key` y precio fijo: `starter_500_pack` 49 €, `pro_1500_pack` 119 €, `pro_3000_pack` 229 €, `studio_10000_pack` 699 €, `premium_custom_pack` y `enterprise_custom_pack` contractuales | Canon | Bolsa pequena del canon (500 cr) difiere de la mediana de la hipotesis (500 cr) en nombre y precio (49 € vs sin precio). | `CID.SAAS.STRIPE.PRODUCTS.PRICES.1`. |
| C9 | Limites por plan | `cid_plans_modules_matrix_v1.md` define valores cuantitativos; este canon los reproduce | Coherente | Canon respeta la matriz | Sin cambio. | n/a. |
| C10 | Usuarios adicionales | Matriz tiene +1/19 € (Pro), +1/15 € (Studio), +1/12 € (Premium) | `TBD_PRICING` | Canon | La matriz es referencia provisional; el canon afirma la disponibilidad y deja el precio para `CID.SAAS.USER_SEATS.PRICING.1`. | `CID.SAAS.USER_SEATS.PRICING.1`. |
| C11 | Almacenamiento adicional | No definido en matriz ni en hipotesis | `TBD_PRICING` | Canon | Canon afirma la disponibilidad del add-on; precio se cierra en fase dedicada. | `CID.SAAS.STORAGE.PRICING.1`. |
| C12 | Coste por operacion (creditos) | `cid_credits_business_model_v1.md` tabla §19 con valores 1-3 cr por operacion ligera, hasta 300 cr por video. Contrato SaaS v1 tabla §9 con 20-100 cr por operacion. | Mapeo orientativo a 4 rangos (`low_cost`, `medium_cost`, `high_cost`, `enterprise_cost`) | Canon | El canon no fija coste por operacion; cierra los rangos. La tabla de coste concreta se decide en fase dedicada. | `CID.SAAS.CREDITS.USAGE.MODEL.1`. |
| C13 | Estados de credito | Contrato SaaS v1 §9: 4 estados (disponible, reservado, consumido, caducado). Plans/modules matrix v1: 4 estados (id.). | 6 estados: `available`, `reserved`, `consumed`, `expired`, `refunded`, `adjusted` | Canon | Se anaden `refunded` y `adjusted` para cubrir devoluciones y correcciones manuales. | `CID.SAAS.CREDIT.LEDGER.BACKEND.1`. |
| C14 | Orden de consumo de creditos | No definido explicitamente en docs previos | Orden canonico: trial/ajuste -> incluidos -> comprados (FIFO por expiracion) -> enterprise | Canon | El sistema tendra un orden de consumo determinista. | `CID.SAAS.CREDIT.LEDGER.BACKEND.1`. |
| C15 | Anti-abuso trial | No definido | Trial: 1 por organizacion, 1 por tarjeta, deteccion de tarjeta quemada, bloqueo de prepago de baja verificacion | Canon | Reduce fraude y abuso de trial. | `CID.SAAS.BILLING.MODELS.1`. |
| C16 | Cambio de moneda | No definido | EUR canonico; otras monedas via tipo de cambio o contrato Enterprise | Canon | Simplifica el pricing publico inicial. | Internacionalizacion futura. |
| C17 | Pricing publico landing | AILinkCinema landing publica el pricing canonico | Pendiente de alineacion | Canon | La landing debe usar este canon. | `CID.SAAS.PRICING.PUBLIC.LANDING.1`. |
| C18 | Internazionalizacion de mensajes de bloqueo | No definida | Multiidioma minimo (es-ES, en-GB, pt-BR) en v1 | Canon | i18n de mensajes en fase de billing UI. | `CID.SAAS.BILLING.ADMIN.UI.1`. |

## 27. Roadmap derivado

Fases tecnicas futuras que aplican este canon. Se ejecutan en orden sugerido; cada fase con su propio spec, implementacion y cierre de validacion.

1. **CID.SAAS.STRIPE.PRODUCTS.PRICES.1**: crear los productos y precios en Stripe con los `stripe_product_key` y `stripe_price_key` definidos en §18. Migrar el catalogo canonico a Stripe en modo test.
2. **CID.SAAS.BILLING.MODELS.1**: modelo de datos para `subscription`, `invoice`, `payment`, `credit_ledger`, `credit_reservation`, `credit_charge`, `credit_rollback`, `credit_purchase`, `credit_package`. Endpoints admin con gating.
3. **CID.SAAS.SUBSCRIPTION.STATE.BACKEND.1**: implementar la maquina de estados de suscripcion (`active`, `past_due`, `suspended`, `cancelled`) con webhooks idempotentes desde Stripe.
4. **CID.SAAS.CREDIT.LEDGER.BACKEND.1**: implementar el ledger de creditos con los 6 estados canonicos, el orden de consumo, la reserva, el cargo y el rollback. Auditoria completa.
5. **CID.SAAS.PLAN.GATES.BACKEND.1**: introducir `require_plan` y los gates derivados (§19) en `src/dependencies/`. Migrar routers existentes gradualmente. Test contract por router.
6. **CID.SAAS.MODULE.GATES.BACKEND.1**: extender `require_module_access` con los 5 estados (`included`, `limited`, `add_on`, `not_included`, `enterprise_only`) y la cuota del modulo. Migrar routers. Test contract por modulo.
7. **CID.SAAS.CREDIT.GATES.BACKEND.1**: introducir `require_credit(credit_estimate)`. Middleware que rechaza con `402` si saldo insuficiente. Eventos audit.
8. **CID.SAAS.BILLING.ADMIN.UI.1**: panel de admin para gestionar plan, modulos add-on, bolsas de creditos, historial de pagos, facturas. UI conectada a `/api/billing/*` con gating. Mensajes canonicos de bloqueo.
9. **CID.SAAS.PRICING.PUBLIC.LANDING.1**: pagina publica de pricing consistente con el canon. Sincronizada con backend, no hardcodeada en frontend. Idioma y formato de moneda canonicos.
10. **CID.SAAS.USER_SEATS.PRICING.1**: cerrar el precio de usuarios adicionales (Pro, Studio, Premium). Migrar el canon con el precio definido.
11. **CID.SAAS.STORAGE.PRICING.1**: cerrar el precio de almacenamiento adicional (Pro, Studio, Premium). Migrar el canon con el precio definido.

Fases de soporte (no bloqueantes, planificables en paralelo):

- **CID.SAAS.DEMO.CLIENT.1**: soporte explicito para `demo_client` con flag `is_demo=true`, limites enforzados sin plan, conversion automatica a `private_beta` o trial Pro.
- **CID.SAAS.PRIVATE.BETA.1**: soporte para `private_beta` con `is_beta=true`, `beta_end_date`, override de quotas, conversion a plan de pago.
- **CID.SAAS.ENTERPRISE.OVERRIDE.1**: soporte para modulos, permisos y quotas custom Enterprise. Evento `enterprise_override_applied`.
- **CID.SAAS.GRACE.PERIOD.1**: implementar la maquina de estados de downgrade con periodo de gracia de 30 dias configurable por plan y modulo.
- **CID.SAAS.CREDITS.USAGE.MODEL.1**: cerrar la tabla de coste por operacion en creditos, con los 4 rangos canonicos.
- **CID.SAAS.PRICING.CANONICALIZATION.IMPLEMENTATION.1**: migrar `src/config/plans.yml` a los 5 planes canonicos. Frontend `PlanRoute` actualizado. Quitar el legacy. Esta fase es prerequisito de cualquier lanzamiento monetizado.

## 28. Criterio GO

Este canon v1 se considera **GO** para guiar las fases tecnicas futuras cuando se cumplen todos los puntos siguientes:

1. Crea unicamente `docs/business/cid_pricing_canonical_v1.md`. No modifica ningun otro archivo.
2. No modifica codigo fuente (`src/`, `src_frontend/`, `tests/`, `scripts/`, `alembic/`).
3. No modifica backend (no se cambia el gating cerrado, no se introducen endpoints, no se modifican routers).
4. No modifica frontend (no se cambian componentes, paginas, contextos, ni se introduce `/api/capabilities`).
5. No modifica `.env`, `backups/`, `*.db`, Docker, compose, ni `src/config/plans.yml`.
6. Resuelve explicitamente las discrepancias de creditos: 500/2.000/7.500/20.000/contractual canonico.
7. Resuelve explicitamente las discrepancias de precios: 99/299/799/1.490/3.500+ € canonico, 990/2.990/7.990/14.900 €/ano canonico.
8. Resuelve explicitamente las discrepancias de bolsas: 5 paquetes canonicos con `package_key` y precio.
9. Fija reglas de trial, demo_client, private_beta y public_saas como 4 modos diferenciados.
10. Fija reglas de upgrade, downgrade, cancelacion e impago.
11. Declara explicitamente que el backend es la fuente de verdad y el frontend solo visibilidad/explicacion.
12. `git diff --check` pasa sin warnings ni errores.
13. `bash scripts/dev/guard_wsl_repo.sh` pasa los 8 checks (PWD WSL, sin Windows path, sin copia anidada, sin `.env` staged, sin `*.db` staged, sin JSON sensible staged, sin secretos en policy dirs).
14. `git status --short --untracked-files=all` muestra unicamente `?? docs/business/cid_pricing_canonical_v1.md`.

Cuando todos estos puntos se cumplen, el canon sirve como base contractual y documental para:

- Disenar `CID.SAAS.STRIPE.PRODUCTS.PRICES.1` y `CID.SAAS.BILLING.MODELS.1`.
- Disenar `/api/capabilities` y la UI de plan/creditos/add-ons/billing.
- Iniciar la migracion de `src/config/plans.yml` a los 5 planes canonicos.
- Disenar el ledger de creditos y la maquina de estados de suscripcion.

El canon no implementa nada. Es un GO de diseno, suficiente para que las fases 1-3 del roadmap arranquen con un modelo de pricing canonico, sin tener que revisarlo en cada sprint.

## Estilo y forma

- Documento tecnico de negocio en Markdown.
- Espanol claro, conciso, sin marketing.
- Tablas operativas siempre que se compare mas de dos elementos.
- Codigos en backticks para `plan_key`, `package_key`, `module_key`, `permission_key`, `stripe_product_key`, `stripe_price_key`, `event_id`.
- Cada seccion tiene titulo, cuerpo y, si aplica, tabla o lista.
- Las referencias a companeros son siempre con ruta relativa al archivo.
- Los numeros economicos son canonicos salvo que se marquen explicitamente como `TBD_PRICING` o `CONTRACTUAL`.
- Sin emojis (regla de estilo del repo).
- Sin `code blocks` de marketing (no se incluyen "testimonios", "ventajas competitivas", ni "casos de exito").
- Las decisiones canonicas (D001-D010) se citan explicitamente cuando se usan.
- Los conflictos resueltos (C01-C18) se citan explicitamente cuando son relevantes.
- No inventar integraciones externas no presentes en los documentos, salvo como futuras.
- No prometer funcionalidades no controladas por modulos/plan/creditos.
