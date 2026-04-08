# Misión 06 — Estado vacío explícito y cierre UX de carga

## Objetivo exacto
Implementar una gestión de estados en la UI (`Loading`, `Empty`, `Error`) que sea coherente con la arquitectura Storage-first, evitando que el usuario se quede bloqueado en un mensaje de "Cargando..." si el almacenamiento está vacío.

## Problema actual a resolver
En `App.tsx`, la condición de renderización solo diferencia entre `error` y `projects.length === 0`. Como el estado inicial de `projects` es `[]`, la app muestra "Cargando datos..." perpétuamente si la API de Storage no devuelve ningún proyecto, impidiendo saber si la carga falló, si está en curso o si simplemente no hay datos.

## Alcance exacto
1.  **Frontend — Gestión de Estado en `App.tsx`**:
    - Introducir un estado explícito `isLoading` (iniciado en `true`).
    - Asegurar que `setLoading(false)` se ejecute siempre al finalizar la petición (éxito o error).
2.  **Frontend — Definición de Bloques de Renderizado**:
    - **Cargando**: Spinner o mensaje temporal mientras `isLoading` es `true`.
    - **Error**: Mensaje descriptivo si la API falla.
    - **Estado Vacío**: Mensaje claro indicando "No hay un proyecto activo en el almacenamiento oficial" cuando la carga termina pero no hay datos.
    - **Dashboard**: Renderizado normal cuando hay al menos un proyecto.

## No alcance
- **Migración de /jobs**: Sigue legacy y fuera de esta misión.
- **Rediseño visual profundo**: Se mantienen los estilos actuales, solo se mejora la lógica de flujo.
- **Funcionalidades de Importación/Creación**: No se añaden botones nuevos, solo se mejora el feedback al usuario.

## Archivos a tocar
- `apps/web/src/App.tsx` (Lógica de estados y renderizado condicional).

## Comportamiento esperado
| Situación | Comportamiento |
| :--- | :--- |
| **Inicio de App** | Muestra "Cargando datos de cine..." |
| **Storage con datos** | Muestra el Dashboard normalmente. |
| **Storage vacío** | Muestra "Aún no tienes proyectos en el almacenamiento oficial." |
| **API Backend caída** | Muestra "Error de conexión con el servidor oficial." |

## Criterios de aceptación
1.  Al abrir la app con el backend detenido, se muestra el mensaje de Error.
2.  Al abrir la app con el backend activo pero el `active-storage.json` vacío, se muestra el mensaje de "Estado Vacío" (no el de "Cargando").
3.  La app ya no muestra "Cargando..." durante más tiempo del estrictamente necesario para el fetch.

## Pruebas manuales mínimas
1. Simular storage vacío (borrando `active-storage.json`) y verificar el mensaje.
2. Simular error de red (deteniendo `app.py`) y verificar el mensaje de error.
3. Verificar que al cargar un proyecto válido, el dashboard aparece correctamente.

## Riesgos
- **Confusión de UX**: Si el mensaje de estado vacío no es claro, el usuario puede pensar que perdió sus datos. **Mitigación**: El mensaje debe ser explícito sobre el "Almacenamiento Oficial (Storage API)".

## Siguiente misión encadenada
- `07_import_ui_simplificada.md` (Añadir un botón simple para disparar el import de JSON desde la UI).
