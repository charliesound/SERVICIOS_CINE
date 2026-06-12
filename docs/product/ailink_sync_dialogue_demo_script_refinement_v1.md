# AILink Sync Dialogue — Demo Script Refinement v1

## 1. Objetivo

Este documento convierte la evidence run de AILink Sync Dialogue en un guion hablado de demo de 5 a 7 minutos.

La finalidad es poder enseñar el prototipo a una persona de confianza sin exagerar el estado del producto, sin prometer sincronización automática final y sin confundir una demo controlada con un producto terminado.

Esta fase responde directamente a:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7.
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1.
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.PHASE7.2.
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.EVIDENCE.RUN.PHASE7.3.

Esta fase es documental y de guion. No implementa código, no modifica scanner, no modifica matching, no modifica exports, no modifica reportes, no crea UI real, no crea backend, no crea frontend, no crea instalador, no crea n8n, no crea CRM, no toca PostgreSQL real, no toca Docker, no toca runtime, no toca configuración y no modifica CID SaaS.

## 2. Estado que debe declararse

Estado actual:

- LIMITED PASS.
- Demo interna permitida.
- Demo con persona de confianza permitida.
- Demo pública no recomendada todavía.
- Contacto con escuelas o productoras no recomendado todavía como demo final.

Frase obligatoria:

> AILink Sync Dialogue está en una fase beta controlada. Ya genera outputs locales útiles para revisar vídeo, audio, metadata y sugerencias de matching, pero todavía no debe presentarse como sincronizador automático final.

## 3. Público permitido para este guion

Permitido:

- Ensayo interno.
- Persona de confianza.
- Colaborador técnico cercano.
- Montador o sonidista de confianza con expectativa controlada.

No recomendado todavía:

- Escuelas de cine como presentación pública.
- Productoras externas como propuesta cerrada.
- Leads fríos.
- LinkedIn público como demo final.
- Venta directa con precio cerrado.

## 4. Objetivo de la demo de 5 a 7 minutos

La demo debe demostrar cuatro cosas:

1. Hay un problema real antes de montaje: ordenar vídeo, audio y metadata consume tiempo.
2. El prototipo ya puede escanear o generar una muestra controlada y producir outputs.
3. El reporte permite leer la situación de forma más clara que una carpeta suelta.
4. La beta necesita feedback real antes de convertirse en herramienta comercial pública.

La demo no debe intentar demostrar:

- Sincronización automática final.
- Waveform sync.
- Transcripción.
- Detección visual de claqueta.
- Integración directa con editores.
- Instalador final.
- Procesamiento de material sensible de cliente.
- Funcionamiento cloud.
- Funcionamiento SaaS CID.

## 5. Material recomendado para enseñar

Para esta fase el material recomendado es:

- Metadata demo controlada para enseñar matching sugerido.
- Report HTML generado.
- CSV de media files.
- CSV de match suggestions.
- JSON solo si el interlocutor es técnico.

La e2e demo con dummy fixture puede mencionarse como evidencia técnica, pero no debe ser la pieza visual principal si se quiere explicar matching, porque puede dar 0 match suggestions por no tener metadata real.

Frase para explicar el dummy fixture:

> En esta ejecución e2e los matches salen a 0 porque el fixture usa archivos dummy sin metadata real. No es un fallo de ejecución; es una prueba de flujo local para comprobar que genera JSON, CSV y HTML sin tocar material real.

## 6. Mensaje central

Mensaje central:

> AILink Sync Dialogue no pretende sustituir al montador ni cerrar una sincronización final. Ahora mismo ayuda a revisar material audiovisual local, detectar estructura de vídeo y audio, proponer coincidencias cuando hay señales suficientes y generar un reporte que facilita decidir el siguiente paso antes de montaje.

Versión corta:

> Es una herramienta local-first para ordenar vídeo, audio y metadata antes de montaje, con reporte y sugerencias de matching en beta controlada.

Versión honesta:

> Lo valioso hoy no es prometer automatización total, sino ahorrar revisión manual inicial y descubrir problemas antes de entrar en montaje.

## 7. Guion hablado completo — 5 a 7 minutos

### 0:00–0:40 — Apertura

Objetivo:

- Situar el problema.
- Declarar que es beta controlada.
- Bajar expectativas de producto final.

Texto recomendado:

> Te voy a enseñar una demo controlada de AILink Sync Dialogue. No es todavía un sincronizador final ni una herramienta cerrada de postproducción. Es una beta local-first pensada para revisar vídeo, audio y metadata antes de montaje y generar un reporte útil para detectar coincidencias, huecos y problemas.

Mostrar:

- Nombre AILink Sync Dialogue.
- Carpeta o assets de demo controlada.
- No mostrar material real de cliente.

No decir:

- “Esto sincroniza todo automáticamente”.
- “Esto ya sustituye a PluralEyes, DaVinci o Avid”.
- “Esto ya funciona con cualquier rodaje real”.

### 0:40–1:20 — Problema

Objetivo:

- Conectar con un dolor real de montaje/postproducción.
- Hablar desde experiencia audiovisual.

Texto recomendado:

> En muchos rodajes, antes de empezar a montar, alguien tiene que revisar qué vídeos hay, qué audios hay, qué nombres coinciden, qué timecodes existen, qué archivos están incompletos y qué material puede emparejarse. En producciones pequeñas o escuelas esto muchas veces se hace a mano, y ahí se pierde tiempo o se arrastran errores al montaje.

Mostrar:

- Lista simple de vídeo/audio.
- Ejemplo de nombres escena/toma.
- Idea de “antes de montaje”.

No decir:

- “La IA monta por ti”.
- “Esto resuelve todo el workflow de postproducción”.

### 1:20–2:10 — Qué hace hoy

Objetivo:

- Explicar alcance actual real.
- Diferenciar outputs de promesas futuras.

Texto recomendado:

> Lo que hace hoy esta beta es ordenar una muestra controlada de material, leer datos disponibles, generar una tabla de archivos, proponer posibles matches cuando hay señales como timecode, duración o nombre, y crear un reporte HTML que una persona puede revisar sin entrar en una herramienta técnica.

Mostrar:

- `media_files.csv`.
- `match_suggestions.csv`.
- `report.html`.

Puntos permitidos:

- Escaneo local.
- Metadata.
- Sugerencias de matching.
- Reporte HTML.
- CSV.
- JSON como salida técnica.

Puntos no permitidos:

- Waveform sync.
- Transcripción.
- Claqueta visual.
- Integración con NLE.
- Instalador final.

### 2:10–3:10 — Evidence run real

Objetivo:

- Apoyar el discurso con evidencias reales.
- Usar números concretos.

Texto recomendado:

> En la evidence run interna, la metadata demo generó 3 vídeos, 4 audios, 5 sugerencias de matching y 2 sugerencias de alta confianza. Además generó JSON, CSV y HTML. Eso demuestra que el flujo local produce outputs revisables.

Mostrar:

- Resumen de metadata demo.
- Report HTML.
- Tabla de match suggestions.

Números permitidos:

- 3 vídeos.
- 4 audios.
- 5 match suggestions.
- 2 high confidence.
- 7 media rows.
- 5 match rows.

No exagerar:

- No decir que estos números representan material real de cliente.
- No decir que la precisión está validada en rodajes reales.
- No decir que el sistema ya decide el sync final.

### 3:10–4:20 — Lectura del reporte

Objetivo:

- Enseñar qué debe mirar una persona.
- Traducir la salida técnica a utilidad práctica.

Texto recomendado:

> Aquí lo importante no es que el sistema tome la decisión final, sino que ordena información. Puedo ver qué vídeo se relaciona con qué audio, qué confianza tiene la sugerencia, por qué lo propone y qué casos necesitan revisión manual.

Mostrar:

- Columna de confidence.
- Razones como matching_timecode.
- Razones como duration_delta_lte_3s.
- Razones como shared_name_tokens.

Explicación de shared_name_tokens:

> shared_name_tokens no es un token secreto y no es una credencial. Es una razón técnica que indica que vídeo y audio comparten partes del nombre, por ejemplo escena o toma.

No decir:

- “High confidence significa sincronización aprobada”.
- “Low confidence se descarta automáticamente”.
- “El reporte reemplaza al criterio del montador”.

### 4:20–5:10 — Explicación del e2e dummy

Objetivo:

- Evitar que el resultado 0 matches parezca fallo.
- Explicar por qué existe esa prueba.

Texto recomendado:

> También hay una demo e2e con archivos dummy. Esa prueba sirve para comprobar el flujo completo sin material real: crea una fixture local, genera JSON, CSV y HTML, y no toca datos sensibles. En esa ejecución puede salir 0 match suggestions porque los archivos dummy no tienen metadata real. Eso es esperado y no debe venderse como una prueba de matching.

Mostrar:

- Si se enseña, solo enseñar resumen.
- No dedicar demasiado tiempo.
- Volver rápido al reporte de metadata demo.

Frase clave:

> La metadata demo enseña el matching; la e2e dummy enseña que el flujo local genera outputs sin material real.

### 5:10–6:00 — Límites honestos

Objetivo:

- Proteger la credibilidad.
- Evitar claims peligrosos.

Texto recomendado:

> Lo que todavía no hay que prometer es waveform sync, transcripción, detección automática de claqueta visual, instalador final, integración directa con DaVinci, Avid o Premiere, ni sincronización final sin revisión humana. Esta fase sirve para validar si el reporte y las sugerencias ayudan realmente antes de montaje.

Lista rápida de límites:

- No waveform sync.
- No transcripción.
- No claqueta visual.
- No instalador final.
- No integración directa con editores.
- No sincronización final garantizada.
- No material sensible de cliente en demo.

### 6:00–6:45 — Qué feedback pedir

Objetivo:

- Convertir demo en aprendizaje.
- No vender antes de validar.

Texto recomendado:

> Lo que me interesa ahora no es venderlo como producto terminado. Quiero saber si este reporte ayuda, qué columnas sobran o faltan, si las razones de matching se entienden, qué formatos usáis y qué tendría que resolver para que os mereciera la pena probar una beta con material controlado.

Preguntas concretas:

- ¿El reporte se entiende en menos de dos minutos?
- ¿Qué columna falta para montaje?
- ¿Qué te daría más confianza en una sugerencia?
- ¿Qué formatos usáis normalmente?
- ¿Dónde encajaría esto en vuestro flujo?
- ¿Qué tendría que hacer para que pagaras una beta barata?

### 6:45–7:00 — Cierre

Objetivo:

- Cerrar con beta controlada.
- No forzar venta.

Texto recomendado:

> Mi siguiente paso es pulir la demo con feedback de una persona de confianza y después decidir si tiene sentido abrir una beta privada muy controlada. Prefiero ir paso a paso y no prometer más de lo que el sistema demuestra hoy.

CTA permitido:

> Si te parece útil, me interesa que me digas qué parte te aporta valor y qué parte no enseñarías todavía a un equipo real.

## 8. Qué enseñar y qué no enseñar

### Enseñar

- Report HTML de metadata demo.
- Tabla de media files.
- Tabla de match suggestions.
- Resumen de evidence run.
- Mensaje local-first.
- Estado LIMITED PASS.

### Mencionar con cuidado

- E2E dummy.
- JSON.
- CSV técnico.
- Futuras integraciones.
- Posible beta privada.

### No enseñar todavía como promesa comercial

- Material real de cliente.
- Demo pública a escuelas.
- Demo pública a productoras.
- Precio cerrado.
- Formulario real de pago.
- Integración con editores.
- Workflow SaaS CID.
- Automatización final.

## 9. Frases prohibidas

No usar:

- “Sincroniza automáticamente todo el material”.
- “Ya está listo para productoras”.
- “Reemplaza el trabajo del montador”.
- “Funciona con cualquier cámara y cualquier grabador”.
- “Detecta claqueta visual”.
- “Transcribe diálogos”.
- “Se integra con DaVinci, Avid y Premiere”.
- “Puedes subir material sensible sin problema”.
- “Es el módulo final de CID”.
- “Ya está preparado para venta pública”.

## 10. Frases permitidas

Usar:

- “Beta controlada”.
- “Demo local-first”.
- “Outputs revisables”.
- “Sugerencias de matching”.
- “Ayuda a ordenar material antes de montaje”.
- “No sustituye la revisión humana”.
- “No es sincronización final”.
- “La demo usa material controlado”.
- “Estamos validando utilidad real”.
- “LIMITED PASS para demo interna”.

## 11. Respuestas preparadas

### Si preguntan si ya sincroniza automáticamente

Respuesta:

> No todavía. Ahora genera sugerencias y un reporte revisable. La sincronización automática final requiere más validación, waveform sync, casos reales y revisión de errores.

### Si preguntan por DaVinci, Avid o Premiere

Respuesta:

> La integración directa no está en esta fase. Primero estoy validando que el reporte previo a montaje sea útil. Después tendrá sentido estudiar exportaciones o integración con editores.

### Si preguntan por transcripción

Respuesta:

> No forma parte de esta demo. Puede ser una fase futura, pero hoy no quiero mezclarlo con lo que ya está demostrado.

### Si preguntan por claqueta visual

Respuesta:

> Todavía no se está enseñando detección visual de claqueta. Esta demo se centra en metadata, nombres, duración, timecode cuando existe y reporte.

### Si preguntan por privacidad

Respuesta:

> La demo actual es local-first y usa material controlado. La regla es no usar material sensible ni material de cliente en una demo sin garantías adicionales.

### Si preguntan por precio

Respuesta:

> Todavía no estoy cerrando precio comercial. El objetivo ahora es validar utilidad con una beta controlada y entender qué valor real tiene para montaje o postproducción.

### Si preguntan por escuelas o productoras

Respuesta:

> Antes de abrirlo a escuelas o productoras quiero ensayarlo con una persona de confianza. La evidence run da LIMITED PASS, no PASS público.

## 12. Checklist antes de ensayar

Antes del ensayo:

- Confirmar que el repo está limpio.
- Confirmar que no se enseña material de cliente.
- Tener abierta la metadata demo o sus capturas.
- Tener claro que la e2e dummy puede dar 0 matches.
- Tener preparada la frase de LIMITED PASS.
- Tener preparada la lista de límites.
- Tener preparada la plantilla de feedback.
- No abrir módulos CID.
- No abrir n8n.
- No abrir CRM.
- No abrir configuración ni secretos.

## 13. Plantilla de feedback post-demo

Preguntas para la persona de confianza:

1. ¿Has entendido qué problema resuelve?
2. ¿Has entendido que no es sincronización final?
3. ¿Qué parte del reporte te parece útil?
4. ¿Qué parte no se entiende?
5. ¿Qué columna falta?
6. ¿Qué salida necesitarías para montaje?
7. ¿Te parece suficiente para una beta privada?
8. ¿Qué no debería enseñar todavía?
9. ¿Qué pregunta haría una escuela?
10. ¿Qué pregunta haría una productora?

## 14. Criterio de éxito de Phase7.4

Esta fase pasa si existe:

- Guion hablado de 5 a 7 minutos.
- Mensaje LIMITED PASS explícito.
- Explicación de 0 matches en e2e dummy.
- Lista de frases prohibidas.
- Lista de frases permitidas.
- Respuestas preparadas.
- Checklist antes de ensayar.
- Plantilla de feedback.
- Non-goals técnicos claros.

## 15. Siguiente paso recomendado

La siguiente fase recomendada es:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.DRY.RUN.PHASE7.5

Objetivo:

- Ensayar el guion sin grabar vídeo público.
- Cronometrar la demo.
- Detectar frases peligrosas.
- Ajustar el orden de pantalla.
- Decidir si pasa de LIMITED PASS a PASS interno con persona de confianza.

## 16. Resumen ejecutivo

AILink Sync Dialogue ya tiene evidencias técnicas locales suficientes para una demo interna.

La comunicación todavía debe ser prudente.

El guion correcto no vende automatización final; vende una beta local-first que genera outputs revisables para ordenar material antes de montaje.

La demo debe cerrar pidiendo feedback, no venta.
