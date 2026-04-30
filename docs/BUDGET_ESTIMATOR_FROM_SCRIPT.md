# Budget Estimator from Script

## Overview

El Budget Estimator genera presupuestos orientativos automáticamente desde el guion o proyecto. Es una herramienta de estimación, NO un presupuesto definitivo.

## Características

### Entradas
- Guion (texto)
- Proyecto existente (script en Project o ScriptVersion)
- Breakdown (ProductionBreakdown)

### Niveles de Presupuesto
- **low** (conservador): tarifas mínimas × 0.7
- **medium**: tarifas base
- **high**: tarifas elevadas × 1.4

### Salidas
- Presupuesto con total_min, total_estimated, total_max
- Contingencia (% según nivel)
- Líneas de presupuesto por categoría
- Role summaries

## Categorías de Presupuesto

| Categoría | Descripción |
|----------|------------|
| desarrollo | Desarrollo y derechos |
| preproducción | Locaciones, diseño arte |
| producción | Producción por jornada |
| dirección | Director, ayte. dirección |
| reparto | Actores, figuración |
| equipo_técnico | DOP, gaffer |
| cámara | Cámara, grip |
| sonido | Sonido |
| arte | Escenografía |
| vestuario | Vestuario actores |
| maquillaje | Maquillaje |
| localizaciones | Tasas ubicación |
| transporte | Furgonetas |
| alojamiento_dietas | Hotel + manutención |
| seguros_permisos | Seguro, permisos |
| postproducción_imagen | Edición, color |
| postproducción_sonido | Edición sonido, mezcla |
| música | Banda sonora |
| vfx_ia | VFX |
| marketing | Material promocional |
| distribución | Festivales |
| contingencia | Contingencia |

## API Endpoints

```
GET  /api/projects/{project_id}/budgets              List budgets
POST /api/projects/{project_id}/budgets/generate    Generate new budget
GET  /api/projects/{project_id}/budgets/active   Get active budget
GET  /api/projects/{project_id}/budgets/{id}     Get specific budget
POST /api/projects/{project_id}/budgets/{id}/activate
POST /api/projects/{project_id}/budgets/{id}/recalculate
POST /api/projects/{project_id}/budgets/{id}/archive
GET  /api/projects/{project_id}/budgets/{id}/export/json
GET  /api/projects/{project_id}/budgets/{id}/export/csv
```

## Integración Dashboard

El dashboard muestra:
- **Sin presupuesto**: status "missing", action "Generar presupuesto estimado"
- **Con presupuesto**: status "ready", total_estimated

## Role Summaries

### Producer
- riesgo_financiero
- partidas_grandes
- advertencias

### Production Manager
- jornadas_estimadas
- localizaciones
- necesidades_operativas

### Director
- impacto_creativo
- secuencias_costosas
- necesidades_visuales

### Editor
- postproducción_imagen
- postproducción_sonido
- vfx_ia
- coste_finishing

### Viewer
- Solo lectura

## Aviso Legal

> Esta es una estimación orientativa generada automáticamente. Las tarifas son reglas internas-heurísticas, NO tarifas oficiales. Validar con producción real antes de usar.

## Limitaciones

- No es presupuesto definitivo
- No substituye al jefe de producción
- Tarifas orientativas, no oficiales
- No incluye financiación/subvenciones
- No incluye CRM

## Archivos Creados

- `/src/models/budget_estimator.py` - Modelos
- `/src/services/budget_rules.py` - Reglas
- `/src/services/budget_estimator_service.py` - Servicio
- `/src/routes/budget_routes.py` - Endpoints
- `/src_frontend/src/api/budget.ts` - API frontend
- `/src_frontend/src/pages/BudgetEstimatorPage.tsx` - UI