# AILink Sync Dialogue — Demo Video Script v1

## 1. Objetivo

Este documento define el guion comercial y técnico para grabar un vídeo demo de AILink Sync Dialogue.

El objetivo del vídeo es explicar en poco tiempo qué problema resuelve, qué hace el prototipo actual, qué outputs genera y por qué el enfoque local-first es importante para escuelas, productoras y equipos de postproducción.

No es un anuncio de producto final cerrado. Es un vídeo de presentación para beta privada.

## 2. Alcance

Este documento prepara:

- Guion principal de 60–90 segundos.
- Guion ampliado de 2 minutos.
- Versión corta de 30–45 segundos para redes.
- Storyboard por bloques.
- Texto de voz en off.
- Texto en pantalla.
- Lista de capturas recomendadas.
- CTA final para beta privada.
- Checklist antes de grabar.
- Limitaciones que deben comunicarse con honestidad.

No implementa:

- Edición de vídeo.
- Motion graphics.
- Render final.
- Landing real.
- Formulario real.
- CRM.
- Supabase.
- Tracking.
- Frontend.
- Backend CID.
- Runtime.
- Subida de material audiovisual.

## 3. Mensaje principal

**Prepara el material de rodaje para montaje en minutos.**

AILink Sync Dialogue ayuda a revisar carpetas locales de vídeo y audio antes de montaje. Detecta archivos, lee metadata cuando está disponible, sugiere posibles matches y genera informes HTML, CSV y JSON.

El material permanece en el disco del cliente. En la versión actual no hay cloud.

## 4. Público del vídeo

Prioridad alta:

- Ayudantes de montaje.
- Escuelas de cine.
- Productoras pequeñas y medianas.
- DIT/data wranglers.
- Equipos de postproducción.

Prioridad secundaria:

- Productores.
- Coordinadores de producción.
- Directores independientes.
- Docentes de montaje o postproducción.

## 5. Assets recomendados

Usar solo assets auditados y metadata controlada:

- `docs/product/assets/ailink_sync_dialogue/hero-report-mockup.png`
- `docs/product/assets/ailink_sync_dialogue/report-summary.png`
- `docs/product/assets/ailink_sync_dialogue/match-suggestions-table.png`
- `docs/product/assets/ailink_sync_dialogue/media-files-table.png`
- `docs/product/assets/ailink_sync_dialogue/privacy-local-first.png`
- `docs/product/assets/ailink_sync_dialogue/linkedin-beta-card.png`

No usar:

- Material audiovisual real de clientes.
- Rutas personales del sistema.
- Nombres reales de producciones.
- Emails reales.
- Logos de terceros sin autorización.
- Imágenes de editores comerciales si no se tienen derechos o permiso.

## 6. Promesa comercial permitida

Se puede decir:

- Ayuda a revisar material antes de montaje.
- Ayuda a ordenar vídeo y audio.
- Genera una primera lectura del material.
- Sugiere posibles matches con razones.
- Genera informes compartibles.
- Trabaja localmente en la versión actual.
- No sube el material a la nube en la versión actual.

No se debe decir:

- Que sincroniza todo automáticamente.
- Que sustituye al montador.
- Que sustituye al ayudante de montaje.
- Que ya tiene waveform sync.
- Que ya tiene transcripción.
- Que ya detecta claqueta visual.
- Que ya tiene instalador final.
- Que ya se integra directamente con DaVinci Resolve, Avid Media Composer o Adobe Premiere Pro.
- Que es un producto final cerrado.

## 7. Guion principal — 60–90 segundos

### 0–8 segundos — Problema

**Imagen sugerida:** plano del hero mockup o montaje de carpetas simuladas.

**Voz en off:**

> Antes de empezar a montar, alguien tiene que entender qué hay dentro de la carpeta de rodaje: vídeos, audios separados, nombres de archivo, timecode, duración y metadata.

**Texto en pantalla:**

> Antes de montar, hay que ordenar el material.

### 8–18 segundos — Presentación

**Imagen sugerida:** `linkedin-beta-card.png` o `hero-report-mockup.png`.

**Voz en off:**

> AILink Sync Dialogue es una herramienta local para preparar material de vídeo y audio antes de montaje.

**Texto en pantalla:**

> AILink Sync Dialogue
> Ingesta, metadata y posibles matches.

### 18–35 segundos — Qué hace

**Imagen sugerida:** `media-files-table.png`.

**Voz en off:**

> Escanea una carpeta local, detecta archivos de vídeo y audio, lee metadata cuando está disponible y organiza la información en tablas claras.

**Texto en pantalla:**

> Detecta vídeo/audio
> Lee metadata
> Organiza el material

### 35–52 segundos — Matching sugerido

**Imagen sugerida:** `match-suggestions-table.png`.

**Voz en off:**

> Después sugiere posibles parejas de vídeo y audio usando señales como timecode, nombre, carpeta y duración. No decide por el montador: entrega candidatos con score y razones.

**Texto en pantalla:**

> Match suggestions
> Score + razones explicables

### 52–66 segundos — Outputs

**Imagen sugerida:** `report-summary.png`.

**Voz en off:**

> El resultado se entrega como un reporte HTML imprimible y archivos CSV y JSON para revisar o compartir con montaje y postproducción.

**Texto en pantalla:**

> `report.html`
> `media_files.csv`
> `match_suggestions.csv`
> `scan_result.json`

### 66–78 segundos — Privacidad

**Imagen sugerida:** `privacy-local-first.png`.

**Voz en off:**

> En la versión actual, el material no se sube a la nube. El análisis se ejecuta localmente y los outputs se generan en una carpeta del usuario.

**Texto en pantalla:**

> Local-first
> Sin cloud en la versión actual

### 78–90 segundos — CTA

**Imagen sugerida:** `linkedin-beta-card.png`.

**Voz en off:**

> Estamos abriendo una beta privada para escuelas, productoras y equipos de postproducción. Si quieres probarlo con un caso controlado, contacta con AILinkCinema.

**Texto en pantalla:**

> Beta privada
> Escuelas · Productoras · Postproducción
> Solicita acceso

## 8. Guion ampliado — 2 minutos

### 0–15 segundos — Apertura

> En montaje, una parte del trabajo empieza antes de abrir el editor. Hay que saber qué hay en cada carpeta, qué clips son vídeo, qué archivos son audio, si existe timecode, si la duración coincide y qué material puede estar relacionado.

### 15–30 segundos — Problema real

> En rodajes pequeños, escuelas o productoras sin equipo técnico grande, esta revisión suele hacerse a mano. Eso consume tiempo y puede generar errores antes de llegar a la parte creativa del montaje.

### 30–45 segundos — Presentación de la herramienta

> AILink Sync Dialogue nace para esa primera capa: revisar material de vídeo y audio antes de montaje y generar un informe claro.

### 45–65 segundos — Escaneo y metadata

> La herramienta escanea una carpeta local, detecta extensiones de vídeo y audio, y lee metadata si `ffprobe` está disponible. Con eso genera una tabla de inventario del material.

### 65–90 segundos — Match suggestions

> A partir de esa información, sugiere posibles matches entre vídeo y audio. Usa señales como timecode, nombre de archivo, carpeta y duración. Cada sugerencia incluye score y razones para que el equipo pueda revisar con criterio.

### 90–110 segundos — Outputs

> Los outputs principales son `report.html`, `media_files.csv`, `match_suggestions.csv` y `scan_result.json`. El reporte HTML sirve para revisión rápida y los CSV/JSON permiten continuar el trabajo de forma más estructurada.

### 110–125 segundos — Privacidad

> En esta versión no hay cloud. El análisis se ejecuta localmente y el material permanece en el disco del usuario.

### 125–140 segundos — Limitaciones honestas

> Todavía no incluye waveform sync, transcripción, detección de claqueta visual, instalador final ni integración directa con editores. Es una beta para validar utilidad real.

### 140–120 segundos — CTA final

> Buscamos escuelas, productoras y equipos de postproducción que quieran probar la beta privada con casos controlados. Si te interesa, contacta con AILinkCinema.

Nota: al grabar, ajustar tiempos para que el bloque final cierre en 2 minutos reales.

## 9. Versión corta — 30–45 segundos

**Voz en off:**

> AILink Sync Dialogue es una herramienta local para preparar material de vídeo y audio antes de montaje.
>
> Escanea carpetas, detecta archivos, lee metadata cuando está disponible y sugiere posibles matches por timecode, nombre, carpeta y duración.
>
> Genera `report.html`, CSV y JSON para revisar el material antes de abrir el editor.
>
> En la versión actual, el material no se sube a la nube.
>
> Estamos abriendo una beta privada para escuelas, productoras y equipos de postproducción.

**Texto en pantalla:**

> Prepara material antes de montaje
> Vídeo · Audio · Metadata · Matches
> Local-first
> Beta privada

## 10. Capturas recomendadas

Orden recomendado para la edición:

1. `linkedin-beta-card.png`
2. `hero-report-mockup.png`
3. `media-files-table.png`
4. `match-suggestions-table.png`
5. `report-summary.png`
6. `privacy-local-first.png`
7. `linkedin-beta-card.png`

## 11. Texto en pantalla reutilizable

Frases cortas:

- Prepara material antes de montaje.
- Escaneo local de vídeo y audio.
- Metadata y duración.
- Posibles matches explicables.
- Score y razones.
- Reporte HTML.
- CSV y JSON.
- Local-first.
- Sin cloud en la versión actual.
- Beta privada.

## 12. CTA final

Versión principal:

> Solicita acceso a la beta privada de AILink Sync Dialogue.

Versión para LinkedIn:

> Si trabajas en montaje, postproducción, escuela de cine o productora y quieres probar la beta, escríbeme.

Versión para landing:

> Solicitar acceso beta.

Versión para reuniones:

> Si queréis probarlo con una carpeta controlada, podemos preparar una demo corta.

## 13. Requisitos antes de grabar

Antes de grabar el vídeo:

- Usar solo assets auditados.
- Revisar que no aparecen rutas personales.
- Revisar que no aparecen datos personales.
- Revisar que no aparecen nombres reales de clientes o producciones.
- Revisar que no aparecen logos de terceros.
- Mantener el mensaje de beta privada.
- Mantener limitaciones actuales.
- No prometer automatización total.
- No pedir envío de material audiovisual.
- No decir que es CID.
- No decir que es un producto final.
- No decir que ya tiene instalador.
- No decir que ya tiene integración directa con editores.

## 14. Notas de tono

Tono recomendado:

- Profesional.
- Claro.
- Audiovisual.
- Honesto.
- Comercial sin exagerar.
- Enfocado en ahorro de tiempo y orden.
- Enfocado en beta privada.

Evitar:

- Tono futurista excesivo.
- Promesas de inteligencia artificial total.
- Frases grandilocuentes.
- Comparativas agresivas.
- Lenguaje legal definitivo.
- Exceso de tecnicismos para público no técnico.

## 15. Estructura visual sugerida

Formato horizontal:

- 1920x1080.
- Pensado para landing, YouTube privado, reuniones y LinkedIn.

Formato cuadrado:

- 1080x1080.
- Pensado para LinkedIn y Facebook.

Formato vertical futuro:

- 1080x1920.
- Pensado para stories/reels, si se decide.

## 16. Música y sonido

Recomendación:

- Música discreta.
- Sin música que tape la voz.
- Voz clara.
- Ritmo medio.
- Pausas breves entre bloques.

No usar música sin licencia.

## 17. Nombre de archivos sugeridos

Archivos de trabajo:

- `ailink_sync_dialogue_demo_video_script_v1.md`
- `ailink_sync_dialogue_demo_video_60_90s_v1.mp4`
- `ailink_sync_dialogue_demo_video_30_45s_social_v1.mp4`
- `ailink_sync_dialogue_demo_video_subtitles_es_v1.srt`

## 18. Checklist final antes de publicar

- El vídeo dice beta privada.
- El vídeo dice local-first.
- El vídeo dice sin cloud en la versión actual.
- El vídeo muestra outputs reales del prototipo.
- El vídeo no promete waveform sync.
- El vídeo no promete transcripción.
- El vídeo no promete claqueta visual.
- El vídeo no promete instalador final.
- El vídeo no promete integración directa con editores.
- El vídeo no pide subir material audiovisual.
- El vídeo no muestra datos reales.
- El vídeo no contiene rutas personales.
- El CTA es claro.
- El vídeo tiene subtítulos o texto suficiente para verse sin sonido.

## 19. Non-goals de esta fase

Esta fase no debe:

- Renderizar vídeo.
- Crear archivos MP4.
- Crear subtítulos reales.
- Crear assets nuevos.
- Tocar frontend.
- Tocar backend.
- Tocar CID.
- Tocar Supabase.
- Tocar CRM.
- Tocar formulario.
- Tocar `.env`.
- Añadir dependencias.
- Activar tracking.
- Publicar nada.

## 20. Criterios de aceptación

La fase se considera válida si:

- Existe guion principal de 60–90 segundos.
- Existe guion ampliado de 2 minutos.
- Existe versión corta de 30–45 segundos.
- Se referencian assets auditados.
- Se incluyen textos en pantalla.
- Se incluyen CTAs.
- Se incluyen limitaciones honestas.
- Se incluye checklist antes de publicar.
- No se prometen funciones inexistentes.
- No se toca runtime.
