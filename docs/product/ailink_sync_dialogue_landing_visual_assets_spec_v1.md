# AILink Sync Dialogue — Landing Visual Assets Spec v1

## 1. Título

**AILink Sync Dialogue — Landing Visual Assets Spec v1**

Especificación de assets visuales necesarios para implementar una landing profesional de AILink Sync Dialogue: hero visual, capturas de reporte, iconos, mockups, material social, y checklist de privacidad y publicación.

## 2. Objetivo del documento

Este documento define los assets visuales necesarios para implementar una landing profesional de AILink Sync Dialogue, sin generar archivos binarios todavía.

Los assets cubren:

* Hero visual de la landing.
* Capturas del reporte HTML (`report.html`).
* Captura de tabla de matches (`match_suggestions.csv`).
* Mini demo GIF o vídeo futuro.
* Iconos para cards de funcionalidades.
* Mockups de producto.
* Imagen para compartir en LinkedIn/Facebook.
* Checklist de privacidad visual.
* Checklist antes de publicar la landing.

Este documento es especificación, no implementación. No se crean imágenes, iconos ni vídeos en esta fase.

## 3. Principios visuales

Todos los assets deben seguir estos principios:

* **Profesional audiovisual.** El lenguaje visual debe conectar con montadores, DIT, escuelas y postproducción.
* **Sobrio.** Sin exceso de color, sin elementos decorativos innecesarios.
* **Claro.** La funcionalidad actual se explica con capturas reales, no con ilustraciones abstractas.
* **No estética genérica de IA.** Evitar el look habitual de startups de IA: neones, gradientes agresivos, tipografía futurista.
* **No exceso futurista.** Mostrar lo que la herramienta hace hoy, no promesas visuales de producto final.
* **Mostrar producto real antes que imágenes abstractas.** Las capturas del reporte HTML y CSV valen más que cualquier ilustración.
* **Privacidad/local-first.** Los assets nunca deben mostrar rutas personales, nombres reales de clientes ni material sensible.
* **Orden, precisión y confianza.** El diseño debe transmitir que la herramienta es útil, honesta y respeta el material del usuario.
* **Compatibilidad con perfiles variados.** El aspecto visual debe funcionar tanto para escuelas como para productoras y equipos de postproducción.

## 4. Assets imprescindibles para primera landing

Lista priorizada de assets, de mayor a menor urgencia:

### 4.1 Captura de report.html (resumen + matches)

- **Nombre del asset:** `hero-report-mockup.png`
- **Propósito:** Asset principal del hero. Muestra el reporte generado localmente.
- **Formato recomendado:** PNG
- **Tamaño recomendado:** 1200 × 800 px (landscape)
- **Estado:** Imprescindible
- **Origen:** Capturar de la demo existente (`create_sync_dialogue_metadata_demo.py`)
- **Notas de privacidad:** No mostrar rutas reales. Usar solo metadata controlada.
- **Contenido:** Summary del reporte con conteos, tabla de match suggestions con 2-3 filas y etiqueta de demo.

### 4.2 Captura de tabla match_suggestions.csv

- **Nombre del asset:** `match-suggestions-table.png`
- **Propósito:** Mostrar los campos concretos que genera la herramienta.
- **Formato recomendado:** PNG
- **Tamaño recomendado:** 800 × 600 px
- **Estado:** Imprescindible
- **Origen:** Capturar CSV abierto en hoja de cálculo o generar vista desde el reporte HTML.
- **Notas de privacidad:** Mostrar solo rutas relativas, nunca rutas absolutas ni nombres de proyecto reales.

### 4.3 Captura de resumen del demo metadata

- **Nombre del asset:** `report-summary.png`
- **Propósito:** Enseñar la cabecera del reporte: totales, alertas, resumen de vídeo/audio.
- **Formato recomendado:** PNG
- **Tamaño recomendado:** 800 × 500 px
- **Estado:** Imprescindible
- **Origen:** Capturar del `report.html` generado por `create_sync_dialogue_metadata_demo.py`
- **Notas de privacidad:** No incluir datos personales ni rutas del sistema del usuario.

### 4.4 Logo AILinkCinema

- **Nombre del asset:** `ailinkcinema-logo.svg` (recomendado) o `.png`
- **Propósito:** Marca en header y footer de la landing.
- **Formato recomendado:** SVG con fallback PNG
- **Tamaño recomendado:** Logo header ~200 × 40 px; logo footer ~150 × 30 px
- **Estado:** Imprescindible
- **Origen:** Diseño corporativo de AILinkCinema (no crear ahora).
- **Notas de privacidad:** Sin notas especiales.

### 4.5 Favicon

- **Nombre del asset:** `favicon.ico` / `favicon.svg`
- **Propósito:** Identificador en pestaña del navegador.
- **Formato recomendado:** .ico (32×32) + .svg
- **Tamaño recomendado:** 32 × 32 px
- **Estado:** Recomendable
- **Origen:** Derivado del logo AILinkCinema.

### 4.6 Iconos simples para cards

- **Nombre del asset:** `icon-*.svg` (7 iconos)
- **Propósito:** Acompañar cada card de funcionalidad en la landing.
- **Formato recomendado:** SVG
- **Tamaño recomendado:** 48 × 48 px
- **Estado:** Recomendable
- **Origen:** Crear desde el diseño corporativo o usar iconos libres coherentes.
- **Notas de privacidad:** Sin notas especiales.

### 4.7 Imagen para compartir en LinkedIn/Facebook

- **Nombre del asset:** `social-preview-beta.png`
- **Propósito:** Imagen que aparece al compartir el enlace de la landing en redes.
- **Formato recomendado:** PNG
- **Tamaño recomendado:** 1200 × 630 px (estándar Open Graph)
- **Estado:** Recomendable para lanzamiento
- **Origen:** Derivado del hero visual + logo + CTA.
- **Notas de privacidad:** Misma política que hero: sin datos reales.

## 5. Captura principal del hero

### Composición recomendada

La captura principal del hero debe simular un entorno de trabajo profesional:

* Fondo: escritorio limpio o panel flotante del reporte HTML.
* Elemento central: ventana del reporte HTML con la pestaña «Match Suggestions» visible.
* Elementos destacados:
  - Conteo de vídeos detectados.
  - Conteo de audios detectados.
  - Confidence y score de los matches.
  - 1-2 matches con etiqueta «HIGH» o «ALTA».
* No debe mostrar:
  - Rutas de archivo sensibles (usar paths de ejemplo como `/proyectos/rodaje/`).
  - Nombres reales de clientes o proyectos.
  - Emails reales.
  - Ningún dato que pueda identificar a un usuario o producción real.

### Texto que debe acompañar la imagen

> Reporte local generado a partir de metadata controlada. Ejemplo de demo. No contiene material real de cliente.

### Notas adicionales

* Si no hay una captura limpia disponible, se puede usar un mockup de portátil con la captura insertada.
* El mockup debe ser sobrio, sin brillos excesivos ni reflejos falsos.
* No usar maquetas de Apple gratuitas que parezcan anuncio de producto.

## 6. Capturas del reporte HTML

### 6.1 Summary del reporte

- **Uso en landing:** Sección «Qué hace» o «Outputs».
- **Tamaño aproximado:** 700 × 400 px.
- **Contenido que debe verse:**
  - Título del reporte.
  - Fecha de generación.
  - Total de archivos de vídeo.
  - Total de archivos de audio.
  - Número de match suggestions generadas.
  - Alertas si las hay.
- **Contenido que debe ocultarse:**
  - Ruta completa del sistema de archivos.
  - Nombre del usuario del sistema.
- **Criterio de aceptación visual:** La captura debe ser legible en móvil y desktop. No usar texto menor de 10 px.

### 6.2 Tabla de media files

- **Uso en landing:** Sección «Outputs» o «Cómo funciona».
- **Tamaño aproximado:** 700 × 500 px.
- **Contenido que debe verse:**
  - Columnas: filename, type, duration, codec, timecode.
  - 4-5 filas de ejemplo (2 vídeos, 2 audios).
  - Alternancia de color en filas para legibilidad.
- **Contenido que debe ocultarse:**
  - Paths absolutos.
  - Datos de proyectos reales.
- **Criterio de aceptación visual:** La tabla debe entenderse sin necesidad de ampliar.

### 6.3 Tabla de match suggestions

- **Uso en landing:** Bloque central «Qué hace» y «Outputs».
- **Tamaño aproximado:** 700 × 500 px.
- **Contenido que debe verse:**
  - Columnas: vídeo, audio, confidence, score, strategy, reasons.
  - 2-3 filas con matches.
  - Al menos 1 match con alta confianza.
- **Contenido que debe ocultarse:**
  - Paths absolutos.
  - Nombres reales de persona o proyecto.
- **Criterio de aceptación visual:** Debe quedar claro que la herramienta sugiere, no decide.

### 6.4 Alertas (si aplica)

- **Uso en landing:** Demostrar que la herramienta señala problemas.
- **Tamaño aproximado:** 700 × 200 px.
- **Contenido que debe verse:**
  - Alerta de archivo sin timecode o sin metadata.
  - Alerta de duración inesperada.
- **Criterio de aceptación visual:** Debe verse como advertencia útil, no como error de la herramienta.

### 6.5 Footer de privacidad

- **Uso en landing:** Reforzar privacidad en outputs.
- **Contenido:** Texto «Generado localmente por AILink Sync Dialogue. El material permanece en el disco del cliente.»
- **Criterio de aceptación visual:** Coherente con el tono del reporte.

## 7. Captura de match_suggestions.csv

### Contenido que debe mostrar

| video_relative_path | audio_relative_path | confidence | score | strategy | reasons | duration_delta_seconds |
|---|---|---|---|---|---|---|
| footage/dia1/A001_C001.mov | audio/dia1/A001_C001.wav | high | 0.95 | timecode | Timecode match exacto | 0.03 |
| footage/dia1/A001_C002.mov | audio/dia1/A001_C002.wav | medium | 0.88 | filename | Nombre coincide | 0.15 |

### Contenido que no debe mostrar

* Paths absolutos del sistema (C:, /Users/, /home/).
* Nombres reales de proyectos.
* Material sensible.
* Datos de clientes reales.
* Emails o datos personales.

## 8. Mini demo GIF/vídeo futuro

### Guion de 20-30 segundos

#### Pantalla 1 (3-4 segundos)
**Texto en pantalla:** «Carpeta de rodaje típica»
**Visual:** Árbol de carpetas con subcarpetas VIDEO/, AUDIO/, NOTAS/
**Acción:** Zoom suave a la estructura.
**Nota:** Usar nombres de ejemplo. No usar material real.

#### Pantalla 2 (5-6 segundos)
**Texto en pantalla:** «AILink Sync Dialogue analiza los archivos»
**Visual:** Terminal o UI futura mostrando progreso de escaneo.
**Acción:** Aparecen filas de archivos detectados una por una.
**Nota:** Usar demo de metadata controlada.

#### Pantalla 3 (4-5 segundos)
**Texto en pantalla:** «Outputs generados»
**Visual:** Iconos de report.html, media_files.csv, match_suggestions.csv, scan_result.json apareciendo.
**Acción:** Fundido de los 4 iconos.

#### Pantalla 4 (5-6 segundos)
**Texto en pantalla:** «Match suggestions listas para revisar»
**Visual:** Captura del reporte HTML con tabla de matches.
**Acción:** Resaltar la fila de mayor confianza.
**Nota:** No mostrar rutas reales.

#### Pantalla 5 (3-4 segundos)
**Texto en pantalla:** «Sin subir archivos. Privacidad local.»
**Visual:** Icono de disco local con escudo de privacidad.
**CTA:** «Solicitar acceso beta»
**Nota:** Texto profesional, sin exageraciones.

### Aclaraciones

* No crear vídeo ni GIF ahora.
* No usar material real de producción.
* Usar únicamente la demo de metadata controlada.
* Versión futura cuando haya capturas limpias de CLI o UI gráfica.
* Si se hace GIF, mantenerlo por debajo de 5 MB para la landing.

## 9. Imagen hero alternativa sin interfaz

Si aún no hay una captura bonita del reporte HTML, usar esta opción secundaria:

### Composición

* Fondo oscuro (gris muy oscuro, no negro puro).
* Elementos visibles:
  - Carpeta de rodaje estilizada con subcarpetas VIDEO y AUDIO.
  - Fragmentos de timecode flotando (ej: 01:23:45:12).
  - Icono de escudo/disco local pequeño.
  - Logo AILinkCinema integrado.
* Sin personas reconocibles.
* Sin cámaras ni logos comerciales reales (ninguna marca de cámara).
* Sin texto que prometa automatización total.

### Estilo

* Vectorial, dibujo técnico, no realista.
* Colores: grises, azul acero, blanco.
* Evitar neones, gradientes psicodélicos o brillos excesivos.

### Texto que debe acompañar

> AILink Sync Dialogue. Material local. Informes claros.

## 10. Iconos para cards

### 10.1 Escaneo local
- **Metáfora visual:** Carpeta con lupa.
- **Estilo recomendado:** Lineal, trazo consistente 1.5-2px.
- **Evitar:** Carpetas 3D, iconos de nube.
- **Color/contraste:** Blanco o gris claro sobre fondo oscuro de card.

### 10.2 Vídeo/audio
- **Metáfora visual:** Claqueta (vídeo) y onda sonora (audio) combinadas.
- **Estilo recomendado:** Lineal, misma familia que el resto.
- **Evitar:** Iconos de cámara fotográfica.
- **Color/contraste:** Misma línea que escaneo.

### 10.3 Metadata
- **Metáfora visual:** Tabla con columnas y filas o etiqueta «i».
- **Estilo recomendado:** Lineal.
- **Evitar:** Gráficos complejos.
- **Color/contraste:** Misma línea.

### 10.4 Match suggestions
- **Metáfora visual:** Dos fichas/piezas encajando o flecha de conexión.
- **Estilo recomendado:** Lineal.
- **Evitar:** Corazones, checkmarks exagerados.
- **Color/contraste:** Misma línea.

### 10.5 Reporte HTML
- **Metáfora visual:** Documento con gráfico o tabla.
- **Estilo recomendado:** Lineal.
- **Evitar:** Iconos de impresora.
- **Color/contraste:** Misma línea.

### 10.6 CSV/JSON
- **Metáfora visual:** Documento con etiquetas «csv» y «json».
- **Estilo recomendado:** Lineal.
- **Evitar:** Discos flexibles, hojas de cálculo 3D.
- **Color/contraste:** Misma línea.

### 10.7 Privacidad/local-first
- **Metáfora visual:** Disco duro o chip con escudo.
- **Estilo recomendado:** Lineal, destacar escudo.
- **Evitar:** Nubes tachadas, iconos de candado genéricos.
- **Color/contraste:** Acento de color (azul acero o verde oscuro) para destacar.

## 11. Paleta visual recomendada

No definir CSS todavía. Describir criterios cromáticos:

* **Fondo principal:** Oscuro o neutro. Ej: #1a1a2e, #16213e, #0f0f1a. Sin llegar a negro puro.
* **Texto principal:** Claro sobre fondo oscuro. Ej: #e0e0e0, #f5f5f5.
* **Acento principal:** Azul acero o gris azulado. Ej: #4a90d9, #5b8def.
* **Acento secundario:** Verde oscuro o gris claro. Ej: #2d6a4f, #8a8a8a.
* **Fondo de cards:** Ligeramente más claro que el fondo principal. Ej: #232338.
* **Alertas:** Amarillo/ámbar suave. Ej: #d4a017.
* **Errores/importante:** Rojo no saturado. Ej: #b54747.
* **Éxito:** Verde sobrio. Ej: #3a7d4f.
* **Blancos y grises:** Usar gamas de gris, no blanco puro (#ffffff) para evitar fatiga visual.

### Lo que se debe evitar

* Neones (rosa, verde fosforito, azul eléctrico).
* Paletas de startup IA genérica (morado + rosa + azul).
* Look gaming o infantil.
* Gradientes agresivos en fondos.
* Saturación excesiva.

## 12. Tipografía recomendada

No añadir fuentes ni archivos. Definir criterios:

* **Familia:** Sans serif legible. Recomendadas: Inter, System UI, SF Pro, Roboto.
* **Uso en cuerpo:** Regular 16-18 px, interlineado 1.5.
* **Uso en títulos:** Semibold, jerarquía clara (H1: 36 px, H2: 28 px, H3: 22 px).
* **Uso en tablas:** Monospace o sans serif compacta para datos. Tamaño 13-14 px.
* **Uso en etiquetas de estado:** Bold, 12-13 px, mayúsculas.
* **No usar:** Tipografías decorativas, serifa para cuerpo, aspecto infantil o gaming.
* **Legibilidad:** Contraste suficiente sobre fondo oscuro. Peso regular o medium para texto principal.

## 13. Material social

### 13.1 Imagen cuadrada LinkedIn/Facebook

- **Objetivo:** Publicación de apertura de beta.
- **Formato:** 1080 × 1080 px (cuadrado).
- **Composición:**
  - Fondo oscuro.
  - Logo AILinkCinema arriba.
  - Texto central: «Beta privada abierta: AILink Sync Dialogue».
  - Subtítulo: «Prepara material de rodaje para montaje en minutos.»
  - Icono de disco/privacidad.
  - CTA: «Solicitar acceso» con URL o indicación.
- **Claim permitido:** «Beta privada para escuelas, productoras y equipos de postproducción.»
- **Claim prohibido:** «Sincroniza todo automáticamente» / «Sustituye al montador» / «IA que monta por ti.»

### 13.2 Banner horizontal

- **Objetivo:** Imagen de cabecera en LinkedIn o Facebook.
- **Formato:** 1200 × 627 px.
- **Composición:**
  - Misma línea que imagen cuadrada.
  - Espacio para texto a la izquierda.
  - Logo + nombre producto a la derecha.
  - Fondo oscuro consistente.
- **Claim permitido:** «Herramienta local para revisar material de vídeo y audio antes de montaje.»

### 13.3 Mini carrusel de 3 slides

- **Objetivo:** Explicación rápida en LinkedIn.
- **Formato:** 1080 × 1080 px por slide.
- **Slide 1:** Problema (carpetas desordenadas).
- **Slide 2:** Solución (escaneo local + outputs).
- **Slide 3:** CTA beta.
- **Claim permitido:** «Escanea, sugiere y comparte informes sin subir material a la nube.»
- **Claim prohibido:** Misma lista que 13.1.

### 13.4 Imagen para post beta privada

- **Objetivo:** Post de texto con imagen de apoyo.
- **Formato:** 1200 × 800 px.
- **Composición:**
  - Mockup del reporte HTML.
  - Texto: «Buscamos betatesters para AILink Sync Dialogue.»
  - Subtítulo: «Escuelas, productoras y equipos de postproducción.»
  - Indicación: «Link en comentarios / bio.»

## 14. Carrusel LinkedIn futuro

### Guion de 5 slides

#### Slide 1 — Problema

**Texto:**
Antes de montar, alguien tiene que entender el material.

Carpetas desordenadas, vídeo y audio separados, metadata difícil de revisar.

Esa revisión inicial consume tiempo antes de llegar al montaje creativo.

**Visual sugerido:** Carpeta de rodaje estilizada con elementos dispersos.

#### Slide 2 — Qué hace AILink Sync Dialogue

**Texto:**
AILink Sync Dialogue escanea una carpeta local de rodaje, detecta archivos de vídeo y audio, lee metadata si está disponible y sugiere posibles matches.

Todo sin subir el material a la nube.

**Visual sugerido:** Diagrama simple: carpeta → escaneo → tabla de resultados.

#### Slide 3 — Outputs que genera

**Texto:**
La herramienta genera cuatro outputs locales:

- `report.html` para revisión visual.
- `media_files.csv` para tabla de clips.
- `match_suggestions.csv` con candidatos de sincronía.
- `scan_result.json` para integraciones futuras.

**Visual sugerido:** Los 4 iconos de documentos con nombres.

#### Slide 4 — Privacidad

**Texto:**
El material no sale del disco del cliente. No se sube vídeo ni audio a servidores.

La herramienta funciona en local. Ideal para material sensible, proyectos privados o ejercicios de escuela.

**Visual sugerido:** Disco con escudo de privacidad.

#### Slide 5 — CTA beta

**Texto:**
Buscamos escuelas, productoras y equipos de postproducción para nuestra beta privada con plazas limitadas.

Solicita acceso en [URL de landing].

**Visual sugerido:** Logo AILinkCinema + CTA «Solicitar beta».

## 15. Checklist de privacidad visual

Antes de publicar cualquier asset visual, verificar:

- [ ] Sin rutas de archivo personales (C:/Users/, /home/, /Users/).
- [ ] Sin nombres reales de clientes o producciones.
- [ ] Sin nombres de proyectos reales.
- [ ] Sin emails reales.
- [ ] Sin material audiovisual sensible (vídeo, audio, transcripciones).
- [ ] Sin logos de terceros no autorizados (cámaras, software, marcas).
- [ ] Sin marcas de cámara/grabadora sin permiso explícito.
- [ ] Usar únicamente metadata controlada de la demo.
- [ ] Las capturas no deben contener datos que puedan identificar a una persona o producción.
- [ ] Cualquier path mostrado debe ser relativo y de ejemplo.
- [ ] Los nombres de archivo en las capturas deben ser genéricos (A001_C001, etc.).

## 16. Checklist antes de publicar landing

Antes de lanzar la landing pública:

- [ ] Revisar ortografía de todos los textos visibles.
- [ ] Revisar acentos y tildes en español.
- [ ] Revisar privacidad de todos los assets visuales (ver sección 15).
- [ ] Comprobar que las capturas coinciden con funcionalidades reales y actuales.
- [ ] No mostrar funciones futuras como si estuvieran disponibles hoy.
- [ ] Comprobar que el formulario funciona correctamente.
- [ ] Preparar aviso legal y política de privacidad antes de activar el formulario.
- [ ] Comprobar CTA principal y email de contacto.
- [ ] Verificar que los enlaces a política de privacidad, aviso legal y condiciones beta existen.
- [ ] Comprobar responsive futuro (mobile first).
- [ ] Probar la landing en navegadores principales (Chrome, Firefox, Safari, Edge).
- [ ] Verificar que la imagen Open Graph (social preview) se muestra correctamente al compartir.
- [ ] Cargar la landing sin errores de consola.
- [ ] Verificar tiempos de carga de imágenes (optimizar PNG, usar lazy loading).

## 17. Nombres de archivo recomendados

No crear estos archivos en esta fase. Nomenclatura futura:

| Nombre de archivo | Asset |
|---|---|
| `hero-report-mockup.png` | Captura principal del hero con reporte HTML |
| `report-summary.png` | Resumen del reporte HTML |
| `match-suggestions-table.png` | Tabla de match suggestions |
| `media-files-table.png` | Tabla de media files |
| `privacy-local-first.png` | Icono o imagen de privacidad |
| `linkedin-beta-card.png` | Imagen cuadrada para LinkedIn/Facebook |
| `banner-beta-horizontal.png` | Banner horizontal para redes |
| `carrusel-slide-1.png` al `carrusel-slide-5.png` | Slides para carrusel LinkedIn |
| `social-preview-beta.png` | Imagen Open Graph para compartir |
| `landing-demo-preview.gif` | Mini demo GIF futuro |
| `favicon.ico` | Favicon |
| `ailinkcinema-logo.svg` | Logo AILinkCinema |
| `icon-scan.svg` | Icono escaneo local |
| `icon-video-audio.svg` | Icono vídeo/audio |
| `icon-metadata.svg` | Icono metadata |
| `icon-matching.svg` | Icono match suggestions |
| `icon-report.svg` | Icono reporte HTML |
| `icon-csv-json.svg` | Icono CSV/JSON |
| `icon-privacy.svg` | Icono privacidad/local-first |

## 18. Ubicación futura recomendada

No crear carpetas de assets ahora. Ubicación propuesta para cuando se implemente:

* `docs/product/assets/ailink_sync_dialogue/` — Documentación y referencia.
* `src_frontend/public/assets/ailink_sync_dialogue/` — Assets web públicos cuando se implemente frontend.

No crear ninguna de estas carpetas en esta fase.

## 19. Relación con demo actual

Para generar la base visual de los assets, usar la demo existente:

### Pasos para generar la base visual

1. Activar el entorno:
   ```bash
   cd /opt/SERVICIOS_CINE
   source .venv/bin/activate
   ```

2. Ejecutar el script de demo con metadata controlada:
   ```bash
   python scripts/demo/create_sync_dialogue_metadata_demo.py \
     --output-dir /tmp/ailink_sync_dialogue_metadata_demo \
     --force
   ```

3. Abrir el reporte generado:
   ```bash
   xdg-open /tmp/ailink_sync_dialogue_metadata_demo/report.html
   ```
   (o abrir manualmente en el navegador)

4. Identificar las secciones limpias para capturar:
   - Cabecera del reporte con resumen.
   - Tabla de media files.
   - Tabla de match suggestions.
   - Alertas si existen.

5. Capturar con herramienta de captura de pantalla:
   - Recortar cada sección individualmente.
   - No incluir barras de herramientas del navegador.
   - No incluir rutas del sistema.

6. Guardar las capturas con los nombres definidos en la sección 17.

### Reglas estrictas para las capturas

* No usar material real de producción.
* Mantener metadata controlada de la demo.
* Si hay rutas de sistema visibles, recortarlas o reemplazarlas.
* No incluir datos personales ni de clientes.
* Revisar que no aparezcan errores del sistema operativo en las capturas.

## 20. Criterios de aceptación

Este documento se considera aceptado si:

* Está en español correcto, con acentos y tildes cuidados.
* No implementa código.
* No crea assets reales (imágenes, iconos, vídeos) todavía.
* Sirve como checklist visual completo para la landing.
* Mantiene privacidad/local-first como criterio central.
* No promete funciones inexistentes.
* Distingue claramente entre assets actuales y futuros.
* Conecta correctamente AILink Sync Dialogue con AILinkCinema.
* No vende la herramienta como CID.
