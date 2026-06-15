# AILink Script-to-Production Breakdown - Excel Visual Polish

**Phase:** AILINK.CID.SCRIPT_TO_PRODUCTION_BREAKDOWN.DEMO.EXCEL.VISUAL.POLISH.PHASE5.3
**Version:** 1.0
**Date:** 2026-06-15
**Status:** Excel demo polish / stdlib-only

---

## 1. Propósito

Pulir visualmente el Excel demo de Script-to-Production Breakdown después de una revisión manual con resultado LIMITED PASS.

Objetivos:

- Mejorar claridad de primera apertura para productor.
- Convertir la hoja Resumen en portada clara.
- Reordenar hojas para una presentación comercial segura.
- Hacer visibles límites de demo.
- Mantener `.xlsx` stdlib-only, sin openpyxl.
- No ampliar alcance funcional.

---

## 2. Resultado manual actual

Resultado manual: LIMITED PASS.

La demo funciona técnicamente:

- Genera JSON.
- Genera Markdown.
- Genera Excel `.xlsx`.
- No genera PDF/HTML/CSV.
- Usa Proyecto Demo Bruma.
- No usa guiones reales.
- No usa IA real.

El problema detectado es visual/comercial: el Excel funciona, pero necesita mayor claridad antes de enseñarlo a una persona de confianza o productor.

---

## 3. Mejoras aplicadas

- Hoja `Resumen` convertida en portada clara para productor.
- Textos visibles añadidos:
  - Proyecto Demo Bruma.
  - demo controlada.
  - guion ficticio.
  - no presupuesto definitivo.
  - revisión humana.
  - presupuesto preliminar.
  - guion → producción → finanzas.
- Orden de hojas orientado a presentación:
  1. Resumen.
  2. Viabilidad.
  3. Presupuesto.
  4. Riesgos.
  5. Escenas.
  6. Personajes.
  7. Localizaciones.
  8. Recomendaciones.
  9. Revisión humana.
  10. Metadata.
- Presupuesto marcado como preliminar/revisable.
- Leyenda textual de semáforos añadida en `Viabilidad`.
- Metadata mantenida al final.
- `organization_id`, `tenant_id`, `project_id` y `film_id` se mantienen.
- Fórmulas `SUM` de presupuesto se mantienen.
- Anchos de columna básicos se declaran en OOXML stdlib.
- Freeze panes se mantienen en hojas tabulares.

---

## 4. Límites mantenidos

- No se añaden dependencias.
- No se importa openpyxl.
- No se usa IA real.
- No se usan guiones reales.
- No se genera PDF.
- No se genera HTML.
- No se genera CSV.
- No se toca backend SaaS.
- No se toca DB.
- No se toca Alembic.
- No se toca CreditBalance.
- No se toca Sync Dialogue.
- No se cambia el parser.
- No se cambia la CLI.
- No se cambia JSON ni Markdown.

---

## 5. Criterio esperado tras polish

Resultado esperado: PASS para enseñar a persona de confianza, manteniendo mensaje de demo controlada.

PASS significa:

- El Excel abre correctamente.
- El Resumen explica el contexto y límites.
- El presupuesto no parece definitivo ni fiscal oficial.
- La viabilidad incluye leyenda textual.
- La revisión humana es visible.
- Metadata queda al final sin protagonismo comercial.

---

## 6. Riesgos

- El exportador OOXML stdlib debe seguir simple.
- Colores avanzados no se fuerzan para evitar complejidad.
- La mejora visual no debe convertirse en promesa de producto final.
- El Excel sigue siendo una demo, no un presupuesto definitivo.

---

## 7. No-goals

- No backend SaaS.
- No DB.
- No Alembic.
- No Docker.
- No `.env`.
- No modelos SQLAlchemy.
- No pagos.
- No billing runtime.
- No CreditBalance.
- No Sync Dialogue.
- No guiones reales.
- No IA real.
- No OCR.
- No PDF/HTML/CSV.
- No dependencias nuevas.
