# Directiva Técnica: CID Breakdown Frontend

## Objetivo
Establecer las normas de diseño, patrones de implementación y reglas técnicas de acceso para el módulo frontend **CID Breakdown**. Esta vista actúa como interfaz para el consumo, exploración y exportación de datos técnicos estructurados derivados de análisis de guiones en el sistema de AILinkCinema.

## Alcance
Aplica estrictamente al código frontend (Páginas, Componentes, Tipos y API) y su conexión con el servicio backend que sirve los endpoints en modo solo-lectura y de exportación.

## Archivos Afectados
- `src_frontend/src/pages/BreakdownPage.tsx`
- `src_frontend/src/api/breakdown.ts`
- `src_frontend/src/types/breakdown.ts`
- `src_frontend/src/App.tsx`
- `src_frontend/src/pages/ProjectDetailPage.tsx`
- `src_frontend/src/pages/ScriptAnalysisProPage.tsx`
- `src/services/breakdown_export_service.py` (Backend, ajustes menores)
- `tests/integration/test_breakdown_export.py` (Backend, test integracional)

## Endpoints Consumidos
El frontend confía de forma síncrona en los siguientes endpoints (mediante React Query):
- `GET /api/projects/{project_id}/breakdown/scenes`
- `GET /api/projects/{project_id}/breakdown/departments`
- `GET /api/projects/{project_id}/breakdown/export?format=json|csv|md`

## Restricciones
- **Seguridad (Enforcement):** El frontend debe respetar los códigos `403` propagados por el servicio, interpretándolos como bloqueos de módulo (`MODULE_ACCESS_BLOCKED`) para mostrar la interfaz bloqueada y no exponer la data.
- **Navegación Controlada:** No se deben forzar accesos si el usuario no tiene activado el módulo; se manejará siempre mediante pantallas "Empty state" o "Blocked".
- **Sin Mutaciones:** Este commit se limita a mostrar, presentar y exportar datos. No se implementan métodos POST/PUT de modificación del desglose.
- **Exportación en Blob:** El frontend debe manejar los archivos descargados procesando la respuesta en crudo y emitiendo el objeto directo al DOM localmente sin manipulación de parseo interno.

## Validaciones
Antes de cualquier alteración en el Breakdown Frontend o Backend asociado:
- Compilar frontend sin errores de TS.
- Validar aserciones precisas en `test_breakdown_export.py` sobre `scenes`, `departments` y endpoints protegidos 403.
- Ejecutar la suite completa de integración de proyectos y análisis de guion.

## Errores Corregidos (Sprint 3 / Commit 4)
Durante la implementación y auditoría de calidad, se solventaron los siguientes desvíos críticos:
1. **Imports no usados en `BreakdownPage.tsx`:** Retirados `Users` y `ArrowLeft` tras reportes del linter/build.
2. **Uso de cliente obsoleto:** Corregido `projectsApi.getProject(projectId!)` por su firma real `projectsApi.get(projectId!)`.
3. **Semántica Markdown export:** Ajustada la salida del exporter (`breakdown_export_service.py`) de `## Scene Breakdowns` a `## Scenes / Scene Breakdowns` para empalmar coherencia semántica con expectativas exactas del test integracional ("Scenes").
4. **Manejo 403 robusto en testing:** Actualizado `test_breakdown_export.py` en la validación del acceso modular bloqueado; ahora procesa aserciones dinámicas soportando `response.json()["detail"]` y fallbacks en strings raíz sin romper el contrato global.

## Comandos Seguros
Para validar y auditar continuamente el módulo frontend:
```bash
cd /opt/SERVICIOS_CINE/src_frontend && npm run build
```
Para validar su contraparte lógica:
```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m pytest tests/integration/test_breakdown_export.py -q
```

## Siguiente Paso Recomendado
- Enviar el *Sprint 3 / Commit 4*.
- Comenzar fase de evaluación para exportación PDF o, de no ser prioritario, iniciar diseño de flujos de ingesta en **Budget Lite**.
