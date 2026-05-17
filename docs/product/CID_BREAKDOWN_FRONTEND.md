# CID Breakdown Frontend

## Resumen Ejecutivo
Implementación del módulo frontend para el **CID Breakdown**, proporcionando una interfaz de usuario integrada y orientada a producto. Este módulo permite a los usuarios visualizar los resultados del desglose técnico de guiones (escenas, personajes, localizaciones, props, y más) generado a partir de la ejecución de Script Analysis Pro. Se han incorporado controles de acceso para garantizar el cumplimiento de restricciones comerciales, integrando además funcionalidades de exportación de datos en diversos formatos y conexiones directas en los flujos operativos de AILinkCinema.

## Ruta Frontend Creada
- `/projects/:projectId/breakdown`

## Archivos Frontend Creados/Modificados
- `src_frontend/src/pages/BreakdownPage.tsx` (Creado)
- `src_frontend/src/api/breakdown.ts` (Creado)
- `src_frontend/src/types/breakdown.ts` (Creado)
- `src_frontend/src/api/index.ts` (Modificado)
- `src_frontend/src/App.tsx` (Modificado)
- `src_frontend/src/pages/ProjectDetailPage.tsx` (Modificado)
- `src_frontend/src/pages/ScriptAnalysisProPage.tsx` (Modificado)

## Endpoints Consumidos
- `GET /api/projects/{project_id}/breakdown/scenes`
- `GET /api/projects/{project_id}/breakdown/departments`
- `GET /api/projects/{project_id}/breakdown/export?format=json|csv|md`

## Comportamiento de Export (JSON / CSV / Markdown)
La página `BreakdownPage` provee botones de exportación directos.
- Al accionar cualquiera de los botones, se cambia el estado a `exporting` con un indicador visual `loading` en el botón presionado, bloqueando acciones concurrentes.
- Se ejecuta la solicitud de descarga en formato blob, generando un archivo `breakdown-{projectId}.{format}`.
- La descarga es automática usando utilidades del navegador (`window.URL.createObjectURL`).
- En caso de error, se informa al usuario mediante una alerta simple.

## Navegación Añadida
- **Desde ProjectDetailPage:** Añadido enlace de acceso contextual al "CID Breakdown" dentro del encabezado y la lista de módulos de cada proyecto.
- **Desde ScriptAnalysisProPage:** Incorporada navegación hacia Breakdown en la lista de `DOWNSTREAM_MODULES`, proveyendo contexto como paso subsiguiente en el ciclo de trabajo del proyecto.

## Relación con Script Analysis Pro, Budget Lite, Production Manager y Call Sheet
El módulo de *Breakdown* actúa como nexo crítico en el pipeline general:
- **Script Analysis Pro:** Provee los datos base. El *Breakdown* exige que la ingesta y análisis del guion estén completados.
- **Budget Lite:** Los datos estructurados del breakdown (ej. localizaciones, props, volumen de personajes) se utilizarán más adelante para poblar las estimaciones automáticas.
- **Production Manager / Call Sheet:** En fases futuras, los departamentos y requerimientos técnicos alimentarán de forma directa el plan de rodaje y la gestión de set.

## Estados UX Implementados
- **Loading:** Indicador circular animado durante la carga concurrente de endpoints (`project`, `scenes`, `departments`).
- **Error:** Presentado vía alertas de usuario si la exportación o carga sufre problemas.
- **Empty:** Textos orientativos informando al usuario cuando un proyecto no posee todavía desgloses o departamentos generados.
- **Blocked 403:** Identificación de falta de acceso por el plan del usuario, devolviendo el módulo a una pantalla de error restrictiva clara que instruye solicitar habilitación y provee un botón para volver al proyecto.

## Validaciones Ejecutadas
- `npm run build` **OK**
- `tests/unit` **OK**
- `test_breakdown_export.py` **OK**
- `test_script_analysis_enforcement.py` **OK**
- `test_script_analysis_export.py` **OK**
- `test_project_script_analysis_flow.py` **OK**

## Limitaciones Conocidas
- **Sin Test Runner Frontend:** Actualmente no hay pruebas unitarias ni de integración corriendo en el frontend, careciendo de entorno configurado.
- **Sin Export PDF:** La funcionalidad de exportación a formato PDF requiere orquestación adicional por parte del backend y no está disponible en esta primera iteración.
- **Datos dependen de breakdown_json existente:** La interfaz asume y depende de que los datos estén empaquetados y precalculados por el backend; cualquier desincronización resultará en un estado vacío o un fallo de renderizado.
- **No hay edición manual todavía:** La vista de desglose es, por ahora, de "solo lectura". Edición y persistencia manuales quedan para una fase posterior.

## Siguiente Commit Recomendado
- Proceder al cierre del "Sprint 3 / Commit 4" en el repositorio.
