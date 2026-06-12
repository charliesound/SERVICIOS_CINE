# AILink Sync Dialogue — Demo Readiness v1

## 1. Objetivo

Este documento audita el estado de preparación de la demo de AILink Sync Dialogue.

La finalidad es decidir qué partes del producto pueden enseñarse ya, qué partes deben presentarse como beta, qué límites hay que explicar con honestidad y qué falta antes de mostrar la herramienta a escuelas de cine, productoras, montadores o técnicos de postproducción.

Esta fase es documental y de preparación comercial. No implementa código, no modifica scanner, no modifica matching, no modifica exports, no modifica reportes, no crea UI real, no crea backend, no crea frontend, no crea instalador, no crea n8n, no crea CRM, no toca PostgreSQL real, no toca Docker, no toca runtime, no toca configuración y no modifica CID SaaS.

## 2. Contexto

AILink Sync Dialogue es una herramienta independiente de AILinkCinema orientada a ingesta, revisión y preparación de material audiovisual para montaje.

El foco actual no es sustituir a DaVinci Resolve, Avid, Premiere o herramientas profesionales de conformado. El foco es ofrecer una capa previa de análisis local que ayude a entender carpetas de rodaje, detectar vídeo/audio, leer metadata cuando exista, sugerir matches y generar reportes claros.

## 3. Estado actual conocido

El producto ya cuenta con piezas documentadas y validadas en fases anteriores:

- Scanner local de archivos.
- Esquemas de datos.
- Export JSON.
- Export CSV.
- Sugerencias de matching.
- Reporte HTML imprimible.
- Fixture demo reproducible.
- Runner demo end-to-end.
- Demo con metadata real mínima.
- Landing estática exportable.
- Social launch pack.
- Guion de vídeo demo.
- Subtítulos de vídeo demo.
- Runbook de montaje del vídeo demo.
- Production pack spec.
- Beta leads operations runbook.
- Outreach starter pack.
- Commercial readiness QA.
- Launch index summary.

## 4. Qué se puede enseñar ya

Se puede enseñar como demo controlada:

- Escaneo local de una carpeta.
- Detección de archivos de vídeo.
- Detección de archivos de audio.
- Generación de JSON de resultado.
- Generación de CSV de media.
- Generación de CSV de sugerencias de matching.
- Generación de reporte HTML.
- Flujo end-to-end reproducible.
- Explicación de scoring y reasons en matching cuando existan datos suficientes.
- Enfoque local-first y prudente con privacidad.
- Utilidad para preparar revisión de material antes de montaje.

## 5. Qué debe presentarse como beta

Debe presentarse como beta:

- Matching automático.
- Interpretación de metadata según archivos reales.
- Fiabilidad de sugerencias según naming, timecode y estructura de carpeta.
- Reporte HTML como primera versión de salida.
- Flujo de trabajo de revisión para montaje.
- Uso con material heterogéneo de rodaje.
- Posible evolución hacia PDF, transcripción, claqueta, waveform y NLE bridges.

## 6. Qué no se debe prometer todavía

No prometer todavía:

- Sincronización perfecta en todos los casos.
- Lectura universal de todos los formatos profesionales.
- Sustitución de DaVinci Resolve, Avid, Premiere o herramientas de sonido.
- Export XML/AAF/EDL definitivo.
- Transcripción robusta.
- Detección automática de claqueta.
- Matching por waveform.
- OCR de claqueta.
- Instalador Mac/Windows.
- UI profesional final.
- SaaS multiusuario.
- Procesamiento cloud.
- Integración real con CID SaaS.
- Integración real con CRM/n8n.
- Garantía legal o contractual de resultados.

## 7. Mensaje honesto de demo

Mensaje recomendado:

AILink Sync Dialogue es una herramienta local-first para analizar carpetas de material, detectar vídeo y audio, leer metadata disponible, sugerir posibles correspondencias y generar reportes claros para preparar el trabajo de montaje.

No pretende sustituir al montador ni al DIT. Busca ahorrar tiempo en la primera revisión del material y crear una base ordenada para decidir qué falta, qué coincide y qué necesita revisión humana.

## 8. Demo comercial de 5 a 7 minutos

Estructura recomendada:

### Minuto 0:00–0:45 — Problema

Explicar el problema:

- Carpetas de rodaje desordenadas.
- Audio y vídeo separados.
- Naming irregular.
- Metadata no siempre clara.
- Montaje recibe material sin una vista rápida.
- Mucho tiempo perdido antes de empezar a editar.

### Minuto 0:45–1:30 — Propuesta

Explicar la propuesta:

- Escaneo local.
- Detección de media.
- Metadata disponible.
- Sugerencias de matching.
- Reporte operativo.
- Privacidad local-first.

### Minuto 1:30–3:30 — Demo técnica controlada

Mostrar:

- Carpeta demo.
- Ejecución del flujo local.
- Archivos generados.
- JSON.
- CSV.
- Reporte HTML.
- Explicación de matches si existen.
- Alertas o limitaciones.

### Minuto 3:30–5:00 — Lectura del reporte

Mostrar cómo se interpreta:

- Qué archivos se detectaron.
- Qué audios/vídeos aparecen.
- Qué sugerencias se generan.
- Qué necesita revisión humana.
- Cómo ayuda a montaje.

### Minuto 5:00–6:15 — Beta y límites

Explicar:

- Qué está validado.
- Qué falta probar con material real.
- Qué no se promete todavía.
- Qué feedback se busca.

### Minuto 6:15–7:00 — Invitación

Cerrar con:

- Beta privada.
- Perfil de testers buscado.
- Tipo de material útil.
- Contacto o lista de espera.
- Próximos pasos.

## 9. Checklist antes de enseñar a terceros

Antes de enseñar a terceros, comprobar:

- Repo limpio.
- Demo runner funciona.
- Fixture demo funciona.
- Reporte HTML se abre correctamente.
- No hay rutas internas sensibles visibles.
- No hay datos personales reales.
- No hay material audiovisual de cliente.
- Mensaje comercial está claro.
- Claims prohibidos revisados.
- Limitaciones explicadas.
- Preguntas frecuentes preparadas.
- Oferta beta definida.
- Flujo de feedback preparado.

## 10. Checklist técnico de demo

Comprobar:

- El comando de demo se ejecuta desde WSL.
- La carpeta de trabajo es segura.
- La demo no depende de red.
- La demo no depende de GPU.
- La demo no toca CID SaaS.
- La demo no toca PostgreSQL real.
- La demo no requiere n8n.
- La demo no requiere Docker.
- Los outputs se generan en rutas controladas.
- El reporte HTML es legible.

## 11. Checklist comercial de demo

Comprobar:

- Se explica el problema en lenguaje de montaje/postproducción.
- Se evita vender humo.
- Se dice claramente que es beta.
- Se pide feedback concreto.
- Se explica para quién sirve.
- Se explica para quién no sirve todavía.
- Se define qué tipo de material interesa para prueba.
- Se evita prometer integración inmediata con NLE.
- Se evita prometer automatización completa.

## 12. Preguntas esperables

Preguntas probables:

- ¿Sincroniza audio y vídeo automáticamente?
- ¿Lee timecode?
- ¿Funciona con archivos de sonido directo?
- ¿Funciona con material de cámara profesional?
- ¿Genera XML para DaVinci o Avid?
- ¿Transcribe diálogos?
- ¿Detecta claqueta?
- ¿Funciona sin subir material?
- ¿Qué pasa con material sin timecode?
- ¿Qué diferencia hay con hacerlo manualmente?
- ¿Cuánto costará la beta?
- ¿Qué datos se guardan?

## 13. Respuestas recomendadas

Respuesta sobre sincronización:

La herramienta no debe venderse todavía como sincronizador perfecto. En la fase actual su valor es analizar material, extraer metadata disponible, sugerir correspondencias y generar un reporte que acelere la revisión humana.

Respuesta sobre timecode:

Si la metadata está disponible y ffprobe puede leerla, la herramienta puede usarla como señal. Si no hay timecode o los archivos no lo exponen bien, se apoya en otras señales como nombre, duración o carpeta, siempre con una confianza limitada.

Respuesta sobre nube:

La orientación actual es local-first. La demo no necesita subir material sensible a la nube.

Respuesta sobre beta:

La beta busca probar la herramienta con casos reales, detectar formatos problemáticos, mejorar matching y validar si el reporte ayuda realmente al flujo de montaje.

## 14. Huecos actuales

Huecos importantes antes de una demo más ambiciosa:

- PDF real exportable.
- Mejor dataset de demo con media válida.
- Ejemplos con metadata real diversa.
- Más explicación visual del scoring.
- Posible output para NLE en fase futura.
- Transcripción opcional.
- Waveform matching futuro.
- Claqueta/OCR futuro.
- Instalador futuro.
- UI futura.

## 15. Criterios de demo lista

La demo puede considerarse lista para una primera presentación controlada si:

- Ejecuta end-to-end sin errores.
- Produce outputs comprensibles.
- Se puede explicar en menos de 7 minutos.
- No muestra datos sensibles.
- No promete funciones no implementadas.
- Tiene mensaje comercial claro.
- Tiene límites claros.
- Permite pedir feedback concreto.
- Permite detectar interés real.

## 16. Criterios para no enseñar todavía

No enseñar todavía si:

- La demo falla de forma intermitente.
- El reporte no se entiende.
- Los outputs requieren demasiada explicación técnica.
- Se confunde con CID SaaS.
- se vende como sincronizador final.
- No está claro qué feedback se pide.
- No hay material de ejemplo seguro.
- Se necesitan dependencias no controladas.

## 17. Recomendación operativa

La recomendación es preparar primero una demo interna repetible.

Después, una demo semiprivada con 1 o 2 personas de confianza del sector.

Solo después conviene abrir contacto con escuelas o productoras.

## 18. Próximas fases recomendadas

Fases posibles:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.GATING.AUDIT.PHASE7.1
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SCRIPT.REFINEMENT.PHASE7.2
- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.SAFE_SAMPLE.PHASE7.2
- AILINK.PRODUCT.SYNC_DIALOGUE.REPORT.PDF.CONTRACT.PHASE8
- AILINK.PRODUCT.SYNC_DIALOGUE.NLE.EXPORT.CONTRACT.PHASE8

La recomendación inmediata es hacer un gating audit de demo readiness antes de crear más funcionalidades.

## 19. Resumen ejecutivo

AILink Sync Dialogue ya tiene una base suficiente para preparar una demo controlada.

La demo debe vender claridad, orden y preparación para montaje, no automatización total.

La prioridad ahora es demostrar valor real sin prometer más de lo implementado.
