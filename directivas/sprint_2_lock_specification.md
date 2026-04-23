# Sprint 2 Locking Specification: Narrative Ingestion

## 1. Objetivo del Sprint
Transformar AILinkCinema de una herramienta de generación aislada en un **Orquestador Narrativo**, permitiendo al usuario estructurar Proyectos cinematográficos en Secuencias, Escenas y Personajes con trazabilidad íntegra.

## 2. Alcance Exacto
### Entra:
- **Jerarquía de Datos:** Implementación de modelos `Project`, `Sequence`, `Scene` y `Character`.
- **Navegación Narrativa:** Flujo que obliga a estar dentro de una "Escena" para lanzar un "Job".
- **Character Hub:** Creación y persistencia de personajes vinculados a proyectos.
- **Ingesta Manual:** Formulario de creación de escenas con área de texto para el guion de la escena.
- **Relación Funcional:** Un Job ahora "pertenece" a una Escena específica.

### No Entra:
- **Parser de Guion Avanzado:** No se extraen metadatos automáticamente de un PDF.
- **Sequencer/Timeline:** No hay visualización de montaje ni timeline de vídeo.
- **Consistency Engine:** No hay lógica de LoRA automático por personaje (se queda en metadatos/seeds).

## 3. Vistas Finales
1.  **Project Selector:** (V1 ya existente, mejorada).
2.  **Project Overview (Dashboard de Proyecto):** Resumen de secuencias, estado de producción y personajes principales.
3.  **Narrative Explorer (Scenes List):** Vista de lista/grid de todas las escenas organizadas por secuencias.
4.  **Scene Workspace (Scene Detail):** Espacio de trabajo de la escena (Script, Personajes presentes, Historial de Renders/Jobs).
5.  **Character Gallery (Characters List):** Directorio de personajes del proyecto.
6.  **Character Sheet (Character Detail Base):** Ficha técnica con descripción, rasgos y "Consistency Seed".

## 4. Acciones del Usuario por Vista
- **Project Overview:** Ver progreso general (%) y accesos rápidos a personajes.
- **Narrative Explorer:** Añadir/Eliminar escenas, reordenar (básico), ver mini-estado de cada escena.
- **Scene Workspace:** Editar guion de la escena, vincular personajes, lanzar Renders (Jobs) directamente asociados a esta escena.
- **Character Hub:** Crear nuevo personaje, definir prompt base visual del personaje.

## 5. Datos Demo Obligatorios
Para validar el sprint, debe existir una "Película Demo" (ej: *The Robot's Journey*) con:
- Al menos 2 Secuencias.
- 4 Escenas (con guiones cortos reales).
- 2 Personajes recurrentes con sus descripciones visuales.

## 6. Placeholders Permitidos
- Botón de "Auto-Parse Script from PDF" (Deshabilitado, con tooltip "Coming in S4").
- Sección de "Scene Cost Analytics" (Visual solo, sin lógica real de coste monetario aún).
- Gráfico de "Continuity Check" (UI solo).

## 7. Criterios de Terminado (DoD)
- [ ] La base de datos soporta la jerarquía completa.
- [ ] Es imposible crear un "Job" que no esté vinculado a una "Escena".
- [ ] El Sidebar cambia dinámicamente al entrar en un Proyecto (Project context).
- [ ] El portal de cliente muestra los resultados agrupados por Escena.
- [ ] Demo Interna funcional: "Navegar de Proyecto a una Escena y lanzar un render que aparezca en el historial de esa escena".

## 8. Exclusiones
- Edición de guion en tiempo real (colaborativa tipo Google Docs).
- Importación de archivos .fountain o Final Draft.
- Generación de escenas completas (solo jobs individuales dentro de la escena).

## 10. Decisiones Congeladas tras Sprint 2
1.  **Jerarquía SSS:** Se bloquea el modelo *Sequence -> Scene -> Shot/Job* como el estándar del pipeline.
2.  **Project Centricity:** A partir de aquí, el sistema es 100% "Project-First". No se permiten acciones huérfanas de proyecto.
3.  **Character Mapping:** Los personajes se definen a nivel de Proyecto, no globales de usuario.
