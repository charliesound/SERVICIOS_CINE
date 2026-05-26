# Auditoría End-to-End del Flujo Storyboard
**Fecha:** 2026-05-26  
**Rol:** Principal Product Engineer + UX Architect (AILinkCinema/CID)

---

## 1. Estado Actual del Flujo y Hallazgos de la Auditoría

### A. Qué Funciona Correctamente (GO)
1. **Ciclo Visual (Renders y Vinculaciones):**
   - El test de humo `smoke_storyboard_visual_cycle.sh` pasa al 100%. Esto confirma que los schemas de comunicación (`shot_schema.py`), la persistencia de metadatos de render y estados (`render_status`), y los badges del frontend en `ShotCard.tsx` están alineados estructuralmente.
2. **Optimización de Miniaturas:**
   - La directiva de optimización de miniaturas (`ui_thumbnail_optimization.md`) se encuentra correctamente implementada. Las imágenes se sirven de forma autenticada (tenant-safe) a través de `/shots/{shot_id}/thumbnail` y `/shots/{shot_id}/image`.
3. **Desglose de Escenas en Detalles de Proyecto:**
   - El test de humo `smoke_scene_breakdown_ux.sh` pasa al 100%. Esto asegura que la paginación y límites de visualización de escenas en la página de detalle del proyecto (`ProjectDetailPage.tsx`) y el modal de selección funcionan de manera fluida y scrollable.

### B. Qué Falla o Presenta Huecos Críticos (Gaps)

#### 1. Incoherencias en Frontend frente a Tests de Humo de UX (Crítico para Demo)
El test `smoke_storyboard_sequence_selection_ux.sh` falla con **6 errores** debido a discrepancias en `StoryboardBuilderPage.tsx`:
- **Modal no integrado:** El componente `StoryboardSequenceSelectorModal` está importado en la página de detalles del proyecto, pero **no se usa ni se importa en la página del Storyboard Builder**.
- **Botón y Handler Ausentes:** Faltan los botones de `"Seleccionar secuencia"`, `"Planificar storyboard"`, y el handler `handlePlanSequenceFromList` (que debería llamar al endpoint `/plan` de la secuencia).
- **Textos de UI Incompletos:** Falta renderizar el contador de `"secuencias disponibles"`, el bloque `"Secuencia seleccionada:"` y el helper `dedupeList` dentro de la página del Builder.

#### 2. Confusión Escena vs. Secuencia en Visualizaciones
- **Etiqutas Fijas:** El visualizador del storyboard (filmstrip y grid) y las tarjetas del ShotCard usan fijamente la palabra "Escena" (`Escena: {shot.scene_number}`). Si el guion utiliza secuencias en lugar de escenas (analizado mediante cabeceras `SEC` / `SECUENCIA`), esto resulta confuso e incorrecto para el usuario. El backend sí detecta y almacena `sequence_label` en los metadatos del plano, pero el frontend los ignora.

#### 3. Exposición de Rutas Internas del Servidor (Brecha de Seguridad)
- **Ruta Física en JSON:** En el endpoint `/api/projects/{project_id}/storyboard/sheet`, el backend retorna un campo `artifact_path` que expone la ruta física absoluta en el servidor (p. ej., `/opt/SERVICIOS_CINE/exports/...`). Aunque no se visualiza en la interfaz, se filtra en la respuesta del API.

#### 4. Vulnerabilidad de Timeout en Generación y Auto-export
- **Proceso Síncrono:** La generación de la hoja de storyboard (PDF/PNG) durante el auto-export se ejecuta de manera síncrona en la misma petición de generación del storyboard. Si la secuencia tiene muchos planos, la petición puede expirar antes de que se complete el renderizado y la exportación de páginas.

---

## 2. Pantallas y Endpoints Afectados

### Pantallas Afectadas
1. **`StoryboardBuilderPage.tsx`:** Requiere la integración del modal de selección, botones de planificación, estados de secuencia seleccionada y adaptabilidad de etiquetas (Escena vs. Secuencia).
2. **`ShotCard.tsx`:** Requiere ajustar la visualización de la etiqueta de forma dinámica (mostrar "Secuencia" o "Escena" según la procedencia del guion).
3. **`StoryboardSequenceSelectorModal.tsx`:** Ajustar la visualización del scroll y etiquetas de secuencia.

### Endpoints Afectados
1. **`GET /api/projects/{project_id}/storyboard`:** Debe asegurar el paso correcto del `sequence_label` en el payload de shots.
2. **`POST /api/projects/{project_id}/storyboard/sheet`:** Limpiar o sanitizar el campo `artifact_path` para que no contenga rutas internas.
3. **`POST /api/projects/{project_id}/storyboard/generate`:** Adaptar `_generate_auto_exports` para ser resiliente a timeouts o asíncrono.

---

## 3. Prioridad por Impacto en Demo y Quick Wins

| Impacto | Tarea / Corrección | Componente | Tipo |
| :--- | :--- | :--- | :--- |
| **Alta** | Integrar `StoryboardSequenceSelectorModal` y handlers en `StoryboardBuilderPage.tsx` para pasar el smoke test de UX. | Frontend | Corrección / Gap |
| **Alta** | Ajustar textos de "Escena" a "Secuencia" en visualizadores de planos si se detecta guion por secuencias. | Frontend | UX / Terminología |
| **Media** | Sanitizar las respuestas de exportación de storyboard sheets para remover la ruta física del servidor. | Backend | Seguridad |
| **Baja** | Convertir el auto-export síncrono del endpoint `/generate` en una tarea asíncrona. | Backend | Optimización |

### Quick Wins (Victorias rápidas)
1. Implementar los botones, estados y el helper `dedupeList` en `StoryboardBuilderPage.tsx` para pasar los checks de humo.
2. Leer `shot.metadata_json.sequence_label` en frontend y cambiar la etiqueta "Escena" por el label dinámico de la secuencia.
3. Modificar la respuesta del endpoint de exportación de hojas de storyboard para que devuelva solo URLs seguras.

---

## 4. Plan de Implementación por Fases (STORYBOARD.UX.2)

### Fase 1: Alineación de Tests de Humo de UX (Frontend)
- Importar `StoryboardSequenceSelectorModal` en `StoryboardBuilderPage.tsx`.
- Definir la función `dedupeList` y el handler `handlePlanSequenceFromList` que actualiza el estado de planificación (`shotPlan`).
- Añadir los elementos visuales requeridos por el script de humo:
  - Botón `"Seleccionar secuencia"`.
  - Botón `"Planificar storyboard"`.
  - Texto `"secuencias disponibles"`.
  - Bloque `"Secuencia seleccionada:"`.
- Validar el paso completo de `smoke_storyboard_sequence_selection_ux.sh`.

### Fase 2: Flexibilidad de Nomenclatura (Escena vs. Secuencia)
- En `StoryboardBuilderPage.tsx` (modos filmstrip y grid) y `ShotCard.tsx`, modificar la visualización para evaluar si existe `shot.metadata_json.sequence_label` (ej. "Sec 1").
- De ser así, mostrar `"Secuencia: {label}"` en lugar de `"Escena: {scene_number}"`.

### Fase 3: Seguridad y Robustez de Exportación
- Modificar `storyboard_presentation_routes.py` para evitar retornar `artifact_path` absoluto del sistema de archivos, o transformarlo en una ruta relativa antes de enviarlo al cliente.
- Agregar control de timeouts o warning de límite de páginas al auto-exportar.

---

## 5. Recomendación de GO/NO-GO

### **Dictamen:** **GO (Con Condición)**

El backend del ciclo visual y el desglose de escenas son estables y pasan sus smoke tests correspondientes. El único impedimento real es el desalineamiento del Builder de Storyboard frente al test de humo de la selección de secuencias de la UI, y la rigidez en la nomenclatura escena/secuencia.

**Condición para STORYBOARD.UX.2:**
La fase de desarrollo de STORYBOARD.UX.2 debe comenzar inmediatamente con la **Fase 1** para estabilizar la UI y asegurar que los tests de humo pasen en verde, seguido de la adaptación dinámica de secuencias antes de lanzar la demo del producto.
