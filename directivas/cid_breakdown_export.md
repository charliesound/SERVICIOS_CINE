# Directiva: CID Breakdown Export

## Objetivo
Reglas y restricciones operativas para mantener, extender o consumir el servicio de exportación de CID Breakdown (`BreakdownExportService`).

## Contexto
Breakdown Export provee endpoints (`/api/projects/{id}/breakdown/export`) para descargar el desglose de producción en JSON, CSV y Markdown. Es una feature vendible protegida por `require_module_access("breakdown")`.

## Archivos Afectados
- `src/services/breakdown_export_service.py`
- `src/routes/intake_routes.py` (rutas)
- `tests/integration/test_breakdown_export.py`

## Entradas
- ID de Proyecto.
- Formato solicitado (`json`, `csv`, `md`).
- Datos obtenidos desde `ProductionBreakdown.breakdown_json`.

## Salidas
- JSON puro o descargas de archivos con cabeceras `Content-Disposition: attachment; filename="..."` para CSV y Markdown.

## Validaciones y Reglas
1. **Enforcement estricto**: Todo endpoint nuevo relacionado a leer o exportar el breakdown para uso profesional DEBE requerir `require_module_access("breakdown")`.
2. **Reutilización**: Usar `breakdown_export_service.build_export_payload` para obtener los datos normalizados en lugar de parsear `breakdown_json` directamente en el enrutador.
3. **Robustez ante datos faltantes**: El modelo de datos puede venir vacío si el análisis heurístico/LLM no detectó ciertos departamentos. Todos los `.get()` deben tener fallbacks seguros (ej: listas o diccionarios vacíos `[]`, `{}`).
4. **Independencia de formato**: No incluir lógica de transformación de formato (CSV/MD) dentro de la ruta `intake_routes.py`. Esa lógica pertenece exclusivamente al `BreakdownExportService`.
5. **Alineamiento con Script Analysis**: La fuente de datos sigue siendo `script_analysis`. Si se añade una nueva extracción por IA (ej: "Armas" o "Vehículos"), debe primero persistirse en `breakdown_json` durante la ingesta y posteriormente exponerse en `BreakdownExportService`.

## Casos Borde
- Proyecto sin script o sin análisis procesado: Devolverá Error 404 (No breakdown found).
- Solicitud de un formato no compatible (ej: `xml`): Error 422 Controlado.
- Datos con estructuras irregulares (null en listas, keys no encontradas): `BreakdownExportService` filtra silenciosamente o devuelve los defaults pre-calculados, evitando el desplome con Error 500.

## Errores Aprendidos
- Evitar devolver `application/json` si el usuario pidió `csv`. Se requiere ajustar los `Response` de FastAPI con `media_type` y `headers` apropiados.
- El formato del JSON de Breakdown originado por IA es altamente volátil. Siempre usar `_dict_or_empty` y `_list_or_empty` para normalizar las listas y objetos en Python de forma segura.

## Comandos Seguros (Test)
```bash
python -m pytest tests/integration/test_breakdown_export.py -q
```
