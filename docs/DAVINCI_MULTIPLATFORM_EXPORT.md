# DaVinci Resolve Multiplatform Export

## Overview

CID puede exportar paquetes FCPXML para DaVinci Resolve en múltiples plataformas:
- Windows
- macOS
- Linux
- Offline/relink manual

## Platform URI Examples

### Windows

```xml
<asset id="r2" name="S1_SH1_TK1" 
       src="file:///C:/CID_DaVinci_Export/media/S1_SH1_TK1.mov"
       start="0s" duration="288/24s" 
       hasVideo="1" hasAudio="1" format="r1" />
```

### macOS

```xml
<asset id="r2" name="S1_SH1_TK1" 
       src="file:///Users/CLIENTE/CID_DaVinci_Export/media/S1_SH1_TK1.mov"
       start="0s" duration="288/24s" 
       hasVideo="1" hasAudio="1" format="r1" />
```

O si el archivo está en un volumen externo:

```xml
<asset id="r2" name="S1_SH1_TK1" 
       src="file:///Volumes/DRIVE_NAME/CID_DaVinci_Export/media/S1_SH1_TK1.mov"
       start="0s" duration="288/24s" 
       hasVideo="1" hasAudio="1" format="r1" />
```

### Linux

```xml
<asset id="r2" name="S1_SH1_TK1" 
       src="file:///home/CLIENTE/CID_DaVinci_Export/media/S1_SH1_TK1.mov"
       start="0s" duration="288/24s" 
       hasVideo="1" hasAudio="1" format="r1" />
```

O para montajes:

```xml
<asset id="r2" name="S1_SH1_TK1" 
       src="file:///mnt/DRIVE_NAME/CID_DaVinci_Export/media/S1_SH1_TK1.mov"
       start="0s" duration="288/24s" 
       hasVideo="1" hasAudio="1" format="r1" />
```

### Offline/Relink Manual

```xml
<asset id="r2" name="S1_SH1_TK1" 
       src="file:///tmp/S1_SH1_TK1.mov"
       start="0s" duration="288/24s" 
       hasVideo="1" hasAudio="1" format="r1" />
```

## API Endpoint

```
POST /api/projects/{project_id}/editorial/export/davinci-package
```

### Request Body

```json
{
  "platform": "windows",
  "root_path": "C:/CID_Project",
  "include_media": false,
  "audio_mode": "conservative"
}
```

### Parameters

| Parameter | Type | Description | Default |
|-----------|------|--------------|---------|
| platform | string | Target platform | "windows" |
| root_path | string | Root path for media | Platform default |
| include_media | boolean | Include media in package | false |
| audio_mode | string | Audio export mode | "conservative" |

### Platform Values

- `windows` - Windows path (C:/)
- `mac` - macOS path (/Users/ or /Volumes/)
- `linux` - Linux path (/home/ or /mnt/)
- `offline` - Offline with /tmp paths
- `all` - Generate all platforms

## Export Options

### Audio Mode

- **conservative**: Audio as external resource with note (SAFE)
- **experimental**: Audio on separate synchronized track (CANDIDATE)

Recommendation: Use `conservative` for production. The experimental mode requires manual DaVinci validation.

## Package Contents

Each platform export includes:

1. **assembly_{platform}.fcpxml** - FCPXML for the platform
2. **media_relink_report_{platform}.json** - Media paths for relinking
3. **README_IMPORT_DAVINCI.md** - Import instructions

## How to Use

### 1. Generate Package

Using the API:

```bash
curl -X POST "http://127.0.0.1:8010/api/projects/{project_id}/editorial/export/davinci-package" \
  -H "Content-Type: application/json" \
  -d '{"platform": "windows", "root_path": "C:/My_Project"}'
```

### 2. Download FCPXML

The API returns a file download.

### 3. Prepare Media Folder

Create the media folder at the root path:

```
C:/My_Project/
└── media/
    ├── S1_SH1_TK1.mov
    ├── S1_SH1_TK1.wav
    ├── S1_SH2_TK1.mov
    └── S1_SH2_TK1.wav
```

### 4. Import into DaVinci

1. Open DaVinci Resolve
2. File > Import > Timeline > Import AAF, EDL, XML...
3. Select the downloaded FCPXML
4. Verify timeline loads correctly

### 5. Relink Media (if needed)

If clips show as offline:
1. Select offline clips
2. File > Relink Selected Clips...
3. Navigate to media folder
4. Select matching files

## Troubleshooting

### Clips Offline

Check `media_relink_report.json` for correct paths. Verify media files are named correctly.

### Wrong Platform Path

Regenerate package with correct platform value. The path is set at export time.

### Audio Not Synced

Use conservative mode for reliable audio. The experimental mode requires manual verification.

## Platform Differences

| Platform | Path Format | External Drive Support |
|----------|------------|---------------------|
| Windows | C:/ | Yes (D:, E:, etc.) |
| macOS | /Users/ | Yes (/Volumes/) |
| Linux | /home/ | Yes (/mnt/) |

## Limitations

- Linked audio experimental requires DaVinci validation
- Media must be on same filesystem for relink
- Long path names may cause issues on Windows

## Next Steps

1. Test import on each platform
2. Validate audio sync behavior
3. Document any platform-specific issues

---

## Flujo Operativo: Media ya Ingestada

CID NO es el sistema de ingesta física.

### Flujo Real de Producción

1. **DaVinci Resolve o DIT ingesta el material** de la tarjeta de memoria al sistema de almacenamiento.
2. **El usuario proporciona la ruta raíz** donde está la media ya ingestada.
3. **CID escanea e indexa** los archivos existentes.
4. **CID lee metadata** (BWF/iXML) de los archivos.
5. **CID cruza con reports** de cámara y sonido.
6. **CID crea Takes** con referencias a la media existente.
7. **CID genera AssemblyCut** desde las tomas recomendadas.
8. **CID exporta FCPXML** apuntando a la ruta original.

### Comportamiento Clave

- **CID no mueve archivos**:lee la ubicación existente.
- **CID no copia archivos**: salvo que `include_media=true`.
- **CID no renombra archivos**: respeta estructura de carpetas.
- **include_media=false**: FCPXML apunta a la ruta original de los archivos.
- **include_media=true**: CID copia los archivos al paquete portable.

### Ruta de Media (Media Root Path)

El usuario proporciona la ruta donde el material ya fue ingestado por DaVinci/DIT:

| Plataforma | Ejemplo de ruta |
|-------------|----------------|
| Windows | `D:/PROYECTO/MEDIA` |
| macOS | `/Volumes/PROYECTO/MEDIA` o `/Users/usuario/PROYECTO/MEDIA` |
| Linux | `/mnt/proyecto/media` o `/home/usuario/proyecto/media` |

### Paquetes Portables

- **Paquete con include_media=false**: Ligero, solo FCPXML. Requiere que la media exista en la ruta especificada.
- **Paquete con include_media=true**: Pesado, incluye copia de media para portability.

---

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

- **Qué es**: Camera reports, sound reports, script notes, director notes, hojas de script, PDFs, CSVs, XLSX, DOCX, TXT, MD.
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