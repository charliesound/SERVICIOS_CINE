# AILink Script-to-Production Breakdown - Budget Total

**Phase:** AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.DEMO.EXCEL.BUDGET.TOTAL.PHASE5.4
**Version:** 1.0
**Date:** 2026-06-15
**Status:** Excel demo budget total / stdlib-only

---

## 1. Propósito

Añadir un bloque visible de totales en la hoja `Presupuesto` del Excel demo de Script-to-Production Breakdown.

La mejora responde a un PASS externo con mejora menor: el Excel ya contenía fórmulas `SUM`, pero el total no quedaba suficientemente visible para una primera reunión de producción.

---

## 2. Cambios aplicados

- Se mantiene la fila técnica `TOTAL` con fórmulas `SUM`.
- Se añade un bloque visible en `Presupuesto` con:
  - `Total bajo`.
  - `Total medio`.
  - `Total alto`.
  - `Presupuesto preliminar revisable`.
  - `No presupuesto definitivo`.
  - `Requiere revisión humana`.
- Se añade color básico de alerta en OOXML stdlib:
  - Verde para OK / bajo / viable.
  - Amarillo para atención / medio / revisar.
  - Rojo para alerta / alto / requiere decisión.
- El color se limita a:
  - `Viabilidad`.
  - `Riesgos`.
  - advertencias básicas en `Resumen`.

---

## 3. Reglas visuales mantenidas

El color nunca es la única información. El Excel mantiene textos visibles como:

- `verde`.
- `amarillo`.
- `rojo`.
- `riesgo bajo`.
- `riesgo medio`.
- `riesgo alto`.
- `viable`.
- `revisar`.
- `alerta`.

---

## 4. Límites mantenidos

- No se añaden dependencias.
- No se importa openpyxl.
- No se usa IA real.
- No se usan guiones reales.
- No se genera PDF.
- No se genera HTML.
- No se genera CSV.
- No se convierte el Excel en hoja fiscal oficial.
- No se toca backend SaaS.
- No se toca DB.
- No se toca Alembic.
- No se toca Docker.
- No se toca `.env`.
- No se tocan modelos SQLAlchemy.
- No se tocan pagos.
- No se toca billing runtime.
- No se toca CreditBalance.
- No se toca Sync Dialogue.
- No se cambia el parser.
- No se cambia la CLI.
- No se cambia JSON ni Markdown.
- No se usa OCR.

---

## 5. Criterio esperado

Resultado esperado: PASS para primera reunión de producción controlada.

PASS significa:

- `Presupuesto` muestra totales bajo, medio y alto de forma visible.
- Las fórmulas `SUM` se mantienen.
- Las advertencias de presupuesto preliminar y revisión humana son visibles.
- El color ayuda a la lectura, pero no sustituye el texto.
- El `.xlsx` sigue siendo ZIP/XLSX válido y stdlib-only.
- No se generan PDF, HTML ni CSV.

---

## 6. No-goals

- No presupuesto definitivo.
- No estimación fiscal oficial.
- No integración SaaS runtime.
- No persistencia en DB.
- No automatización con IA real.
- No soporte para guiones reales.
