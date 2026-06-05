# CID Sound Ingest — Field Recorders Spec v1

Línea de producto: `CID.SOUND.INGEST.FIELD_RECORDERS.MVP.1`
Fase: `CID.SOUND.INGEST.FIELD_RECORDERS.SPEC.1` (documental, sin código de aplicación).

## 1. Resumen ejecutivo

### Qué resuelve el módulo

El módulo de ingesta de sonido directo de CID resuelve el flujo de entrada al sistema de los archivos generados por los grabadores de campo de producción (`production sound`): WAV/BWF con iXML/BEXT, sound reports en CSV/ALE/PDF, y metadatos de rodaje (escena, slate, take, timecode, FPS, sample rate, canales).

El objetivo es doble:

1. **Trazabilidad**: dejar registro auditable de qué se grabó, en qué condiciones, con qué equipo y con qué configuración de timecode.
2. **Disponibilidad**: exponer esa información a través del modelo de datos de CID para que pueda ser consultada, enlazada con el resto del proyecto (storyboards, shots, breakdown) y eventualmente enlazada con el etalonaje, el montaje y la postproducción de sonido.

### Por qué no debe controlar directamente los grabadores como API viva

Los grabadores de campo profesionales (Aaton Cantar, Sound Devices 6/8 Series, Zoom F-series) no exponen una API HTTP estable, ni documentación pública uniforme, ni superficie de control remoto consistente. Intentarlo introduce varios problemas:

- **Riesgo de integridad**: una API que escribe directamente sobre la tarjeta del grabador podría corromper una sesión en curso, perder takes, o competir con la operación humana del sonidista.
- **Acoplamiento por marca**: cada grabador tiene su propio dialecto de metadata (iXML chunks propietarios, BEXT fields custom, layouts de carpetas específicos). Un wrapper unificado terminaría siendo un subconjunto limitado del más restrictivo.
- **Latencia y robustez de red**: en set, la red no es confiable. Una capa de control remoto con reconexión y timeouts añade complejidad sin valor inmediato.
- **Seguridad**: el grabador está físicamente accesible al sonidista, que es quien decide cuándo empezar y cuándo parar. El sistema no debe asumir autoridad sobre el dispositivo.

### Por qué la vía base debe ser carpeta vigilada / ingest manual seguro

El patrón recomendado es:

1. El sonidista **termina su rollo o su día** y exporta las tarjetas a una **carpeta de ingest** montada en el backend de CID (vía SMB/NFS/USB, o subida manual desde la app de escritorio complementaria).
2. Un **watcher de carpeta** o un **ingest manual** ejecuta el pipeline: detección, parsing, checksum, registro.
3. El backend **nunca toca los originales en su ubicación de origen**: solo lee, hashea, copia de preservación, y registra metadatos.

Este patrón aporta:

- **Idempotencia**: si un archivo ya está registrado (por checksum), se ignora.
- **Aislamiento**: la operación del set no depende de la disponibilidad del backend.
- **Auditabilidad**: cada paso queda en una `ingest_batch` con su estado.
- **Compatibilidad universal**: cualquier grabador cuyo output sea una carpeta con WAV/BWF + sound report puede ser ingerido, sin necesidad de driver propietario.

## 2. Grabadores objetivo

| Marca | Modelo | Notas |
|---|---|---|
| Aaton | Cantar 3 | Formato propietario `.cantar` opcional + WAV/BWF con BEXT extendido y carpetas `TAKES`/`SCENES`. |
| Aaton | Cantar X3 | Hereda Cantar 3 + iXML chunks. |
| Aaton | Cantar X3 Mini | Versión compacta. |
| Sound Devices | 6-Series (633, 664, 688) | WAV/BWF polifónico con iXML completo. |
| Sound Devices | 8-Series (833, 888, Scorpio) | iXML con scene/take/track names; sample rates hasta 192 kHz. |
| Sound Devices | MixPre II (6, 10 II) | Polifónico con iXML; uso más común en indie/ENG. |
| Zoom | F6 | 6 canales, 32-bit float, iXML. |
| Zoom | F8 / F8n / F8n Pro | 8 canales, BWF + iXML. |
| Generic | BWF / iXML recorder | Cualquier dispositivo que emita WAV/BWF con iXML o BEXT estándar. |

## 3. Formatos soportados

| Formato | Uso | Parsing |
|---|---|---|
| WAV/BWF | Audio contenedor base | RIFF parser + extensión `fmt ` + `data` chunks. |
| iXML | Metadata extendida por toma | Chunk iXML dentro del BWF, XML embebido. |
| BEXT | Broadcast Wave Extension | Chunk `bext` con originator, originator_reference, time_reference, coding_history. |
| CSV sound report | Reporte plano del sonidista | Encodings variables: UTF-8, Latin-1, UTF-16 con/sin BOM. |
| ALE (Avid Log Exchange) | Reporte Avid-compatible | Texto delimitado por tab con secciones `Heading`/`Column`/`Data`. |
| PDF sound report | Reporte visual/impreso | Texto + tablas; parsing frágil. |
| SHA-256 | Integridad | Hash streaming sobre el archivo completo. |

## 4. Principio de preservación

El módulo sigue un principio estricto de **originales intocables**:

1. **Original intocable** — el archivo en la carpeta de ingest se trata como read-only. CID no modifica, renombra, ni borra originales.
2. **Copia de preservación con checksum** — al ingestar, se genera una copia bit-a-bit en el storage de preservación de CID. Se calcula SHA-256 sobre el original y se almacena. Cualquier verificación posterior compara contra ese hash.
3. **Copia de trabajo / proxy opcional** — opcionalmente, se puede generar un proxy (WAV 48 kHz / 24-bit normalizado, MP3, AAC) para escuchar / reproducir en la UI sin necesidad de servir el original pesado.
4. **Metadata extraída a base de datos CID** — todos los campos útiles (escena, slate, take, timecode, channels, sample rate, etc.) se persisten en tablas relacionales para consulta, búsqueda, y enlazado con el resto del modelo de proyecto.

El flujo nunca borra originales. Si una re-ingesta es necesaria, se detecta por checksum y se ofrece reemplace o merge, nunca delete implícito.

## 5. Arquitectura propuesta

```
┌─────────────────────┐
│ Folder ingest /     │
│ manual upload       │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Watcher / Watchdog  │
│ (filesystem events) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐    ┌──────────────────┐
│ Recorder Detector   │───▶│ Adapter layer    │
└─────────┬───────────┘    │ (per-recorder)   │
          │                └──────────────────┘
          ▼
┌─────────────────────┐
│ BWF / iXML / BEXT   │
│ Parsers             │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Report Parsers      │
│ (CSV / ALE / PDF)   │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Checksum Service    │
│ (SHA-256 streaming) │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ Ingest Service      │──▶ Preservation copy → Storage
│ (DB writes)         │──▶ Metadata rows      → Postgres
└─────────────────────┘
```

### Componentes

| Componente | Responsabilidad |
|---|---|
| `watcher` | Detecta nuevos archivos en la carpeta de ingest vía inotify/FS events. Throttle + dedupe por path. |
| `recorder_detector` | Clasifica el origen del archivo (carpeta, naming pattern, primer byte) y delega al adapter correcto. |
| `bwf_parser` | Lee chunks RIFF, valida BWF, extrae `fmt ` y `data` sizes. |
| `ixml_parser` | Parsea el chunk iXML embebido, valida XML, normaliza campos. |
| `bext_parser` | Lee el chunk `bext`, expone originator, originator_reference, time_reference, coding_history. |
| `ale_parser` | Interpreta el formato Avid Log Exchange. |
| `csv_report_parser` | Acepta encodings variables, normaliza delimitadores, mapea a `scene/slate/take`. |
| `pdf_report_parser` | Extrae texto y tablas; clasifica por heurística de marca. |
| `checksum_service` | Hash SHA-256 streaming sobre el archivo completo, sin cargar en memoria. |
| `ingest_service` | Orquesta la ingest: idempotencia por checksum, transacción de metadata, copia de preservación. |
| `adapter_layer` | Encapsula particularidades por grabador (naming, fields propietarios, iXML quirks). |

## 6. Adaptadores

Cada adapter encapsula las particularidades del grabador. Viven bajo `src/services/sound_ingest/adapters/` y exponen una interfaz común:

```python
class RecorderAdapter(Protocol):
    brand: str
    model: str

    def detect(self, file_path: Path) -> bool: ...
    def parse(self, file_path: Path) -> SoundMetadata: ...
    def naming_hint(self, file_path: Path) -> NamingHint | None: ...
```

### `aaton_cantar_adapter.py`

- Reconoce carpetas `TAKES/`, `SCENES/`, `MIX/`.
- Soporta `.cantar` sidecar (parsing opcional, versionado).
- Aplica heurística de naming Cantar: `<ROLL>_<TAKE>_<SCENE>_<SLATE>.wav`.
- BEXT extendido con campos propietario (origen Aaton).

### `sound_devices_adapter.py`

- Reconoce la jerarquía de carpetas Sound Devices (`<ROLL>/<TAKE>.wav`).
- iXML completo con `SCENE`, `TAKE`, `TRACK_LIST`, `TIMECODE_FLAGS`, `SPEED`, `TIMECODE_RATE`.
- MixPre II / 6-Series / 8-Series cubiertos por la misma lógica.
- Mapea `TRACK_LIST` a `sound_tracks` (uno por canal).

### `zoom_f_series_adapter.py`

- iXML estándar.
- Naming: `ZOOM<ROLL>_<SCENE>_<TAKE>_<TRACK>.wav` (heurística configurable).
- 32-bit float flag en el header (`fmt ` chunk).

### `generic_bwf_adapter.py`

- Catch-all para cualquier BWF/iXML que no encaje en los adapters anteriores.
- Extrae solo lo que el estándar garantiza: `fmt `, `data`, `bext`, `ixml` opcional.
- Marca `adapter_used = "generic_bwf"` y `confidence = "low"` cuando faltan campos.

## 7. Modelo de datos futuro

> Esta fase es documental. La creación efectiva de tablas y migraciones ocurre en `CID.SOUND.INGEST.FIELD_RECORDERS.MODELS.1`.

### Tablas propuestas

#### `sound_ingest_batches`

Una batch representa una sesión de ingest (carpeta subida, día de rodaje, o subida manual).

| Campo | Tipo | Notas |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid FK | Project |
| `shoot_day_id` | uuid FK nullable | ShootDay |
| `created_by` | uuid FK | User |
| `created_at` | timestamptz | |
| `status` | enum | `pending`, `scanning`, `processing`, `completed`, `failed` |
| `source_path` | text | Carpeta de origen (no se modifica) |
| `total_files` | int | |
| `processed_files` | int | |
| `failed_files` | int | |
| `adapter_used` | text | Adapter dominante o `mixed` |
| `notes` | text nullable | |

#### `sound_source_files`

Una fila por archivo físico detectado.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | uuid | PK |
| `batch_id` | uuid FK | sound_ingest_batches |
| `project_id` | uuid FK | denormalizado para query |
| `file_path` | text | Ruta del original (read-only) |
| `original_filename` | text | |
| `checksum_sha256` | text | Único por proyecto |
| `file_size_bytes` | bigint | |
| `mtime` | timestamptz | |
| `recorder_brand` | text nullable | |
| `recorder_model` | text nullable | |
| `recorder_serial` | text nullable | |
| `firmware_version` | text nullable | |
| `sample_rate` | int nullable | Hz |
| `bit_depth` | int nullable | |
| `channels` | int nullable | |
| `duration_seconds` | numeric nullable | |
| `start_tc` | text nullable | `HH:MM:SS:FF` |
| `end_tc` | text nullable | `HH:MM:SS:FF` |
| `fps` | numeric nullable | |
| `raw_ixml_json` | jsonb nullable | iXML tal cual |
| `raw_bext_json` | jsonb nullable | bext tal cual |
| `adapter_used` | text | |
| `parse_status` | enum | `ok`, `partial`, `failed` |
| `parse_errors` | jsonb nullable | Lista de errores |
| `ingest_status` | enum | `pending`, `preserved`, `proxied`, `failed` |
| `preservation_path` | text nullable | Ruta de la copia de preservación |

#### `sound_rolls`

Agrupa takes por rollo/carpeta del grabador.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid FK | |
| `batch_id` | uuid FK | |
| `roll_name` | text | `<ROLL>` del filename o del iXML |
| `recorder_brand` | text | |
| `recorder_model` | text | |
| `recorder_serial` | text | |
| `firmware_version` | text | |
| `first_tc` | text nullable | |
| `last_tc` | text nullable | |
| `fps` | numeric nullable | |
| `take_count` | int | |
| `notes` | text nullable | |

#### `sound_takes`

Una fila por take, deducida del filename, iXML, o sound report.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid FK | |
| `batch_id` | uuid FK | |
| `roll_id` | uuid FK | sound_rolls |
| `scene` | text | |
| `slate` | text nullable | |
| `take` | int | |
| `circled` | bool | Default false |
| `notes` | text nullable | Notas del sonidista |
| `start_tc` | text | `HH:MM:SS:FF` |
| `end_tc` | text nullable | |
| `fps` | numeric | |
| `sample_rate` | int | |
| `bit_depth` | int | |
| `channels` | int | |
| `duration` | numeric | seconds |
| `raw_report_json` | jsonb nullable | Entrada del sound report si existe |

#### `sound_tracks`

Una fila por canal de audio del take.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | uuid | PK |
| `take_id` | uuid FK | sound_takes |
| `track_index` | int | 1..N |
| `track_name` | text nullable | del iXML `TRACK_LIST` |
| `character_name` | text nullable | Si el sonidista lo etiquetó |
| `mic_source` | text nullable | boom, lav, plant, etc. |
| `channel_layout` | text nullable | mono, stereo, etc. |
| `notes` | text nullable | |

#### `sound_reports`

Reports originales ingeridos como artefactos documentales.

| Campo | Tipo | Notas |
|---|---|---|
| `id` | uuid | PK |
| `project_id` | uuid FK | |
| `batch_id` | uuid FK | |
| `report_format` | enum | `csv`, `ale`, `pdf` |
| `file_path` | text | Original |
| `checksum_sha256` | text | |
| `parsed_rows` | int | |
| `parse_status` | enum | `ok`, `partial`, `failed` |
| `parse_errors` | jsonb nullable | |
| `storage_path` | text nullable | Copia preservada |
| `created_at` | timestamptz | |

## 8. API futura

> Rutas propuestas para una fase posterior (`CID.SOUND.INGEST.FIELD_RECORDERS.ROUTES.1`). Se documentan aquí, **no se implementan en esta fase**.

Todas las rutas viven bajo `/api/projects/{project_id}/sound/...` y siguen el contrato de gating consolidado en `docs/architecture/backend_gating_contract_v1.md` (tenant context, `validate_project_access` o helper local equivalente, `require_write_permission` en mutantes, módulo `sound_ingest` si se introduce como módulo gate).

| Método | Path | Mutante | Descripción |
|---|---|:---:|---|
| `POST` | `/api/projects/{project_id}/sound/ingest/preview` | sí | Recibe ruta de carpeta o lista de archivos; devuelve análisis (qué se detectó, qué adapter aplicaría, qué se va a copiar) sin tocar archivos. |
| `POST` | `/api/projects/{project_id}/sound/ingest/batches` | sí | Confirma el preview anterior y crea una `sound_ingest_batches` con el pipeline corriendo. |
| `POST` | `/api/projects/{project_id}/sound/ingest/confirm` | sí | Alternativa explícita en dos pasos (preview + confirm) para ingest manual sin preview previo. |
| `GET`  | `/api/projects/{project_id}/sound/ingest/batches` | no | Lista batches con filtros (shoot_day, status, fecha). |
| `GET`  | `/api/projects/{project_id}/sound/rolls` | no | Lista rolls. |
| `GET`  | `/api/projects/{project_id}/sound/takes` | no | Lista takes con filtros (scene, take range, circled only). |
| `GET`  | `/api/projects/{project_id}/sound/reports` | no | Lista reports. |

Detalle de los mutantes:

- **`POST /preview`**: retorna JSON con: archivos detectados, adapter que aplicaría, errores de parseo anticipados, total size, estimación de tiempo. No escribe DB ni toca archivos.
- **`POST /batches`**: ejecuta el pipeline. Devuelve `batch_id` y estado `processing`. La completion se observa vía polling o webhook.
- **`POST /confirm`**: pensado para ingest manual desde la UI (drag-and-drop) sin preview previo. Equivalente a `POST /batches` con menos fricción.

Los endpoints de lectura devuelven payloads paginados con `cursor` o `offset/limit`, y exponen los campos clave (escena, slate, take, timecode, circled, tracks) más los enlaces a la metadata cruda (`raw_ixml_json`, etc.) bajo demanda.

## 9. UI futura

> Componentes propuestos para una fase posterior (`CID.SOUND.INGEST.FIELD_RECORDERS.FRONTEND.1`). Se documentan, no se implementan.

### `SoundIngestPage.tsx`

- Drag-and-drop de carpeta o archivos.
- Botón "Preview" que llama a `POST /preview` y muestra la tabla de archivos detectados con su adapter.
- Botón "Confirm ingest" que llama a `POST /batches`.
- Progreso en vivo de la batch (scanning → processing → completed).
- Resumen al terminar: total ingested, total failed, lista de errores.

### `SoundRollDetailPage.tsx`

- Cabecera con metadata del rollo: brand, model, serial, firmware, FPS, primer/último TC.
- Tabla de takes con columnas: scene, slate, take, start TC, duración, circled, channels.
- Filtro por `circled only`.
- Enlace a cada take.

### `SoundTakeDetailPage.tsx`

- Metadata completa del take: scene, slate, take, start/end TC, FPS, sample rate, bit depth, channels, duración.
- Lista de tracks con `track_name`, `character_name`, `mic_source`.
- Sección "Raw metadata" colapsable con `raw_ixml_json`, `raw_bext_json`, `raw_report_json`.
- Enlace al sound report original (si existe) y al archivo de preservación.

## 10. Integraciones opcionales posteriores

Estas integraciones no se incluyen en el MVP pero se documentan como camino evolutivo:

- **Dropbox / Cantar backup** — algunos sonidistas suben a Dropbox desde el grabador. La ingest puede monitorizar una carpeta Dropbox sincronizada localmente.
- **Frame.io C2C webhook** — cuando un take se enlaza a un asset de Frame.io, se puede propagar el estado de aprobación a la fila `sound_takes`.
- **n8n automation** — disparadores en lote: al cerrar una `batch`, generar emails de QC, notificar al montador, etc.
- **DaVinci Resolve / Avid / ALE export** — `sound_takes` se puede exportar a ALE para enlazar con el flujo de edición. El módulo ya ingesta ALE, lo que allana el camino.
- **Postproducción de sonido** — enlace a Pro Tools / Reaper / iZotope RX vía AAF/OMF o CSV; los IDs de take de CID pueden ser referenciados desde herramientas externas.

## 11. Riesgos

| Riesgo | Mitigación propuesta |
|---|---|
| Metadata inconsistente entre marcas | Adapter layer + `adapter_used` por fila + `parse_status` (`ok`/`partial`/`failed`) + `parse_errors` jsonb. |
| Timecode / FPS ambiguo | Validar que `start_tc` parsea como `HH:MM:SS:FF`; exigir `fps` consistente entre iXML y el sound report. Marcar inconsistencias. |
| PDF parsing frágil | No usar PDF como fuente primaria. Intentar parsear y degradar a `parse_status=partial` con metadatos vacíos si falla. El PDF se preserva tal cual como artefacto. |
| Duplicados | Idempotencia por `checksum_sha256` único por proyecto. Re-ingest de un mismo archivo se ignora o se ofrece merge manual. |
| Archivos incompletos durante copia | Hash streaming; verificar tamaño esperado al cierre; abortar la batch si la copia falla. |
| Encoding de CSV/ALE | Detector de encoding (UTF-8 BOM, UTF-16 BOM, Latin-1 fallback). Normalización a UTF-8 antes de persistir. |
| Seguridad sobre archivos originales | Originales en modo read-only para el proceso del backend. Solo la copia de preservación y los proxies son escribibles. Permisos de filesystem reforzados en la carpeta de ingest. |

## 12. Fases futuras sugeridas

| Fase | Scope |
|---|---|
| `CID.SOUND.INGEST.FIELD_RECORDERS.MODELS.1` | Crear migraciones Alembic + modelos SQLAlchemy para `sound_ingest_batches`, `sound_source_files`, `sound_rolls`, `sound_takes`, `sound_tracks`, `sound_reports`. |
| `CID.SOUND.INGEST.FIELD_RECORDERS.PARSERS.1` | Implementar `bwf_parser`, `ixml_parser`, `bext_parser`, `ale_parser`, `csv_report_parser`, `pdf_report_parser`. |
| `CID.SOUND.INGEST.FIELD_RECORDERS.SERVICE.1` | Implementar `ingest_service`, `checksum_service`, `recorder_detector`, watcher de carpeta, e integrar parsers. |
| `CID.SOUND.INGEST.FIELD_RECORDERS.ROUTES.1` | Implementar las rutas de `POST /preview`, `POST /batches`, `POST /confirm`, `GET /batches`, `GET /rolls`, `GET /takes`, `GET /reports` con el contrato de gating consolidado. |
| `CID.SOUND.INGEST.FIELD_RECORDERS.FRONTEND.1` | Implementar `SoundIngestPage`, `SoundRollDetailPage`, `SoundTakeDetailPage`. |
| `CID.SOUND.INGEST.CANTAR.ADAPTER.1` | `aaton_cantar_adapter.py` con soporte Cantar 3 / X3 / X3 Mini. |
| `CID.SOUND.INGEST.SOUND_DEVICES.ADAPTER.1` | `sound_devices_adapter.py` con soporte 6-Series, 8-Series, MixPre II. |
| `CID.SOUND.INGEST.ZOOM_F_SERIES.ADAPTER.1` | `zoom_f_series_adapter.py` con soporte F6, F8, F8n, F8n Pro. |

## Referencias

- `docs/architecture/backend_gating_contract_v1.md` — contrato de gating backend.
- `docs/architecture/cid_backend_gating_policy_v1.md` — política general de gating.
- `/tmp/cid_backend_gating_closure_audit_7.md` — baseline de cierre del bloque de gating.
- Estándares EBU TECH 3285 (BWF), iXML 2.0, Avid Log Exchange (ALE).
