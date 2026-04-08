# Misión 01 — Unificación controlada del backend oficial

## Objetivo exacto
Consolidar `apps/api/src/app.py` como el backend oficial del proyecto sin eliminar de forma agresiva `apps/api/src/main.py` ni las rutas legacy. Se busca asegurar la operatividad del frontend actual mientras se establece una única base de código para el desarrollo futuro.

## Problema actual a resolver
1.  **Entrypoints duplicados**: Coexistencia de `main.py` y `app.py` con lógicas de enrutamiento y configuración divergentes.
2.  **Desalineación Frontend-Backend**: El frontend actual (`apps/web`) consume rutas legacy (`/projects`, `/scenes`, `/shots`, `/jobs`) que solo están completamente habilitadas en `main.py`.
3.  **Inconsistencia de Configuración**: `app.py` usa `src.settings`, mientras que `main.py` usa hardcoding para CORS (`localhost:5173`) y no soporta el patrón de almacenamiento unificado.

## Alcance exacto
1.  **Declaración de Backend Maestro**: Configurar `apps/api/src/app.py` como el punto de entrada definitivo.
2.  **Capa de Compatibilidad**: Importar los routers legacy (`src.routes.projects`, `src.routes.scenes`, `src.routes.jobs`) en `app.py` para evitar roturas en `apps/web`.
3.  **Transformación de `main.py`**: Convertir `main.py` en un wrapper mínimo que importe el objeto `app` de `app.py`, garantizando que cualquier arranque accidental desde `main.py` ejecute la lógica unificada.
4.  **Etiquetado en OpenAPI**: Marcar los routers legacy con el tag `LEGACY-DEPRECATED` para visibilidad en `/docs`.
5.  **Unificación de CORS**: Asegurar que las políticas de CORS en `app.py` cubren las necesidades del frontend detectadas en `main.py`.

## No alcance
1.  **Eliminación de archivos de ruta**: `projects.py`, `scenes.py`, etc., permanecen en el disco.
2.  **Migración de lógica Frontend**: No se altera `App.tsx` para usar `/api/storage`.
3.  **Cambio de Base de Datos**: No se migra la lógica de los mocks legacy a la base de datos real en esta fase.

## Archivos a tocar
- `apps/api/src/app.py` (Inclusión de routers legacy y logs de arranque).
- `apps/api/src/main.py` (Reducción a wrapper de `app.py`).
- `apps/api/README.md` (Actualización de instrucciones de arranque).
- `CINE AI PLATFORM — GUÍA COMPLETA...` (Documentar el cambio).

## Decisiones de arquitectura permitidas
- **Inclusión de Routers Legacy**: Se permite importar routers que no sigan el patrón de factoría actual en `app.py` como medida de transición.
- **Shadowing de Entrypoint**: `main.py` puede sobrevivir como alias de `app.py`.

## Decisiones no permitidas
- **Borrado de endpoints activos**: No se permite quitar ninguna ruta que devuelva 200/201 actualmente en `main.py`.
- **Modificación de la lógica de `StorageService`**.

## Criterios de aceptación
1.  `python -m src.app` (o comando oficial) expone tanto `/api/storage` como `/projects`.
2.  El frontend (`apps/web/src/App.tsx`) carga los datos correctamente al conectarse al backend oficial.
3.  `main.py` ya no contiene lógica propia de FastAPI, sino que delega en `app.py`.
4.  `/docs` muestra la jerarquía completa (Oficial + Legacy).

## Pruebas manuales mínimas
1. Arrancar `app.py` y verificar en el navegador que el frontend lista los proyectos demo.
2. Verificar que `GET /projects` devuelve datos válidos desde el puerto de `app.py`.
3. Verificar que `GET /api/storage/summary` sigue funcionando.

## Riesgos
- **Importaciones Circulares**: Riesgo al referenciar `app.py` desde `main.py` si no se estructura correctamente.
- **Mismatch de Puertos**: Asegurar que los scripts de arranque del frontend no apunten a un puerto que quede desactivado.

## Siguiente misión encadenada
- `02_limpieza_repo_y_endurecimiento_base.md` (Eliminación progresiva de legacy).