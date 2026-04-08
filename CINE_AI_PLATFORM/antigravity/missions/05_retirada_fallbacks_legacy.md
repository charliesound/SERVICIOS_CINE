# Misión 05 — Retirada controlada de fallbacks legacy y cierre de lectura híbrida (Refined)

## Objetivo exacto
Consolidar la arquitectura "Storage-First" eliminando la lógica de recuperación (fallbacks) que revertía la lectura a endpoints legacy (`/projects`, `/scenes`) cuando la Storage API devolvía listas vacías.

## Alcance exacto
1.  **Frontend — Limpieza de `dashboardApi.ts`**:
    - Eliminar el bloque de lógica `if (projects.length === 0)` en `loadDashboardData`.
    - Eliminar tipos y constantes huérfanos que solo daban soporte a la lectura legacy (p. ej., llamadas directas a `/projects` o `/scenes`).
2.  **Backend — Marcado en `app.py`**:
    - Añadir el tag `LEGACY-DEPRECATED` a los routers de `projects` y `scenes` en la instancia de FastAPI a través de `app.include_router(..., tags=["LEGACY-DEPRECATED"])`.
3.  **Documentación de Estado**:
    - Declarar el comportamiento "Dashboard vacío" como estado esperado cuando no hay datos en el almacenamiento activo.

## No alcance
- **Mutación de Jobs**: No se toca la lógica de trabajos activos (`/jobs` se mantiene funcional pero intacto).
- **Backend Funcional**: No se toca `storage_service.py`, `storage_routes.py` ni la lógica de persistencia.
- **Rediseño UI**: No se alteran componentes visuales.

## Archivos a tocar
- `apps/api/src/app.py` (Marcado de rutas legacy).
- `apps/web/src/services/dashboardApi.ts` (Remoción de fallbacks y tipos).

## Criterios de aceptación
1.  La carga inicial del dashboard solo realiza peticiones a `/api/storage/*` y `/jobs`.
2.  No hay logs de error en la consola del navegador por tipos inexistentes o rutas fallidas.
3.  Si el almacenamiento oficial tiene datos, estos se muestran correctamente sin intentar cargar los antiguos.
4.  Si el almacenamiento oficial está vacío, el dashboard muestra el estado vacío correctamente.

## Pruebas manuales
1.  **Inspección de Tráfico**: Verificar en el Network Tab que no se llama a `GET /projects` ni `GET /scenes`.
2.  **Consistencia de Datos**: Confirmar que los nombres de los proyectos coinciden con el archivo `active-storage.json`.
3.  **Persistencia de Jobs**: Verificar que la lista de trabajos (si hay) sigue consultando `/jobs` con éxito (200 OK).

## Riesgos
- **UI Vacía**: Si el almacenamiento oficial no ha sido inicializado o importado, el dashboard aparecerá vacío. **Mitigación**: Se ha documentado como comportamiento esperado.

## Siguiente misión encadenada
- `06_crud_completo_proyectos_y_escenas.md` (Añadir capacidad de crear/borrar desde el frontend).
