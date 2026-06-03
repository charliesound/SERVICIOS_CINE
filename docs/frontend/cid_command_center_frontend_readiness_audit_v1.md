# CID Command Center - Frontend Readiness Audit

**Documento:** `docs/frontend/cid_command_center_frontend_readiness_audit_v1.md`
**Version:** 1.0
**Fecha:** 2026-06-03
**Tags:** `CID`, `frontend`, `audit`, `command-center`, `readiness`

---

## 1. Resumen ejecutivo

El frontend actual **si permite iniciar** una primera microfase segura de Command Center, pero **no esta preparado** para una implementacion completa de las tres ramas en una sola pasada.

**Veredicto:**
- **GO** para `CID.FRONTEND.COMMAND.CENTER.SHELL.1`
- **NO-GO** para una implementacion completa end-to-end del Command Center en una sola fase

Motivos principales:
- ya existen rutas y paginas utiles por proyecto para varias piezas de Rama 1, Rama 2 y Rama 3
- ya existen patrones reutilizables de shell, cards, modulos, status badges, hooks y React Query
- el frontend sigue mezclando dos modelos: una experiencia moderna i18n/Tailwind y varias paginas legacy con textos hardcodeados, estilos inconsistentes y acoplamiento por modulo
- la navegacion y los tipos todavia responden a taxonomias antiguas (`creator`, `producer`) y no al modelo funcional actual de ramas, roles, usuarios por proyecto y creditos por proyecto

---

## 2. Base funcional usada para esta auditoria

Documentos base:
- `docs/product/cid_project_command_center_branches_v1.md`
- `docs/product/cid_project_access_model_v1.md`
- `docs/product/cid_project_command_center_data_model_v1.md`
- `docs/business/cid_credits_business_model_v1.md`
- `docs/business/cid_pricing_competitive_baseline_v1.md`
- `docs/product/cid_command_center_readiness_audit_v1.md`

Criterios funcionales adicionales incorporados en esta auditoria:
- **Rama 1 = Produccion & Financiacion + preparacion operativa del rodaje**
- **Rama 2 = Creativo & Rodaje + planificacion/ejecucion creativa**
- las ramas son **responsabilidades funcionales**, no silos
- debe existir el concepto funcional futuro de **BranchImpact / Solicitud de Impacto entre ramas**

---

## 3. Alcance frontend auditado

Rutas, paginas y piezas revisadas:
- `src_frontend/src/App.tsx`
- `src_frontend/src/components/AppShell.tsx`
- `src_frontend/src/components/modules/ModuleCard.tsx`
- `src_frontend/src/components/FundingOpportunitiesDashboard.tsx`
- `src_frontend/src/pages/Dashboard.tsx`
- `src_frontend/src/pages/ProducerStudioHubPage.tsx`
- `src_frontend/src/pages/ProjectDetailPage.tsx`
- `src_frontend/src/pages/ProjectDashboardPage.tsx`
- `src_frontend/src/pages/ModulesCatalogPage.tsx`
- `src_frontend/src/pages/StoryboardBuilderPage.tsx`
- `src_frontend/src/pages/ProjectFundingPage.tsx`
- `src_frontend/src/pages/BudgetEstimatorPage.tsx`
- `src_frontend/src/pages/ProjectMembersPage.tsx`
- `src_frontend/src/pages/ChangeRequestsPage.tsx`
- `src_frontend/src/pages/EditorialAssemblyPage.tsx`
- `src_frontend/src/pages/ReviewsOverviewPage.tsx`
- `src_frontend/src/pages/DeliveryOverviewPage.tsx`
- `src_frontend/src/pages/DeliverableDetailPage.tsx`
- `src_frontend/src/pages/DistributionPackPage.tsx`
- `src_frontend/src/pages/CommercialCrmPage.tsx`
- `src_frontend/src/pages/DocumentsPage.tsx`
- `src_frontend/src/pages/ReportsPage.tsx`
- `src_frontend/src/pages/MediaAssetsPage.tsx`
- `src_frontend/src/hooks/useProjectDashboard.ts`
- `src_frontend/src/hooks/usePlans.ts`
- `src_frontend/src/hooks/useModules.ts`
- `src_frontend/src/hooks/useDocuments.ts`
- `src_frontend/src/hooks/useReports.ts`
- `src_frontend/src/hooks/useIngest.ts`
- `src_frontend/src/hooks/useFundingOpportunities.ts`
- `src_frontend/src/api/projects.ts`
- `src_frontend/src/api/projectFunding.ts`
- `src_frontend/src/api/projectMembers.ts`
- `src_frontend/src/api/moduleCatalog.ts`
- `src_frontend/src/api/plans.ts`
- `src_frontend/src/types/auth.ts`
- `src_frontend/src/types/user.ts`
- `src_frontend/src/types/modules.ts`
- `src_frontend/src/i18n/index.ts`

---

## 4. Rutas encontradas

### 4.1 Shell y acceso principal

| Ruta | Estado | Observacion |
|---|---|---|
| `/cid` | Existe | Dashboard general actual, no Command Center por ramas |
| `/cid/demo` | Existe | Modelo legacy por programa |
| `/cid/creator` | Existe | Taxonomia legacy |
| `/cid/producer` | Existe | Producer hub, no Command Center final |
| `/cid/studio` | Existe | Taxonomia legacy |
| `/cid/enterprise` | Existe | Taxonomia legacy |
| `/dashboard` | Existe | Dashboard global actual |
| `/projects` | Existe | Lista de proyectos |
| `/projects/:projectId` | Existe | Detalle de proyecto actual |
| `/projects/:projectId/dashboard` | Existe | Dashboard de proyecto, util como precursor |

### 4.2 Rama 1 - Produccion & Financiacion

| Ruta | Estado |
|---|---|
| `/projects/:projectId/budget` | Existe |
| `/projects/:projectId/funding` | Existe |
| `/projects/:projectId/producer-pitch` | Existe |
| `/projects/:projectId/members` | Existe |
| `/projects/:projectId/change-requests` | Existe |

### 4.3 Rama 2 - Creativo & Rodaje

| Ruta | Estado |
|---|---|
| `/projects/:projectId/script-analysis` | Existe |
| `/projects/:projectId/breakdown` | Existe |
| `/projects/:projectId/storyboard-builder` | Existe |
| `Concept Art` | Existe como panel dentro de `ProjectDetailPage`, no como ruta propia |

### 4.4 Rama 3 - Postproduccion, Entrega & Comercializacion

| Ruta | Estado |
|---|---|
| `/projects/:projectId/editorial` | Existe |
| `/projects/:projectId/reviews` | Existe |
| `/projects/:projectId/reviews/:reviewId` | Existe |
| `/projects/:projectId/delivery` | Existe |
| `/projects/:projectId/delivery/:deliverableId` | Existe |
| `/projects/:projectId/distribution` | Existe |
| `/projects/:projectId/crm` | Existe |

### 4.5 Transversales

| Ruta | Estado | Observacion |
|---|---|---|
| `/modules` | Existe | Catalogo comercial/tecnico de modulos |
| `/documents` | Existe | Global, no scoped por proyecto |
| `/reports/:reportType` | Existe | Global, no scoped por proyecto |
| `/ingest/assets` | Existe | Global, no scoped por proyecto |
| `/ingest/scans` | Existe | Global, no scoped por proyecto |
| `/plans` | Existe | Basado en limites de jobs/analisis/storyboards, no en modelo Command Center |

---

## 5. Componentes reutilizables actuales

### 5.1 Reutilizables claros

- `AppShell.tsx`: shell lateral ya existente, aunque hoy es global y no por proyecto/rol
- `ModuleCard.tsx`: patron util para tarjetas de modulo con badges y CTA
- `StatusBadge.tsx`, `ModuleStatusBadge.tsx`, `ModuleAccessBadge.tsx`, `ModulePackBadge.tsx`: base valida para estados y permisos
- `FundingOpportunitiesDashboard.tsx`: buen ejemplo de dashboard con summary cards, filtros, lista y panel de evidencia
- `ProjectDashboardPage.tsx`: mejor precursor del futuro Command Center de proyecto
- `ProducerStudioHubPage.tsx`: util como referencia visual para hero, quick actions y flujo recomendado
- componentes storyboard: base fuerte para Rama 2
- hooks React Query ya existentes para funding, documents, reports, ingest, plans y dashboard

### 5.2 Reutilizables parciales

- `ProjectMembersPage.tsx`: sirve para usuarios por proyecto, pero no refleja todavia el modelo completo de roles/rama/visibilidad
- `ChangeRequestsPage.tsx`: es el antecedente mas cercano a `BranchImpact`, pero hoy opera como lista de change requests por modulo, no por rama
- `ModulesCatalogPage.tsx`: sirve para catalogo y activacion comercial, no para navegacion operativa del Command Center

### 5.3 Lo que falta crear

- shell especifico de Command Center por proyecto
- navegacion por ramas y subareas
- tarjetas de estado por rama
- barra de contexto de proyecto, rol activo y estado del proyecto
- modelo visual de `BranchImpact / Solicitud de Impacto entre ramas`
- vista de creditos IA por proyecto separada de planes y jobs
- estado vacio y pantalla de acceso restringido estandarizados para ramas/modulos

---

## 6. Dashboard actual

### 6.1 Que hace hoy

`Dashboard.tsx` es un dashboard general de plataforma:
- lista proyectos recientes
- muestra conteos de jobs, analisis, storyboards y plan
- expone cola y jobs recientes

`ProjectDashboardPage.tsx` ya se acerca mas a un dashboard de proyecto:
- hero del proyecto
- progreso general
- quick actions
- grupos de modulos
- proximas acciones
- warnings

### 6.2 Que se puede conservar

- layout general de `ProjectDashboardPage.tsx`
- summary card + quick actions + next actions
- carga con `useProjectDashboard`
- uso de badges de estado

### 6.3 Que le falta

- agrupacion explicita por ramas funcionales actuales
- visibilidad por rol según Access Model
- estado por rama con riesgo + siguiente accion
- soporte para `BranchImpact`
- creditos IA por proyecto
- usuarios por proyecto visibles como parte del contexto del Command Center
- estados del proyecto alineados con `PREPROD / ACTIVE / FROZEN / WRAPPING / ARCHIVED / CLOSED`

### 6.4 Que habria que reemplazar

- taxonomia actual de grupos (`priority`, `development`, `commercial`, `operational`) por ramas funcionales
- enlaces rotos o incoherentes de modulos desde `getModuleRoute`
- mezcla de dashboard global de plataforma con dashboard operativo por proyecto

---

## 7. Mapeo del frontend actual contra las ramas

### 7.1 Rama 1 - Produccion & Financiacion

**Cobertura actual parcial-alta** en:
- presupuesto
- funding
- producer pitch
- miembros del proyecto
- change requests

**Cobertura baja o ausente** en:
- preparacion operativa del rodaje
- contratacion de personal
- negociacion y gestion de equipo
- logistica
- transporte
- alojamiento
- permisos
- seguros
- coordinacion con proveedores
- cost reports
- cashflow / tesoreria

Conclusion:
- Rama 1 tiene una base frontend real, pero le faltan precisamente varios bloques del criterio actualizado

### 7.2 Rama 2 - Creativo & Rodaje

**Cobertura actual alta** en:
- guion
- script analysis
- breakdown
- storyboard
- concept art / visual support

**Cobertura parcial** en:
- continuidad / raccord
- necesidades de escena
- ejecucion creativa del rodaje

Conclusion:
- Rama 2 es la rama mejor adelantada en frontend operativo

### 7.3 Rama 3 - Postproduccion, Entrega & Comercializacion

**Cobertura actual media** en:
- editorial assembly
- reviews
- delivery
- distribution pack
- commercial CRM

**Cobertura desigual**:
- algunas paginas estan razonablemente integradas
- otras siguen en formato legacy, con mas mock visual y menos normalizacion i18n/estilo

Conclusion:
- Rama 3 tiene superficie suficiente para entrar en Command Center, pero no tiene una experiencia unificada

---

## 8. Preparacion frente a requisitos clave

### 8.1 Arquitectura piramidal

**Preparacion:** media-baja

Existe base conceptual en:
- `ProjectDashboardPage.tsx`
- `ProjectMembersPage.tsx`
- `useProjectDashboard.ts`

Faltan:
- rol activo por proyecto
- fallback de visibilidad por rama
- navegacion condicionada por acceso

### 8.2 Visibilidad por rol

**Preparacion:** baja

Hoy hay señales parciales:
- `PlanRoute.tsx`
- `CIDRoute.tsx`
- `ProjectMembersPage.tsx`
- `useProjectDashboard.ts` devuelve `role_dashboard` y `permissions`

Pero no existe todavia:
- una capa comun de permisos por rama
- ocultacion uniforme de modulos no accesibles
- pantalla de acceso restringido normalizada para Command Center

### 8.3 Usuarios por proyecto

**Preparacion:** media

Base disponible:
- `ProjectMembersPage.tsx`
- `api/projectMembers.ts`

Gap:
- el modelo visual actual no refleja bien `roleId`, `secondaryRoles`, `assignedBranchIds`, `accessLevels`, accesos temporales ni estados de acceso del Access Model

### 8.4 Creditos IA separados

**Preparacion:** baja

El producto documental define creditos por proyecto y separados de licencias.

El frontend actual sigue centrado en:
- plan del usuario
- jobs activos/cola
- analisis/storyboards

No existe todavia:
- vista de `CreditPool` por proyecto
- dashboard de consumo IA por proyecto
- alertas de consumo por proyecto

### 8.5 Tarjetas del Command Center

**Preparacion:** media

Ya hay patrones reutilizables en:
- `ProjectDashboardPage.tsx`
- `ProducerStudioHubPage.tsx`
- `FundingOpportunitiesDashboard.tsx`

Falta:
- modelo de tarjeta por rama
- wiring de riesgo, siguiente accion, dependencias y branch impacts

### 8.6 BranchImpact / Solicitud de Impacto entre ramas

**Preparacion:** baja-media

Antecedente util:
- `ChangeRequestsPage.tsx`

Lo que ya sugiere:
- lista de solicitudes
- estados `proposed / pending_approval / approved / rejected / applied`
- severidad y aprobacion

Lo que falta para BranchImpact real:
- rama origen y rama destino
- tipo de impacto: presupuesto, contratacion, logistica, permisos, seguros, calendario, entregables, compromisos
- trazabilidad funcional entre R1, R2 y R3
- UI de impacto cruzado, no solo por modulo

---

## 9. Riesgos principales

### R1 - Taxonomias legacy de planes/programas

El frontend sigue usando `creator` y `producer` como programas en:
- `App.tsx`
- `AppShell.tsx`
- `PlanRoute.tsx`
- `types/auth.ts`
- `store/auth.ts`

Esto no coincide con el modelo documental actual de planes `Starter / Pro / Studio / Premium / Enterprise`.

### R2 - Enlaces de dashboard no alineados con rutas reales

En `ProjectDashboardPage.tsx`:
- `documents` apunta a `/projects/:projectId/documents`, pero esa ruta no existe
- `media` apunta a `/ingest/scans`, que es global y no por proyecto
- `breakdown` apunta a `/projects/:projectId`, no a `/projects/:projectId/breakdown`

### R3 - Frontend visualmente heterogeneo

Hay dos familias claras:
- paginas modernas con Tailwind + i18n + cards consistentes
- paginas legacy con estilos claros, hardcodes y semantica distinta

Casos visibles:
- `ReviewsOverviewPage.tsx`
- `DeliveryOverviewPage.tsx`
- `DeliverableDetailPage.tsx`
- `CommercialCrmPage.tsx`
- partes de `DistributionPackPage.tsx`

### R4 - Textos hardcodeados e i18n incompleto

Ejemplos:
- labels fijos en `AppShell.tsx`
- textos fijos en `ProjectDashboardPage.tsx`
- paginas Rama 3 con multiples textos hardcodeados
- `ProjectMembersPage.tsx` mezcla `t(...)` con literales como `Activo`, `Remover`, `Puedes gestionar permisos...`

### R5 - Falta de scope por proyecto en modulos transversales

`DocumentsPage`, `ReportsPage` y `MediaAssetsPage` son globales, no orientados a contexto de proyecto. Para Command Center esto rompe la expectativa de aislamiento por proyecto.

### R6 - Modelo de creditos no representado

No hay tipos ni vistas de `CreditPool`, consumo mensual, alertas ni creditos extra por proyecto.

### R7 - BranchImpact ausente

El frontend no tiene hoy ninguna abstraccion de impacto cruzado entre ramas. Solo existe el precursor `ChangeRequestsPage`.

### R8 - Acoplamiento pagina-endpoint

Varias paginas usan `fetch` directo o contratos locales en vez de un patron comun fuerte de API/types. Esto aumentaria el coste de introducir visibilidad por rol y branch impact de forma consistente.

---

## 10. Componentes a crear o adaptar en una futura implementacion

### 10.1 Rutas y paginas

- nueva pagina shell de Command Center por proyecto
- vista principal por ramas
- vista de tarjetas por rama
- vista de `BranchImpact / Solicitud de Impacto`
- panel de creditos IA por proyecto

### 10.2 Componentes

- `CommandCenterShell`
- `ProjectContextHeader`
- `BranchTabs` o `BranchRail`
- `BranchStatusCard`
- `BranchImpactList`
- `BranchImpactCard`
- `ProjectCreditPoolCard`
- `RoleVisibilityGuard`

### 10.3 Tipos TypeScript

- `CommandCenterProjectView`
- `ProjectBranchSummary`
- `BranchImpactRequest`
- `ProjectCreditPoolView`
- `ProjectRoleVisibility`

### 10.4 Hooks y servicios

- hook para contexto de proyecto actual
- hook para visibilidad por rama/rol
- hook para resumen del Command Center
- API frontend para branch impacts
- API frontend para credit pool y consumo IA por proyecto

### 10.5 i18n

- nueva familia de keys `internal.commandCenter.*`
- normalizar hardcodes de shell, dashboards y Rama 3 legacy

---

## 11. Plan de implementacion por microfases

### Microfase 1 - `CID.FRONTEND.COMMAND.CENTER.SHELL.1`

Objetivo:
- crear shell de Command Center por proyecto sin reemplazar modulos existentes

Alcance seguro:
- nueva entrada desde `ProjectDashboardPage`
- header de proyecto con estado y rol
- navegacion por ramas
- 3 tarjetas vacias/placeholder conectadas a datos existentes basicos
- sin tocar backend
- sin mover paginas de modulo todavia

Salida esperada:
- estructura navegable
- contrato i18n base
- superficie lista para enchufar Rama 1, Rama 2 y Rama 3 despues

### Microfase 2 - `CID.FRONTEND.COMMAND.CENTER.BRANCH.CARDS.1`

- convertir datos actuales de dashboard en tarjetas por rama
- mapear quick actions a ramas
- corregir rutas incoherentes

### Microfase 3 - `CID.FRONTEND.COMMAND.CENTER.VISIBILITY.1`

- introducir visibilidad por rol y acceso por rama
- ocultacion de modulos y estados restringidos

### Microfase 4 - `CID.FRONTEND.COMMAND.CENTER.BRANCH.IMPACT.1`

- introducir UI de `BranchImpact / Solicitud de Impacto`
- reutilizar parte del flujo de `ChangeRequestsPage`

### Microfase 5 - `CID.FRONTEND.COMMAND.CENTER.CREDITS.1`

- credit pool por proyecto
- consumo mensual
- alertas de uso

---

## 12. Veredicto GO / NO-GO

### GO para empezar frontend

**Si el alcance inicial es solo `CID.FRONTEND.COMMAND.CENTER.SHELL.1`.**

Razones:
- ya existe shell autenticada
- ya existe dashboard de proyecto reutilizable
- ya existen modulos reales en las tres ramas
- ya existe base de hooks, APIs y componentes para una primera capa de orquestacion frontend

### NO-GO para una fase unica de implementacion completa

No es seguro intentar de una sola vez:
- shell final
- ramas completas
- visibilidad por rol
- branch impact
- creditos IA por proyecto
- normalizacion i18n de legacy pages

---

## 13. Siguiente fase recomendada

**`CID.FRONTEND.COMMAND.CENTER.SHELL.1`**

Secuencia recomendada:
1. crear shell por proyecto y navegacion por ramas
2. reusar `ProjectDashboardPage` como fuente inicial de tarjetas
3. no migrar todavia modulos individuales
4. dejar `BranchImpact` documentado como contrato visual para la siguiente microfase

---

## 14. Historial de revisiones

| Fecha | Version | Cambios |
|---|---|---|
| 2026-06-03 | 1.0 | Auditoria inicial de readiness frontend para CID Project Command Center. Veredicto: GO para microfase shell, NO-GO para implementacion completa en una sola fase. |
