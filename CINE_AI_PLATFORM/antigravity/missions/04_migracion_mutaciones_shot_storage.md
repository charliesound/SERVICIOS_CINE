# Misión 04 — Migración de mutaciones de shot a Storage API (Hardened)

## Objetivo exacto
Migrar de forma segura la actualización de planos (Shots) desde el contrato legacy (`PUT /shots/{id}`) hacia el contrato oficial de la Storage API (`PATCH /api/storage/shot/{id}`), garantizando que los parámetros técnicos (seed, cfg, steps) se persistan correctamente mediante su normalización en el backend.

## Dependencia Backend Verificada
- **Endpoint**: `PATCH /api/storage/shot/{shot_id}` (Verificado en `storage_routes.py:601`).
- **Respuesta**: `{ "ok": true, "shot": {...} }` (Verificado en `storage_service.py:1124`).
- **Comportamiento**: Realiza un merge `{**shot, **payload}` seguido de `_normalize_shot`.

## Bloqueo Real Detectado
- **Pérdida de Datos**: El backend (`SQLiteShotsStore`) solo persiste columnas específicas. Campos como `seed`, `cfg`, `steps` y `workflow_key` enviados por el frontend son **descartados** porque no existen como columnas ni se mapean automáticamente a `render_inputs`.
- **Contrato Incompatible**: El frontend envía `refs`, el backend espera `references`.

## Alcance exacto por bloques

### Bloque A: Verificación y Desbloqueo Backend (Safe-Update)
1.  **Refactor de Normalización**: Modificar `StorageService._normalize_shot` para que detecte campos de generación en la raíz (`seed`, `cfg`, `steps`, `workflow_key`) y los mueva de forma segura al objeto `render_inputs`.
2.  **Mapeo de Referencias**: Asegurar que si el payload contiene `refs`, se mapee a `references` para cumplir con el esquema de base de datos.
3.  **Prueba Unitaria de Persistencia**: Verificar (vía script o log) que un `PATCH` parcial realmente actualiza el archivo `active-storage.json` / SQLite sin borrar el resto del objeto.

### Bloque B: Migración Frontend (Integration)
1.  **Actualización de `dashboardApi.ts`**:
    - Cambiar `updateLegacyShot` para usar `api.patch`.
    - Cambiar la ruta a `/api/storage/shot/${id}`.
2.  **Adaptación de Desestructuración**: Ajustar el retorno de la función para leer `response.data.shot`.
3.  **Limpieza Legacy**: Marcar o eliminar el endpoint `PUT /shots/{id}` si ya no tiene dependencias.

## Criterios de aceptación
- El monitor de red confirma llamadas exitosas a `PATCH /api/storage/shot/{id}`.
- Los valores técnicos (`seed`, `cfg`, `steps`) persisten tras un F5 (recarga de página) al leer desde el nuevo storage.
- No hay pérdida de atributos colaterales (ej. `title` no se borra al actualizar solo el `prompt`).

## Pruebas manuales
1. Cambiar el "Prompt" de un Shot y verificar que el cambio se guarda.
2. Cambiar el "Seed" y verificar en el archivo físico `active-storage.json` que el valor está dentro de `render_inputs`.

## Riesgos
- **Sobreescritura Destructiva**: Riesgo de que un `PATCH` parcial de un objeto anidado (ej. `metadata`) borre el contenido previo si no se realiza un merge profundo (deep merge).

## Bloque C: Rehidratación técnica del editor (Estrategia de Lectura)

### Estrategia Recomendada
**"Extended Summary List + Full Detail"**. 
Para minimizar cambios en la arquitectura de `App.tsx` (que carga todos los shots al inicio), ampliaremos la lista con los campos técnicos esenciales, pero reservaremos el objeto "crudo" completo para el endpoint de detalle.

### Endpoints exactos a tocar
1.  **GET `/api/storage/shots` (Lista extendida)**:
    - **Shape Mínimo**: `id, title, prompt, negative_prompt, status, scene_id, sequence_id, seed, cfg, steps, workflow_key, refs`.
    - **Razón**: Permite al dashboard rehidratar el editor inmediatamente al seleccionar un plano sin un fetch adicional por cada click.
2.  **GET `/api/storage/shot/{id}` (Detalle completo)**:
    - **Shape Completo**: Todo el objeto `shot` normalizado (incluyendo `metadata`, `render_inputs`, `layers`, `created_at`, etc.).
    - **Razón**: Proporciona acceso a logs técnicos complejos o metadatos de depuración si fuera necesario en el futuro.

### Criterios de aceptación
- El `GET /api/storage/shots` devuelve objetos que cumplen con la interfaz `Shot` de TypeScript (11 campos verificados).
- La UI del editor (`ShotBuilderPanel`) se autocompleta correctamente al cambiar de plano en la barra lateral.
- La recarga de la página (F5) no vacía los inputs del editor.
- No hay errores de "undefined" en los componentes que consumen la lista (DashboardCards).

### Pruebas manuales
1.  **Inspección de Red**: Abrir DevTools -> Network. Verificar que la respuesta de `shots` contiene `seed` y `cfg` como números (no nulos).
2.  **Prueba de Rehidratación**: Modificar un plano, guardar, recargar la página. Verificar que el plano seleccionado por defecto muestra su configuración guardada.

### Riesgos
- **Desincronización de Tipos**: Si el backend envía `null` donde el frontend espera `number` (corregido por la coerción del Bloque A).
- **Consumo de Memoria**: Aumentar el payload de la lista puede ralentizar el renderizado inicial si el número de planos supera los 1000 (no es el caso actual).
