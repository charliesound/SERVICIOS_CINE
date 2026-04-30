# Editorial Pro: BWF / iXML / Dual-System

## Que soporta ahora CID

- Lectura segura de WAV con metadata basica (`sample_rate`, `channels`, `duration_seconds`, `bit_depth`, `file_size`).
- Parser RIFF no destructivo para chunks `bext` e `iXML` cuando existen.
- Persistencia de metadata de audio y estado dual-system en `Take`.
- Reconciliacion camara/audio por `scene/shot/take`, iXML `scene/take`, slate, `sound_roll + take`, filename y timecode cercano.
- Scoring con peso de audio profesional, sync confidence y conflictos.
- Export FCPXML conservador: video principal estable, audio externo trazado en resources, notas y `media_relink_report.json`.

## Metadata leida

- WAV: `sample_rate`, `channels`, `duration_seconds`, `bit_depth`, `codec`, `file_size`.
- BWF/BEXT: `description`, `originator`, `originator_reference`, `origination_date`, `origination_time`, `time_reference_samples`, `umid`.
- iXML: `project`, `scene`, `shot`, `take`, `tape/roll`, `circled`, `note`, `start_timecode`, `fps`.

## Que es BWF

- Broadcast Wave Format extiende WAV para audio de rodada con time reference y campos descriptivos de postproduccion.

## Que es iXML

- iXML es metadata XML embebida en audio de sonido directo usada para escena, toma, roll, circled take y timecode.

## Flujo Operativo: Media Ya Ingestada

CID NO es el sistema de ingesta física. CID es el sistema de lectura, indexación, análisis editorial y exportación.

### Flujo Real de Producción

1. **DaVinci Resolve o DIT ingiere el material** de tarjetas/discos al sistema de almacenamiento.
2. **Usuario proporciona la ruta raíz** donde la media ya existe (ej: D:/PROYECTO/MEDIA).
3. **CID escanea e indexa** los archivos existentes (no los copia).
4. **CID lee metadata** BWF/iXML directamente de los archivos.
5. **CID crea MediaAsset** referencias a la ruta original (canonical_path).
6. **Usuario proporciona reports** de cámara, sonido, script y dirección.
7. **CID ejecuta reconcile, score, assembly y export FCPXML** como en flujo validado.

### Conceptos Clave

- **CID no ingiere material**: Lo escanea desde ubicación existente.
- **CID no mueve archivos**: Solo lee y mantiene referencia.
- **CID no copia archivos**: Salvo que usuario pide `include_media=true`.
- El flujo es: DaVinci/DIT → Ruta raíz a CID → Scan → Index → Analyze → Export.

## Reconciliacion camara/audio

- Prioridad actual:
  1. `scene + shot + take` exactos
  2. `iXML scene/take`
  3. slate
  4. `sound_roll + take`
  5. filename pattern
  6. timecode near
  7. fallback manual

## Export a DaVinci

- El video sigue siendo el clip principal de timeline.
- Si el audio dual-system no se puede asociar de forma segura sin riesgo para importabilidad, CID marca `dual_system_audio_export_partial`.
- El audio externo queda trazado en `editorial_notes.txt` y `media_relink_report.json`.

## Limitaciones actuales

- No hay OTIO ni EDL.
- No hay linked-audio avanzado especifico para cada NLE.
- Timecode near es heuristico.
- WAV invalidos o sin chunks ricos no bloquean; caen a `partial`, `unsupported` o `error` controlado.

## Criterios GO / NO-GO para material real

### GO

- FCPXML valido.
- Video importable.
- Media real resuelta o relinkable.
- Audio metadata al menos `partial` sin bloquear timeline.
- `dual_system_status` mayoritariamente `matched` o `metadata_warning` controlado.

### NO-GO

- FCPXML invalido.
- Reconciliacion masiva en `conflict`.
- Paths no resolubles para media real.
- Export que rompa la importacion base validada en DaVinci.

## Diferencia Entre Media y Reports

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