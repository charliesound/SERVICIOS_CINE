# Directiva: Auditoria de CID Breakdown

## Objetivo

Auditar el estado real del modulo `breakdown` para determinar que falta para convertirlo en un modulo comercial vendible e independiente dentro del ecosistema CID.

## Contexto

CID Breakdown existe hoy como capacidad embebida en el flujo de Script Analysis, con lectura de escenas y departamentos desde `ProductionBreakdown.breakdown_json`. La base funcional existe, pero faltan capacidades clave para venderlo como SKU independiente: enforcement por modulo, pantalla propia, export propio, contrato funcional profesional y pruebas dedicadas.

El roadmap comercial y el estado en `modules.yml` lo ubican como `PARCIAL_INICIAL` y comercialmente `PENDIENTE`, con priorizacion para Sprint 3.

## Archivos afectados

### Documentacion
- `docs/product/CID_BREAKDOWN_AUDIT.md` - auditoria comercial y tecnica del modulo
- `directivas/cid_breakdown_audit.md` - esta directiva

### Backend auditado
- `src/routes/intake_routes.py` - endpoints `/breakdown/scenes` y `/breakdown/departments`
- `src/routes/project_routes.py` - endpoints productores de analisis consumidos por breakdown
- `src/routes/budget_routes.py` - consumidores aguas abajo
- `src/services/script_intake_service.py` - persistencia de `breakdown_json`
- `src/services/script_analysis_export_service.py` - referencia de patron export
- `src/services/budget_estimator_service.py` - consumo de datos de breakdown/script
- `src/models/production.py` - `ProductionBreakdown`, `DepartmentLineItem`
- `src/models/narrative.py` - `Scene`, `Character`, `Sequence`
- `src/models/budget_estimator.py` - modelos de presupuesto relacionados
- `src/config/modules.yml` - estado de modulo breakdown
- `src/config/plans.yml` - feature flags por plan

### Frontend auditado
- `src_frontend/src/pages/ProjectDetailPage.tsx` - visualizacion actual embebida
- `src_frontend/src/pages/ScriptAnalysisProPage.tsx` - referencia de modulo
- `src_frontend/src/pages/BudgetEstimatorPage.tsx` - consumidor downstream

### Tests auditados
- `tests/integration/test_project_script_analysis_flow.py`
- `tests/integration/test_script_analysis_export.py`
- `tests/integration/test_script_analysis_enforcement.py`

## Entradas

- Roadmap y auditorias previas de producto
- Configuracion modular (`modules.yml`, `plans.yml`)
- Rutas y servicios relacionados con breakdown/script analysis/budget
- Modelos de persistencia y entidades narrativas
- Frontend actual de consumo
- Pruebas de integracion existentes

## Salidas

- `docs/product/CID_BREAKDOWN_AUDIT.md` con estado actual, gaps y plan de cierre
- `directivas/cid_breakdown_audit.md` con reglas de auditoria y validacion

## Flujo de trabajo

1. Leer roadmap y auditorias relacionadas en `docs/product`
2. Auditar configuracion modular y feature flags (`modules.yml`, `plans.yml`)
3. Inventariar endpoints breakdown productores/consumidores
4. Clasificar ownership, auth, tenant, persistencia y enforcement
5. Auditar modelos y estrategia de persistencia (JSON blob vs tablas)
6. Auditar frontend actual y ausencia/presencia de pagina propia
7. Auditar cobertura de pruebas disponible
8. Definir contrato de `Breakdown vendible`
9. Construir tabla estado actual vs estado vendible
10. Proponer arquitectura de cierre y roadmap por commits
11. Ejecutar validaciones tecnicas de QA

## Validaciones

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m compileall src
python -m pytest tests/unit/ -q
python -m pytest tests/integration/test_project_script_analysis_flow.py -q
python -m pytest tests/integration/test_script_analysis_export.py -q
cd src_frontend && npm run build
git status --short
git diff --stat
```

## Casos borde

- Endpoints breakdown viven en `intake_routes.py`, por lo que ownership tecnico y comercial estan desacoplados
- Breakdown depende de salida de Script Analysis; cambios de schema en `breakdown_json` impactan Budget y modulos aguas abajo
- Existe `DepartmentLineItem`, pero el flujo actual no lo usa como base operativa de breakdown
- No hay tests dedicados de breakdown; regresiones pueden ocultarse tras tests de script analysis

## Restricciones conocidas

- Durante la auditoria no se modifica codigo funcional backend/frontend
- No se crean endpoints productivos ni cambios de schema en esta fase
- No se ejecutan renders reales ni llamadas a ComfyUI `/prompt`
- No se exponen secretos ni artefactos sensibles

## Errores aprendidos

- Asumir que un endpoint existente equivale a modulo vendible induce falsos GO comerciales
- Reusar JSON blob acelera MVP, pero sin contrato funcional y pruebas dedicadas aumenta deuda para escalado comercial
- Sin enforcement por modulo, la matriz de planes no se cumple de forma estricta

## Comandos seguros

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m compileall src
python -m pytest tests/integration/test_project_script_analysis_flow.py -q
python -m pytest tests/integration/test_script_analysis_export.py -q
cd src_frontend && npm run build
git status --short
```
