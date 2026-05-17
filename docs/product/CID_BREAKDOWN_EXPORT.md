# CID Breakdown - Export Feature

## Objetivo
Implementar la capacidad de exportar un Breakdown (desglose de producción) como artefacto compartible y vendible dentro del flujo de AILinkCinema/CID.

## Contexto
Durante el Sprint 3 (CID Breakdown Breakdown), se identificó que el backend podía generar breakdowns de escenas y departamentos, pero estos sólo existían como sub-productos del módulo `script_analysis`. Para que el Breakdown fuera un SKU comercial independiente y vendible, se requería un exportador nativo que devolviera los datos consolidados en formatos comunes para los profesionales (JSON, CSV, Markdown) y protegiera el endpoint con `require_module_access("breakdown")`.

## Archivos afectados
- `src/services/breakdown_export_service.py` (nuevo)
- `src/routes/intake_routes.py` (modificado)
- `tests/integration/test_breakdown_export.py` (nuevo)

## Detalles del Endpoint
- **Ruta**: `GET /api/projects/{project_id}/breakdown/export?format=json|csv|md`
- **Módulo Propietario**: `breakdown`
- **Autorización**: Requiere acceso al proyecto (tenant-isolated) y feature flag/SKU `module_breakdown`.

### Formatos Soportados
1. **JSON**: (`application/json`) Exporta toda la metadata del breakdown, incluyendo personajes, localizaciones, props, vestuario, etc., junto con los arrays completos de breakdowns y departments.
2. **CSV**: (`text/csv`) Genera un archivo tabular para Excel/Google Sheets, ideal para Line Producers o Asistentes de Dirección, detallando por fila: Scene ID, Heading, Int/Ext, Location, Time, Characters, Props, Complexity, Dialogue/Action lines.
3. **Markdown**: (`text/markdown`) Exporta un documento legible con formato que resume la dificultad, notas de producción, advertencias, listado detallado de elementos por departamento, y resúmenes estructurados escena a escena.

## Relación con Módulos
- **Script Analysis Pro**: Genera la materia prima (`ProductionBreakdown.breakdown_json`) que este servicio luego normaliza y exporta. Si no existe un breakdown generado previamente, el export fallará con `404 No breakdown found`.
- **Budget Lite**: Consume los breakdowns para la estimación financiera. El export proporciona a los usuarios visibilidad del desglose en el que se basa el Budget Lite.
- **Production Manager / Call Sheet**: Son consumidores directos de las listas y métricas proporcionadas por Breakdown Export (personajes, ubicaciones, complejidad, etc.).

## Limitaciones Conocidas
- Actualmente se basa de la estructura JSON guardada por `script_analysis_service`. Si la estructura de `ProductionBreakdown.breakdown_json` cambia (ej: de un JSON crudo a un esquema SQL relacional en el futuro), `BreakdownExportService` requerirá actualización.
- Aún no soporta la exportación a formato PDF (requerirá un motor de renderizado HTML-to-PDF o ReportLab en Sprints futuros).
- Por ahora, cualquier cambio manual a las escenas y personajes en UI aún debe sincronizarse correctamente con la persistencia para que el exportador refleje los datos editados.

## Siguiente Commit Recomendado
- **Pantalla Propia Breakdown**: Crear `BreakdownPage.tsx` en Frontend para visualizar y gestionar el breakdown independientemente de Script Analysis Pro. Permitirá invocar estos endpoints de exportación desde la interfaz de usuario.
