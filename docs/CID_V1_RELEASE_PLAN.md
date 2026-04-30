# CID V1 Release Plan

## Visión

**CID V1** es una plataforma completa para acompañar un proyecto audiovisual desde el guion hasta la venta y la postproducción, con el flujo editorial ya validado.

## Sprint Recomendados

---

### SPRINT A — Product Dashboard Unificado

**Objetivo:** Dashboard mostrando estado del proyecto en todas las fases con accesos rápidos.

**Entregables:**
1. `DashboardPage.tsx` mejorado
2. Estado visual de cada módulo (Script, Budget, Funding, Storyboard, Editorial)
3. Accesos rápidos a módulos incompletos
4. Progreso百分比 del proyecto
5. Próximas acciones sugeridas

**Backend:**
- Crear `project_summary_service.py` (aggregación de estado)
- No nuevos modelos

**UI:**
- Modificar `Dashboard.tsx` existente
- No nueva ruta

**Riesgo:** Bajo
**Duración estimada:** 3 días

---

### SPRINT B — Budget Estimator desde Guion

**Objetivo:** Presupuesto automático generado desde análisis de guion.

**Entregables:**
1. Integración con `script_intake_service.py`
2. Partidas automáticas por género
3. UI de/edición de presupuesto
4. Export PDF/XLSX
5. Coste bajo/medio/alto

**Backend:**
- `budget_estimator_service.py` ya existe
- Extender para aceptar script_id
- Crear `budget_line` model (si es necesario)

**UI:**
- Nueva `BudgetPage.tsx` o integrar en `ProjectDetailPage.tsx`
-Tabla editable de partidas

**Riesgo:** Bajo (servicio ya existe)
**Duración estimada:** 5 días

---

### SPRINT C — Funding & Grants Assistant

**Objetivo:** Mejora del sistema de ayudas con scoring, checklists y alertas.

**Entregables:**
1. Scoring de encaje mejorado
2. Checklist documental por ayuda
3. Sistema de alertas de plazos
4. Historial de aplicaciones
5. Notificaciones

**Backend:**
- Extender `funding_matcher_service.py`
- Crear `grant_checklist_service.py`
- Crear `funding_alert_service.py`

**UI:**
- Extender `ProjectFundingPage.tsx`
- Nuevos filtros y scoring visual

**Riesgo:** Medio
**Duración estimada:** 7 días

---

### SPRINT D — Producer Pitch Pack

**Objetivo:** Dossier completo para productores.

**Entregables:**
1. Template de dossier мн др Producer
2. Logline editable
3. Sinopsis (larga/corta)
4. Nota de intención (director)
5. Presupuesto incluido
6. Storyboard preview
7. Mood board
8. Export PDF completo

**Backend:**
- Extender `project_document_service.py`
- Nuevos templates

**UI:**
- Nuevo tab en `ProjectDetailPage.tsx`

**Riesgo:** Bajo
**Duración estimada:** 5 días

---

### SPRINT E — Distribution Pack

**Objetivo:** Presentaciones para distribuidores, cines y plataformas.

**Entregables:**
1. Template de distribución
2. One-sheet generator
3. Email templates
4. Comparables database
5. Registro de envíos

**Backend:**
- Crear `distribution_service.py`
- Crear templates

**UI:**
- Nueva página o tabs en proyecto

**Riesgo:** Alto (nuevo flujo)
**Duración estimada:** 7 días

---

### SPRINT F — CRM Comercial

**Objetivo:** Gestión de contactos y oportunidades de venta.

**Entregables:**
1. Modelo de contactos
2. Catálogo de productoras
3. Catálogo de distribuidoras
4. Pipeline de ventas
5. Registro de comunicaciones
6. Estado de oportunidad

**Backend:**
- Crear `crm_service.py`
- Crear modelos

**UI:**
- Nueva página CRM
- Kanban de oportunidades

**Riesgo:** Alto (nuevo módulo)
**Duración estimada:** 10 días

---

### SPRINT G — UI Commercial Hardening

**Objetivo:** Mejora de UI para uso comercial y onboarding.

**Entregables:**
1. Navegación mejorada
2. Onboarding nuevos usuarios
3. Demo mode
4. Tutoriales
5. Documentación in-app

**UI:**
- Actualizar existentes

**Riesgo:** Bajo
**Duración estimada:** 5 días

---

### SPRINT H — Real Pilot

**Objetivo:** Prueba con proyecto/productor real.

**Entregables:**
1. Primer piloto real
2. Feedback collection
3. Correcciones críticas
4. Casos edge

**Riesgo:** Alto (depende de tercero)
**Duración estimada:** Variable

---

## Orden de Prioridad Recomendado

```
1. SPRINT A (Dashboard)
2. SPRINT B (Budget)
3. SPRINT D (Producer Pack)
4. SPRINT C (Funding)
5. SPRINT E (Distribution)
6. SPRINT F (CRM)
7. SPRINT G (UI Hardening)
8. SPRINT H (Real Pilot)
```

## Dependencias

- SPRINT B depende de SPRINT A (llama a script_analysis)
- SPRINT D depende de SPRINT B (incluye presupuesto)
- SPRINT E depende de SPRINT D (usa dossier producer)
- SPRINT F depende de SPRINT E (pipeline ventas)

## Exclusiones de V1

No incluir en V1:
- OTIO import/export
- EDL support
- DaVinci scripting
- VFX pipeline
- Blender/Houdini integration
- IA generativa de video
- Real-time collaboration

## Criterios de Release V1

1. Dashboard funcional
2. Flujo Script → Budget → Producer Pack completo
3. Funding search + scoring funcional
4. Editorial flow CLOSED
5. CRM básico operativo
6. npm build pasa
7. smoke tests pasan
8. No errores críticos en logs

## Riesgos已知

1. Módulos nuevos pueden romper flujo existente
2. Falta de feedback real de usuarios
3. UI dispersion (muchas páginas)
4. Datos de funding pueden estar desactualizados

---

## Recomendación Final

**Empezar por SPRINT A (Dashboard)** — Es el punto de entrada unificado y de bajo riesgo.

Este sprint:
- No modifica flujos existentes
- Unifica acceso a módulos
- Muestra estado del proyecto
- Accesos rápidos