# AILink Sync Dialogue — Landing & Beta Copy v1

## 1. Título

**AILink Sync Dialogue — Landing & Beta Copy v1**

Documento base de copy comercial para futura landing, invitación a beta privada, publicaciones sociales, email y formulario de interés.

## 2. Posicionamiento corto

AILink Sync Dialogue es una herramienta local para preparar material de vídeo y audio antes de montaje. Analiza carpetas, detecta archivos de vídeo/audio, sugiere posibles matches y genera informes en HTML, CSV y JSON.

El material no sale del disco del cliente: la revisión se ejecuta localmente y los outputs se generan en una carpeta elegida por el usuario.

## 3. Hero principal para landing

### Variante A

**Titular:** Prepara el material de rodaje para montaje en minutos.

**Subtitular:** Escanea carpetas locales de vídeo y audio, revisa metadata y detecta posibles parejas antes de abrir el proyecto de edición. Genera informes claros para montaje y postproducción sin subir el material a la nube.

**CTA principal:** Solicitar acceso beta

**CTA secundario:** Ver cómo funciona

### Variante B

**Titular:** Convierte carpetas de vídeo y audio en un informe claro para postproducción.

**Subtitular:** AILink Sync Dialogue detecta clips, audios separados, metadata disponible y candidatos de sincronía con razones explicables. Pensado para equipos que necesitan ordenar material antes de montar.

**CTA principal:** Unirme a la beta privada

**CTA secundario:** Descargar ejemplo de informe

### Variante C

**Titular:** Detecta, ordena y revisa posibles sincronías antes de montar.

**Subtitular:** Una herramienta local para ayudantes de montaje, escuelas y productoras que necesitan una primera lectura del material de rodaje: vídeo, audio, timecode, duración y reportes compartibles.

**CTA principal:** Probar en beta

**CTA secundario:** Hablar con AILinkCinema

## 4. Problema que resuelve

Antes de empezar a montar, alguien tiene que entender qué hay dentro de la carpeta de rodaje. En equipos pequeños, escuelas o productoras medianas, esa tarea suele hacerse a mano: abrir carpetas, mirar nombres, revisar audios, comprobar duraciones y buscar si el timecode existe.

El problema no es solo técnico. Es tiempo perdido antes de llegar al montaje creativo:

- Carpetas de rodaje desordenadas o copiadas sin estructura clara.
- Vídeo y audio separados que deben relacionarse manualmente.
- Metadata difícil de revisar archivo por archivo.
- Dudas sobre duración, fps, canales, codec o timecode.
- Falta de un informe simple para compartir con montaje o postproducción.

AILink Sync Dialogue ayuda a convertir esa primera revisión en un proceso más claro. No promete sincronizarlo todo automáticamente: entrega información y candidatos para que el equipo revise con criterio.

## 5. Qué hace ahora

Funcionalidades actuales del prototipo:

- Escanea una carpeta local.
- Detecta vídeo/audio por extensiones soportadas.
- Lee metadata si `ffprobe` está disponible.
- Sugiere matches por timecode, nombre, carpeta y duración.
- Genera `scan_result.json`.
- Genera `media_files.csv`.
- Genera `match_suggestions.csv`.
- Genera `report.html` imprimible.
- Permite una demo local sin nube.

## 6. Qué no hace todavía

Limitaciones actuales:

- No hay waveform sync todavía.
- No hay transcripción todavía.
- No hay detección de claqueta visual todavía.
- No hay integración directa con DaVinci Resolve, Avid Media Composer o Adobe Premiere Pro todavía.
- No hay UI gráfica todavía.
- No hay instalador todavía.
- No hay cloud.
- No hay SaaS conectado todavía.
- No sustituye al montador ni al ayudante de montaje.

## 7. Bloque de privacidad

### El material no sale del disco del cliente.

AILink Sync Dialogue está planteado como una herramienta local. En la versión actual, el análisis se ejecuta sobre una carpeta del usuario y los resultados se escriben en una carpeta local.

Esto significa:

- No hay subida de material audiovisual a servidores.
- No hay cloud en esta versión.
- Los outputs se generan localmente: HTML, CSV y JSON.
- Es adecuado para pruebas con material sensible, privado o de producción.
- Reduce fricción legal y operativa para escuelas, productoras y equipos independientes.

## 8. Público objetivo

AILink Sync Dialogue está pensado para:

- Escuelas de cine que necesitan enseñar ingesta y organización de material.
- Productoras pequeñas y medianas sin DIT dedicado en todos los proyectos.
- Ayudantes de montaje que preparan material antes de editar.
- DIT/data wranglers que necesitan entregar reportes claros.
- Equipos de postproducción que reciben vídeo/audio de diferentes fuentes.
- Coordinadores de producción que necesitan visibilidad rápida del material.

## 9. Beneficios

- Menos tiempo revisando carpetas manualmente.
- Visión rápida del material detectado.
- Informe compartible para montaje y postproducción.
- Candidatos de sincronía explicables, con score y reasons.
- Preparación previa al montaje sin abrir aún el proyecto de edición.
- Útil para formación, rodajes pequeños y equipos medianos.
- Privacidad por diseño: el material permanece local.

## 10. Cómo funciona

1. **Selecciona carpeta local.** El usuario indica la carpeta del día de rodaje o del proyecto.
2. **Analiza vídeo/audio.** La herramienta detecta archivos soportados y lee metadata cuando está disponible.
3. **Genera sugerencias e informe.** Produce candidatos de matching y outputs en JSON, CSV y HTML.
4. **Revisa y entrega a montaje.** El equipo usa el reporte para decidir qué revisar, importar o sincronizar.

Estado actual: el prototipo se ejecuta por CLI. La interfaz gráfica vendrá después si la beta valida utilidad real.

## 11. Oferta beta privada

Propuesta de beta:

- Acceso temprano a una herramienta local de ingesta y matching sugerido.
- Beta orientada a escuelas, productoras y equipos de postproducción.
- Plazas limitadas para poder acompañar pruebas reales.
- Feedback a cambio de precio reducido y soporte cercano.
- Sin compromiso de permanencia.
- Casos controlados para evitar promesas fuera del estado actual.

Precio orientativo prudente:

- Desde 25 €/mes durante los primeros meses de beta.
- Alternativa: precio beta por definir según perfil, tamaño de equipo y uso previsto.

Mensaje recomendado: “Estamos abriendo una beta privada para validar si esta herramienta ahorra tiempo real antes del montaje. No es un producto final cerrado; es acceso anticipado con feedback directo.”

## 12. Formulario de interés

Campos recomendados:

- Nombre.
- Email.
- Empresa/escuela.
- Rol.
- País/ciudad.
- Tipo de proyecto.
- Software de montaje usado: DaVinci Resolve, Avid Media Composer, Adobe Premiere Pro, otro.
- ¿Trabajáis con timecode?
- ¿Grabáis audio separado?
- Volumen aproximado de material por proyecto.
- Principal problema actual al preparar material.
- Interés en beta de pago.
- Permiso para contacto.

## 13. FAQ comercial

### ¿Sube mi material a la nube?

No en la versión actual. La herramienta trabaja localmente y genera outputs en la carpeta que el usuario elige.

### ¿Necesito GPU?

No. El prototipo actual no usa GPU.

### ¿Funciona con DaVinci/Avid/Premiere?

Todavía no hay integración directa. Hoy genera HTML, CSV y JSON que pueden servir como referencia antes de trabajar en el editor.

### ¿Sincroniza automáticamente?

No. Sugiere posibles matches vídeo/audio con razones explicables. La decisión final sigue siendo del equipo de montaje.

### ¿Lee timecode?

Sí, cuando la metadata está disponible y `ffprobe` puede leerla. Si no hay timecode, usa señales secundarias como nombre, carpeta y duración.

### ¿Qué archivos genera?

Genera `scan_result.json`, `media_files.csv`, `match_suggestions.csv` y `report.html`.

### ¿Es CID?

No. AILink Sync Dialogue es una herramienta independiente de AILinkCinema. CID es el SaaS integral y no es necesario para usar esta herramienta.

### ¿Necesito instalar algo?

Ahora mismo es un prototipo local ejecutado por CLI en un entorno preparado. Un instalador final queda para una fase posterior.

### ¿Puedo usarlo en una escuela?

Sí, es uno de los casos de uso más claros: ordenar material, enseñar ingesta y revisar candidatos de sincronía sin subir archivos a servidores.

### ¿Cuándo estará disponible?

La beta privada se abrirá de forma controlada. El objetivo es probar con casos reales antes de convertirlo en producto final.

### ¿Puedo probarlo con material real?

Sí, con autorización y en entorno local. La recomendación inicial es empezar con una carpeta pequeña y controlada.

## 14. Copy para LinkedIn

### A. Post teaser corto

Estamos preparando **AILink Sync Dialogue**, una herramienta local para revisar material de vídeo y audio antes de montaje.

Escanea carpetas, detecta clips y audios, sugiere posibles matches y genera un informe HTML/CSV/JSON sin subir el material a la nube.

No sustituye al montador. Ayuda a empezar con más orden.

CTA: Si trabajas en montaje, postproducción o formación audiovisual y quieres probar la beta privada, escríbeme.

### B. Post problema/solución

Una parte poco visible del montaje empieza antes de montar: entender qué hay en una carpeta de rodaje.

Vídeos, audios separados, nombres inconsistentes, timecode que hay que revisar, metadata dispersa y pocas horas para preparar el material.

AILink Sync Dialogue nace para resolver esa primera capa: escanear una carpeta local, detectar vídeo/audio, sugerir candidatos de sincronía y generar un informe claro para montaje o postproducción.

No promete sincronizarlo todo automáticamente. Entrega información, score y razones para revisar mejor.

CTA: Buscamos escuelas, productoras y equipos de postproducción para beta privada.

### C. Post beta privada

Abrimos lista de interés para la beta privada de **AILink Sync Dialogue**.

Qué hace hoy:

- Escanea carpetas locales.
- Detecta vídeo/audio.
- Lee metadata si está disponible.
- Sugiere matches por timecode/nombre/carpeta/duración.
- Genera HTML, CSV y JSON.

Qué no hace todavía: waveform sync, transcripción, claqueta visual, instalador o integración directa con editores.

CTA: Si quieres probarlo con un caso controlado, envíame tu rol, software de montaje y tipo de proyectos.

## 15. Copy para Facebook

### Versión A

Estoy preparando una herramienta local para equipos de cine y montaje: **AILink Sync Dialogue**.

Sirve para revisar una carpeta de rodaje, detectar vídeos y audios, ver metadata disponible y generar un informe claro antes de empezar a montar.

El material no se sube a la nube. Todo se trabaja en local.

Si eres montador/a, estudiante de cine, profe, productora o trabajas en postproducción, estoy buscando gente para probar la beta.

### Versión B

¿Te ha llegado alguna vez una carpeta de rodaje con vídeos, audios separados y poca información clara?

AILink Sync Dialogue intenta ordenar esa primera revisión: detecta archivos, genera tablas, sugiere posibles parejas vídeo/audio y crea un reporte HTML para compartir con montaje.

No monta por ti. No sustituye a nadie. Ayuda a preparar mejor el material.

Si quieres entrar en la beta privada, escríbeme.

## 16. Email corto de invitación beta

**Asunto:** Invitación beta privada: AILink Sync Dialogue para preparación de material de montaje

Hola [Nombre],

Estoy preparando **AILink Sync Dialogue**, una herramienta local de AILinkCinema para revisar carpetas de rodaje antes de montaje.

El prototipo actual detecta vídeo/audio, lee metadata si está disponible, sugiere posibles matches y genera informes en HTML, CSV y JSON. El material no se sube a la nube: se trabaja localmente.

Me gustaría invitaros a una beta privada con casos controlados, especialmente si trabajáis con audio separado, timecode o mucho material que preparar antes de editar.

No es un producto final cerrado; buscamos feedback real de escuelas, productoras y equipos de postproducción.

CTA: ¿Te interesaría ver una demo de 10 minutos o probarlo con una carpeta pequeña?

Un saludo,

Juan Carlos / AILinkCinema

## 17. Mensaje corto para WhatsApp/DM

Hola [Nombre], estoy preparando **AILink Sync Dialogue**, una herramienta local para revisar carpetas de rodaje antes de montaje: detecta vídeo/audio, metadata y posibles matches, y genera un informe HTML/CSV/JSON. No sube material a la nube. Estoy abriendo beta privada con casos controlados. ¿Te interesaría verlo en una demo corta?

## 18. Frases que NO usar

- “Sincroniza todo automáticamente.”
- “Sustituye al montador.”
- “IA que monta por ti.”
- “Compatible con todos los formatos.”
- “100% exacto.”
- “Sube tus archivos y lo hacemos todo.”
- “CID para todo el mundo” aplicado a esta herramienta.
- “No tendrás que revisar nada.”
- “Funciona igual en cualquier cámara y grabadora.”

## 19. Mensaje aprobado de conexión con AILinkCinema/CID

AILink Sync Dialogue es una herramienta independiente de AILinkCinema para una tarea concreta: preparar material de vídeo/audio antes de montaje.

En el futuro, capacidades similares podrán conectarse dentro de CID. CID es el SaaS integral: **Cinematic Intelligence Direction**.

No vender esta herramienta como CID. El mensaje correcto es: “AILink Sync Dialogue funciona por sí sola, y más adelante podrá alimentar workflows más amplios dentro del ecosistema AILinkCinema.”

## 20. Criterios de aceptación

Este documento se considera aceptado si:

- Está en español claro.
- Es comercial pero honesto.
- No promete funcionalidades inexistentes.
- Distingue prototipo, beta y futuro.
- Mantiene privacidad como punto fuerte.
- No usa “CID” como nombre de la herramienta independiente.
- Sirve como base para landing, LinkedIn, Facebook, email y formulario beta.
