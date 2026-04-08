# Misión 02 — Limpieza del repo y endurecimiento de la base (Refinada)

## Objetivo exacto
Establecer una base de repositorio profesional, segura y reproducible en CINE_AI_PLATFORM sin alterar la lógica de negocio ni los contratos API. El foco es la higiene del control de versiones y la estandarización de la configuración inicial.

## Problema actual a resolver
1.  **`.gitignore` inconsistente**: El archivo actual contiene residuos de comandos PowerShell y no cubre adecuadamente la estructura de monorepo (Python/React).
2.  **Exposición de secretos y falta de plantillas**: Ausencia de archivos `.env.example`, lo que dificulta el setup limpio sin comprometer credenciales reales.
3.  **Ruido de sistema y build**: Acumulación de artefactos generados (`dist`, `__pycache__`, `.venv`, `node_modules`) que oscurecen el foco del código fuente.
4.  **Falta de justificación de exclusiones**: Necesidad de documentar por qué ciertos activos (como outputs de storage) deben estar fuera del control de versiones.

## Alcance exacto
1.  **Saneamiento de `.gitignore`**: Limpieza del archivo raíz para excluir correctamente:
    - Artefactos Python: `__pycache__`, `*.pyc`, `.venv`, `.pytest_cache`.
    - Artefactos Frontend: `node_modules`, `dist`, `.next` (si existiera), `.eslintcache`.
    - Secretos: `.env`, `.env.local`, `.env.*.local`.
    - Datos generados: `*.sqlite`, `active-storage.json`.
2.  **Creación de `.env.example`**: Generar plantillas de configuración para `apps/api` y `apps/web` con valores por defecto seguros.
3.  **Higiene de Secretos**: Identificar de forma explícita qué archivos `.env` reales deben ser ignorados por seguridad.
4.  **Justificación de Exclusión de Almacenamiento**:
    - `storage/outputs/*` y `storage/thumbs/*`: Se excluyen por ser **artefactos generados** en tiempo de render. No forman parte del código fuente.
    - `storage/assets/*`: Se excluyen por ser **activos binarios pesados** que deben gestionarse fuera de Git (o como LFS, pero en este caso se decide exclusión por simplicidad de desarrollo inicial).
5.  **Identificación de Sobrantes**: Documentar archivos residuales (ej. `package-lock.json` en carpetas Python) sin borrarlos agresivamente.

## No alcance
1.  **Modificación de Código**: Prohibido tocar `app.py`, `main.py`, rutas o servicios.
2.  **Borrado Automático de Entornos**: No se borrarán automáticamente `.venv` ni `node_modules` locales del usuario para no obligar a reinstalaciones inmediatas, solo se asegura su exclusión del repo.
3.  **Cambios en Contratos API**: No se altera ningún esquema ni respuesta de red.

## Archivos a tocar
- `.gitignore` (Raíz)
- `apps/api/.env.example` (NUEVO)
- `apps/web/.env.example` (NUEVO)
- `README.md` (Sección de Setup actualzada con el uso de `.env.example`)

## Criterios de aceptación
1.  Los archivos `.env.example` existen y reflejan todas las variables necesarias para el arranque (según auditoría).
2.  El archivo `.gitignore` es legible, estándar y no tiene errores de sintaxis.
3.  Cualquier nuevo archivo `.pyc` o carpeta `__pycache__` aparece como ignorado al ejecutar comandos de Git.
4.  Existe un documento de setup mínimo que explica: `cp .env.example .env`.

## Pruebas manuales mínimas
1. Verificar que al crear un archivo `test.pyc` en cualquier subcarpeta, no aparece en los cambios pendientes de Git.
2. Intentar arrancar el backend usando solo la información presente en `.env.example` (copiándolo a `.env`).

## Riesgos
- **Mismatch de Variables**: Si se olvida una variable crítica en el `.example`, la app fallará para nuevos usuarios.
- **Confusión de Datos**: Al ignorar `active-storage.json`, el desarrollador debe saber que ese estado es volátil y local.

## Siguiente misión encadenada
- `03_migracion_frontend_a_storage_api.md`