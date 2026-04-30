# DaVinci Resolve Import Validation

## 1. Generar FCPXML desde CID

1. Abrir `EditorialAssemblyPage` del proyecto.
2. Ejecutar `Reconciliar material`, `Calcular tomas recomendadas` y `Generar AssemblyCut` si todavia no existe assembly.
3. Revisar la seccion `Exportacion DaVinci`.
4. Ejecutar `Validar FCPXML`.
5. Ejecutar `Exportar FCPXML` o `Exportar paquete editorial ZIP`.

## 2. Donde encontrar el archivo

- Export FCPXML: `exports/<organization_id>/editorial/*_assembly.fcpxml`
- Paquete editorial: `exports/<organization_id>/editorial/*_editorial_package.zip`
- Manifest asociado: `exports/<organization_id>/editorial/*_manifest.json`

## 3. Como importarlo en DaVinci Resolve

1. Abrir proyecto de destino en DaVinci Resolve.
2. Ir a `File -> Import -> Timeline -> Import AAF, EDL, XML...`.
3. Seleccionar `assembly.fcpxml` o el `.fcpxml` exportado por CID.
4. Confirmar importacion de timeline.

## 4. Como relinkar media

1. Si Resolve muestra clips offline, abrir Media Pool.
2. Seleccionar clips offline.
3. Ejecutar `Relink Selected Clips...`.
4. Apuntar al directorio real de camara/audio usado por `MediaAsset`.
5. Verificar coincidencia por nombre y ruta.
6. Consultar `media_relink_report.json` para ver `resolved_path`, `fcpxml_uri` y assets offline.

## 5. Que comprobar en la timeline

- Timeline creada sin error de XML.
- Numero de clips coincide con `assembly_summary.json`.
- Orden editorial coincide con el AssemblyCut.
- Duraciones visibles en Resolve son consistentes con `duration_frames`.
- Clips con media real relinkan sin usar fallback `/tmp`.
- Notas editoriales aparecen cuando Resolve conserva `note` del `asset-clip`.

## 6. Capturas y evidencias a guardar

- Pantalla CID con `Exportacion DaVinci`.
- Archivo `assembly.fcpxml` generado.
- `media_relink_report.json`.
- Captura de importacion en Resolve.
- Captura de timeline importada.
- Captura de relink completado o lista de offline si falla.

## 7. Errores frecuentes

- `No assembly cut available for export`: falta generar AssemblyCut.
- Clips offline en Resolve: `MediaAsset` sin ruta real resoluble.
- `xml_not_well_formed`: export corrupto o truncado.
- `asset_clip_missing_asset_ref`: FCPXML inconsistente.
- Fallback `/tmp`: asset sin ruta real disponible.
- Audio sin metadata rica: parser BWF completo aun no implementado.

## 8. Checklist Go/No-Go

### Go

- `Validar FCPXML` devuelve `valid=true`.
- `resolved_media_count > 0` cuando hay media real.
- Timeline importa en Resolve.
- Relink funciona para los assets reales.
- Fallback offline solo afecta clips sin ruta real.

### No-Go

- XML invalido.
- Timeline no importa.
- Todos los assets caen en `/tmp` teniendo media real.
- Clip count de Resolve no coincide con CID.
- Relink report no refleja el estado real de media.

## 9. Estado BWF minimo

- Se expone `get_audio_metadata(asset) -> AudioMetadataResult`.
- WAV usa parser seguro con modulo `wave` cuando aplica.
- Si no hay parser/libreria adecuada, el sistema cae a metadata disponible sin romper smoke tests.

## 10. Validacion con audio dual-system

- CID puede leer `bext` e `iXML` cuando existen en WAV reales.
- `Take` guarda `audio_metadata_status`, `dual_system_status`, `sync_method` y `sync_confidence`.
- El FCPXML mantiene video principal para no romper importabilidad.
- Si el audio externo no se inserta de forma segura como linked audio, CID emite `dual_system_audio_export_partial` y documenta el audio en `media_relink_report.json` y `editorial_notes.txt`.
- Para validacion real revisar:
  - `sync_method`
  - `sync_confidence`
  - `dual_system_status`
  - `audio_metadata_status`
  - warnings del relink report

## 11. FCPXML Variantes (Dual-System)

CID genera dos variantes de FCPXML para audio dual-system:

### Variante Conservadora (SAFE)
- Archivo: `*_conservative.fcpxml`
- Estado: Audio como recurso con nota en clip
- Uso: Importacion segura en DaVinci
- Timeline: Solo clips de video
- Audio: Marcado en campo `note` del asset-clip
- Decision: SAFE, usar para produccion

### Variante Experimental (CANDIDATE)
- Archivo: `*_linked_audio_experimental.fcpxml`
- Estado: Audio en pista sincronizada
- Uso: Requiere validacion manual en DaVinci
- Timeline: Video + pista de audio separada
- Audio track: "Linked Audio" con offset basado en timecode
- Decision: CANDIDATE, verificar en DaVinci antes de usar

### Como importar variantes

1. En CID ejecutar generacion de variantes via `fcpxml_dual_system_variant_service`
2. Exportar paquete editorial con variantes
3. En DaVinci: File > Import > Timeline > Import AAF, EDL, XML...
4. Probar conservador primero (siempre debe funcionar)
5. Si conservador funciona, probar experimental

## 12. Flujo Operativo: Media Ya Ingestada

CID no es el sistema de ingesta física.

### Flujo Real

1. **DaVinci Resolve o DIT ingesta** el material de tarjetas/discos al almacenamiento.
2. **Usuario proporciona la ruta raíz** donde la media ya existe.
3. **CID escanea e indexa** los archivos existentes (no los copia).
4. **CID lee metadata** BWF/iXML de los archivos.
5. **CID cruza con reports** de cámara y sonido.
6. **CID crea Takes** referenciando la ubicación original.
7. **CID exporta FCPXML** pointing a la ruta original.

### Conceptos Clave

- **CID no mueve archivos**: Solo lee la ubicación existente.
- **CID no copia archivos**: Salvo que `include_media=true`.
- **CID no renombra**: Respeta estructura de carpetas original.
- **include_media=false**: Ligero, solo FCPXML. Requiere que media exista.
- **include_media=true**: Copia media al paquete portable.

## 13. Diferencia Entre Media y Reports

### Media de Rodaje

- **Qué es**: Archivos pesados de cámara (MOV, MXF, R3D, BRAW) y sonido (WAV, BWF).
- **Qué hace CID**: Escanea e indexa. No ingesta físicamente.
- **Flujo**:
  1. DaVinci/DIT ingiere la media al almacenamiento.
  2. Usuario proporciona la ruta raíz.
  3. CID lee metadata y crea referencias.
  4. CID no mueve, copia ni renombra archivos.

### Reports / Documentación Editorial

- **Qué es**: Camera reports, sound reports, script notes, director notes, PDFs, CSVs, XLSX, DOCX, TXT, MD.
- **Qué hace CID**: Sí puede ingestar como documentos.
- **Flujo**:
  1. Usuario sube/importa reports a CID.
  2. CID extrae, clasifica y estructura.
  3. CID convierte en: CameraReport, SoundReport, ScriptNote, DirectorNote.
  4. CID cruza con la media indexada.

### Resumen

| Tipo | CID Action | Comportamiento |
|------|-----------|----------------|
| Media (video/audio) | Indexar | Escanea desde ruta existente |
| Reports (PDF, CSV, etc) | Ingestar | Puede subir, importar, extraer |

**CID no sustituye la ingesta profesional de DaVinci Resolve, DIT o auxiliar de montaje. La media pesada se ingiere fuera de CID. En cambio, los reports y documentos editoriales sí pueden incorporarse a CID.**
