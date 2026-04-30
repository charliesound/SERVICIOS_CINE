# CID User Flows

## FLOW 1 — Del Guion al Dossier de Productor

### Descripción
Usuario crea proyecto, sube guion, genera análisis, desglose, presupuesto, storyboard y dossier para productores.

### Pasos

1. **Crear Proyecto**
   - Ruta: `/create` o `/projects/new`
   - UI: `NewProjectPage.tsx`
   - Input: Nombre proyecto, tipo (largometraje, documental, etc.)

2. **Subir/Pegar Guion**
   - Ruta: `/projects/{id}/script`
   - UI: `ProjectDetailPage.tsx` (tab script)
   - Input: Archivo (PDF/DOCX/TXT) o texto directo
   - Backend: `script_intake_service.py`

3. **Analizar Guion**
   - Automático tras upload
   - Extrae: escenas, personajes, localizaciones, tono
   - Guardado en: Script entity

4. **Generar Desglose** (FUTURO)
   - UI: `ProductionBreakdownPage.tsx` (NO EXISTE)
   - Extrae requisitos por escena
   - Localizaciones, personajes, VFX, sonido

5. **Generar Presupuesto Estimado**
   - Ruta: `/projects/{id}/budget`
   - UI: `BudgetEstimatorPage.tsx` (NO EXISTE pero API existe)
   - Backend: `budget_estimator_service.py`
   - Output: Partidas, coste bajo/medio/alto

6. **Generar Storyboard**
   - Ruta: `/projects/{id}/storyboard`
   - UI: `StoryboardBuilderPage.tsx`
   - Backend: `storyboard_service.py`
   - Output: Frames visuales

7. **Generar Dossier Productor**
   - Ruta: `/projects/{id}/export/dossier`
   - Backend: `project_document_service.py`
   - Output: PDF con logline, sinopsis, presupuesto, storyboard

8. **Exportar**
   -Formats: PDF, ZIP
   - Incluye: todo lo generado

### Estado
- Pasos 1-3: PARTIAL
- Pasos 4-5: MISSING/EXISTS
- Pasos 6-8: PARTIAL

---

## FLOW 2 — Del Guion a las Ayudas

### Descripción
Usuario busca ayudas/subvenciones que encajan con su proyecto y genera documentación.

### Pasos

1. **Analizar Proyecto**
   - Extrae perfil del proyecto (género, duración, equipo, localizaciones)
   - Backend: `script_intake_service.py`

2. **Extraer Perfil**
   - Género, duración estimada, presupuesto, territorio

3. **Buscar Ayudas**
   - Ruta: `/funding`
   - UI: `ProjectFundingPage.tsx`
   - Backend: `funding_catalog_routes.py`
   - Input: Filtros (año, territorio, género)

4. **Clasificar Oportunidades**
   - Por encaje (match score)
   - Por plazo (fecha límite)
   - Por requisitos

5. **Recomendar Ayudas**
   - Algoritmo simple de matching
   - Muestra las mejores 5-10

6. **Generar Checklist Documental**
   - ¿Qué documentos necesito?
   - Estado: pendiente/completo

7. **Guardar Oportunidad**
   - Favoritos o aplicar
   - Estado: guardada/aplicada

8. **Crear Tarea/Alerta**
   - Notificación de fecha límite

### Estado
- Pasos 1-3: PARTIAL
- Pasos 4-8: STUB/MISSING

---

## FLOW 3 — Del Guion a Distribuidoras

### Descripción
Usuario crea pitch comercial para distribuidores y gestiona oportunidades de venta.

### Pasos

1. **Crear Pitch Comercial**
   - Logline actualizada
   - Sinopsis (100 palabras)
   - Target audience
   - Comparables (películas similares)

2. **Generar Comparables**
   - Películas del mismo género
   - Mismo territorio
   - Resultados de box office

3. **Definir Target**
   - Territorios objetivo
   - Distribuidoras target
   - Estrategias de estreno

4. **Generar Presentación**
   - One-sheet
   - Deck de distribución (NO EXISTE)
   - Email template

5. **Seleccionar Distribuidoras**
   - De catálogo o CRM
   - Priorizar

6. **Registrar Envío**
   - Fecha de envío
   - Método (email, portal)
   - Estado: enviado/pendiente

7. **Seguimiento CRM**
   - Registrar跟进
   - Actualizar estado
   - Notas

### Estado
- Todos los pasos: MISSING (excepto CRM parcial)

---

## FLOW 4 — Del Proyecto a Cines/Plataformas

### Descripción
Usuario crea propuestas para exhibidores y plataformas de streaming.

### Pasos

1. **Crear Propuesta de Exhibición**
   - Argumento comercial
   - Público objetivo
   - Estrategia de lanzamiento

2. **Crear One-Sheet**
   - Poster oficial
   - Sinopsis corta
   - Datos técnicos

3. **Crear Argumento Comercial**
   - Por qué ver esta película
   - Audiencia objetivo
   - Comparables

4. **Generar Email**
   - Template para cines
   - Template para plataformas

5. **Guardar Contacto**
   - Cine o plataforma
   - Datos de contacto

6. **Registrar Estado de Venta**
   - Negociación
   - Contrato
   - Pases

### Estado
- Todos los pasos: MISSING

---

## FLOW 5 — De Rodaje a DaVinci

### Descripción
Flujo confirmado de postproducción editorial.

### Pasos

1. **Media Ya Ingurada**
   - DaVinci/DIT ingestó material
   - Archivos en ruta existente

2. **CID Escanea Media**
   - Ruta: `/ingest/scans`
   - UI: `IngestScansPage.tsx`
   - Backend: `ingest_scan_service.py`
   - NO mueve, NO copia, NO renombra

3. **CID Ingiera Reports**
   - Camera reports, sound reports
   - Script notes, director notes
   - UI: `DocumentsPage.tsx` / `ReportsPage.tsx`

4. **CID Reconcilia**
   -link cámara con audio
   - Dual-system
   - Backend: `editorial_reconciliation_service.py`

5. **CID Recomienda Tomas**
   - Scoring automático
   - Considera circled, metadata
   - Backend: `take_scoring_service.py`

6. **CID Genera AssemblyCut**
   - Timeline propuesto
   - Backend: `assembly_service.py`

7. **CID Exporta FCPXML**
   - Conservador (safe)
   - Experimental (linked audio)
   - Multiplataforma (Windows/macOS/Linux)
   - Backend: `fcpxml_export_service.py`

### Estado
- Todos los pasos: CLOSED/VALIDATED

---

## FLOW 6 — Product Dashboard (FUTURO)

### Descripción
Dashboard unificado mostrando estado del proyecto.

### Componentes

1. **Header**
   - Nombre del proyecto
   - Fase actual
   - Progreso

2. **Módulos**
   - Script Intelligence (✓/✗)
   - Budget (✓/✗)
   - Funding (n oportunidades)
   - Storyboard (n frames)
   - Editorial (✓/✗)

3. **Accesos Rápidos**
   - Continuar donde stopped
   - Próximas acciones
   - Alertas

4. **Metrics**
   - Días desde creación
   - Presupuesto estimado
   - Oportunidades abiertas

### Estado
- MISSING - Necesita desarrollo

---

## Resumen de Estado por Flow

| Flow | Estado | Gap Principal |
|------|--------|-------------|
| 1. Guion → Dossier | PARTIAL | Desglose, UI completa |
| 2. Guion → Ayudas | PARTIAL | Scoring, alertas |
| 3. Guion → Distribuidora | MISSING | Todo |
| 4. Cines/Plataformas | MISSING | Todo |
| 5. Rodaje → DaVinci | CLOSED | — |
| 6. Dashboard | MISSING | Todo |