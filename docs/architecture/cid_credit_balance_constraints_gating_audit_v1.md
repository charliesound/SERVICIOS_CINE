# CID CreditBalance Constraints Gating Audit

**Phase:** CID.SAAS.CREDIT.BALANCE.CONSTRAINTS.GATING.AUDIT.1
**Version:** 1.0
**Date:** 2026-06-15
**Status:** test-only / documental

---

## 1. Propósito

Esta fase audita las constraints actuales de `CreditBalance` sin modificar runtime, modelo, Alembic ni base de datos.

Objetivos:

- Auditar las constraints actuales de `CreditBalance`.
- Confirmar qué protege hoy la DB.
- Detectar huecos de protección.
- Definir decisión recomendada para una futura implementación.
- No modificar runtime ni DB en esta fase.

---

## 2. Estado actual de `CreditBalance`

- Modelo: `CreditBalance`.
- Tabla: `credit_balances`.
- El saldo de créditos SaaS es por `organization_id`.
- Una organización/productora puede tener varias películas, pero la bolsa de créditos puede ser común a la organización.
- Constraint única actual: `uq_credit_balances_organization_id`.
- Check constraint actual: `ck_credit_balances_non_negative_subbalances`.
- Índices actuales:
  - `ix_credit_balances_organization_id`.
  - `ix_credit_balances_last_updated_at`.
- Modelo y migración histórica están alineados con la migración histórica `alembic/versions/20260605_000001_add_cid_billing_models.py`.

---

## 3. Constraints actuales protegidas

La constraint `ck_credit_balances_non_negative_subbalances` protege hoy estos seis subbalances:

- `included_monthly_remaining >= 0`.
- `purchased_balance >= 0`.
- `promotional_balance >= 0`.
- `trial_balance >= 0`.
- `enterprise_balance >= 0`.
- `reserved_active >= 0`.

Esta protección evita valores negativos en las bolsas activas principales y en créditos reservados activos.

---

## 4. Campos no protegidos actualmente por check constraint

Los siguientes campos existen en `CreditBalance`, pero no están incluidos todavía en la check constraint `ck_credit_balances_non_negative_subbalances`:

- `consumed_period`.
- `expired_total`.
- `refunded_total`.
- `adjusted_total`.
- `version`.

Esto significa que la DB no bloquea por sí misma valores inválidos en estos contadores si el servicio falla o si una escritura externa evita las validaciones de aplicación.

---

## 5. Decisión recomendada

Decisión recomendada para una fase futura:

- `consumed_period >= 0` debería protegerse en futura fase.
- `expired_total >= 0` debería protegerse en futura fase.
- `refunded_total >= 0` debería protegerse en futura fase.
- `version >= 1` debería protegerse en futura fase.
- `adjusted_total` debe poder ser negativo o positivo.
- `adjusted_total` debe permanecer firmado porque puede representar ajustes netos positivos o negativos.

Esta fase solo audita y documenta. No cambia constraints reales todavía.

---

## 6. Aislamiento organización/proyecto

- `CreditBalance` es por organización/productora.
- `CreditBalance` no debe duplicarse por película en esta fase.
- Una organización/productora puede tener varias películas, pero una bolsa de créditos común.
- El aislamiento de películas/proyectos debe vivir en entidades con `project_id` / `film_id`.
- Los datos de película/proyecto deben permanecer aislados por `organization_id`/`tenant_id` junto con `project_id`/`film_id` cuando aplique.

Razonamiento:

- El crédito SaaS puede ser una bolsa comercial compartida por la productora.
- El consumo real puede seguir trazándose por `project_id` en entradas de ledger u otras entidades operativas.
- Cambiar `CreditBalance` a granularidad por película requeriría una decisión comercial y técnica separada.

---

## 7. Riesgos actuales

- Si el servicio falla, DB no impide counters negativos en `consumed_period`, `expired_total` o `refunded_total`.
- El test existente podría comprobar solo el nombre de la constraint, no su expresión real.
- Una regresión podría quitar columnas de la check manteniendo el mismo nombre `ck_credit_balances_non_negative_subbalances`.
- `version` sin check permite valores no válidos si el servicio falla.
- `adjusted_total` no debe forzarse a no negativo porque representa un ajuste firmado.

---

## 8. Recomendación de implementación futura

Para implementar protección real en una fase posterior:

- Crear una nueva migración, no editar la histórica.
- No editar la histórica `20260605_000001_add_cid_billing_models.py`.
- Añadir una constraint nueva, por ejemplo `ck_credit_balances_non_negative_counters`.
- Incluir en la nueva constraint:
  - `consumed_period >= 0`.
  - `expired_total >= 0`.
  - `refunded_total >= 0`.
  - `version >= 1`.
- Mantener `adjusted_total` firmado.
- Añadir tests de contrato que inspeccionen la expresión real, no solo el nombre.
- Validar la migración contra PostgreSQL antes de aplicarla en producción.

---

## 9. No-goals

- No modificar modelo.
- No modificar Alembic.
- No crear migración.
- No tocar DB real.
- No tocar runtime.
- No cambiar servicios.
- No cambiar comportamiento de créditos.
- No cambiar tenant/project model.
- No cambiar Script-to-Production Breakdown.
- No tocar `src/models/billing.py`.
- No tocar `src/services/credit_ledger_service.py`.
- No tocar pagos ni billing runtime.
