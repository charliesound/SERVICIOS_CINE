# AILink Sync Dialogue — Real Metadata Demo v1

## Objetivo

Esta demo crea outputs de AILink Sync Dialogue con metadata controlada para enseñar matching real sin usar material sensible ni archivos audiovisuales pesados.

El script no lee carpetas de cámara, no ejecuta `ffprobe` y no crea media real. Construye un resultado de escaneo en memoria con vídeos y audios simulados, ejecuta el motor de matching y genera los mismos outputs que la CLI principal.

## Diferencia frente a la demo dummy

La demo dummy valida ingesta, tablas, CSV, JSON y reporte HTML con archivos placeholder. Como esos archivos no tienen duración ni timecode reales, las sugerencias de matching suelen ser cero.

Esta demo usa metadata controlada para enseñar:

- Timecode exacto.
- Duración cercana.
- Tokens compartidos en nombres.
- Score, confidence y reasons.
- Visualización de matches en CSV y HTML.

## Comando de ejecución

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate

python scripts/demo/create_sync_dialogue_metadata_demo.py \
  --output-dir /tmp/ailink_sync_dialogue_metadata_demo \
  --force
```

## Outputs esperados

En el directorio de salida aparecen:

- `scan_result.json`
- `media_files.csv`
- `match_suggestions.csv`
- `report.html`

Conteos esperados:

- 3 vídeos.
- 4 audios.
- Al menos 2 matches high por timecode.
- Al menos 1 match por duración/nombre.

## Matches que deberían verse

- `video/scene01_take01.mov` con `audio/scene01_take01.wav` por timecode `01:00:00:00`.
- `video/scene01_take02.mov` con `audio/scene01_take02.wav` por timecode `01:00:20:00`.
- `video/scene02_take01.mxf` con `audio/scene02_take01.wav` por duración cercana y tokens compartidos.
- `audio/wildtrack_roomtone.wav` no debería aparecer como high confidence.

## Cómo abrir report.html

Abrir manualmente:

```text
/tmp/ailink_sync_dialogue_metadata_demo/report.html
```

El HTML debe mostrar la tabla de match suggestions con confidence, score, strategy, reasons y duration delta.

## Qué demuestra

- Matching por timecode exacto.
- Matching secundario por duración/nombre/carpeta.
- Score y confidence explicables.
- Reasons legibles para revisar por qué se sugirió un match.
- Export consistente en JSON, CSV y HTML.

## Qué no demuestra

- Lectura real de `ffprobe`.
- Análisis de waveform.
- Transcripción.
- Claqueta visual.
- Integración con editores.
- Compatibilidad real con cámaras o grabadoras específicas.

## Cómo usarlo en una reunión

1. Ejecutar el comando con `--force` antes de la reunión.
2. Abrir `report.html`.
3. Mostrar primero el summary.
4. Ir a la tabla de match suggestions.
5. Explicar que los dos primeros matches son por timecode exacto.
6. Explicar que el tercero es una sugerencia secundaria por duración/nombre.
7. Aclarar que es metadata simulada/controlada, no media real.

## Explicación honesta

Esta demo no pretende falsear una lectura de cámara. Su objetivo es enseñar cómo se verá el matching cuando existan duration, timecode y nombres útiles. Para validar compatibilidad real hará falta una demo posterior con media mínima válida o material autorizado por el cliente.
