# AILink Sync Dialogue — Demo End-to-End v1

## Objetivo

Este documento explica cómo ejecutar la demo end-to-end reproducible de AILink Sync Dialogue con un solo comando. El runner crea una fixture dummy segura, ejecuta el scanner con `--no-probe`, genera outputs y valida que existan.

La demo está diseñada para enseñar el flujo completo sin material real sensible y sin depender de `ffprobe`, red, cloud, CID SaaS ni servicios externos.

## Cuándo usarlo

Usar este runner antes de una reunión, demo interna o validación rápida cuando se necesita confirmar que el flujo base funciona:

1. Crear fixture demo.
2. Ejecutar scanner local.
3. Generar `JSON`, `CSV` y `HTML`.
4. Abrir `report.html` manualmente.

No usarlo para demostrar metadata real, timecode real o sincronía real. La fixture contiene archivos dummy.

## Comando recomendado

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate

python scripts/demo/run_sync_dialogue_demo_e2e.py \
  --work-dir /tmp/ailink_sync_dialogue_demo_e2e \
  --force
```

`--force` permite regenerar `fixture/` y `output/` si ya existen dentro del work-dir.

## Estructura generada

```text
/tmp/ailink_sync_dialogue_demo_e2e/
  fixture/
    demo_sync_dialogue/
      video/
      audio/
      notes/
  output/
    scan_result.json
    media_files.csv
    match_suggestions.csv
    report.html
```

El runner nunca debe borrar el `work-dir` entero. Con `--force`, borra solo `work-dir/fixture` y `work-dir/output`.

## Outputs esperados

- `scan_result.json`: resultado completo estructurado.
- `media_files.csv`: tabla de vídeos/audios detectados.
- `match_suggestions.csv`: tabla de sugerencias de matching.
- `report.html`: reporte imprimible para demo.

Conteos esperados en esta fixture:

- Video count: 3
- Audio count: 3
- Unsupported count: 1
- Match suggestions count: 0 normalmente, porque los archivos son dummy y no tienen metadata real.

## Cómo abrir report.html

Abrir manualmente el archivo:

```text
/tmp/ailink_sync_dialogue_demo_e2e/output/report.html
```

No se abre navegador automáticamente. Si el navegador del sistema no encuentra rutas de WSL, copiar la ruta de salida o abrir el archivo desde el explorador compatible con el entorno local. No usar esta fase para automatizar apertura de navegador.

## Qué valida esta demo

- El generador de fixture funciona.
- El scanner detecta vídeos/audios por extensión.
- Los archivos dummy no requieren media real.
- Se generan los cuatro outputs esperados.
- El reporte HTML existe y puede abrirse manualmente.
- La demo puede repetirse con `--force`.

## Qué no valida

- Lectura real de `ffprobe`.
- Metadata real de cámara o sonido.
- Timecode real.
- Matching real basado en duración/timecode.
- Waveform sync.
- Transcripción.
- Claqueta visual.
- Integración con DaVinci, Avid o Premiere.
- UI gráfica o instalador.

## Por qué usa `--no-probe`

La fixture contiene archivos de texto pequeños con extensiones audiovisuales. No son media real. Por eso el runner ejecuta el scanner con `--no-probe`: se valida ingesta, exports y reporte sin depender de `ffprobe` ni de binarios audiovisuales reales.

## Troubleshooting básico

### La ruta ya existe

Si aparece un error indicando que `fixture` u `output` ya existen, ejecutar con `--force` o elegir otro `--work-dir`.

### Falta `--force`

El runner no sobrescribe carpetas existentes por defecto. Esta protección evita borrar resultados por accidente.

### Permisos

Si `/tmp` no permite escritura en un entorno concreto, usar otra ruta local controlada, por ejemplo una carpeta temporal dentro del home del usuario.

### No puedo abrir el HTML desde WSL

El runner imprime la ruta exacta de `report.html`. Abrirla manualmente con el navegador o desde un explorador compatible. No forma parte de esta fase abrir navegador automáticamente.

## Checklist antes de reunión

- [ ] Ejecutar el runner con `--force`.
- [ ] Confirmar que termina con exit code 0.
- [ ] Confirmar que `report.html` existe.
- [ ] Abrir `report.html` manualmente antes de enseñar.
- [ ] Preparar explicación: archivos dummy, no media real.
- [ ] Explicar que matching real requiere metadata o media válida.
- [ ] No enseñar rutas sensibles.

## Checklist después de reunión

- [ ] Anotar preguntas sobre metadata, timecode y formatos.
- [ ] Preguntar si el usuario necesita demo con media real mínima.
- [ ] Preguntar qué export le resulta más útil: HTML, CSV o JSON.
- [ ] Registrar si entiende el valor de una demo local sin cloud.
- [ ] Decidir si la siguiente demo debe incluir `ffprobe` real.

## Siguiente paso recomendado

Preparar una fixture con media mínima válida o metadata controlada para enseñar matching real sin usar material sensible. Esa fase debe seguir evitando cloud, backend CID y archivos pesados.
