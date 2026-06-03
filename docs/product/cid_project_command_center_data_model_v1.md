# CID Project Command Center — Modelo de datos funcional

**Documento:** `docs/product/cid_project_command_center_data_model_v1.md`
**Versión:** 2.1
**Fecha:** 2026-06-03
**Tags:** `CID`, `product-architecture`, `data-model`, `entities`, `relationships`
**Basado en:** `cid_project_command_center_branches_v1.md`, `cid_project_access_model_v1.md`, `cid_credits_business_model_v1.md`, `cid_funding_taxonomy_v1.md`, `cid_funding_intelligence_data_model_v1.md`

---

## Índice

1. [Resumen ejecutivo](#1-resumen-ejecutivo)
2. [Principios del modelo de datos](#2-principios-del-modelo-de-datos)
3. [Organization](#3-organization)
4. [Project](#4-project)
5. [User](#5-user)
6. [Role](#6-role)
7. [Branch](#7-branch)
8. [Task](#8-task)
9. [Milestone](#9-milestone)
10. [Risk](#10-risk)
11. [Budget](#11-budget)
12. [FundingSource](#12-fundingsource)
13. [FundingOpportunity](#13-fundingopportunity)
14. [Script](#14-script)
15. [ScriptAnalysis](#15-scriptanalysis)
16. [CharacterBible](#16-characterbible)
17. [VisualBible](#17-visualbible)
18. [Storyboard](#18-storyboard)
19. [Sequence](#19-sequence)
20. [Shot](#20-shot)
21. [ShootingPlan](#21-shootingplan)
22. [ShootingDay](#22-shootingday)
23. [Asset](#23-asset)
24. [Deliverable](#24-deliverable)
25. [DistributionPackage](#25-distributionpackage)
26. [FestivalStrategy](#26-festivalstrategy)
27. [SalesStrategy](#27-salesstrategy)
28. [CreditConsumption](#28-creditconsumption)
29. [CreditPool](#29-creditpool)
30. [Estados](#30-estados)
31. [Dependencias entre entidades](#31-dependencias-entre-entidades)
32. [Métricas](#32-metricas)
33. [Visibilidad conceptual por rol](#33-visibilidad-conceptual-por-rol)
34. [Qué NO incluye este modelo](#34-que-no-incluye-este-modelo)
35. [Próxima fase](#35-proxima-fase)

---

## 1. Resumen ejecutivo

Este documento define el **modelo de datos funcional** del Project Command Center de CID. Describe las entidades que componen el dominio del producto, sus relaciones, estados y visibilidad. Es un modelo conceptual que sirve como base para las fases de implementación técnica.

El modelo cubre 26 entidades principales agrupadas en 7 dominios:

| Dominio | Entidades |
|---|---|
| **Organizacional** | Organization, Project, User, Role, Branch |
| **Planificación** | Task, Milestone, Risk |
| **Financiero** | Budget, FundingSource, FundingOpportunity |
| **Creativo** | Script, ScriptAnalysis, CharacterBible, VisualBible, Storyboard, Sequence, Shot |
| **Producción** | ShootingPlan, ShootingDay |
| **Media** | Asset, Deliverable, DistributionPackage, FestivalStrategy, SalesStrategy |
| **Créditos IA** | CreditConsumption, CreditPool |

Este documento no especifica implementación técnica (SQL, tablas, backend, API, frontend). Es puramente arquitectura de datos conceptual.

---

## 2. Principios del modelo de datos

### P1 — Separación por rama funcional
Cada entidad pertenece a una rama principal. Los datos de una rama no son visibles por defecto en otra rama, salvo dependencia funcional documentada.

### P2 — Identidad de proyecto
Toda entidad operativa pertenece a un proyecto. No existen datos huérfanos fuera del contexto de un proyecto.

### P3 — Visibilidad por rol
Los campos de cada entidad tienen un nivel de visibilidad asociado al rol del usuario. Un campo puede ser visible para todos, para la rama responsable, para dirección, o para un rol específico.

### P4 — Trazabilidad de cambios
Toda entidad incluye metadatos de creación y modificación. Las entidades críticas (Budget, FundingSource, Script) tienen control de versiones.

### P5 — Separación de créditos
Las entidades de créditos IA son ortogonales a las entidades de producción. CreditConsumption y CreditPool no dependen del plan de licencia ni de los permisos de acceso.

### P6 — Estado explícito
Toda entidad con ciclo de vida tiene un estado explícito. No se infiere el estado a partir de datos derivados.

### P7 — Documentación de fuentes ausentes
Las entidades FundingOpportunity y campos de FundingSource que dependen de `cid_funding_taxonomy_v1.md` y `cid_funding_intelligence_data_model_v1.md` están disponibles en `docs/finance_intelligence/`. Los valores concretos deben contrastarse con esos documentos en diseño técnico.

---

## 3. Organization

**Propósito:** Agrupación legal o comercial que posee uno o varios proyectos. Es el contenedor de suscripción y membresía.

**Rama responsable:** Transversal (todas).

**Propietario:** Admin de organización.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Todos |
| `name` | Texto | Todos |
| `legalName` | Texto (razón social) | Dirección, Rama 1 |
| `taxId` | Texto (NIF/CIF/VAT) | Dirección, Rama 1 |
| `country` | Texto | Dirección, Rama 1 |
| `orgType` | Texto (productora / distribuidora / plataforma / agencia / estudio) | Todos |
| `website` | Texto (URL) | Todos |
| `contactEmail` | Texto | Rama 1 |
| `planId` | Referencia a plan de licencia | Dirección |
| `creditPoolId` | Referencia a CreditPool | Dirección |
| `createdAt` | Fecha | Dirección |
| `updatedAt` | Fecha | Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Organization → Project | 1:N | Una organización tiene múltiples proyectos |
| Organization → User | N:M | Una organización tiene múltiples miembros |
| Organization → FundingSource | 0:N | Una organización puede tener fuentes de financiación |
| Organization → CreditPool | 0:1 | Agregado de facturación de la organización (no es un pool operativo; el pool operativo pertenece al proyecto) |

---

## 4. Project

**Propósito:** Raíz del Command Center. Representa una producción cinematográfica individual.

**Rama responsable:** Transversal (todas).

**Propietario:** Productor Propietario.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Todos |
| `title` | Texto | Todos |
| `logline` | Texto | Todos |
| `synopsis` | Texto largo | Rama 1, Rama 2, Dirección |
| `status` | Estado del proyecto | Todos |
| `currentPhase` | Texto (preproduccion / rodaje / postproduccion / entrega) | Todos |
| `organizationId` | Referencia a Organization | Todos |
| `producerId` | Referencia a User | Todos |
| `executiveProducerId` | Referencia a User (opcional) | Dirección |
| `startDate` | Fecha | Todos |
| `estimatedEndDate` | Fecha | Todos |
| `actualEndDate` | Fecha (opcional) | Todos |
| `budgetId` | Referencia a Budget (activo) | Rama 1, Dirección |
| `healthScore` | Métrica calculada | Dirección |
| `tags` | Lista de texto | Todos |
| `createdAt` | Fecha | Dirección |
| `updatedAt` | Fecha | Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Project → Organization | N:1 | Pertenece a una organización |
| Project → User (Producer) | 1:1 | Exactamente un Productor Propietario |
| Project → User (ExecutiveProducer) | 0:1 | Opcional Productor Ejecutivo |
| Project → Budget | 1:N | Múltiples versiones de presupuesto (1 activa) |
| Project → Script | 1:N | Múltiples versiones de guion (1 activa) |
| Project → Milestone | 1:N | Múltiples hitos |
| Project → Risk | 1:N | Múltiples riesgos |
| Project → Task | 1:N | Múltiples tareas |
| Project → Asset | 1:N | Múltiples assets |
| Project → CreditConsumption | 1:N | Historial de consumo de créditos |
| Project → CreditPool | 1:1 | Pool de créditos del proyecto |

---

## 5. User

**Propósito:** Persona física que accede a CID. Es el sujeto de todos los permisos.

**Rama responsable:** Transversal (todas).

**Propietario:** El propio usuario (datos personales); Productor Propietario (acceso al proyecto).

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Todos |
| `displayName` | Texto | Todos |
| `email` | Texto (protegido) | Dirección, Rama 1 |
| `avatarUrl` | Texto (URL) | Todos |
| `accessStatus` | Estado de acceso en el proyecto | Dirección |
| `roleId` | Referencia a Role (primario) | Todos |
| `secondaryRoleIds` | Lista de referencias a Role | Dirección |
| `assignedBranchIds` | Lista de referencias a Branch | Dirección |
| `grantedAt` | Fecha | Dirección |
| `grantedBy` | Referencia a User | Dirección |
| `expiresAt` | Fecha (opcional, accesos temporales) | Dirección |
| `lastAccessAt` | Fecha | Dirección |
| `creditLimit` | Número (tope de créditos del usuario en el proyecto, opcional) | Productor |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| User → Project | N:M | Un usuario pertenece a múltiples proyectos |
| User → Role | 1:1 (primario) + 0:N (secundarios) | Un rol principal + roles secundarios opcionales |
| User → Task | 1:N (asignado) | Un usuario tiene tareas asignadas |
| User → CreditConsumption | 1:N | Un usuario consume créditos |

### Estados de acceso

`INVITADO` → `ACTIVO` → `SUSPENDIDO` → `ACTIVO`
`ACTIVO` → `REVOCADO` (terminal)
`ACTIVO` → `AUDITADO` (solo lectura)

---

## 6. Role

**Propósito:** Perfil funcional que determina el acceso del usuario a módulos, ramas y operaciones.

**Rama responsable:** Transversal (todas).

**Propietario:** Productor Propietario (asignación); sistema (definición).

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Todos |
| `name` | Texto (Productor Propietario, Director, etc.) | Todos |
| `level` | Entero (1, 2, 3) | Todos |
| `primaryBranchId` | Referencia a Branch | Todos |
| `permissions` | Mapa de permisos por módulo | Dirección |
| `isSystemRole` | Booleano | Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Role → Branch | N:1 | Cada rol pertenece a una rama principal |
| Role → User | 1:N | Un rol puede tener múltiples usuarios |

### Roles predefinidos

| Rol | Nivel | Rama principal |
|---|---|---|
| Productor Propietario | 1 | Todas (global) |
| Productor Ejecutivo | 1 | Rama 1 |
| Jefe de Producción | 2 | Rama 1 |
| Director | 2 | Rama 2 |
| Guionista | 3 | Rama 2 |
| Script Supervisor | 3 | Rama 2 |
| Ayudante de Dirección | 3 | Rama 2 |
| Montador / Editor | 3 | Rama 3 |
| Editor de Sonido | 3 | Rama 3 |
| Post Supervisor | 2 | Rama 3 |
| Distribuidor | 3 | Rama 3 (Comercialización) |
| Agente de Ventas | 3 | Rama 3 (Comercialización) |

---

## 7. Branch

**Propósito:** Una de las tres ramas funcionales del ciclo de producción cinematográfica.

**Rama responsable:** Transversal.

**Propietario:** Productor Propietario (activación).

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Todos |
| `name` | Texto (Producción y Financiación / Creativo y Rodaje / Postproducción, Entrega y Comercialización) | Todos |
| `shortName` | Texto (rama1 / rama2 / rama3) | Todos |
| `color` | Texto | Todos |
| `order` | Entero (1, 2, 3) | Todos |
| `isActiveForProject` | Booleano | Todos |
| `activationMilestoneId` | Referencia a Milestone | Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Branch → Role | 1:N | Una rama contiene múltiples roles |
| Branch → Task | 1:N | Una rama contiene múltiples tareas |
| Branch → Asset | 1:N | Los assets se etiquetan por rama de origen |

### Ramas predefinidas

| Rama | ID | Ciclo |
|---|---|---|
| Producción y Financiación | `rama1` | Desarrollo financiero, presupuesto, financiación, contratación |
| Creativo y Rodaje | `rama2` | Guion, storyboard, arte, rodaje |
| Postproducción, Entrega y Comercialización | `rama3` | Montaje, sonido, VFX, entregas, distribución, ventas |

---

## 8. Task

**Propósito:** Unidad de trabajo atómica dentro de un módulo.

**Rama responsable:** Según módulo al que pertenece.

**Propietario:** Usuario asignado.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Según rama |
| `title` | Texto | Según rama |
| `description` | Texto largo | Según rama |
| `status` | Estado de tarea | Según rama |
| `branchId` | Referencia a Branch | Según rama |
| `moduleId` | Texto | Según rama |
| `assignedToId` | Referencia a User | Según rama |
| `createdById` | Referencia a User | Según rama |
| `milestoneId` | Referencia a Milestone (opcional) | Según rama |
| `dueDate` | Fecha | Según rama |
| `completedAt` | Fecha (opcional) | Según rama |
| `priority` | Texto (baja / media / alta / crítica) | Según rama |
| `dependencyIds` | Lista de referencias a Task | Dirección |
| `estimatedHours` | Número | Rama 1, Dirección |
| `actualHours` | Número (opcional) | Rama 1, Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Task → Branch | N:1 | Pertenece a una rama |
| Task → Milestone | N:0:1 | Opcionalmente asociada a un hito |
| Task → Task | N:N | Puede depender de otras tareas |
| Task → User (assigned) | N:1 | Asignada a un usuario |

---

## 9. Milestone

**Propósito:** Hito significativo en el calendario del proyecto. Marca transiciones entre fases y activa ramas.

**Rama responsable:** Transversal (origen en rama específica).

**Propietario:** Productor Propietario.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Todos |
| `name` | Texto | Todos |
| `description` | Texto largo | Todos |
| `projectId` | Referencia a Project | Todos |
| `branchId` | Referencia a Branch | Todos |
| `targetDate` | Fecha | Todos |
| `completedDate` | Fecha (opcional) | Todos |
| `isCompleted` | Booleano | Todos |
| `triggersBranchActivation` | Referencia a Branch (opcional) | Dirección |
| `triggeredTaskIds` | Lista de referencias a Task | Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Milestone → Project | N:1 | Pertenece a un proyecto |
| Milestone → Branch | N:1 | Se origina en una rama |
| Milestone → Task | 1:N | Desbloquea tareas al completarse |

### Hitos predefinidos

| Hito | Rama origen | Activa |
|---|---|---|
| Guion bloqueado | Rama 2 | Desbloquea storyboard y desglose |
| Rodaje completado | Rama 2 | Activa Rama 3 para Director |
| Primer corte completado | Rama 3 | Activa versión para inversores |
| Entrega completada | Rama 3 | Activa CRM y distribución |
| Hito de financiación | Rama 1 | Alimenta el plan de rodaje con presupuesto |

---

## 10. Risk

**Propósito:** Riesgo identificado que puede afectar al proyecto en una o varias ramas.

**Rama responsable:** Transversal (origen en rama específica, impacto multi-rama).

**Propietario:** Productor Propietario o Productor Ejecutivo.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Dirección |
| `title` | Texto | Dirección |
| `description` | Texto largo | Dirección |
| `status` | Estado de riesgo | Dirección |
| `severity` | Texto (baja / media / alta / crítica) | Dirección |
| `probability` | Texto (baja / media / alta) | Dirección |
| `originBranchId` | Referencia a Branch | Dirección |
| `impactedBranchIds` | Lista de referencias a Branch | Dirección |
| `ownerId` | Referencia a User | Dirección |
| `mitigationPlan` | Texto largo (opcional) | Dirección |
| `identifiedAt` | Fecha | Dirección |
| `resolvedAt` | Fecha (opcional) | Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Risk → Project | N:1 | Pertenece a un proyecto |
| Risk → Branch (origin) | N:1 | Se origina en una rama |
| Risk → Branch (impacted) | N:M | Puede impactar múltiples ramas |

### Reglas
- Solo visible para Dirección (Productor Propietario y Productor Ejecutivo).
- Riesgos con severidad alta o crítica generan alertas en el dashboard del Productor.

---

## 11. Budget

**Propósito:** Presupuesto del proyecto con partidas por departamento y niveles de confianza.

**Rama responsable:** Rama 1 — Producción y Financiación.

**Propietario:** Jefe de Producción.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 1, Dirección |
| `projectId` | Referencia a Project | Rama 1, Dirección |
| `version` | Texto (v1.0, v2.0) | Rama 1, Dirección |
| `totalEstimated` | Número | Rama 1, Dirección |
| `totalExecuted` | Número | Rama 1, Dirección |
| `totalCommitted` | Número | Rama 1, Dirección |
| `currency` | Texto (EUR, USD) | Rama 1, Dirección |
| `confidenceLevel` | Texto (baja / media / alta) | Rama 1, Dirección |
| `lineItems` | Lista de BudgetLineItem | Rama 1, Dirección |
| `isActive` | Booleano | Rama 1, Dirección |
| `lastUpdated` | Fecha | Rama 1, Dirección |

### BudgetLineItem (sub-entidad)

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 1, Dirección |
| `department` | Texto | Rama 1, Dirección |
| `category` | Texto | Rama 1, Dirección |
| `estimatedAmount` | Número | Rama 1, Dirección |
| `executedAmount` | Número | Rama 1, Dirección |
| `committedAmount` | Número | Rama 1, Dirección |
| `confidenceLevel` | Texto (baja / media / alta) | Rama 1, Dirección |
| `notes` | Texto largo | Rama 1 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Budget → Project | N:1 | Pertenece a un proyecto |
| Budget → BudgetLineItem | 1:N | Contiene múltiples partidas |

### Reglas
- Un proyecto puede tener múltiples versiones de presupuesto, pero solo una activa a la vez.
- `totalExecuted` = suma de `executedAmount` de todas las partidas.
- `confidenceLevel` global = mínimo de los niveles de confianza de las partidas.
- No visible fuera de Rama 1 y Dirección.

---

## 12. FundingSource

**Propósito:** Fuente de financiación del proyecto: ayudas públicas, incentivos fiscales, inversores, preventas, créditos, crowdfunding, subvenciones.

**Rama responsable:** Rama 1 — Producción y Financiación.

**Propietario:** Productor Ejecutivo.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 1, Dirección |
| `type` | Texto (ayuda_publica / incentivo_fiscal / inversor / preventa / credito / crowdfunding / subvencion) | Rama 1, Dirección |
| `name` | Texto | Rama 1, Dirección |
| `amount` | Número | Rama 1, Dirección |
| `currency` | Texto (EUR, USD) | Rama 1, Dirección |
| `status` | Estado de fuente | Rama 1, Dirección |
| `applicationDate` | Fecha (opcional) | Rama 1, Dirección |
| `approvalDate` | Fecha (opcional) | Rama 1, Dirección |
| `expectedCollectionDate` | Fecha | Rama 1, Dirección |
| `territory` | Texto (España, Canarias, Navarra, UE, etc.) | Rama 1, Dirección |
| `projectId` | Referencia a Project | Rama 1, Dirección |
| `organizationId` | Referencia a Organization (opcional) | Rama 1, Dirección |
| `eligibilityScore` | Métrica calculada | Rama 1, Dirección |
| `riskFlag` | Texto (verde / ámbar / rojo) | Rama 1, Dirección |

> **NOTA:** Los campos `eligibilityScore` y `riskFlag` se definen según `cid_funding_taxonomy_v1.md` (disponible en `docs/finance_intelligence/`). Revisar en fase de diseño técnico.

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| FundingSource → Project | N:1 | Pertenece a un proyecto |
| FundingSource → Organization | N:0:1 | Opcionalmente asociada a la organización |

---

## 13. FundingOpportunity

**Propósito:** Oportunidad de financiación identificada (convocatoria abierta, incentivo fiscal disponible, línea de crédito cultural) a la que el proyecto puede optar.

**Rama responsable:** Rama 1 — Producción y Financiación.

**Propietario:** Productor Ejecutivo.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 1, Dirección |
| `name` | Texto | Rama 1, Dirección |
| `type` | Texto (convocatoria / incentivo_fiscal / credito_cultural / premio / fondo_autonomico / fondo_europeo) | Rama 1, Dirección |
| `territory` | Texto | Rama 1, Dirección |
| `openingDate` | Fecha | Rama 1, Dirección |
| `closingDate` | Fecha | Rama 1, Dirección |
| `maxAmount` | Número | Rama 1, Dirección |
| `currency` | Texto | Rama 1, Dirección |
| `requirements` | Texto largo | Rama 1 |
| `compatibilityNotes` | Texto largo | Rama 1 |
| `matchScore` | Métrica calculada | Rama 1, Dirección |
| `status` | Texto (identificada / en_evaluacion / solicitada / cerrada) | Rama 1, Dirección |
| `projectId` | Referencia a Project (opcional) | Rama 1, Dirección |

> **NOTA:** Esta entidad depende de `cid_funding_taxonomy_v1.md` y `cid_funding_intelligence_data_model_v1.md` (disponibles en `docs/finance_intelligence/`). Los campos `type`, `requirements`, `compatibilityNotes` y `matchScore` deben revisarse contra esos documentos en la fase de diseño técnico.

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| FundingOpportunity → Project | N:0:1 | Opcionalmente vinculada a un proyecto |
| FundingOpportunity → FundingSource | 1:1 | Si se solicita, se convierte en FundingSource |

---

## 14. Script

**Propósito:** Guion de la producción. Es la fuente principal para storyboard, desglose y análisis.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Guionista.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2, Dirección |
| `projectId` | Referencia a Project | Rama 2, Dirección |
| `title` | Texto | Rama 2, Dirección |
| `currentVersion` | Texto (v3.2) | Rama 2, Dirección |
| `status` | Estado de guion | Rama 2, Dirección |
| `pageCount` | Número | Rama 2, Dirección |
| `sceneCount` | Número | Rama 2, Dirección |
| `writerId` | Referencia a User | Rama 2, Dirección |
| `blockedAt` | Fecha (opcional) | Rama 2, Dirección |
| `estimatedDuration` | Número (minutos) | Rama 2, Dirección |
| `genreTags` | Lista de texto | Rama 2 |
| `uploadedAt` | Fecha | Rama 2, Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Script → Project | N:1 | Pertenece a un proyecto |
| Script → ScriptAnalysis | 1:N | Un guion puede tener múltiples análisis |
| Script → Storyboard | 1:1 | El storyboard se basa en la versión activa |

### Estados

`EN_DESARROLLO` → `ANALIZADO` → `BLOQUEADO` → `EN_REVISION` → `BLOQUEADO`

El estado `BLOQUEADO` es un hito que habilita la generación de storyboard y desglose.

---

## 15. ScriptAnalysis

**Propósito:** Resultado del análisis IA del guion: estructura narrativa, personajes detectados, localizaciones, arcos, riesgos de producción.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Sistema (generado por IA).

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2, Dirección |
| `scriptId` | Referencia a Script | Rama 2, Dirección |
| `analysisType` | Texto (narrativo / personajes / localizaciones / riesgos / coherencia / comparacion) | Rama 2, Dirección |
| `status` | Texto (en_progreso / completado / fallido) | Rama 2, Dirección |
| `summary` | Texto largo | Rama 2, Dirección |
| `narrativeStructure` | Texto largo (actos, puntos de giro) | Rama 2 |
| `detectedCharacters` | Lista de CharacterRef | Rama 2 |
| `detectedLocations` | Lista de texto | Rama 2 |
| `riskFlags` | Lista de texto | Dirección |
| `inconsistencies` | Lista de texto (opcional) | Rama 2, Dirección |
| `creditCost` | Número (créditos consumidos) | Dirección |
| `generatedAt` | Fecha | Rama 2, Dirección |
| `generatedBy` | Referencia a User | Rama 2, Dirección |

### CharacterRef (sub-entidad)

| Campo | Tipo |
|---|---|
| `name` | Texto |
| `role` | Texto (protagonista / secundario / antagonista / menor) |
| `scenesAppears` | Número |
| `hasArc` | Booleano |
| `description` | Texto largo |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| ScriptAnalysis → Script | N:1 | Pertenece a un guion |
| ScriptAnalysis → CharacterBible | 1:N | Los personajes detectados pueden promoverse a CharacterBible |

---

## 16. CharacterBible

**Propósito:** Fichas de personaje con imagen generada por IA, descripción extraída del guion y consistencia visual entre generaciones.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Director.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2 |
| `projectId` | Referencia a Project | Rama 2 |
| `characterName` | Texto | Rama 2 |
| `description` | Texto largo | Rama 2 |
| `role` | Texto (protagonista / secundario / antagonista / menor / extra) | Rama 2 |
| `imageUrl` | Texto (URL) | Rama 2 |
| `variants` | Lista de CharacterVariant | Rama 2 |
| `lockedModelRef` | Texto (referencia al modelo ligero) | Sistema |
| `sourceScriptAnalysisId` | Referencia a ScriptAnalysis (opcional) | Rama 2 |
| `createdAt` | Fecha | Rama 2 |
| `createdBy` | Referencia a User | Rama 2 |

### CharacterVariant (sub-entidad)

| Campo | Tipo |
|---|---|
| `id` | UUID |
| `type` | Texto (expresion / angulo / vestuario / epoca) |
| `prompt` | Texto |
| `imageUrl` | Texto (URL) |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| CharacterBible → Project | N:1 | Pertenece a un proyecto |
| CharacterBible → ScriptAnalysis | N:0:1 | Opcionalmente originado de un análisis |
| CharacterBible → Shot | 1:N | El personaje aparece en múltiples planos |

---

## 17. VisualBible

**Propósito:** Definición del estilo visual coherente del proyecto: paleta de color, iluminación, textura, atmósfera.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Director.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2 |
| `projectId` | Referencia a Project | Rama 2 |
| `name` | Texto | Rama 2 |
| `colorPalette` | Lista de códigos hex | Rama 2 |
| `lightingStyle` | Texto | Rama 2 |
| `textureRefs` | Lista de texto (URLs) | Rama 2 |
| `moodKeywords` | Lista de texto | Rama 2 |
| `referenceImageUrls` | Lista de texto (URLs) | Rama 2 |
| `generatedPreviewUrl` | Texto (URL, opcional) | Rama 2 |
| `isActive` | Booleano | Rama 2 |
| `createdAt` | Fecha | Rama 2 |
| `createdBy` | Referencia a User | Rama 2 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| VisualBible → Project | 1:1 | Un proyecto tiene una Visual Bible activa |
| VisualBible → Storyboard | 1:N | Aplica estilo a planos del storyboard |

---

## 18. Storyboard

**Propósito:** Representación visual del guion mediante secuencias de planos, personajes y composición.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Director.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2, Dirección |
| `projectId` | Referencia a Project | Rama 2, Dirección |
| `scriptId` | Referencia a Script (versión activa) | Rama 2, Dirección |
| `scriptVersion` | Texto | Rama 2, Dirección |
| `totalSequences` | Número | Rama 2, Dirección |
| `completedSequences` | Número | Rama 2, Dirección |
| `totalShots` | Número | Rama 2, Dirección |
| `completedShots` | Número | Rama 2, Dirección |
| `directorId` | Referencia a User | Rama 2, Dirección |
| `status` | Estado de storyboard | Rama 2, Dirección |
| `visualBibleId` | Referencia a VisualBible (opcional) | Rama 2 |

> **Nota sobre Sequence:** En la versión 1.0 de este documento, Sequence era una sub-entidad embebida en Storyboard. En esta versión se promueve a entidad independiente (ver §19) para permitir su propio ciclo de vida, relación 1:N con Shot, y seguimiento individual de estado. Storyboard conserva `totalSequences` y `completedSequences` como campos calculados/agregados, no como lista.

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Storyboard → Script | 1:1 | Basado en la versión activa del guion |
| Storyboard → Sequence | 1:N | Contiene múltiples secuencias (modeladas como entidad independiente, ver §19) |
| Storyboard → VisualBible | N:0:1 | Opcionalmente guiado por una Visual Bible |

---

## 19. Sequence

**Propósito:** Secuencia narrativa dentro del storyboard. Agrupa planos de una misma escena o unidad dramática.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Director.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2 |
| `storyboardId` | Referencia a Storyboard | Rama 2 |
| `number` | Entero | Rama 2 |
| `title` | Texto | Rama 2 |
| `sceneCount` | Número | Rama 2 |
| `shotCount` | Número | Rama 2 |
| `completedShots` | Número | Rama 2 |
| `status` | Texto (pendiente / en_progreso / completado) | Rama 2 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Sequence → Storyboard | N:1 | Pertenece a un storyboard |
| Sequence → Shot | 1:N | Contiene múltiples planos |

---

## 20. Shot

**Propósito:** Plano individual dentro de una secuencia del storyboard. Representa una toma con composición, personajes y prompt de generación.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Director.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2 |
| `sequenceId` | Referencia a Sequence | Rama 2 |
| `number` | Entero | Rama 2 |
| `description` | Texto | Rama 2 |
| `composition` | Texto (plano_americano / primer_plano / plano_general / etc.) | Rama 2 |
| `charactersInShot` | Lista de referencias a CharacterBible | Rama 2 |
| `prompt` | Texto (para generación IA) | Rama 2 |
| `imageUrls` | Lista de texto (URLs) | Rama 2 |
| `status` | Texto (pendiente / generado / aprobado / rechazado) | Rama 2 |
| `generationAttempts` | Número | Rama 2 |
| `creditCost` | Número (créditos consumidos en generación) | Dirección |
| `approvedAt` | Fecha (opcional) | Rama 2 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Shot → Sequence | N:1 | Pertenece a una secuencia |
| Shot → CharacterBible | N:M | Puede contener múltiples personajes |
| Shot → Asset | 1:N | Las imágenes generadas son assets |

---

## 21. ShootingPlan

**Propósito:** Plan de rodaje con desglose por jornadas, localizaciones y recursos.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Ayudante de Dirección.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2, Dirección |
| `projectId` | Referencia a Project | Rama 2, Dirección |
| `totalDays` | Número | Rama 2, Dirección |
| `completedDays` | Número | Rama 2, Dirección |
| `status` | Estado de plan de rodaje | Rama 2, Dirección |
| `startDate` | Fecha | Rama 2, Dirección |
| `endDate` | Fecha | Rama 2, Dirección |
| `breakdownComplete` | Booleano | Rama 2 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| ShootingPlan → Project | 1:1 | Un proyecto tiene un plan de rodaje activo |
| ShootingPlan → ShootingDay | 1:N | Contiene múltiples jornadas |
| ShootingPlan → Storyboard | 1:1 | Derivado del desglose del storyboard |

---

## 22. ShootingDay

**Propósito:** Jornada individual de rodaje. Contiene la orden de llamada, localización, escenas y recursos del día.

**Rama responsable:** Rama 2 — Creativo y Rodaje.

**Propietario:** Ayudante de Dirección.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 2 |
| `shootingPlanId` | Referencia a ShootingPlan | Rama 2 |
| `dayNumber` | Entero | Rama 2 |
| `date` | Fecha | Rama 2 |
| `location` | Texto | Rama 2 |
| `sceneIds` | Lista de referencias escena | Rama 2 |
| `callTime` | Hora | Rama 2 |
| `estimatedHours` | Número | Rama 2 |
| `actualHours` | Número (opcional) | Rama 2, Dirección |
| `crewCount` | Número | Rama 2 |
| `status` | Texto (planificado / en_rodaje / completado / cancelado) | Rama 2 |
| `notes` | Texto largo (parte de rodaje) | Rama 2 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| ShootingDay → ShootingPlan | N:1 | Pertenece a un plan de rodaje |
| ShootingDay → Task | 1:N | Las tareas del día se registran como tareas |

---

## 23. Asset

**Propósito:** Recurso digital del proyecto: imágenes, videos, audio, documentos, archivos de montaje.

**Rama responsable:** Según tipo de asset (Rama 2: imágenes/creative; Rama 3: video/audio/entregables).

**Propietario:** Usuario que lo subió o generó.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Según rama |
| `type` | Texto (imagen / video / audio / documento / fcpxml / davinci / otros) | Según rama |
| `name` | Texto | Según rama |
| `branchId` | Referencia a Branch | Según rama |
| `projectId` | Referencia a Project | Según rama |
| `uploadedById` | Referencia a User | Según rama |
| `fileSize` | Número (bytes) | Según rama |
| `mimeType` | Texto | Según rama |
| `thumbnailUrl` | Texto (URL) | Según rama |
| `status` | Estado de asset | Según rama |
| `tags` | Lista de texto | Según rama |
| `version` | Texto (opcional) | Según rama |
| `reviewStatus` | Texto (pendiente / aprobado / rechazado / cambios_solicitados) | Según rama |
| `creditCost` | Número (créditos si fue generado por IA) | Dirección |
| `parentAssetId` | Referencia a Asset (opcional, versionado) | Según rama |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Asset → Project | N:1 | Pertenece a un proyecto |
| Asset → Branch | N:1 | Pertenece a una rama |
| Asset → Asset (parent) | N:0:1 | Versionado recursivo |
| Asset → Deliverable | 1:N | Un asset puede ser entregable |
| Asset → Shot | N:1 | Una imagen de shot es un asset |

---

## 24. Deliverable

**Propósito:** Entregable final del proyecto: master DCP, ProRes, trailer, key art, press kit, subtítulos, closed captions.

**Rama responsable:** Rama 3 — Postproducción, Entrega y Comercialización.

**Propietario:** Post Supervisor.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 3, Dirección |
| `projectId` | Referencia a Project | Rama 3, Dirección |
| `type` | Texto (master_dcp / master_prores / trailer / teaser / clip / key_art / press_kit / subtitle_file / closed_captions / dubbing_track) | Rama 3, Dirección |
| `name` | Texto | Rama 3, Dirección |
| `status` | Estado de entregable | Rama 3, Dirección |
| `dueDate` | Fecha | Rama 3, Dirección |
| `deliveredAt` | Fecha (opcional) | Rama 3, Dirección |
| `recipient` | Texto | Rama 3, Dirección |
| `assetId` | Referencia a Asset | Rama 3, Dirección |
| `format` | Texto (DCP / ProRes 422 / H.264 / H.265 / WAV / PDF) | Rama 3 |
| `resolution` | Texto (4K / 2K / HD / SD) | Rama 3 |
| `qcStatus` | Texto (pendiente / aprobado / rechazado) | Rama 3, Dirección |
| `distributionPackageId` | Referencia a DistributionPackage (opcional) | Rama 3, Dirección |
| `festivalStrategyId` | Referencia a FestivalStrategy (opcional) | Rama 3, Dirección |
| `notes` | Texto largo | Rama 3 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| Deliverable → Project | N:1 | Pertenece a un proyecto |
| Deliverable → Asset | N:1 | Un entregable tiene exactamente un asset |
| Deliverable → DistributionPackage | N:0:1 | Opcionalmente agrupado en un paquete |
| Deliverable → FestivalStrategy | N:0:1 | Opcionalmente vinculado a un festival |

---

## 25. DistributionPackage

**Propósito:** Paquete de materiales preparado para distribución comercial: distribuidor, agente de ventas, plataforma, cine, prensa.

**Rama responsable:** Rama 3 — Postproducción, Entrega y Comercialización.

**Propietario:** Distribuidor.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 3, Dirección |
| `projectId` | Referencia a Project | Rama 3, Dirección |
| `type` | Texto (distribuidor / agente_ventas / plataforma / cine / prensa / festival) | Rama 3, Dirección |
| `name` | Texto | Rama 3, Dirección |
| `status` | Texto (en_preparacion / completado / enviado) | Rama 3, Dirección |
| `deliverableIds` | Lista de referencias a Deliverable | Rama 3, Dirección |
| `createdById` | Referencia a User | Rama 3 |
| `sentAt` | Fecha (opcional) | Rama 3, Dirección |
| `recipientName` | Texto | Rama 3, Dirección |
| `recipientContact` | Texto (email) | Rama 3 |
| `notes` | Texto largo | Rama 3 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| DistributionPackage → Project | N:1 | Pertenece a un proyecto |
| DistributionPackage → Deliverable | 1:N | Contiene múltiples entregables |

---

## 26. FestivalStrategy

**Propósito:** Estrategia de festivales: selección de festivales, fechas clave, requisitos de formato, histórico de submissions.

**Rama responsable:** Rama 3 — Postproducción, Entrega y Comercialización.

**Propietario:** Distribuidor.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 3, Dirección |
| `projectId` | Referencia a Project | Rama 3, Dirección |
| `festivalName` | Texto | Rama 3, Dirección |
| `festivalType` | Texto (clase_a / clase_b / especializado / nacional / internacional) | Rama 3, Dirección |
| `submissionDeadline` | Fecha | Rama 3, Dirección |
| `festivalDate` | Fecha | Rama 3, Dirección |
| `status` | Texto (identificado / en_preparacion / enviado / aceptado / rechazado / seleccionado) | Rama 3, Dirección |
| `requiredDeliverableIds` | Lista de referencias a Deliverable | Rama 3, Dirección |
| `submissionFee` | Número (opcional) | Rama 3 |
| `result` | Texto (pendiente / seleccionado / no_seleccionado / pendiente_respuesta) | Rama 3, Dirección |
| `notes` | Texto largo | Rama 3 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| FestivalStrategy → Project | N:1 | Pertenece a un proyecto |
| FestivalStrategy → Deliverable | 1:N | Requiere entregables específicos |

---

## 27. SalesStrategy

**Propósito:** Estrategia de ventas por territorio: agentes, plataformas, condiciones, estado de negociación.

**Rama responsable:** Rama 3 — Postproducción, Entrega y Comercialización (Comercialización).

**Propietario:** Agente de Ventas.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Rama 3 (Comercialización), Dirección |
| `projectId` | Referencia a Project | Rama 3, Dirección |
| `territory` | Texto | Rama 3, Dirección |
| `platformType` | Texto (cine / tv / streaming / físico / venta_internacional) | Rama 3, Dirección |
| `agentName` | Texto | Rama 3 |
| `status` | Texto (identificado / contacto_iniciado / negociacion / cerrado / rechazado) | Rama 3, Dirección |
| `estimatedValue` | Número (opcional) | Dirección |
| `closedValue` | Número (opcional) | Dirección |
| `currency` | Texto | Dirección |
| `contractDate` | Fecha (opcional) | Dirección |
| `deliverableIds` | Lista de referencias a Deliverable | Rama 3, Dirección |
| `notes` | Texto largo | Rama 3 |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| SalesStrategy → Project | N:1 | Pertenece a un proyecto |
| SalesStrategy → Deliverable | 1:N | Los entregables asociados a la venta |

---

## 28. CreditConsumption

**Propósito:** Registro individual de consumo de créditos IA. Cada operación de IA genera un registro.

**Rama responsable:** Transversal (la operación se origina en la rama del módulo que la ejecuta).

**Propietario:** Sistema (generado automáticamente).

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Dirección |
| `projectId` | Referencia a Project | Dirección |
| `userId` | Referencia a User | Dirección |
| `operationType` | Texto (storyboard / concept_art / character_bible / visual_bible / image_gen / video_gen / dubbing / voice_cloning / transcription / restoration / analysis / ocr / agent / training) | Dirección |
| `creditsConsumed` | Número | Dirección |
| `creditsFromPlan` | Número (créditos del plan consumidos) | Dirección |
| `creditsFromExtra` | Número (créditos extra consumidos, 0 si no) | Dirección |
| `moduleId` | Texto (módulo CID donde se ejecutó) | Dirección |
| `entityType` | Texto (tipo de entidad sobre la que se operó: shot / character / script / etc.) | Dirección |
| `entityId` | Referencia UUID (opcional) | Dirección |
| `metadata` | Mapa (detalles de la operación: resolución, duración, modelo) | Dirección |
| `status` | Texto (completado / fallido / reembolsado) | Dirección |
| `consumedAt` | Fecha | Dirección |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| CreditConsumption → Project | N:1 | Pertenece a un proyecto |
| CreditConsumption → User | N:1 | Consumido por un usuario |
| CreditConsumption → CreditPool | N:1 | Descontado de un pool |

### Reglas
- Un registro por operación de IA ejecutada.
- Si la operación falla por error del sistema, el registro se marca como `fallido` y los créditos se reembolsan.
- No se almacenan datos sensibles de la operación (prompts, contenido generado) en este registro.

---

## 29. CreditPool

**Propósito:** Pool de créditos operativo del proyecto. Contiene los créditos del plan, créditos comprados extra y el consumo acumulado. El pool es 1:1 con el proyecto; la organización tiene solo un agregado de facturación (no un pool operativo).

**Rama responsable:** Transversal.

**Propietario:** Productor Propietario.

### Campos mínimos

| Campo | Tipo | Visibilidad |
|---|---|---|
| `id` | UUID | Dirección |
| `projectId` | Referencia a Project | Dirección |
| `organizationId` | Referencia a Organization | Dirección |
| `planCreditsMonthly` | Número (créditos incluidos en el plan) | Dirección |
| `planCreditsRemaining` | Número | Dirección |
| `extraCreditsRemaining` | Número | Dirección |
| `extraCreditsExpiring` | Fecha (opcional, del lote más antiguo) | Dirección |
| `totalConsumedThisMonth` | Número | Dirección |
| `planCreditsResetDay` | Entero (día del mes de reinicio) | Dirección |
| `monthlyHistory` | Lista de MonthlySummary | Dirección |

### MonthlySummary (sub-entidad)

| Campo | Tipo |
|---|---|
| `month` | Texto (YYYY-MM) |
| `planCreditsAllocated` | Número |
| `planCreditsConsumed` | Número |
| `extraCreditsPurchased` | Número |
| `extraCreditsConsumed` | Número |

### Relaciones

| Relación | Cardinalidad | Descripción |
|---|---|---|
| CreditPool → Project | 1:1 | Un proyecto tiene un pool |
| CreditPool → Organization | 0:1 | Agregado de facturación (el pool operativo pertenece 1:1 al proyecto) |
| CreditPool → CreditConsumption | 1:N | Historial de consumo asociado |

---

## 30. Estados

### Estados de Project

`PREPROD` → `ACTIVE` → `FROZEN` → `ACTIVE`
`ACTIVE` → `WRAPPING` → `ARCHIVED` → `CLOSED`

| Estado (ID EN) | Etiqueta ES | Descripción |
|---|---|---|
| `PREPROD` | Preproducción | Preparación inicial. Script en desarrollo, presupuesto en elaboración. |
| `ACTIVE` | Activo | Producción activa. Rodaje o postproducción en curso. Acepta invitaciones. |
| `FROZEN` | Congelado | Pausado temporalmente. Acceso de solo lectura. No acepta invitaciones. |
| `WRAPPING` | Cierre | Cierre de producción. Últimos entregables. Invitaciones restringidas. |
| `ARCHIVED` | Archivado | Proyecto finalizado. Solo visible para Productor Propietario y Admins. Sin modificaciones. |
| `CLOSED` | Cerrado | Proyecto terminado. Todos los accesos revocados excepto Productor Propietario. |

### Estados de Task

`PENDING` ↔ `BLOCKED`
`PENDING` → `IN_PROG` → `REVIEW` → `DONE`
`REVIEW` → `IN_PROG` (rechazada)
`DONE` → `REOPENED` → `IN_PROG`

### Estados de Risk

`IDENTIFIED` → `ACTIVE` → `MITIGATED` → `RESOLVED` (terminal)
`IDENTIFIED` → `DISMISSED` (terminal)
`MITIGATED` → `ACTIVE` (si la mitigación falla)

### Estados de FundingSource

`IDENTIFICADA` → `SOLICITADA` → `APROBADA` → `CONCEDIDA` → `COBRADA` (terminal)
`SOLICITADA` → `RECHAZADA` (terminal)

### Estados de Script

`EN_DESARROLLO` → `ANALIZADO` → `BLOQUEADO` ↔ `EN_REVISION`

### Estados de Storyboard

`EN_PROGRESO` → `COMPLETADO` → `APROBADO`

### Estados de Asset

`SUBIDO` → `PROCESANDO` → `DISPONIBLE` → `ERROR` (terminal)

### Estados de Deliverable

`PENDIENTE` → `EN_PRODUCCION` → `COMPLETADO` → `ENTREGADO`
`ENTREGADO` → `RECHAZADO` → `EN_PRODUCCION`
`QCStatus`: `PENDIENTE` → `APROBADO` → `RECHAZADO`

---

## 31. Dependencias entre entidades

| Origen | Destino | Tipo | Descripción |
|---|---|---|---|
| Organization | Project | Contenedor | Organización contiene proyectos |
| Project | Budget | Asignación | Proyecto tiene presupuesto |
| Project | Script | Asignación | Proyecto tiene guion |
| Project | CreditPool | Asignación | Proyecto tiene pool de créditos |
| Script | ScriptAnalysis | Generación | El guion se analiza |
| Script | Storyboard | Generación | Storyboard se genera del guion |
| Storyboard | Sequence | Composición | Storyboard contiene secuencias |
| Sequence | Shot | Composición | Secuencia contiene planos |
| Shot | Asset | Generación | Plano genera imágenes |
| ScriptAnalysis | CharacterBible | Promoción | Personajes detectados se promueven a bible |
| VisualBible | Storyboard | Influencia | Estilo visual guía el storyboard |
| CharacterBible | Shot | Asignación | Personaje aparece en planos |
| Storyboard | ShootingPlan | Derivación | Plan de rodaje se deriva del desglose |
| ShootingPlan | ShootingDay | Composición | Plan contiene jornadas |
| Budget | FundingSource | Financiación | Presupuesto se financia con fuentes |
| FundingOpportunity | FundingSource | Conversión | Oportunidad solicitada se convierte en fuente |
| Asset | Deliverable | Asignación | Asset se marca como entregable |
| Deliverable | DistributionPackage | Agrupación | Entregables se agrupan en paquetes |
| Deliverable | FestivalStrategy | Asignación | Entregables se envían a festivales |
| Deliverable | SalesStrategy | Asignación | Entregables se venden por territorio |
| User | CreditConsumption | Consumo | Usuario consume créditos |
| CreditPool | CreditConsumption | Contabilidad | Pool descuenta créditos consumidos |
| Milestone | Task | Desbloqueo | Hito desbloquea tareas |
| Branch | Milestone | Activación | Hito activa ramas |

---

## 32. Métricas

### Métricas globales

| Métrica | Fórmula | Visible para |
|---|---|---|
| `healthScore` | Ponderado (presupuesto 30%, progreso 30%, riesgos 20%, hitos 20%) | Productor Propietario, Productor Ejecutivo |
| `budgetConsumptionRate` | `totalExecuted / totalEstimated × 100` | Rama 1, Dirección |
| `fundingCoverageRate` | `sum(approved funding) / totalEstimated × 100` | Rama 1, Dirección |
| `overallProgress` | `completedMilestones / totalMilestones × 100` | Todos |
| `riskBurden` | `count(active risks with severity >= alta)` | Dirección |
| `creditConsumptionRate` | `(planCreditsAllocated - planCreditsRemaining) / planCreditsAllocated × 100` | Dirección |
| `creditProjectedRunout` | Días hasta agotar créditos al ritmo actual | Dirección |

### Métricas de Rama 1

| Métrica | Fórmula | Visible para |
|---|---|---|
| `budgetVariance` | `totalEstimated - totalExecuted` | Rama 1, Dirección |
| `budgetCommitmentRate` | `(totalExecuted + totalCommitted) / totalEstimated × 100` | Rama 1, Dirección |
| `fundingAchieved` | `sum(approved+collected) / target × 100` | Rama 1, Dirección |
| `fundingAtRisk` | `count(riskFlag=rojo) / totalSources × 100` | Rama 1, Dirección |
| `pendingApplications` | `count(status=solicitada)` | Rama 1 |

### Métricas de Rama 2

| Métrica | Fórmula | Visible para |
|---|---|---|
| `scriptProgress` | Según estado actual + análisis completado | Rama 2, Dirección |
| `storyboardCompletion` | `completedShots / totalShots × 100` | Rama 2, Dirección |
| `shootingProgress` | `completedDays / totalDays × 100` | Rama 2, Dirección |
| `charactersCompleted` | `charactersDefined / totalCharacters × 100` | Rama 2 |
| `sceneBreakdownProgress` | `scenesBreakdowned / totalScenes × 100` | Rama 2 |

### Métricas de Rama 3

| Métrica | Fórmula | Visible para |
|---|---|---|
| `pendingReviews` | `count(assets with reviewStatus=pendiente)` | Rama 3 |
| `deliverableCompletion` | `completed / total × 100` | Rama 3, Dirección |
| `deliverableOnTime` | `deliveredOnTime / totalDelivered × 100` | Rama 3, Dirección |
| `festivalSubmissions` | `count(status=enviado OR aceptado)` | Rama 3, Dirección |
| `salesPipelineValue` | Suma de `estimatedValue` de estrategias activas | Dirección |

---

## 33. Visibilidad conceptual por rol

La tabla muestra qué entidades puede ver cada rol, en qué nivel de detalle. Basado en `cid_project_access_model_v1.md`.

| Entidad | Productor Propietario | Productor Ejecutivo | Jefe de Producción | Director | Guionista | Post Supervisor | Distribuidor |
|---|---|---|---|---|---|---|---|
| Organization | Completo | Completo | Completo | Completo | Completo | Completo | Completo |
| Project | Completo | Completo | Completo | Completo | Completo | Completo | Completo |
| User | Completo | Completo | Completo | Completo (nombres) | Solo nombres | Completo (nombres) | Solo nombres |
| Role | Completo | Completo | Completo | Completo | Completo | Completo | Completo |
| Branch | Completo | Completo | Completo | Completo | Solo su rama | Completo | Solo su rama |
| Task | Todas | Todas | Solo R1+parcial R2 | Solo R2+parcial R3 | Solo R2 | Solo R3 | Solo Comercialización |
| Milestone | Completo | Completo | Completo | Completo | Solo hitos R2 | Completo | Solo hitos entrega |
| Risk | Completo | Completo | Solo R1 | Solo R2 | No | Solo R3 | No |
| Budget | Completo | Completo | Completo | Solo lectura | No | No | No |
| FundingSource | Completo | Completo | Completo | No | No | No | No |
| FundingOpportunity | Completo | Completo | Completo | No | No | No | No |
| Script | Completo | Solo lectura | No | Completo | Completo | No | No |
| ScriptAnalysis | Completo | Solo lectura | No | Completo | Completo | No | No |
| CharacterBible | Completo | Solo lectura | No | Completo | Completo | No | No |
| VisualBible | Completo | Solo lectura | No | Completo | Lectura | No | No |
| Storyboard | Completo | Solo lectura | No | Completo | Solo guion | No | No |
| Sequence | Completo | Solo lectura | No | Completo | Solo guion | No | No |
| Shot | Completo | Solo lectura | No | Completo | Solo guion | No | No |
| ShootingPlan | Completo | Solo lectura | Parcial (planificación) | Completo | No | No | No |
| ShootingDay | Completo | Solo lectura | Parcial (costes) | Completo | No | No | No |
| Asset | Completo | Completo | Por rama | Por rama | Solo R2 | Por rama | Solo Comercialización |
| Deliverable | Completo | Completo | Parcial (costes) | Parcial (versión final) | No | Completo | Completo |
| DistributionPackage | Completo | Completo | No | No | No | Completo | Completo |
| FestivalStrategy | Completo | Completo | No | No | No | Parcial | Completo |
| SalesStrategy | Completo | Completo | No | No | No | No | Completo |
| CreditConsumption | Completo | Completo | No | No | No | No | No |
| CreditPool | Completo | Completo | No | No | No | No | No |

---

## 34. Qué NO incluye este modelo

| Aspecto | Motivo |
|---|---|
| **Suscripciones y planes de pago** | Depende de la estrategia de monetización. Definido en `cid_project_access_model_v1.md`. |
| **Facturación y pagos** | No es modelo de datos de producto. Depende de sistema de billing. |
| **Log de auditoría de acceso** | Entidad transversal que se definirá en fase de implementación técnica. |
| **Notificaciones** | Depende de infraestructura de eventos, no de modelo de datos de dominio. |
| **Roles personalizados (RBAC)** | Los roles son predefinidos en esta fase. La personalización se abordará en fase Enterprise. |
| **Integraciones externas** | APIs de terceros (Stripe, Qdrant, Ollama, ComfyUI) no forman parte del modelo de dominio. |
| **Cache / vistos / favoritos** | Son datos de interacción de usuario, no de dominio del proyecto. |
| **Comentarios y discusiones** | Dependen del módulo de colaboración, no definido en esta fase. |
| **Trazabilidad de prompts IA** | Los prompts se registran en el metadata de CreditConsumption sin almacenar el contenido sensible. |
| **Métricas de rendimiento de GPU** | Son datos de infraestructura, no de dominio del producto. |

---

## 35. Próxima fase

**CID.PRODUCT.ARCHITECTURE.CROSS.DOCUMENT.VALIDATION.1** — Validación cruzada entre documentos de producto:

1. Validar coherencia entre `cid_project_command_center_branches_v1.md`, `cid_project_access_model_v1.md`, `cid_project_command_center_data_model_v1.md` y `cid_credits_business_model_v1.md`.
2. Identificar contradicciones entre los cuatro documentos (nombres de entidades, cardinalidades, visibilidad, límites de licencia).
3. Verificar que los nombres de módulos, roles y ramas son consistentes.
4. Verificar que los costes de créditos por operación en el modelo de créditos tienen cobertura en las entidades de datos.
5. Generar un informe de consistencia y recomendaciones de armonización.
6. Validar las dependencias con `cid_funding_taxonomy_v1.md` y `cid_funding_intelligence_data_model_v1.md` (disponibles en `docs/finance_intelligence/`) contra las entidades FundingSource y FundingOpportunity.

---

## Historial de revisiones

| Fecha | Versión | Cambios |
|---|---|---|
| 2026-06-02 | 1.0 | Creación inicial con 16 entidades + 2 sub-entidades. |
| 2026-06-03 | 2.0 | Revisión completa: 26 entidades + 5 sub-entidades. Añadidas ScriptAnalysis, CharacterBible, VisualBible, Sequence, Shot, ShootingDay, DistributionPackage, FestivalStrategy, SalesStrategy, CreditConsumption, CreditPool, FundingOpportunity. Añadidas secciones de visibilidad por rol, dependencias, métricas y principios. Marcadas dependencias pendientes de verificación para FundingOpportunity. |
| 2026-06-03 | 2.1 | Revisión DATA.MODEL.REVIEW.1: añadida nota aclaratoria sobre promoción de Sequence a entidad independiente (ver §19), corregida próxima fase para evitar referencia circular. Sin cambios estructurales. |
| 2026-06-03 | 2.2 | Estados de proyecto unificados con Access Model (§30): ON_HOLD→FROZEN, COMPLETED→ARCHIVED+CLOSED. Tabla con ID EN + etiqueta ES. |
