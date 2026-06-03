# CID Command Center — Auditoría de coherencia documental

**Documento:** `docs/product/cid_command_center_readiness_audit_v1.md`
**Versión:** 1.1
**Fecha:** 2026-06-03
**Tags:** `CID`, `product-architecture`, `audit`, `readiness`, `go-no-go`
**Basado en:** los 9 documentos CID de producto, negocio y financiación

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Alcance](#2-alcance)
3. [Metodología](#3-metodología)
4. [Dimensiones auditadas](#4-dimensiones-auditadas)
5. [Contradicciones críticas](#5-contradicciones-críticas)
6. [Contradicciones menores](#6-contradicciones-menores)
7. [Inconsistencias de nomenclatura](#7-inconsistencias-de-nomenclatura)
8. [Lagunas documentales](#8-lagunas-documentales)
9. [Aciertos de coherencia](#9-aciertos-de-coherencia)
10. [Análisis de impacto por área](#10-análisis-de-impacto-por-área)
11. [Veredicto GO/NO-GO](#11-veredicto-gono-go)
12. [Resoluciones requeridas](#12-resoluciones-requeridas)
13. [Próxima fase](#13-próxima-fase)

---

## 1. Resumen ejecutivo

Se auditan 9 documentos CID para determinar si el modelo funcional es suficientemente coherente para autorizar el inicio de la implementación del Command Center frontend. Se identifican **4 contradicciones críticas**, **5 contradicciones menores**, **3 inconsistencias de nomenclatura** y **4 lagunas documentales**.

**VEREDICTO INICIAL: NO-GO condicional** (v1.0). Las 4 contradicciones críticas fueron resueltas en **CID.PRODUCT.ARCHITECTURE.CROSS.DOCUMENT.RESOLUTION.1**. Veredicto actual: **GO con retoques** (resolver menores M3, M4, N1, N3, L1–L4 como trabajo posterior).

---

## 2. Alcance

| # | Documento | Versión | Ruta |
|---|---|---|---|
| D1 | Branches | 1.0 | `docs/product/cid_project_command_center_branches_v1.md` |
| D2 | Data Model | 2.1 | `docs/product/cid_project_command_center_data_model_v1.md` |
| D3 | Access Model | 1.0 | `docs/product/cid_project_access_model_v1.md` |
| D4 | Credits | 1.0 | `docs/business/cid_credits_business_model_v1.md` |
| D5 | Pricing | 1.0 | `docs/business/cid_pricing_competitive_baseline_v1.md` |
| D6 | Funding Taxonomy | 1.0 | `docs/finance_intelligence/cid_funding_taxonomy_v1.md` |
| D7 | Funding Data Model | 1.0 | `docs/finance_intelligence/cid_funding_intelligence_data_model_v1.md` |
| D8 | Spain Funding Research | 1.0 | `docs/finance_intelligence/spain_funding_sources_research_v1.md` |
| D9 | Europe Funding Research | 1.0 | `docs/finance_intelligence/europe_funding_sources_research_v1.md` |

---

## 3. Metodología

- **Comparación pareada** de cada dimensión entre todos los documentos que la mencionan.
- **Gravedad**: crítica (bloquea implementación), menor (requiere armonización), cosmética (no bloquea).
- **Criterio GO**: todas las contradicciones críticas resueltas + plan de resolución para las menores.
- Solo se audita coherencia entre documentos existentes. No se evalúa corrección de las decisiones de producto.

---

## 4. Dimensiones auditadas

| Dimensión | Documentos involucrados |
|---|---|
| Planes de licencia (nombres, capacidad, estructura) | D1, D3, D4, D5 |
| Estados de proyecto | D2, D3 |
| Nombres de roles y ramas | D1, D2, D3 |
| Niveles de acceso por rol | D1, D2, D3 |
| Modelo de cómputo de licencia (Modelo C) | D3, D5 |
| Créditos IA por plan | D4, D5 |
| Entidades financieras (FundingSource, FundingOpportunity) | D2, D6, D7 |
| Estructura organizacional y roles organizacionales | D2, D3 |
| Métricas y health score | D1, D2 |
| Flujos de invitación, cambio de rol, revocación | D3 (contra sí mismo) |

---

## 5. Contradicciones críticas

### C1 — Plan Premium no existe en 3 de 4 documentos [RESUELTO]

| Documento | Planes definidos (inicial) | Planes definidos (tras resolución) |
|---|---|---|
| Access Model (D3) | Starter, Pro, Studio, Enterprise | Starter, Pro, Studio, **Premium**, Enterprise |
| Credits (D4) | Starter, Pro, Studio, Enterprise | Starter, Pro, Studio, **Premium**, Enterprise |
| Pricing (D5) | Starter, Pro, Studio, **Premium**, Enterprise | Sin cambios (ya tenía Premium) |
| Branches (D1) | Menciona "Producer", "Creator" | Corregido a "Pro", "Starter" |

**Resolución aplicada:** Se mantiene Premium como plan real (5 planes). Se actualizaron D3 §10 (capacidad + guía UX + techo por plan), D3 §11 (guía UX), D4 §20 (3.000 créditos/mes, acumulación 1.000). D5 no requirió cambios. D1 §17 corregido (M1).

---

### C2 — Estados de proyecto diferentes entre Data Model y Access Model [RESUELTO]

| Estado unificado | ID EN | Etiqueta ES | Descripción |
|---|---|---|---|
| Preproducción | `PREPROD` | Preproducción | Preparación inicial. Script, presupuesto. |
| Activo | `ACTIVE` | Activo | Producción activa. Acepta invitaciones. |
| Congelado | `FROZEN` | Congelado | Pausado temporalmente. Solo lectura. |
| Cierre | `WRAPPING` | Cierre | Últimos entregables. Invitaciones restringidas. |
| Archivado | `ARCHIVED` | Archivado | Finalizado. Solo visible para Propietario y Admins. |
| Cerrado | `CLOSED` | Cerrado | Accesos revocados excepto Propietario. |

**Transiciones:** `PREPROD → ACTIVE → FROZEN → ACTIVE`, `ACTIVE → WRAPPING → ARCHIVED → CLOSED`

**Resolución aplicada:** Se actualizó D2 §30 (antes `ON_HOLD`→`FROZEN`, `COMPLETED`→`ARCHIVED`+`CLOSED`, tabla con ID+etiqueta). Se actualizó D3 §6 (añadidos `PREPROD`, `WRAPPING` + transiciones).

---

### C3 — Anexo C R2 del Access Model referencia Model A (cómputo por rama) tras migración a Model C [RESUELTO]

En D3 Anexo C (Riesgos de implementación), R2 decía:
> *"Límites de licencia ambiguos... documentar que un usuario en N ramas cuenta N veces"*

Mientras §10 de D3 ya se migró a Model C: "*un usuario en N ramas cuenta 1 vez*".

**Resolución aplicada:** R2 actualizado a: "*documentar que un usuario en N ramas cuenta 1 vez (Modelo C: cómputo por proyecto, multi-rama ilimitado)*".

---

### C4 — Visibilidad entre ramas inconsistente entre Branches y Access Model [RESUELTO]

D1 (§5 matriz) dividía Rama 3 en 4 subcolumnas: Postproducción / Entrega / Comercialización.
D3 (§7 matriz) divide en 2: Rama 3 / Comercialización.

**Resolución aplicada:** Se unificó D1 con D3: matriz de Branches cambió a 4 columnas (Rama 1, Rama 2, Rama 3, Comercialización). Rama 3 unifica Postproducción y Entrega. Se añadió nota aclaratoria en ambos documentos. Se actualizó D3 línea 130: "Rama 3 (Postproducción)" → "Rama 3 (Postproducción y Entrega)". Los valores de celda en D1 se alinearon con D3.

---

## 6. Contradicciones menores

### M1 — Branches menciona planes "Producer" y "Creator" inexistentes

D1 (§17): "*Los módulos de Rama 1 requieren plan Producer o superior. Los módulos de Rama 2 están disponibles desde plan Creator.*"

Ningún otro documento usa estos nombres. Los planes reales son Starter/Pro/Studio/Enterprise/Premium.

**Resolución:** Actualizar D1 §17 con los nombres de plan reales.

---

### M2 — Capacidad de guía UX vs. capacidad real en Access Model

D3 §10 tabla de "Capacidad sugerida por rama (guía UX)" usa filas Starter/Pro/Studio/Enterprise con 3/5/10/configurable usuarios por rama.
D3 §10 tabla de "Capacidad por plan" usa techos globales 9/15/30/configurable.

Las guías UX suman más que el techo global (ej. Starter: 3+3+3=9, exacto; Pro: 5+5+5=15, exacto; Studio: 10+10+10=30, exacto). En la práctica, las guías no suman más que el techo pero podrían confundir.

**Resolución:** Añadir nota en la guía UX que aclare que los valores por rama son orientativos y el límite real es el techo global del proyecto.

---

### M3 — Data Model no incluye roles organizacionales (Admin/Member)

D3 (§5) define `Admin de organización` y `Member de organización` como entidades de acceso.
D2 (§3) define Organization pero no tiene referencia a `orgRole` o `orgPermissions`.

**Resolución:** Añadir campo `orgRole` (Admin/Member) a la entidad Organization en D2, o añadir una entidad OrganizationMembership separada.

---

### M4 — Funding source type enum no normalizado entre documentos

D2 (§12) FundingSource.type usa: `ayuda_publica / incentivo_fiscal / inversor / preventa / credito / crowdfunding / subvencion`
D6 (§4) source_type usa: `public_grant / tax_incentive / european_fund / iberoamerican_fund / coproduction_framework / broadcaster / platform / presale / private_equity / gap_financing / regional_support`

Los conjuntos solapan pero no son idénticos. D2 usa español y menos tipos; D6 usa inglés y más tipos.

**Resolución:** Unificar el enum de tipos de fuente entre D2 y D6. Recomendación: adoptar la taxonomía de D6 (más completa).

---

### M5 — Acceso del Editor de Sonido ligeramente distinto

D1 (§5): Editor de Sonido → Postproducción "Parcial (sonido)", Entrega "Sin acceso", Comercialización "Sin acceso"
D3 (§7): Editor de Sonido → Rama 3 "Parcial (sonido)", Comercialización "Sin acceso"
D3 (§11): Editor de Sonido → "Parcial (R3 sonido)"

Coherente en esencia pero la estructura de columnas es diferente (D1 separa Postproducción/Entrega/Comercialización vs D3 unifica Rama 3).

**Resolución:** Armonizar junto con C4.

---

## 7. Inconsistencias de nomenclatura

### N1 — Estados de proyecto: inglés vs. español

D2 usa: `PREPROD, ACTIVE, ON_HOLD, WRAPPING, COMPLETED`
D3 usa: `ACTIVO, CONGELADO, ARCHIVADO, CERRADO`

Mismo concepto (estados de proyecto), idiomas diferentes. Los estados de otras entidades en D2 también mezclan inglés y español:
- Script: `EN_DESARROLLO, ANALIZADO, BLOQUEADO, EN_REVISION`
- Storyboard: `EN_PROGRESO, COMPLETADO, APROBADO`
- Asset: `SUBIDO, PROCESANDO, DISPONIBLE, ERROR`

**Resolución:** Estandarizar a un solo idioma. El modelo de datos debe usar un idioma consistente.

---

### N2 — "Producto Propietario" en D3 vs "Productor" en D1/D2

D3 usa sistemáticamente "Productor Propietario".
D1 y D2 usan "Productor" (con la nota de que es el responsable último).
D1 §3 define "Productor" como rol; D2 §6 lista "Productor Propietario" como rol predefinido.

En D2, el campo `producerId` referencia a User para el Productor Propietario.

No es una contradicción funcional porque queda claro que "Productor" en D1 = "Productor Propietario" en D2/D3, pero la falta de consistencia puede confundir.

**Resolución:** Usar "Productor Propietario" en todos los documentos donde se refiera al rol específico con capacidades de dueño del proyecto.

---

### N3 — "Comercialización" como sub-rama de Rama 3

D1 trata Comercialización como una subcolumna dentro de Rama 3.
D3 trata Comercialización como una rama separada (aunque bajo el paraguas Rama 3).
D2 también incluye Comercialización dentro de Rama 3.

La ambigüedad está en si Comercialización es una rama independiente o una subdivisión de Rama 3. El modelo de datos la trata como parte de Rama 3; el access model a veces la trata como entidad separada en la matriz.

**Resolución:** Decidir si Comercialización es rama independiente (Rama 4) o subdivisión de Rama 3. Alinear todos los documentos.

---

## 8. Lagunas documentales

### L1 — No hay entidad "Plan" definida formalmente

Ningún documento define una entidad `Plan` con atributos: id, name, price, maxUsers, maxCredits, features. D3 menciona `planId` en Organization pero no define el objeto Plan.

**Impacto:** Para frontend, no hay un contrato de datos que describa qué es un plan.

**Resolución:** Añadir entidad Plan a D2 o crear un documento específico de modelo de suscripción.

---

### L2 — No hay definición de organización ↔ usuario con roles org

D3 §5 define roles organizacionales (Admin, Member) pero D2 no tiene entidad ni campos para modelar la membresía organizacional con su rol.

**Impacto:** Un frontend no puede representar la página de administración de organización.

**Resolución:** Añadir entidad OrganizationMembership o campo orgRole en D2.

---

### L3 — Acceso de Productor Ejecutivo a invitaciones de Rama 3/Comercialización

D3 §4 dice que Productor Ejecutivo `puedeInvitarComercial` pero D3 §9 dice que Productor Ejecutivo puede invitar a "Roles de Rama 1 y Comercialización". Sin embargo, el nombre `puedeInvitarComercial` sugiere que solo puede invitar a roles de Comercialización (subconjunto de Rama 3), no a roles de Postproducción (Montador, Editor de Sonido, Post Supervisor).

**Impacto:** Ambiguo si el Productor Ejecutivo puede invitar a un Post Supervisor o solo a Distribuidor/Agente de Ventas.

**Resolución:** Aclarar en D3 §4 y D3 §9 si las invitaciones del Productor Ejecutivo cubren toda Rama 3 o solo el subconjunto Comercialización.

---

### L4 — CreditPool.organizationId sin uso definido

D2 §29 CreditPool tiene `organizationId` como campo y relación 0:1 con Organization, descrito como "agregado de facturación". No hay documentación sobre cómo se usa este campo (¿para consolidar consumo entre proyectos de la misma organización? ¿Para facturación centralizada?).

**Impacto:** Un implementador no sabe si debe poblar este campo ni qué lógica de negocio aplica.

**Resolución:** Documentar el propósito de `organizationId` en CreditPool en D2 §29.

---

## 9. Aciertos de coherencia

| Aspecto | Documentos | Estado |
|---|---|---|
| 12 roles definidos consistentemente | D1, D2, D3 | ✓ |
| 3 ramas funcionales (Rama 1/2/3) | D1, D2, D3 | ✓ |
| Matriz de acceso por rama (Completo/Parcial/Lectura/Sin acceso) | D1, D2, D3 | ✓ |
| Pirámide de acceso (Productor global → ramas aisladas) | D1, D2, D3 | ✓ |
| Modelo C adoptado y documentado | D3, D5 | ✓ |
| Créditos como plano ortogonal a licencias | D4, D2 (CreditPool/CreditConsumption) | ✓ |
| Créditos por plan (100/300/1000/3000+) | D4, D5 | ✓ |
| Data model referencing finance_intelligence docs | D2, D6, D7 | ✓ (from PENDIENTE to NOTA) |
| Sequence entity promoted to independent | D2 | ✓ (self-consistent) |
| Organization→CreditPool as billing aggregate only | D2 | ✓ (self-consistent) |
| Flujos de invitación, revocación, cambio de rol | D3 Anexo A | ✓ (self-consistent after Model C fix) |
| User statuses (INVITADO → ACTIVO → SUSPENDIDO/REVOCADO) | D2, D3 | ✓ |

---

## 10. Análisis de impacto por área

### Frontend (Command Center UI)
- ~~**BLOQUEADO por C1**~~ → Resuelto (5 planes definidos)
- ~~**BLOQUEADO por C2**~~ → Resuelto (6 estados unificados)
- ~~**Afectado por M1**~~ → Resuelto (nombres de plan corregidos)
- **Afectado por L1** (sin entidad Plan no hay contrato para mostrar pricing) — retoque pendiente

### Backend (modelo de datos)
- ~~**BLOQUEADO por C2**~~ → Resuelto (project.status unificado)
- ~~**Afectado por C3**~~ → Resuelto (Anexo C R2 corregido)
- **Afectado por M3** (sin org roles en data model) — retoque pendiente
- **Afectado por M4** (FundingSource.type no unificado) — retoque pendiente
- **Afectado por N1** (mixed language en estados) — retoque pendiente
- **Afectado por L4** (CreditPool.organizationId sin uso) — retoque pendiente

### Access control / RBAC
- ~~**Afectado por C4**~~ → Resuelto (Rama 3 columnas unificadas)
- ~~**Afectado por M2**~~ → Resuelto (nota añadida en guía UX)
- **Afectado por L3** (alcance de invitaciones de Productor Ejecutivo) — retoque pendiente

### Pricing & commercial
- ~~**BLOQUEADO por C1**~~ → Resuelto (Premium confirmado, D3/D4 actualizados)
- ~~**Afectado por M1**~~ → Resuelto (plan names corregidos)

### Funding Intelligence
- **Afectado por M4** (tipos de fuente no unificados)
- Sin contradicciones críticas. La integración con D6/D7 está madura.

---

## 11. Veredicto GO/NO-GO

### GO con retoques (desde v1.1)

Las 4 contradicciones críticas (C1–C4) fueron resueltas en **CID.PRODUCT.ARCHITECTURE.CROSS.DOCUMENT.RESOLUTION.1**. 

Se autoriza el inicio de implementación del Command Center frontend. Quedan como trabajo posterior los siguientes retoques no bloqueantes: M3, M4, N1, N3, L1–L4.

---

## 12. Resoluciones requeridas

### Resueltas en v1.1

| ID | Documento | Cambio aplicado |
|---|---|---|
| C1 | D3, D4 | Plan Premium añadido (capacidad, guía UX, créditos). D5 sin cambios. |
| C2 | D2, D3 | Estados unificados: 6 estados (PREPROD/ACTIVE/FROZEN/WRAPPING/ARCHIVED/CLOSED) con ID+etiqueta ES. |
| C3 | D3 | Anexo C R2: "cuenta 1 vez (Modelo C)". |
| C4 | D1, D3 | Rama 3 unificada (Postproducción + Entrega). Columnas alineadas. |
| M1 | D1 | §17: "Producer" → "Pro", "Creator" → "Starter". |
| M2 | D3 | Nota añadida en guía UX de §10. |

### Retoques pendientes (no bloqueantes)

| ID | Documento | Cambio |
|---|---|---|
| M3 | D2 | Añadir orgRole o entidad OrganizationMembership |
| M3 | D2 | Añadir orgRole o entidad OrganizationMembership |
| M4 | D2, D6 | Unificar FundingSource.type enum |
| M5 | D1, D3 | Armonizar columnas (misma resolución que C4) |
| N1 | D2 | Estandarizar idioma de estados |
| N2 | D1, D2 | "Productor" → "Productor Propietario" donde aplique |
| N3 | D1, D2, D3 | Decidir estatus de Comercialización (Rama 4 vs sub-Rama 3) |
| L1 | D2 (nuevo) | Añadir entidad Plan o documento de suscripción |
| L2 | D2 | Añadir OrganizationMembership |
| L3 | D3 | Aclarar alcance de invitaciones del Productor Ejecutivo |
| L4 | D2 | Documentar propósito de CreditPool.organizationId |

---

## 13. Próxima fase

### CID.PRODUCT.ARCHITECTURE.FRONTEND.BOOTSTRAP.1

Las 4 contradicciones críticas (C1–C4) fueron resueltas. Veredicto: GO con retoques.

Siguiente fase: inicio de implementación frontend. Quedan como trabajo posterior los retoques M3, M4, N1, N3, L1–L4.

---

## Historial de revisiones

| Fecha | Versión | Cambios |
|---|---|---|
| 2026-06-03 | 1.0 | Auditoría inicial de coherencia entre 9 documentos CID. Veredicto: NO-GO condicional. 4 contradicciones críticas identificadas. |
| 2026-06-03 | 1.1 | C1–C4 resueltos + M1 + M2. Veredicto actualizado a GO con retoques. Próxima fase: FRONTEND.BOOTSTRAP.1. |
