# CID Script Analysis Pro - Readiness Review Final

## Resumen ejecutivo

Script Analysis Pro alcanza un nivel de madurez suficiente para venta en modalidad asistida y piloto controlado.
La combinacion de enforcement por modulo, endpoint de export funcional, pantalla dedicada, smoke script y guia demo cierra los gaps criticos detectados en la auditoria inicial.

Decision propuesta: **GO para demo asistida** y **GO para piloto controlado**.

Decision no recomendada todavia: **self-serve pleno**.

---

## Matriz de readiness

| Requisito | Estado | Evidencia | Archivo/Ruta | Riesgo | Accion recomendada |
|---|---|---|---|---|---|
| Pantalla propia del modulo | PASS | Ruta dedicada creada y operativa | `src_frontend/src/pages/ScriptAnalysisProPage.tsx`, `/projects/:projectId/script-analysis` | Bajo | Mantener; agregar onboarding interactivo en sprint posterior |
| Endpoint funcional de analisis | PASS | `analysis/run` y `analysis/summary` activos | `src/routes/intake_routes.py` | Bajo | Monitorear latencia y errores por LLM |
| Datos persistentes o reutilizables | PASS | Persistencia en `production_breakdowns.breakdown_json`, resumen reutilizable | `src/services/script_intake_service.py`, `src/services/script_analysis_export_service.py` | Medio | Documentar retention y versionado de payloads |
| Control por plan/modulo | PASS | `require_module_access("script_analysis")` aplicado en 13 endpoints | `src/routes/intake_routes.py`, `src/routes/project_routes.py`, `src/routes/script_version_routes.py`, `src/routes/ollama_storyboard_routes.py` | Bajo | Mantener tests de enforcement en CI |
| Export JSON/Markdown | PASS | Endpoint `/analysis/export?format=json|md` con attachment | `src/routes/intake_routes.py`, `src/services/script_analysis_export_service.py` | Medio | Evaluar PDF como enhancement comercial |
| Demo reproducible | PASS | Guia paso a paso + flujo catalogo -> proyecto -> analisis -> export | `docs/demo/CID_SCRIPT_ANALYSIS_PRO_DEMO_GUIDE.md` | Medio | Crear demo seed autonoma para reducir friccion |
| Smoke script dedicado | PASS | Smoke configurable por `BASE_URL`, `TOKEN`, `PROJECT_ID` | `scripts/smoke_script_analysis_pro.sh` | Bajo | Integrarlo en pipeline de release demo |
| Tests minimos backend | PASS | Export (7), enforcement (6), flow legado (1) | `tests/integration/test_script_analysis_export.py`, `tests/integration/test_script_analysis_enforcement.py`, `tests/integration/test_project_script_analysis_flow.py` | Bajo | Sostener cobertura al tocar rutas compartidas |
| Documentacion de uso | PASS | Audit + enforcement + export + frontend + demo readiness + demo guide | `docs/product/CID_SCRIPT_ANALYSIS_PRO_*.md`, `docs/demo/CID_SCRIPT_ANALYSIS_PRO_DEMO_GUIDE.md` | Bajo | Consolidar en una pagina "Runbook comercial" |
| Texto comercial basico | PASS | Mensajes de valor en UI y docs | `src_frontend/src/pages/ScriptAnalysisProPage.tsx`, `docs/product/CID_SCRIPT_ANALYSIS_PRO_FRONTEND.md` | Bajo | Evolucionar copy por ICP (producer/studio) |
| Limites conocidos documentados | PASS | Riesgos/limitaciones explicitados en docs de export/frontend/demo | `docs/product/CID_SCRIPT_ANALYSIS_PRO_EXPORT.md`, `docs/product/CID_SCRIPT_ANALYSIS_PRO_FRONTEND.md`, `docs/product/CID_SCRIPT_ANALYSIS_PRO_DEMO_READINESS.md` | Bajo | Revisar trimestralmente estado de limites |

---

## Evaluacion comercial

### Se puede enseñar en demo asistida?
**Si.** Existe recorrido completo: catalogo -> proyecto -> analisis -> export JSON/MD -> estado bloqueado por plan.

### Se puede vender como piloto?
**Si, en piloto controlado.**
Condiciones: entorno supervisado, operador tecnico, guion de demo y proyecto de prueba preparado.

### Se puede vender self-serve hoy?
**Parcial / no recomendado como promesa principal.**
Faltan piezas de experiencia y operacion para autoservicio robusto.

### Que falta para self-serve?
- Demo seed autonoma (sin depender de proyecto real previo)
- Onboarding interactivo in-product
- Mayor robustez de polling / estado de jobs en frontend
- Frontend tests (smoke e2e o componente)
- Politica clara de privacidad para guiones reales de clientes
- Export PDF (opcional comercial, no bloqueante tecnico)

### Limitaciones con datos reales de clientes
- Guion es dato sensible; requiere politicas de retencion y acceso por tenant
- Uso de LLM (local/remoto) implica consideraciones de cumplimiento y confidencialidad
- Necesario definir disclaimers de "analysis assistance" y no sustitucion editorial

### Dependencias de Ollama/OpenAI
- El flujo principal de `analysis/run` depende de servicios LLM configurados
- Endpoint local `/analyze/local-ollama` depende de disponibilidad de Ollama y modelos
- Si LLM no responde, la UX puede quedar en espera prolongada

### Dependencias de proyecto existente
- El modulo es project-first por diseno
- Requiere `projectId` y `script_text` para valor real
- Sin guion cargado, el modulo queda en empty state guiado

---

## Riesgos tecnicos

### Endpoints sin proteccion
- En scope `script_analysis`: cobertura principal en PASS
- Rutas relacionadas pero de otros modulos (`breakdown`, `storyboard`) mantienen estrategia separada

### Flujos compartidos con Breakdown/Pitch/Storyboard
- Existe acoplamiento de datos (breakdown_json como fuente)
- Riesgo de regressions cruzadas al evolucionar schema de breakdown

### Exports incompletos
- JSON y MD cubiertos
- PDF no disponible aun (no bloqueante para piloto)

### Frontend tests y lint
- Sin test runner frontend dedicado
- Lint no consolidado como gate de release

### Polling robusto
- Polling actual con `setTimeout` simple
- Falta timeout global, retry strategy y cancelacion

### Proyectos sin analisis
- Backend responde 200 con warnings; comportamiento correcto
- UX depende de guidance, ya disponible

---

## Gaps bloqueantes

**No se identifican gaps bloqueantes para demo asistida o piloto controlado.**

## Gaps no bloqueantes

1. Falta export PDF
2. Falta demo seed autonoma
3. Falta cobertura de tests frontend
4. Polling frontend mejorable
5. Dependencia operativa de LLM sin fallback comercial explicito

---

## Decision GO/NO-GO

- **GO para demo asistida**
- **GO para piloto controlado**
- **NO GO para self-serve pleno** hasta cerrar gaps de experiencia/autonomia

---

## Recomendacion comercial

Posicionar Script Analysis Pro como primer modulo vendible en formato:
- "Pilot-first" con onboarding asistido
- Paquete de demostracion con guion ficticio y export compartible
- Mensaje central: "Convierte un guion en un analisis estructurado exportable, base para Pitch Deck, Breakdown, Storyboard y Budget"

---

## Recomendacion tecnica

Priorizar hardening de experiencia antes de escalar venta self-serve:
1. Demo seed autonoma
2. Polling resiliente + estados de error detallados
3. Test suite frontend minima (smoke e2e o vitest)
4. Roadmap de export PDF

---

## Siguiente modulo recomendado

**Recomendado: Breakdown**

Justificacion:
- Dependencia directa de Script Analysis (ya estabilizado)
- Valor operativo inmediato para preproduccion (departamentos, necesidades, planning)
- Menor dependencia GPU que Storyboard AI
- Facil de convertir en narrativa comercial B2B junto al export de Script Analysis

Orden sugerido de siguiente bloque:
1. Breakdown
2. Budget Lite
3. Pitch Deck
4. Storyboard AI

---

## Siguiente sprint recomendado

Sprint 3 (post-readiness):
1. Breakdown enforcement + UX dedicada
2. Integracion Script Analysis -> Breakdown -> Budget Lite
3. Demo autonoma multi-modulo para venta comercial
