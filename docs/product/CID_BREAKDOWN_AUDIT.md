# CID Breakdown - Auditoria de Estado Comercial y Tecnico

## Resumen ejecutivo

CID Breakdown existe hoy como capacidad backend embebida dentro del flujo de Script Analysis, pero **aun no es un modulo vendible independiente**.

Estado actual:
- Tecnico: **PARCIAL INICIAL**
- Comercial: **PENDIENTE**
- Decisión para iniciar implementación Sprint 3: **GO**

Veredicto:
- Hay base funcional reutilizable (escenas, breakdowns, department breakdown en `ProductionBreakdown.breakdown_json`).
- Faltan piezas clave para SKU vendible: enforcement propio, pantalla propia, export propio, smoke/test dedicados y contrato funcional de desglose profesional.

---

## Endpoints auditados relacionados con Breakdown

### 1) Endpoints nucleares actuales

| Endpoint | Metodo | Proposito | Modulo propietario | Modulos consumidores | Auth/Tenant | Persiste | Control por modulo hoy | Gap comercial |
|---|---|---|---|---|---|---|---|---|
| `/api/projects/{project_id}/breakdown/scenes` | GET | Devuelve lista de escenas desglosadas | breakdown (conceptual), implementado en intake | budget_lite, production_manager_lite, call_sheet (futuro), storyboard/pitch (indirecto) | Si (tenant check) | No (lectura) | **No** `require_module_access("breakdown")` | No SKU gate, no contrato formal |
| `/api/projects/{project_id}/breakdown/departments` | GET | Devuelve desglose departamental agregado | breakdown (conceptual), implementado en intake | budget_lite, production_manager_lite, call_sheet (futuro) | Si (tenant check) | No (lectura) | **No** `require_module_access("breakdown")` | No SKU gate, no versionado/approval |

Evidencia: `src/routes/intake_routes.py`.

### 2) Endpoints productores de datos que Breakdown reutiliza

| Endpoint | Metodo | Proposito | Modulo propietario | Consumidor Breakdown | Persiste |
|---|---|---|---|---|---|
| `/api/projects/{project_id}/analysis/run` | POST | Genera scenes/breakdowns/departments en JSON | script_analysis | Si, fuente primaria | Si (`production_breakdowns`) |
| `/api/projects/{project_id}/analysis/summary` | GET | Estado/resumen de analisis | script_analysis | Si, estado previo | No |
| `/api/projects/{project_id}/analyze` | POST | Flujo analisis document-centric | script_analysis | Si, indirecto | Si |

Evidencia: `src/routes/intake_routes.py`, `src/routes/project_routes.py`, `src/services/script_intake_service.py`.

### 3) Endpoints consumidores aguas abajo del breakdown

| Endpoint | Metodo | Uso de breakdown | Modulo |
|---|---|---|---|
| `/api/projects/{project_id}/budgets/generate` | POST | Usa `source_breakdown_id` y métricas derivadas de guion/breakdown | budget_lite |
| `/api/projects/{project_id}/budgets/*` | GET/POST | Reutiliza contexto de Script/Breakdown para estimación | budget_lite |

Evidencia: `src/routes/budget_routes.py`, `src/services/budget_estimator_service.py`.

---

## Clasificacion de endpoints (detalle)

### `/breakdown/scenes`
- Metodo: GET
- Proposito: lectura de `breakdowns` (escena por escena)
- Owner real de implementacion: `analysis_service` en `script_intake_service`
- Autenticacion/tenant: si
- Persistencia: no escribe
- Plan/modulo: no enforcement de `module_breakdown`
- Gap: no garantiza acceso comercial por SKU Breakdown

### `/breakdown/departments`
- Metodo: GET
- Proposito: lectura de `department_breakdown`
- Owner real de implementacion: `analysis_service` en `script_intake_service`
- Autenticacion/tenant: si
- Persistencia: no escribe
- Plan/modulo: no enforcement de `module_breakdown`
- Gap: salida no normalizada para operación profesional por departamento

---

## Modelos y persistencia auditados

## Fuente de verdad actual

1. `production_breakdowns` (`ProductionBreakdown`)
   - `breakdown_json` (Text) contiene:
     - `scenes`
     - `breakdowns`
     - `department_breakdown`
     - `sequences`
     - `metadata`
   - Estado: persistente, multi-tenant por `organization_id`.

2. `department_line_items` (`DepartmentLineItem`)
   - Existe modelo tabular para líneas departamentales, **pero no se utiliza** en flujo Breakdown actual.

3. `budget_estimates` / `budget_line_items`
   - Consumen contexto de Script/Breakdown para Budget Lite.

4. `narrative.py` (`Scene`, `Character`, `Sequence`)
   - Modelos existen, **pero el flujo Breakdown actual no persiste aquí**; usa JSON blob.

## Persistente vs calculado al vuelo

Persistente:
- scenes/breakdowns/departments en `breakdown_json`
- metadatos agregados (counts, analysis_engine)

Calculado al vuelo:
- lectura filtrada por endpoint (`get_scenes`, `get_departments`)
- parte de derivaciones de budget desde texto/métricas

## Campos disponibles hoy (relevantes)

Cubiertos hoy:
- scene_number
- heading
- int_ext
- location
- time_of_day
- characters
- dialogue_count
- action_lines
- props_detected
- complexity_flags
- department notes básicas

No cubiertos de forma robusta/tabular:
- figuracion detallada
- vestuario por personaje/escena
- maquillaje/peluqueria
- vehiculos
- animales
- armas
- SFX/VFX desglosado por shot
- riesgos de produccion estructurados
- dificultad de escena estandarizada
- estimacion jornada por escena (hoy es agregado heuristico)
- requirements/checklists de preproduccion por escena

---

## Frontend auditado

Estado actual UI:
- Breakdown no tiene pantalla propia.
- La visualizacion principal vive dentro de `ProjectDetailPage.tsx` en tab de analisis.
- `ScriptAnalysisProPage.tsx` menciona Breakdown como modulo downstream, pero no lo abre.
- `BudgetEstimatorPage.tsx` existe como modulo separado y consume datos derivados.

## UX actual

Existe:
- visualizacion parcial de escenas dentro del flujo de analisis
- feedback general de loading/error en Script Analysis Pro

No existe:
- `BreakdownPage.tsx` dedicada
- edicion manual de desglose
- workflow de aprobacion humana
- export propio Breakdown (JSON/CSV/MD)
- smoke e2e propio del modulo Breakdown
- conexión explícita UX Script Analysis -> Breakdown -> Budget con handoff guiado

---

## Definicion exacta de "CID Breakdown vendible"

Debe entregar como minimo:

1. Escenas numeradas
2. INT/EXT
3. Dia/Noche
4. Localizacion principal
5. Personajes por escena
6. Figuracion (cantidad/tipo)
7. Atrezzo
8. Vestuario
9. Maquillaje/Peluqueria
10. Vehiculos
11. Animales
12. Armas
13. SFX/VFX
14. Sonido
15. Arte
16. Produccion
17. Riesgos de produccion
18. Dificultad de escena
19. Estimacion de jornada/tiempo
20. Notas de produccion
21. Export JSON/CSV/Markdown
22. Datos reutilizables por Budget Lite, Production Manager y Call Sheet

---

## Estado actual vs modulo vendible

| Requisito vendible | Existe hoy | Evidencia | Gap | Prioridad | Esfuerzo |
|---|---|---|---|---|---|
| Endpoints breakdown funcionales | Si | `intake_routes.py` | Contrato limitado, acoplado a script_analysis | Alta | 1 commit |
| Control por modulo breakdown | No | sin `require_module_access("breakdown")` | No bloqueo por plan SKU | Alta | 1 commit |
| Pantalla propia Breakdown | No | no existe `BreakdownPage` | UX embebida y débil comercialmente | Alta | 1 commit |
| Export propio Breakdown | No | no endpoint dedicated | Falta artefacto compartible del modulo | Alta | 1 commit |
| Datos por escena profesionales | Parcial | `build_scene_breakdowns` | Cobertura incompleta de departamentos y riesgos | Alta | 1-2 commits |
| Persistencia reusable | Si (JSON blob) | `ProductionBreakdown.breakdown_json` | Falta normalizacion/tablas para operaciones avanzadas | Media | 1-2 commits |
| Integracion con Budget Lite | Parcial | `budget_estimator_service.py` | Handoff no explícito ni trazable por version breakdown | Media | 1 commit |
| Smoke/test dedicados Breakdown | No | no tests directos | Riesgo de regresion silenciosa | Media | 1 commit |
| Demo guiada Breakdown | No | no docs demo propia | No listo para venta asistida autónoma | Media | 1 commit |

---

## Dependencias de modulo

Script Analysis Pro -> Breakdown -> Budget Lite -> Production Manager Lite -> Call Sheet

Dependencias clave:
- `script_analysis` produce insumo de desglose
- `budget_lite` consume breakdown para estimación
- `production_manager_lite` y `call_sheet` requieren desglose confiable y editable

Riesgo actual:
- Si cambia schema de `breakdown_json`, impacta múltiples módulos por acoplamiento implícito.

---

## Propuesta de arquitectura de cierre (Sprint 3)

1. Crear `BreakdownPage` propia
   - Ruta sugerida: `/projects/:projectId/breakdown`
   - Convivir temporalmente con visualización legacy en `ProjectDetailPage`

2. Export propio del modulo
   - Endpoint: `/api/projects/{id}/breakdown/export?format=json|csv|md`
   - Servicio: `breakdown_export_service.py`

3. Enforcement por modulo
   - Aplicar `require_module_access("breakdown")` en endpoints claros de ownership breakdown

4. Reuso de persistencia actual
   - Mantener `ProductionBreakdown.breakdown_json` como fuente inicial
   - Separar semánticamente bloques `script_analysis` vs `breakdown` dentro del payload o capa de servicio

5. Integracion con Budget Lite
   - Budget debe consumir Breakdown como dependencia explícita de datos (no solo texto)

---

## Roadmap propuesto Sprint 3 (commits)

### Commit 1 - Auditoria y contrato funcional
- Documento de contrato de campos Breakdown
- Matriz owner/consumer por endpoint

### Commit 2 - Enforcement backend Breakdown
- `require_module_access("breakdown")` en endpoints breakdown
- Tests de enforcement

### Commit 3 - Export Breakdown JSON/CSV/Markdown
- Nuevo endpoint export
- `breakdown_export_service`
- Tests de export

### Commit 4 - Pantalla propia Breakdown
- `BreakdownPage.tsx`
- Navegación contextual desde proyecto y módulo
- Estados loading/error/empty

### Commit 5 - Demo/Smoke/Readiness Review
- Smoke `smoke_breakdown.sh`
- Demo guide Breakdown
- Readiness review final (GO/NO-GO)

---

## GO/NO-GO para iniciar implementacion

**GO** para comenzar Sprint 3 de implementación de Breakdown.

Motivo:
- Base técnica existente y utilizable
- Dependencia estratégica para Budget/Production/Call Sheet
- Gap comercial claro y acotable en 4-5 commits quirúrgicos

**NO-GO** para vender Breakdown hoy como SKU independiente (antes de Sprint 3).
