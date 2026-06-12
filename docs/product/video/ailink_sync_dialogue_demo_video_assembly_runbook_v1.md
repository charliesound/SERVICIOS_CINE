# AILink Sync Dialogue — Demo Video Assembly Runbook v1

## 1. Objetivo

Este runbook define cómo preparar, grabar y montar el vídeo demo comercial de AILink Sync Dialogue a partir de los materiales ya existentes.

La fase no crea un vídeo final. No renderiza MP4. No genera audio. No crea nuevos assets visuales. No toca frontend, backend, CID SaaS, Supabase, CRM, tracking, cookies ni runtime.

El objetivo es que, cuando se decida producir el vídeo, exista una guía clara para grabarlo con mensaje comercial consistente, limitaciones honestas y material controlado.

## 2. Materiales de entrada

Materiales ya disponibles:

- `docs/product/video/ailink_sync_dialogue_demo_video_script_v1.md`
- `docs/product/video/ailink_sync_dialogue_demo_video_subtitles_es_v1.srt`
- `docs/product/video/ailink_sync_dialogue_demo_video_voiceover_es_v1.txt`
- `docs/product/video/ailink_sync_dialogue_demo_video_subtitles_readme_v1.md`
- `docs/product/assets/ailink_sync_dialogue/hero-report-mockup.png`
- `docs/product/assets/ailink_sync_dialogue/report-summary.png`
- `docs/product/assets/ailink_sync_dialogue/match-suggestions-table.png`
- `docs/product/assets/ailink_sync_dialogue/media-files-table.png`
- `docs/product/assets/ailink_sync_dialogue/privacy-local-first.png`
- `docs/product/assets/ailink_sync_dialogue/linkedin-beta-card.png`
- `docs/product/demo/ailink_sync_dialogue_real_metadata_demo/expected_outputs/report.html`
- `docs/product/demo/ailink_sync_dialogue_real_metadata_demo/expected_outputs/media_files.csv`
- `docs/product/demo/ailink_sync_dialogue_real_metadata_demo/expected_outputs/match_suggestions.csv`
- `docs/product/demo/ailink_sync_dialogue_real_metadata_demo/expected_outputs/scan_result.json`

## 3. Non-goals

Esta fase no debe:

- Crear MP4.
- Crear WAV.
- Crear locución real.
- Crear capturas nuevas.
- Crear assets binarios nuevos.
- Modificar el guion.
- Modificar subtítulos.
- Modificar la landing.
- Implementar formulario.
- Implementar CRM.
- Implementar Supabase.
- Implementar tracking.
- Tocar `.env`.
- Tocar Docker.
- Tocar runtime.
- Tocar backend CID.
- Tocar frontend.
- Añadir dependencias.

## 4. Mensaje central del vídeo

Mensaje:

AILink Sync Dialogue prepara el material audiovisual antes de entrar en montaje: escanea una carpeta local, detecta vídeo y audio, extrae metadata cuando está disponible, sugiere relaciones entre vídeo y audio y genera salidas revisables para el equipo.

El vídeo debe insistir en cuatro ideas:

1. Trabajo local-first.
2. Preparación previa al montaje.
3. Sugerencias explicables, no decisiones automáticas.
4. Beta privada con limitaciones honestas.

## 5. Claims permitidos

Se puede decir:

- Escanea carpetas locales.
- Detecta archivos de vídeo y audio.
- Usa metadata disponible cuando existe.
- Puede usar ffprobe si está disponible.
- Genera report.html.
- Genera media_files.csv.
- Genera match_suggestions.csv.
- Genera scan_result.json.
- Sugiere candidatos de relación vídeo/audio.
- Muestra score y razones explicables.
- Funciona como prototipo local.
- Está orientado a beta privada.
- No necesita subir material audiovisual a la nube para esta demo controlada.

## 6. Claims prohibidos

No se debe decir:

- Que sincroniza todo automáticamente.
- Que sustituye al montador.
- Que ya integra DaVinci Resolve, Avid o Premiere.
- Que ya hace waveform sync.
- Que ya transcribe diálogo.
- Que ya reconoce claqueta visual.
- Que ya es producto final.
- Que ya tiene instalador.
- Que ya es SaaS público.
- Que el usuario debe subir material audiovisual.
- Que garantiza cumplimiento legal.
- Que garantiza resultados perfectos.

Frases críticas que deben quedar prohibidas de forma explícita:

- No se debe prometer waveform sync.
- No se debe prometer transcripción.
- No se debe prometer detección de claqueta visual.
- No se pide subir material audiovisual.

## 7. Duración recomendada

Versiones recomendadas:

- Versión principal: 90 segundos.
- Versión corta: 30 a 45 segundos.
- Versión extendida: máximo 2 minutos.

Para primera publicación comercial se recomienda versión principal de 90 segundos.

## 8. Estructura de montaje recomendada

### 8.1 Apertura

Duración aproximada: 0 a 8 segundos.

Visual:

- Título limpio.
- Logo o marca AILinkCinema si existe asset aprobado.
- Texto: “Prepara vídeo, audio y metadata antes de entrar en montaje”.

Locución:

- Usar las primeras líneas del archivo de locución.

Objetivo:

- Explicar el problema sin tecnicismo excesivo.

### 8.2 Problema

Duración aproximada: 8 a 20 segundos.

Visual:

- Carpeta demo o mockup de archivos.
- Referencia a vídeo, audio separado, nombres, timecode y duración.

Mensaje:

- Antes de editar, alguien tiene que entender qué hay en el material.

### 8.3 Qué hace la herramienta

Duración aproximada: 20 a 45 segundos.

Visual:

- Reporte HTML.
- Tabla de media files.
- Tabla de match suggestions.

Mensaje:

- Escanea.
- Organiza metadata.
- Sugiere relaciones.
- Explica razones.

### 8.4 Salidas

Duración aproximada: 45 a 65 segundos.

Visual:

- `report.html`
- `media_files.csv`
- `match_suggestions.csv`
- `scan_result.json`

Mensaje:

- El equipo recibe salidas revisables y exportables.

### 8.5 Privacidad/local-first

Duración aproximada: 65 a 78 segundos.

Visual:

- Asset `privacy-local-first.png`.

Mensaje:

- La demo trabaja con una carpeta local controlada.
- No se pide subir material audiovisual.

### 8.6 Limitaciones honestas

Duración aproximada: 78 a 88 segundos.

Visual:

- Texto sobrio de limitaciones.

Mensaje:

- No hay waveform sync todavía.
- No hay transcripción todavía.
- No hay claqueta visual todavía.
- No hay instalador final todavía.

### 8.7 Cierre y CTA

Duración aproximada: 88 a 95 segundos.

Visual:

- AILinkCinema.
- CTA beta privada.

Mensaje:

- Beta privada para escuelas, productoras y equipos de postproducción.
- Contactar para probar con casos controlados.

## 9. Capturas recomendadas

Capturas mínimas:

1. Carpeta demo con estructura controlada.
2. Comando o resumen de ejecución local.
3. `report.html` abierto.
4. Sección de resumen del reporte.
5. Tabla de archivos detectados.
6. Tabla de sugerencias de match.
7. CSV de media files.
8. CSV de match suggestions.
9. Asset de privacidad local-first.
10. Pantalla final con CTA.

No usar:

- Material real de clientes.
- Rutas privadas.
- Emails reales.
- Teléfonos reales.
- Contratos.
- Presupuestos.
- Archivos con nombres sensibles.
- Capturas con tokens, claves o variables de entorno.

## 10. Grabación de pantalla

Recomendación:

- Resolución 1920x1080.
- Zoom del navegador entre 100% y 125%.
- Cursor visible pero no protagonista.
- Movimientos lentos.
- Sin notificaciones del sistema.
- Sin terminal con rutas privadas innecesarias.
- Sin mostrar `.env`.
- Sin mostrar claves.
- Sin mostrar ramas experimentales.

Herramientas posibles:

- OBS.
- Grabador del sistema.
- DaVinci Resolve para montaje posterior.
- Cualquier editor local ya controlado por el usuario.

El runbook no exige herramienta concreta.

## 11. Locución

Fuente:

- `docs/product/video/ailink_sync_dialogue_demo_video_voiceover_es_v1.txt`

Recomendación:

- Grabar voz clara.
- Ritmo pausado.
- No improvisar claims.
- Mantener tono profesional.
- No prometer features futuras como disponibles.
- Dejar pausas breves para cortes.

## 12. Subtítulos

Fuente:

- `docs/product/video/ailink_sync_dialogue_demo_video_subtitles_es_v1.srt`

Uso recomendado:

- Importar el SRT en el editor.
- Revisar sincronía tras montar.
- No cambiar significado sin actualizar el archivo fuente.
- Mantener subtítulos legibles.
- Evitar poner subtítulos sobre tablas pequeñas.

## 13. Música y sonido

Recomendación:

- Música muy baja o ninguna.
- Priorizar inteligibilidad de la voz.
- Evitar música con derechos dudosos.
- No usar efectos llamativos que resten seriedad.
- Normalizar volumen antes de exportar.

## 14. Diseño visual

Estilo recomendado:

- Limpio.
- Profesional.
- Oscuro/neutro si encaja con assets existentes.
- Tipografía legible.
- Pocos textos por pantalla.
- Tablas con zoom suficiente.
- CTA final claro.

Evitar:

- Efectos excesivos.
- Promesas agresivas.
- Lenguaje de “magia”.
- Estética de producto terminado si todavía es beta.

## 15. Checklist antes de exportar vídeo real

Antes de exportar:

- Revisar que no aparece material real de terceros.
- Revisar que no aparecen rutas privadas sensibles.
- Revisar que no aparecen secretos.
- Revisar que se menciona beta privada.
- Revisar que se mencionan limitaciones.
- Revisar que no se promete waveform sync.
- Revisar que no se promete transcripción.
- Revisar que no se promete claqueta visual.
- Revisar que no se promete integración directa con editores.
- Revisar que no se pide subir material audiovisual.
- Revisar que el CTA no contradice la landing.
- Revisar que los subtítulos coinciden con la locución.
- Revisar que las salidas mostradas existen en la demo controlada.
- Revisar que el vídeo no excede 2 minutos.

## 16. Checklist de publicación futura

Antes de publicar:

- Validar landing de destino.
- Validar texto legal de la landing.
- Validar formulario beta si existe.
- Validar que el vídeo no enlaza a formularios no preparados.
- Validar miniatura.
- Validar copy de LinkedIn.
- Validar copy de Facebook.
- Validar descripción.
- Validar que no se ofrece acceso inmediato garantizado.
- Validar que se conserva el mensaje local-first.
- Validar que se conserva la separación AILink Sync Dialogue / CID.

## 17. Salidas esperadas de una fase futura

Una fase futura de producción real del vídeo podría crear:

- Vídeo MP4.
- Audio WAV o MP3 de locución.
- Archivo de proyecto de montaje.
- Miniatura.
- Capturas finales.
- Versión corta vertical.
- Versión cuadrada para redes.
- Versión horizontal para landing.

Esas salidas no pertenecen a esta fase.

## 18. Criterios de aceptación

Esta fase se considera válida si:

- Define flujo de montaje del vídeo demo.
- Reutiliza guion, locución, subtítulos y assets existentes.
- Define claims permitidos.
- Define claims prohibidos.
- Define capturas recomendadas.
- Define checklist antes de exportar.
- Define checklist antes de publicar.
- Mantiene mensaje beta privada.
- Mantiene limitaciones honestas.
- No crea vídeo.
- No crea audio.
- No crea assets nuevos.
- No toca runtime.
- No toca frontend.
- No toca backend.
