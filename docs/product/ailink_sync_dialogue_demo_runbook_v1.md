# AILink Sync Dialogue — Demo Runbook v1

## 1. Título

**AILink Sync Dialogue — Demo Runbook v1**

Runbook práctico para preparar y enseñar el prototipo local de AILink Sync Dialogue a productoras, escuelas de cine, equipos de montaje y beta testers.

## 2. Estado actual de la herramienta

AILink Sync Dialogue es actualmente un prototipo local de ingesta y sincronía sugerida para montaje. La herramienta está pensada para convertir una carpeta de rodaje en un conjunto de informes simples y revisables por el equipo editorial.

Estado actual:

- Analiza carpetas locales.
- Detecta archivos de vídeo y audio soportados.
- Extrae metadata técnica si `ffprobe` está disponible.
- Sugiere posibles matches vídeo/audio por timecode, nombre, carpeta y duración.
- Genera `JSON`, `CSV` y un reporte `HTML` imprimible.
- No sube material audiovisual a la nube.
- No depende de CID SaaS para funcionar.

Esta demo no enseña una herramienta final cerrada. Enseña una primera pieza independiente y concreta de AILinkCinema para validar utilidad real con usuarios de postproducción.

## 3. Qué problema demuestra

La demo debe mostrar un problema audiovisual reconocible: el material de rodaje suele llegar a montaje con archivos dispersos, audio separado y poca claridad técnica.

Problemas que se demuestran:

- Mucho material disperso en carpetas de cámara, sonido y notas.
- Audio y vídeo separados que deben relacionarse antes de editar.
- Metadata difícil de revisar manualmente archivo por archivo.
- Necesidad de detectar posibles sincronías antes de abrir el proyecto de montaje.
- Necesidad de entregar un informe legible a montaje o postproducción.

El mensaje central: **la herramienta no monta ni decide por el editor; prepara el material para que montaje empiece con más orden.**

## 4. Público objetivo de la demo

La demo está pensada para:

- Escuelas de cine.
- Productoras pequeñas y medianas.
- Ayudantes de montaje.
- DIT/data wranglers.
- Equipos de postproducción.
- Coordinadores de producción.

El perfil ideal es alguien que recibe material real de rodaje y necesita saber rápidamente qué hay, qué falta, qué tiene metadata y qué posibles parejas de vídeo/audio existen.

## 5. Requisitos locales

Requisitos para ejecutar la demo:

- WSL, Linux, macOS o un entorno con Python compatible con el proyecto.
- Python del proyecto dentro de `.venv`.
- `ffprobe` recomendado para metadata real.
- Acceso a una carpeta local de prueba.
- No requiere GPU.
- No requiere ComfyUI.
- No requiere servidor.
- No requiere CID SaaS.
- No requiere cloud ni subida de material.

Si `ffprobe` no está disponible, usar `--no-probe` o explicar que el escaneo sigue funcionando pero sin metadata técnica profunda.

## 6. Estructura recomendada de carpeta demo

Estructura sugerida:

```text
demo_sync_dialogue/
  video/
    scene01_take01.mov
    scene01_take02.mov
  audio/
    scene01_take01.wav
    scene01_take02.wav
  notes/
    readme.txt
```

Para una demo real, los archivos pueden ser pequeños o dummy, pero deben usar extensiones reales. Si se quiere enseñar metadata real, conviene usar archivos que `ffprobe` pueda leer correctamente.

Recomendación: preparar una carpeta controlada antes de la reunión para evitar enseñar rutas sensibles o material privado de terceros.

## 7. Comando de ejecución

Activación del entorno:

```bash
cd /opt/SERVICIOS_CINE
source .venv/bin/activate
```

Comando principal:

```bash
python scripts/ailink_sync_dialogue_scan.py \
  --input /ruta/a/demo_sync_dialogue \
  --output-dir /ruta/a/demo_sync_dialogue_output
```

Variante sin `ffprobe`:

```bash
python scripts/ailink_sync_dialogue_scan.py \
  --input /ruta/a/demo_sync_dialogue \
  --output-dir /ruta/a/demo_sync_dialogue_output \
  --no-probe
```

No usar rutas Windows en esta demo. Usar rutas reales del entorno WSL/Linux/macOS.

## 8. Outputs esperados

La CLI genera cuatro archivos principales:

### `scan_result.json`

Sirve como export completo y estructurado del análisis. Contiene resumen, media detectada y sugerencias de matching. Lo usaría un equipo técnico, una futura integración o una fase posterior del producto.

Valor: deja una base portable para automatizaciones futuras sin depender de una interfaz.

### `media_files.csv`

Contiene la tabla de archivos de vídeo/audio detectados, con metadata como duración, timecode, fps, canales, codec, formato y estado de `ffprobe`.

Lo usaría un montador, ayudante de montaje, DIT o coordinador que quiera revisar el material en una hoja de cálculo.

Valor: transforma carpetas dispersas en una tabla legible.

### `match_suggestions.csv`

Contiene las posibles parejas vídeo/audio sugeridas por la herramienta, con estrategia, score, confianza y razones explicables.

Lo usaría un ayudante de montaje o editor como lista de candidatos para revisar, no como sincronización automática garantizada.

Valor: acelera la revisión inicial de audio separado.

### `report.html`

Reporte visual para abrir en navegador. Incluye resumen, alertas, tablas de vídeo, tablas de audio y matches sugeridos.

Lo usaría cualquier persona del equipo para entender el estado del material sin abrir CSV o JSON.

Valor: es el output más adecuado para demo comercial y revisión humana.

## 9. Cómo abrir el reporte

Abrir `report.html` con cualquier navegador moderno.

El HTML está pensado para revisión humana y para imprimir/exportar manualmente a PDF desde el navegador si hace falta.

No hay PDF real automático todavía. En esta fase, el PDF se obtiene manualmente desde el navegador con la función de imprimir o guardar como PDF.

## 10. Guion de demo de 2 minutos

### `0:00-0:20` — Problema

“En rodajes pequeños o de escuela, el material suele llegar a montaje como una carpeta con vídeos, audios separados y notas. Antes de editar, alguien tiene que revisar qué hay, qué metadata existe y qué audios podrían corresponder a cada clip.”

### `0:20-0:40` — Carpeta local

Mostrar la carpeta `demo_sync_dialogue/` con subcarpetas `video/`, `audio/` y `notes/`.

“La herramienta trabaja localmente sobre esta carpeta. El material no sale del disco del cliente.”

### `0:40-1:10` — Ejecución CLI

Ejecutar el comando principal.

“El prototipo escanea la carpeta, detecta vídeo/audio, intenta leer metadata con `ffprobe` si está disponible y genera archivos de salida para montaje.”

### `1:10-1:40` — Revisión del HTML

Abrir `report.html`.

Mostrar:

- Resumen de archivos.
- Alertas.
- Tabla de vídeo.
- Tabla de audio.
- Matches sugeridos.

“Esto no sustituye al montador. Le entrega una primera lectura clara del material para empezar con más orden.”

### `1:40-2:00` — Valor y evolución

“Ahora mismo es una herramienta local y concreta. La siguiente evolución es endurecer la demo, añadir PDF real, transcripción básica, sincronía por waveform e integración con editores o con el workflow completo de AILinkCinema.”

Cerrar con llamada a beta privada: “Estamos buscando equipos que prueben esto con material real y nos digan qué ahorra tiempo de verdad.”

## 11. Frases comerciales recomendadas

- “El material no sale del disco del cliente.”
- “Esto no sustituye al montador: prepara el material para que el montaje empiece con más orden.”
- “La herramienta detecta candidatos de sincronía, no fuerza decisiones automáticas.”
- “El informe se puede entregar a montaje o postproducción.”
- “Convierte una carpeta de rodaje en una tabla y un informe entendible.”
- “Es útil para escuelas, productoras pequeñas y equipos que no tienen DIT dedicado.”
- “Es una primera pieza independiente de AILinkCinema; dentro de CID esto podrá conectarse con todo el workflow.”
- “La demo actual valida el valor operativo antes de construir una interfaz completa.”

## 12. Limitaciones actuales

Decirlo con claridad durante la demo si preguntan:

- No hay waveform sync todavía.
- No hay transcripción todavía.
- No hay detección de claqueta visual todavía.
- No hay UI gráfica todavía.
- No hay instalador todavía.
- No hay integración con DaVinci Resolve, Avid Media Composer o Adobe Premiere Pro todavía.
- No hay cloud.
- No hay CID SaaS conectado todavía.
- El matching actual es una sugerencia basada en metadata, nombre, duración y timecode.

No presentar las sugerencias como sincronías garantizadas. Presentarlas como una lista de candidatos para revisión humana.

## 13. Próximas mejoras recomendadas

Orden recomendado:

1. Crear demo fixtures o carpeta de ejemplo controlada.
2. Hardening de HTML/CLI.
3. PDF real o export automático.
4. Transcripción básica.
5. Waveform sync.
6. Integración con editores.
7. UI local.
8. Instalador.

## 14. Checklist antes de enseñar

- [ ] Repo limpio.
- [ ] `.venv` activado.
- [ ] `ffprobe` disponible o decisión clara de usar `--no-probe`.
- [ ] Carpeta demo preparada.
- [ ] Output dir vacío o controlado.
- [ ] Comando probado antes de la llamada.
- [ ] `report.html` abre correctamente.
- [ ] No enseñar rutas internas sensibles.
- [ ] Explicar limitaciones antes de que parezcan fallos.
- [ ] Tener una frase clara de beta privada.

## 15. Checklist después de enseñar

- [ ] Anotar dudas del cliente.
- [ ] Preguntar si usan DaVinci Resolve, Avid Media Composer o Adobe Premiere Pro.
- [ ] Preguntar cómo organizan sonido en rodaje.
- [ ] Preguntar si trabajan con timecode.
- [ ] Preguntar quién prepara el material antes de montaje.
- [ ] Preguntar si pagarían una beta de bajo coste.
- [ ] Registrar feedback sobre outputs: HTML, CSV, JSON y matches sugeridos.
- [ ] Identificar el siguiente caso real para prueba controlada.

## 16. Criterios de aceptación

Este runbook se considera aceptado si:

- Está escrito en español claro.
- Es práctico y ejecutable.
- No contiene promesas falsas.
- No sugiere subir material sensible.
- No menciona funcionalidades inexistentes como si estuvieran hechas.
- Distingue estado actual frente a evolución futura.
- Sirve para que Juan Carlos pueda hacer la demo sin improvisar.
