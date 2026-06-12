# AILink Sync Dialogue — Demo Fixture v1

## Objetivo

Esta fixture permite enseñar AILink Sync Dialogue sin usar material real, sensible o de terceros. Genera una carpeta de demo pequeña, reproducible y segura con archivos dummy que tienen extensiones audiovisuales reales.

La fixture sirve para validar ingesta, detección de tipos, exports y reporte HTML. No sirve para demostrar metadata real, timecode real ni sincronía real porque los archivos no son media válida.

## Cómo generar la carpeta demo

Desde el repositorio:

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate

python scripts/demo/create_sync_dialogue_demo_fixture.py \
  --output-dir /tmp/ailink_sync_dialogue_demo_fixture \
  --force
```

El script crea:

```text
/tmp/ailink_sync_dialogue_demo_fixture/
  demo_sync_dialogue/
    video/
      scene01_take01.mov
      scene01_take02.mov
      scene02_take01.mxf
    audio/
      scene01_take01.wav
      scene01_take02.wav
      scene02_take01.wav
    notes/
      readme.txt
```

Los archivos `.mov`, `.mxf` y `.wav` son texto dummy pequeño con contenido identificable como `dummy demo fixture, not real media`.

## Cómo ejecutar el scanner

Usar `--no-probe` porque los archivos son dummy y no media real:

```bash
python scripts/ailink_sync_dialogue_scan.py \
  --input /tmp/ailink_sync_dialogue_demo_fixture/demo_sync_dialogue \
  --output-dir /tmp/ailink_sync_dialogue_demo_output \
  --no-probe
```

## Outputs esperados

En `/tmp/ailink_sync_dialogue_demo_output` deben aparecer:

- `scan_result.json`
- `media_files.csv`
- `match_suggestions.csv`
- `report.html`

Conteos esperados:

- `video_count`: 3
- `audio_count`: 3
- `unsupported_count`: 1 por `notes/readme.txt`, si el scanner cuenta archivos no soportados

En esta demo, las sugerencias de matching pueden ser inexistentes porque no hay duración ni timecode reales. Esta fixture valida ingesta, tablas, outputs y reporte. Para enseñar matching real hará falta una demo posterior con media mínima válida o metadata controlada por otro mecanismo de prueba.

## Cómo abrir el reporte

Abrir:

```text
/tmp/ailink_sync_dialogue_demo_output/report.html
```

El reporte se abre en navegador y puede imprimirse o guardarse manualmente como PDF desde el propio navegador. No hay PDF automático en esta fase.

## Qué muestra esta demo

- Que la herramienta escanea carpetas locales.
- Que detecta vídeos y audios por extensión.
- Que genera JSON, CSV y HTML.
- Que el reporte se puede enseñar sin material privado.
- Que el material no se sube a servidores.

## Qué no muestra esta demo

- Metadata real de cámara o grabadora.
- Timecode real.
- Sincronía real vídeo/audio.
- Waveform sync.
- Transcripción.
- Claqueta visual.
- Integración con editores.
- Interfaz gráfica.

## Uso antes de una reunión

Checklist recomendado:

- [ ] Regenerar fixture con `--force`.
- [ ] Borrar o controlar el output anterior.
- [ ] Ejecutar scanner con `--no-probe`.
- [ ] Abrir `report.html` antes de la llamada.
- [ ] Confirmar que no aparecen rutas sensibles en pantalla.
- [ ] Explicar claramente que son archivos dummy, no media real.

## Limpieza de `/tmp`

Si se desea limpiar la demo después de la reunión:

```bash
rm -rf /tmp/ailink_sync_dialogue_demo_fixture
rm -rf /tmp/ailink_sync_dialogue_demo_output
```

Usar estos comandos solo con rutas controladas de demo.

## Advertencia

Esta fixture no contiene media real. No representa compatibilidad con cámaras, grabadoras, timecode o metadata propietaria. Es una demo segura para enseñar flujo, outputs y reporte sin exponer material sensible.
