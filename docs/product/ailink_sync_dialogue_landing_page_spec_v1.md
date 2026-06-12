# AILink Sync Dialogue — Landing Page Spec v1

## 1. Título

**AILink Sync Dialogue — Landing Page Spec v1**

Especificación de contenido, estructura y criterios para una futura landing pública de AILink Sync Dialogue. Esta fase no implementa frontend ni web real.

## 2. Objetivo de la página

La landing debe captar interesados cualificados para una beta privada de AILink Sync Dialogue y explicar la herramienta con claridad, sin exagerar el estado actual.

Objetivos principales:

- Captar interesados para beta privada.
- Explicar qué hace la herramienta de forma directa.
- Posicionar privacidad/local-first como ventaja central.
- Evitar promesas de funciones inexistentes.
- Permitir solicitar acceso o contacto.
- Preparar una futura implementación web con copy, estructura y criterios claros.

La página debe vender una beta/prototipo útil, no un producto final cerrado.

## 3. Público objetivo principal

### Público primario

- Ayudantes de montaje.
- Escuelas de cine.
- Productoras pequeñas y medianas.
- DIT/data wranglers.
- Equipos de postproducción.

### Público secundario

- Coordinadores de producción.
- Directores independientes con equipos reducidos.
- Productores que reciben material de rodaje sin estructura clara.
- Docentes de postproducción audiovisual.

### Público no prioritario por ahora

- Grandes estudios con pipelines de ingesta ya maduros.
- Usuarios que buscan edición automática completa.
- Equipos que necesitan integración inmediata con Avid, DaVinci o Premiere.
- Usuarios que esperan waveform sync, transcripción o claqueta visual en esta fase.

## 4. Estructura exacta de la landing

### 1. Header/nav

**Propósito:** identificar marca, producto y navegación básica.

**Texto propuesto:** AILinkCinema · AILink Sync Dialogue

**CTA:** Solicitar beta

**Notas de diseño:** header limpio, fijo o simple, sin sobrecargar.

**Visual sugerido:** logo AILinkCinema a la izquierda y CTA destacado a la derecha.

### 2. Hero

**Propósito:** explicar el valor en menos de 10 segundos.

**Texto propuesto:** ver sección 6.

**CTA:** Solicitar acceso beta / Ver ejemplo de reporte

**Notas de diseño:** hero sobrio con captura futura del reporte HTML o tabla de matches.

**Visual sugerido:** mockup de `report.html` con summary y match suggestions.

### 3. Problem section

**Propósito:** conectar con dolor real antes del montaje.

**Texto propuesto:** ver sección 7.

**CTA:** Ninguno o CTA secundario suave.

**Notas de diseño:** usar 3-4 bullets concretos, no texto largo.

**Visual sugerido:** estructura de carpetas de rodaje desordenada vs informe claro.

### 4. What it does

**Propósito:** mostrar funcionalidades actuales y estado de cada una.

**Texto propuesto:** cards de sección 8.

**CTA:** Ver outputs

**Notas de diseño:** cards con etiqueta de estado: disponible beta, experimental, futuro.

**Visual sugerido:** iconos simples de carpeta, audio, timecode, tabla e informe.

### 5. How it works

**Propósito:** reducir incertidumbre operacional.

**Texto propuesto:** 4 pasos de sección 9.

**CTA:** Solicitar demo

**Notas de diseño:** línea de proceso horizontal en desktop y vertical en móvil.

**Visual sugerido:** carpeta local → análisis → reporte → revisión.

### 6. Example outputs

**Propósito:** enseñar entregables reales que el usuario entiende.

**Texto propuesto:** sección 10.

**CTA:** Ver ejemplo de reporte

**Notas de diseño:** tabs o cards, sin implementar aún.

**Visual sugerido:** captura `report.html`, tabla CSV y snippet JSON.

### 7. Privacy/local-first

**Propósito:** resolver objeción crítica sobre material sensible.

**Texto propuesto:** sección 11.

**CTA:** Solicitar beta local

**Notas de diseño:** bloque fuerte, casi como promesa de producto.

**Visual sugerido:** disco local/carpeta cerrada, sin nube.

### 8. Demo/beta invitation

**Propósito:** convertir visitantes cualificados.

**Texto propuesto:** sección 12.

**CTA:** Solicitar acceso beta

**Notas de diseño:** destacar plazas limitadas y feedback directo.

**Visual sugerido:** panel con condiciones de beta.

### 9. Who it is for

**Propósito:** ayudar al usuario a autoidentificarse.

**Texto propuesto:** sección 3 resumida.

**CTA:** Soy parte de este perfil

**Notas de diseño:** tarjetas por rol.

**Visual sugerido:** montaje, escuela, productora, DIT, postproducción.

### 10. What it does not do yet

**Propósito:** generar confianza y evitar expectativas falsas.

**Texto propuesto:** sección 15.

**CTA:** Ver roadmap beta

**Notas de diseño:** tono honesto, no defensivo.

**Visual sugerido:** checklist “actual / futuro”.

### 11. FAQ

**Propósito:** responder objeciones antes del formulario.

**Texto propuesto:** sección 14.

**CTA:** Solicitar beta

**Notas de diseño:** respuestas cortas, directas.

**Visual sugerido:** acordeón futuro, no implementar ahora.

### 12. Final CTA

**Propósito:** cierre de conversión.

**Texto propuesto:** “Si preparas material de rodaje antes de montaje, queremos probarlo contigo.”

**CTA:** Solicitar acceso beta

**Notas de diseño:** repetir promesa local-first y beta controlada.

**Visual sugerido:** bloque final con formulario breve o botón.

### 13. Footer

**Propósito:** cierre institucional y legal.

**Texto propuesto:** AILinkCinema · AILink Sync Dialogue · Beta privada

**CTA:** Contacto

**Notas de diseño:** incluir enlaces futuros a privacidad, aviso legal y condiciones beta.

**Visual sugerido:** footer oscuro simple.

## 5. Header/nav

**Logo/texto:** AILinkCinema

**Producto mostrado:** AILink Sync Dialogue

**Enlaces:**

- Qué hace
- Privacidad
- Beta
- FAQ
- Contacto

**Botón CTA:** Solicitar beta

Comportamiento futuro: al hacer clic, scroll a formulario o abrir sección de interés beta. No implementar en esta fase.

## 6. Hero final recomendado

**Titular final:** Prepara el material de rodaje para montaje en minutos.

**Subtitular final:** AILink Sync Dialogue analiza carpetas locales de vídeo y audio, detecta metadata disponible y sugiere posibles matches antes de abrir el proyecto de edición. Genera informes HTML, CSV y JSON sin subir el material a la nube.

**CTA principal:** Solicitar acceso beta

**CTA secundario:** Ver ejemplo de reporte

**Microcopy de privacidad:** El material permanece en el disco del cliente. Sin cloud en la versión actual.

## 7. Bloque de problema

Antes de montar, alguien tiene que entender el material.

En muchos rodajes, el equipo de postproducción recibe carpetas con vídeos, audios separados, notas sueltas y metadata difícil de revisar. Esa primera revisión consume tiempo antes de que el montaje creativo pueda empezar.

Problemas frecuentes:

- Carpetas de rodaje desordenadas.
- Vídeo y audio separados.
- Timecode y duración que hay que comprobar manualmente.
- Metadata técnica dispersa.
- Falta de un informe claro para montaje o postproducción.

AILink Sync Dialogue ayuda a convertir esa revisión inicial en una tabla y un reporte entendible.

## 8. Bloque “Qué hace”

### Escaneo local

**Descripción:** analiza una carpeta local del usuario y detecta archivos soportados.

**Estado:** disponible beta.

### Detección vídeo/audio

**Descripción:** identifica archivos de vídeo y audio por extensiones soportadas y los organiza en tablas.

**Estado:** disponible beta.

### Metadata con ffprobe si está disponible

**Descripción:** extrae duración, timecode, fps, canales, codec y formato cuando la metadata puede leerse.

**Estado:** disponible beta.

### Sugerencias de matches

**Descripción:** propone posibles parejas vídeo/audio por timecode, nombre, carpeta y duración, con score y razones explicables.

**Estado:** disponible beta / experimental.

### Reporte HTML

**Descripción:** genera un reporte imprimible para revisión humana y demo.

**Estado:** disponible beta.

### CSV/JSON para revisión

**Descripción:** exporta `media_files.csv`, `match_suggestions.csv` y `scan_result.json`.

**Estado:** disponible beta.

## 9. Bloque “Cómo funciona”

1. **Selecciona carpeta local.** El usuario elige una carpeta de rodaje o proyecto.
2. **Analiza vídeo/audio.** La herramienta detecta archivos y lee metadata si está disponible.
3. **Genera sugerencias e informe.** Produce matches sugeridos, CSV, JSON y HTML.
4. **Revisa y comparte con montaje.** El equipo usa el reporte como base de revisión, no como decisión automática.

Aclaración: el prototipo actual se ejecuta por CLI. La interfaz gráfica vendrá después si la beta valida el flujo. No hay cloud en la versión actual.

## 10. Bloque “Outputs”

### `report.html`

Reporte visual para abrir en navegador. Muestra resumen, alertas, tablas de vídeo/audio y match suggestions.

### `media_files.csv`

Tabla para revisar clips y audios en hoja de cálculo. Útil para ayudantes de montaje, DIT o coordinación.

### `match_suggestions.csv`

Lista de candidatos de sincronía con confidence, score, strategy y reasons.

### `scan_result.json`

Export completo para integraciones futuras o procesamiento técnico.

**Imagen visual futura:** captura del `report.html`, tabla de matches y resumen de clips. No crear imagen todavía.

## 11. Bloque privacidad

### El material no sale del disco del cliente.

AILink Sync Dialogue trabaja localmente. No sube vídeo ni audio a servidores en la versión actual.

Los outputs se generan en una carpeta local:

- HTML para revisar.
- CSV para compartir.
- JSON para integración futura.

Esto hace que la beta sea adecuada para pruebas con material sensible, proyectos privados o ejercicios de escuela donde no se quiere mover media fuera del entorno local.

## 12. Bloque beta privada

Estamos abriendo una beta privada para escuelas, productoras pequeñas/medianas y equipos de postproducción que quieran probar AILink Sync Dialogue con casos controlados.

Propuesta beta:

- Acceso temprano.
- Precio orientativo desde 25 €/mes durante los primeros meses de beta.
- Alternativa: precio beta por definir según perfil y uso.
- Plazas limitadas.
- Feedback directo a cambio de acceso anticipado.
- Sin compromiso de permanencia.
- Pruebas con carpetas controladas y material autorizado.

**CTA:** Solicitar acceso beta

## 13. Formulario beta

### Campos obligatorios

- Nombre.
- Email.
- Empresa/escuela.
- Rol.
- País/ciudad.
- Software de montaje.
- ¿Trabajas con audio separado?
- ¿Trabajas con timecode?
- Principal problema actual.
- Permiso de contacto.
- Aceptación privacidad.

### Campos opcionales

- Volumen aproximado de material.
- Tipo de proyecto.
- Interés en beta de pago.
- Comentarios adicionales.

Notas futuras: el formulario debe evitar pedir material audiovisual. Solo debe recoger información comercial y de flujo.

## 14. FAQ final

### ¿Sube mi material a la nube?

No en la versión actual. La herramienta trabaja localmente y genera outputs locales.

### ¿Necesito GPU?

No. El prototipo actual no usa GPU.

### ¿Sincroniza automáticamente?

No. Sugiere posibles matches con score y razones. La revisión final sigue siendo humana.

### ¿Lee timecode?

Sí, cuando la metadata existe y puede leerse.

### ¿Qué archivos genera?

`scan_result.json`, `media_files.csv`, `match_suggestions.csv` y `report.html`.

### ¿Funciona con DaVinci, Avid o Premiere?

Todavía no hay integración directa. Los CSV/HTML/JSON pueden servir como apoyo previo al montaje.

### ¿Es una herramienta de AILinkCinema?

Sí. AILink Sync Dialogue es una herramienta independiente dentro del ecosistema AILinkCinema.

### ¿Es CID?

No. CID es el SaaS integral. Esta herramienta funciona de forma independiente y puede conectarse a workflows más amplios en el futuro.

### ¿Puedo usarlo en una escuela?

Sí. Es un caso prioritario para beta, especialmente para enseñar ingesta, orden y revisión de material.

### ¿Cuándo estará disponible?

Primero en beta privada con casos controlados.

## 15. Sección “Qué no hace todavía”

AILink Sync Dialogue todavía no incluye:

- Waveform sync.
- Transcripción.
- Detección de claqueta visual.
- Integración directa con editores.
- Instalador final.
- UI gráfica.
- Sustitución del montador o ayudante de montaje.

Esta sección debe mostrarse con tono honesto: “Estamos empezando por resolver bien la preparación inicial del material.”

## 16. Diseño visual recomendado

- Estilo sobrio y profesional.
- Lenguaje visual de postproducción audiovisual.
- Fondo oscuro o neutro.
- Acento visual alineado con AILinkCinema.
- Cards claras para funcionalidades.
- Tablas/capturas del reporte como prueba visual.
- Evitar estética genérica de IA.
- Evitar claims exagerados o futuristas.

Dirección recomendada: precisión, privacidad, orden y confianza.

## 17. Assets futuros necesarios

- Logo AILinkCinema.
- Captura `report.html`.
- Captura `match_suggestions.csv`.
- Mini demo GIF o vídeo corto.
- Iconos simples para cards.
- Imagen hero sobria relacionada con montaje/postproducción.
- Favicon.
- Política de privacidad.
- Aviso legal.
- Condiciones beta.

## 18. Métricas a medir

No implementar analytics todavía. Métricas futuras recomendadas:

- Visitas landing.
- Clics CTA.
- Envíos formulario.
- Tasa de conversión.
- Roles interesados.
- Software de montaje usado.
- Interés en beta pago.
- País/ciudad.
- Problemas más repetidos.

## 19. SEO básico

**Title:** AILink Sync Dialogue — Preparación local de vídeo/audio para montaje

**Meta description:** Herramienta local de AILinkCinema para escanear carpetas de rodaje, detectar vídeo/audio, sugerir matches y generar informes HTML, CSV y JSON antes de montaje.

**H1:** Prepara el material de rodaje para montaje en minutos.

**Keywords razonables:** sincronía vídeo audio, preparación material rodaje, montaje audiovisual, postproducción, herramientas cine, ingesta audiovisual, audio separado, timecode, reporte de rodaje.

**Slug recomendado:** `/ailink-sync-dialogue-beta`

## 20. Copy final listo para implementar

### Header

AILinkCinema · AILink Sync Dialogue

Links: Qué hace · Privacidad · Beta · FAQ · Contacto

CTA: Solicitar beta

### Hero

**Prepara el material de rodaje para montaje en minutos.**

AILink Sync Dialogue analiza carpetas locales de vídeo y audio, detecta metadata disponible y sugiere posibles matches antes de abrir el proyecto de edición. Genera informes HTML, CSV y JSON sin subir el material a la nube.

CTA principal: Solicitar acceso beta

CTA secundario: Ver ejemplo de reporte

Microcopy: El material permanece en el disco del cliente. Sin cloud en la versión actual.

### Problema

Antes de montar, alguien tiene que entender el material. Vídeos, audios separados, metadata dispersa y falta de informes claros consumen tiempo antes de empezar.

### Qué hace

Escaneo local. Detección vídeo/audio. Metadata con `ffprobe` si está disponible. Sugerencias de matches. Reporte HTML. CSV/JSON para revisión.

### Cómo funciona

Selecciona carpeta local. Analiza vídeo/audio. Genera sugerencias e informe. Revisa y comparte con montaje.

### Outputs

`report.html`, `media_files.csv`, `match_suggestions.csv`, `scan_result.json`.

### Privacidad

El material no sale del disco del cliente. No se sube vídeo/audio a servidores en la versión actual.

### Beta privada

Estamos abriendo una beta privada para escuelas, productoras pequeñas/medianas y equipos de postproducción que quieran probar AILink Sync Dialogue con casos controlados.

CTA: Solicitar acceso beta

### Qué no hace todavía

No incluye waveform sync, transcripción, claqueta visual, integración directa con editores, instalador final ni UI gráfica.

### Final CTA

Si preparas material de rodaje antes de montaje, queremos probarlo contigo.

CTA: Solicitar acceso beta

### Footer

AILinkCinema · AILink Sync Dialogue · Beta privada

## 21. Criterios de aceptación

Este documento se considera aceptado si:

- Está en español claro.
- Sirve como especificación directa de landing.
- No implementa código.
- No modifica frontend.
- No promete funcionalidades inexistentes.
- Mantiene privacidad/local-first.
- Distingue beta, prototipo y futuro.
- Conecta correctamente AILink Sync Dialogue con AILinkCinema.
- No vende AILink Sync Dialogue como CID.
