# Misión 03 — Migración del frontend a la Storage API (Corregida)

## Objetivo exacto
Migrar de forma segura y verificada el flujo de **lectura** de datos del frontend (`apps/web`) desde los endpoints legacy de dominio hacia los endpoints unificados de la Storage API, eliminando redundancias y garantizando que el dashboard refleje el estado real de `active-storage.json`.

## Problema actual a resolver
El frontend (`dashboardApi.ts`) mantiene una lógica híbrida compleja: intenta cargar desde `/api/storage/project` pero tiene "fallbacks" a `/projects` (legacy) y usa siempre `/characters`, `/shots` y `/jobs` desde las rutas antiguas. Esto genera confusión sobre qué datos son reales y cuáles son mockeados o residuales.

## Alcance exacto
1.  **Mapeo de Lectura (Bloque 1)**:
    - Sustituir `GET /characters` (Legacy) por `GET /api/storage/characters` (Verified).
    - Sustituir `GET /shots` (Legacy) por `GET /api/storage/shots` (Verified).
2.  **Ajuste de Shape de Respuesta**: Adaptar la lógica de `loadDashboardData` para desestructurar correctamente `{ ok, characters, count }` y `{ ok, shots, count }`.
3.  **Eliminación de Fallbacks**: Una vez verificado el Bloque 1, eliminar el bloque `if (projects.length === 0)` que vuelve a intentar rutas legacy.
4.  **Consolidación de Project/Scenes**: Refinar `loadProjectAndScenesFromStorage` para asegurar que el mapeo de `StorageProject` a `Project` sea robusto.

## No alcance
1.  **Migración de Escritura (Bloque 2)**: No se toca `updateLegacyShot` todavía, ya que requiere validar el contrato `PATCH /api/storage/shot` en el backend.
2.  **Migración de Jobs**: Se mantiene en `/jobs` (Legacy) por ahora.
3.  **Cambios en UI**: La interfaz no debe cambiar de apariencia ni comportamiento.

## Archivos frontend a tocar
- `apps/web/src/services/dashboardApi.ts` (Principalmente `loadDashboardData`).

## Dependencias Backend Verificadas (Endpoints reales en `storage_routes.py`)
- `GET /api/storage/project` -> Retorna `{ ok: true, project: {...} }`
- `GET /api/storage/project/{id}/scenes` -> Retorna `{ ok: true, scenes: [...] }`
- `GET /api/storage/characters` -> Retorna `{ ok: true, characters: [...] }`
- `GET /api/storage/shots` -> Retorna `{ ok: true, shots: [...] }`

## Bloque 1 Seguro de Migración (Lectura)
1.  Actualizar los fetches de `characters` y `shots` dentro de `loadDashboardData`.
2.  Extraer los arrays desde la propiedad correspondiente (`response.data.characters` / `response.data.shots`).
3.  Verificar que el dashboard carga los íconos de personajes y la lista de planos correctamente.

## Criterios de aceptación
1.  `loadDashboardData` no realiza llamadas a `/characters` ni `/shots` (Legacy) en el Network tab.
2.  El frontend carga correctamente el proyecto activo definido en `active-storage.json`.
3.  No hay errores de consola por desestructuración de objetos inexistentes.

## Riesgos
- **Shape Incompatible**: Si `StorageService` devuelve campos con nombres distintos a lo que espera la interfaz (ej. `name` vs `title`), el mapeo fallará.
- **IDs Duplicados**: El frontend debe manejar correctamente los IDs normalizados por el backend.

## Siguiente misión encadenada
- `04_migracion_escritura_storage.md` (Validación de contratos `PATCH` y migración de `updateShot`).