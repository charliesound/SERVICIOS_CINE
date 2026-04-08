# Frontend Integration (Semantic Context)

La nueva RAG vectorial debe integrarse subrepticiamente en la interfaz de React actual, favoreciendo la asistencia al usuario mientras define parámetros o renderiza planos, sin ensuciar la visualización del tablero.

## 1. Auditoría y Ubicación Óptima
En base a la estructura de `apps/web/src/components`:
1. **El Motor de Búsqueda (Search):** Encaja orgánicamente dentro de `SequenceExecutionPanel.tsx` o `ShotBuilderPanel.tsx`. El director/editor consultará el contexto semántico mientras está decidiendo el *prompt* de un plano (Ej: "¿Cómo era el tono frío descrito en la escena 2?").
2. **El Formulario de Ingesta (Ingest):** Encaja perfecto como una pestaña o Pop-up discreto en `ProjectSettingsActionGroup.tsx` (Para Notas globales) o al lado de cada Shot/Scene en `SequenceExecutionPanel.tsx` (Para Notas al pie del director).

## 2. Desarrollo Propuesto (Minimal Changes)

### Servicios (Capa de Conexión)
Crear `src/services/semanticAPI.ts`:
- Emplea autenticación base (la misma del resto del backend).
- Expone `ingestNote(payload)` y `searchContext(query, project_id)`.

### Componentes de UI (Nuevos)
1. **`src/components/SemanticSearchPanel.tsx` (Buscador RAG)**
   - **Input:** `<input type="search">` estilizado con Lucide y Tailwind.
   - **Visualización:** Una lista vertical compacta de "Cards" que mapean la interfaz `{ score, payload: { content, entity_type } }`.
   - **Filtros Ocultos:** Automáticamente inyecta el `project_id` activo del tablero mediante Zustand o Props. Opcionalmente, un dropdown pequeño para filtrar por `entity_type` (ej. Notas de Escena vs Notas de Personaje).

2. **`src/components/SemanticIngestForm.tsx` (Captura)**
   - Un botón "+ Añadir Nota de Director" que expanda un `textarea` sencillo.
   - Un botón "Guardar" que dispare la alerta de éxito nativa del tablero.

### Inyección en Vistas (Modificaciones Menores)
- En `App.tsx` o el contenedor principal, añadir un atajo de teclado (ej. `Ctrl+K` o `Cmd+K`) para un modal global RAG, o simplemente un botón en el header del `ProjectCard`.

## 3. Experiencia de Usuario (UX)
- Al escribir en el Buscador, aparece un *spinner* sutil "Buscando en la memoria del proyecto...".
- Al devolver un resultado superior a ej. `0.75` de Cosine Similarity, el resultado aparece con un tag visual (Ej: `Plano / Continuidad`) facilitando que el usuario "copie al portapapeles" la nota de dirección y la pege en el Prompt de ComfyUI.
