# CID CreditBalance Constraints Implementation

**Phase:** CID.SAAS.CREDIT.BALANCE.CONSTRAINTS.IMPLEMENTATION.1
**Version:** 1.0
**Date:** 2026-06-15
**Status:** ORM + Alembic implementation

---

## 1. Propósito

Esta fase implementa la protección real de contadores adicionales de `CreditBalance` en el modelo ORM y en una migración Alembic nueva.

Objetivos:

- Añadir una nueva constraint para counters de `CreditBalance`.
- Mantener intacta la constraint anterior de subbalances.
- Mantener `adjusted_total` firmado.
- Crear una nueva migración y no editar la histórica.
- Mantener `CreditBalance` por `organization_id`.

---

## 2. Constraint anterior mantenida

La constraint existente `ck_credit_balances_non_negative_subbalances` sigue igual y protege:

- `included_monthly_remaining >= 0`.
- `purchased_balance >= 0`.
- `promotional_balance >= 0`.
- `trial_balance >= 0`.
- `enterprise_balance >= 0`.
- `reserved_active >= 0`.

No se modifica la migración histórica `20260605_000001_add_cid_billing_models.py`.

---

## 3. Nueva constraint de counters

Se añade la nueva constraint `ck_credit_balances_non_negative_counters` sobre la tabla `credit_balances`.

Expresión implementada:

```sql
consumed_period >= 0 AND expired_total >= 0 AND refunded_total >= 0 AND version >= 1
```

Protege:

- `consumed_period >= 0`.
- `expired_total >= 0`.
- `refunded_total >= 0`.
- `version >= 1`.

---

## 4. `adjusted_total` permanece firmado

`adjusted_total` queda fuera de `ck_credit_balances_non_negative_counters`.

Motivo:

- `adjusted_total` puede representar ajustes netos positivos o negativos.
- Forzarlo a `>= 0` rompería la semántica de ajuste firmado.
- La constraint nueva solo protege counters que no deben ser negativos.

---

## 5. Migración nueva y no histórica

Se crea una migración nueva:

`alembic/versions/20260615_000001_add_credit_balance_counter_constraints.py`

La migración usa como `down_revision` el head Alembic detectado antes de editar:

`20260610_000003_ai_job_execution_attempts`

Reglas:

- No editar la histórica.
- No modificar `alembic/versions/20260605_000001_add_cid_billing_models.py`.
- No ejecutar `alembic upgrade` en esta fase.
- No hacer cambios manuales en PostgreSQL.

---

## 6. Aislamiento organización/proyecto

`CreditBalance` sigue siendo por `organization_id`.

Decisión:

- Una organización/productora puede tener varias películas.
- La bolsa de créditos SaaS puede ser común a la organización.
- `CreditBalance` no se convierte en saldo por película.
- El aislamiento de películas/proyectos vive en entidades con `project_id` / `film_id`.
- Las entradas operativas que consumen créditos pueden seguir trazando `project_id` cuando aplique.

---

## 7. Riesgo de migración con datos previos inválidos

Si existen filas previas con counters inválidos, PostgreSQL rechazará la creación de la constraint.

Preflight recomendado antes de aplicar en entorno real:

```sql
SELECT id, organization_id, consumed_period, expired_total, refunded_total, version
FROM credit_balances
WHERE consumed_period < 0
   OR expired_total < 0
   OR refunded_total < 0
   OR version < 1;
```

Si el query devuelve filas, corregir datos antes de aplicar la migración.

---

## 8. Validación esperada

La validación debe comprobar:

- El modelo contiene `ck_credit_balances_non_negative_counters`.
- La migración nueva contiene `ck_credit_balances_non_negative_counters`.
- La migración nueva no toca `ck_credit_balances_non_negative_subbalances`.
- La migración histórica permanece intacta.
- `adjusted_total` no aparece en la nueva constraint.
- No se ejecuta `alembic upgrade` contra DB real.

---

## 9. No-goals

- No editar la histórica.
- No tocar `20260605_000001_add_cid_billing_models.py`.
- No ejecutar `alembic upgrade`.
- No tocar DB real.
- No cambiar `credit_ledger_service.py`.
- No cambiar pagos.
- No cambiar billing runtime fuera del modelo.
- No cambiar frontend.
- No cambiar Docker.
- No cambiar Script-to-Production Breakdown.
