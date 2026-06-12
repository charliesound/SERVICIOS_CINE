# AILink Sync Dialogue — MVP v1

## 1. Título

**AILink Sync Dialogue — MVP v1**

Nombre descriptivo alternativo: **Asistente de Ingesta y Diálogo para Montaje**.

Esta especificación define el primer MVP de una herramienta independiente de AILinkCinema para ingesta, metadata, sincronía sugerida y preparación básica de diálogo para montaje.

## 2. Resumen ejecutivo

AILink Sync Dialogue convierte una carpeta de rodaje en un informe claro y utilizable para montaje. El usuario selecciona una carpeta raíz del proyecto, una jornada de rodaje o una tarjeta copiada a disco. La herramienta analiza los archivos de vídeo y audio, extrae metadata técnica y genera reportes prácticos para el equipo editorial.

En el MVP, la herramienta detecta información como timecode, duración, fps, canales, nombre de archivo, extensión y tamaño. También identifica posibles parejas vídeo/audio usando timecode cuando existe y, como apoyo secundario, señales como nombre, roll, fecha o duración aproximada.

El producto puede extraer o preparar audio para una transcripción básica de diálogo, pensada para localizar contenido hablado al inicio del proceso editorial. Los resultados se exportan como PDF, CSV y JSON para revisión humana, archivo de producción e integraciones futuras.

## 3. Problema que resuelve

En muchos rodajes, especialmente en escuelas, productoras pequeñas y equipos independientes, el material llega a montaje sin un informe técnico claro. Las carpetas contienen vídeos, audios separados, backups parciales y nombres heterogéneos que obligan al montador o al ayudante de montaje a revisar manualmente cada clip.

Problemas principales:

- Material de rodaje desordenado o copiado sin estructura editorial.
- Audio separado difícil de relacionar con cámara.
- Timecode no revisado antes de abrir el proyecto de edición.
- Clips sin informe claro de duración, fps, canales o tamaño.
- Montadores y ayudantes pierden horas revisando metadata básica.
- Escuelas y productoras pequeñas no siempre tienen DIT o post supervisor dedicado.
- El diálogo no está localizado ni transcrito al inicio, lo que dificulta buscar tomas o frases.

AILink Sync Dialogue no sustituye al criterio del equipo de postproducción. Reduce el trabajo mecánico inicial y entrega una base clara para decidir qué se importa, qué se sincroniza y qué requiere revisión.

## 4. Usuario objetivo

Usuarios principales:

- Montadores.
- Ayudantes de montaje.
- Productoras pequeñas.
- Escuelas de cine.
- Ayudantes de dirección.
- DIT básico o responsable de ingesta.
- Directores y productores independientes.

El usuario ideal necesita ordenar y entender material de rodaje sin montar un pipeline profesional completo ni contratar supervisión técnica avanzada para cada proyecto.

## 5. Casos de uso principales

- Escanear una carpeta de rodaje.
- Ver una tabla de clips de vídeo con metadata clave.
- Ver una tabla de audios con canales, duración y formato.
- Detectar timecode disponible en vídeo y audio.
- Detectar parejas vídeo/audio por timecode.
- Detectar posibles parejas por nombre, roll, fecha o duración.
- Generar un reporte PDF para entregar al equipo editorial.
- Exportar CSV para montaje, revisión o hojas compartidas.
- Exportar JSON para integración futura con CID.
- Preparar audio para transcripción.
- Generar transcripción básica de diálogo cuando se active esta opción.

## 6. Flujo MVP del usuario

1. Abrir herramienta.
2. Seleccionar carpeta raíz del proyecto o día de rodaje.
3. Elegir opciones de análisis: vídeo, audio, matches sugeridos y transcripción opcional.
4. Ejecutar escaneo.
5. Ver resumen general: número de vídeos, audios, duración aproximada, formatos y alertas.
6. Revisar clips de vídeo en tabla.
7. Revisar audios en tabla.
8. Ver coincidencias sugeridas entre vídeo y audio.
9. Exportar PDF, CSV y JSON.
10. Guardar informe del día de rodaje.

## 7. Inputs soportados en MVP

Vídeo:

- `.mov`
- `.mp4`
- `.mxf` si `ffprobe` lo lee correctamente

Audio:

- `.wav`
- `.bwf`
- `.mp3` solo como formato secundario/no profesional si aparece

Otros inputs:

- Carpetas locales.
- Nombres de archivo.
- Metadata leíble por `ffprobe`.

El MVP no promete compatibilidad total con todos los formatos propietarios, cámaras, grabadores o estructuras privadas de fabricante. La compatibilidad real dependerá de lo que `ffprobe` pueda leer de forma fiable.

## 8. Outputs del MVP

- PDF de informe de ingesta.
- CSV de clips de vídeo.
- CSV de audios.
- CSV de coincidencias sugeridas.
- JSON completo del análisis.
- TXT o PDF de transcripción básica si se activa.

Los outputs deben estar pensados para humanos primero: revisión rápida, comunicación entre equipos y archivo simple del día de rodaje.

## 9. Funciones incluidas en MVP

MVP obligatorio:

- Escaneo de carpeta.
- Extracción de metadata con `ffprobe`/`ffmpeg`.
- Tabla de vídeos.
- Tabla de audios.
- Detección de duración, fps y timecode si existe.
- Agrupación básica por carpeta, nombre y fecha.
- Sugerencia de sincronía por timecode.
- Sugerencia secundaria por duración y nombre.
- Reporte PDF.
- Export CSV.
- Export JSON.
- Transcripción básica opcional.

MVP no incluye todavía:

- Edición automática.
- Export XML/AAF/EDL profesional.
- Integración directa con DaVinci Resolve, Avid Media Composer o Adobe Premiere Pro.
- Sincronización por waveform avanzada.
- Detección visual de claqueta.
- Multiusuario.
- Cloud SaaS.
- Pagos integrados.
- App installer final.
- GPU.
- ComfyUI.

## 10. Sincronía: niveles

**Nivel 1 — Timecode**

Si vídeo y audio tienen timecode compatible, la herramienta sugiere un match. Este es el nivel principal del MVP porque es rápido, explicable y útil para rodajes con configuración mínima correcta.

**Nivel 2 — Metadata/nombre**

Si no hay timecode, la herramienta usa señales secundarias: nombre de archivo, roll, fecha, carpeta, duración aproximada y cercanía temporal. Estos matches deben presentarse como sugerencias, no como sincronías garantizadas.

**Nivel 3 — Waveform**

No forma parte del MVP. Puede entrar en versión 2 si el MVP valida demanda real y hay margen técnico para análisis de forma de onda.

**Nivel 4 — Claqueta visual**

No forma parte del MVP. Queda como fase futura para detectar imagen de claqueta o golpe visual/sonoro con más coste técnico.

## 11. Transcripción

La transcripción del MVP tiene un alcance realista y operativo:

- Usar WAV existente cuando esté disponible.
- Extraer audio de vídeo cuando sea necesario y viable.
- Generar transcripción básica para localizar diálogo.
- Exportar texto vinculado al archivo original.
- Ayudar a buscar frases, escenas o intervenciones en revisión inicial.

No se debe prometer precisión legal, subtitulado final ni transcripción lista para emisión. En MVP, la transcripción puede ser local si hay modelo disponible o quedar preparada para integración posterior.

## 12. Pantallas o interfaz esperada

Interfaz simple esperada:

- Pantalla de inicio y selección de carpeta.
- Pantalla de opciones de análisis.
- Pantalla de progreso del escaneo.
- Dashboard resumen.
- Tabla de vídeo.
- Tabla de audio.
- Tabla de matches sugeridos.
- Pantalla o panel de exportación de informes.
- Pantalla de transcripción.

La interfaz debe priorizar claridad y confianza. El usuario debe entender qué archivos fueron analizados, qué matches son seguros, qué matches son dudosos y qué información falta.

## 13. Arquitectura técnica recomendada para MVP

**Opción A — CLI primero**

- Más rápido de construir.
- Adecuado para validar extracción de metadata y exports.
- Menos vendible visualmente para demos comerciales.

**Opción B — Web local**

- Backend local con FastAPI + interfaz simple en navegador.
- Más demostrable para beta privada.
- Permite tablas, progreso y exportaciones sin subir material a servidores.

**Opción C — Desktop**

- Tauri, Electron o PySide.
- Mejor percepción como producto instalable.
- Más complejo para instaladores, permisos, firma y soporte Mac/Windows.

Recomendación:

- Empezar con web local o CLI + HTML report.
- Evitar cloud al principio porque el material está en discos del cliente.
- Priorizar una demo fiable antes que una app empaquetada.

## 14. Privacidad y material del cliente

El material audiovisual no debe subirse a servidores en el MVP. La herramienta trabaja localmente sobre la carpeta del cliente y genera metadata, informes y exports derivados.

Esta decisión reduce:

- Riesgos legales.
- Costes de almacenamiento.
- Problemas de confidencialidad.
- Fricción con productoras, escuelas y proyectos sensibles.

El mensaje comercial debe ser claro: el material se queda en el disco del cliente.

## 15. Propuesta de valor comercial

Frases clave:

- “Convierte una carpeta de rodaje en un informe claro para montaje.”
- “Detecta metadata, audio separado y posibles sincronías antes de abrir el proyecto de edición.”
- “Ahorra horas de revisión manual al montador o ayudante de montaje.”
- “Pensado para escuelas de cine, productoras pequeñas y equipos independientes.”

Valor principal:

- Menos tiempo perdido al inicio del montaje.
- Mejor comunicación entre rodaje y postproducción.
- Más control para equipos sin DIT completo.
- Un entregable claro para tomar decisiones editoriales.

## 16. Demo de presentación

Demo de 2 minutos:

- `0:00-0:15` — Problema: carpeta de rodaje desordenada con vídeo y audio separado.
- `0:15-0:30` — Seleccionar carpeta raíz del día.
- `0:30-0:55` — Ejecutar escaneo y mostrar progreso.
- `0:55-1:20` — Mostrar tabla de clips y audios con metadata clave.
- `1:20-1:40` — Mostrar matches sugeridos por timecode o metadata.
- `1:40-1:55` — Exportar PDF, CSV y JSON.
- `1:55-2:00` — Llamada a beta privada.

Objetivo de la demo: que el usuario entienda el valor sin explicar arquitectura ni prometer automatización editorial completa.

## 17. Beta privada

La beta privada debe orientarse a:

- Escuelas de cine.
- Productoras pequeñas.
- Montadores.
- Ayudantes de montaje.
- Equipos independientes.

La beta no debe venderse como producto final cerrado. Debe presentarse como acceso anticipado a una herramienta concreta que ya resuelve ingesta, metadata, reportes y sugerencias iniciales de sincronía.

Objetivos de beta:

- Validar utilidad real con material diverso.
- Recoger feedback de flujo editorial.
- Detectar formatos problemáticos.
- Financiar costes iniciales.
- Identificar qué exportaciones importan más al usuario.

## 18. Precio inicial orientativo

No fijar precio definitivo en esta fase. Rango razonable para beta:

- Beta mensual baja: 9-19 EUR/mes por usuario.
- Precio por proyecto: 15-49 EUR por proyecto analizado.
- Escuela o productora pequeña: 49-149 EUR/mes según número de puestos o proyectos.

La decisión debe depender del feedback de beta: frecuencia de uso, tamaño de proyectos, valor percibido y coste de soporte.

## 19. Relación futura con CID

AILink Sync Dialogue resuelve una tarea concreta: convertir material de rodaje en metadata, reportes y sugerencias útiles para montaje. Debe funcionar de forma independiente y no depender de CID.

CID será el sistema integral. En el futuro, los JSON y exports generados por AILink Sync Dialogue podrán alimentar flujos más amplios dentro de CID, pero la herramienta no debe llamarse CID ni presentarse como módulo interno del backend actual.

La relación correcta es:

- Producto independiente primero.
- Exportaciones claras y portables.
- Integración futura opcional.
- Sin dependencia operativa de CID para funcionar.

## 20. Roadmap posterior

**Fase 1 — Especificación MVP**

- Definir alcance, usuarios, outputs y demo.

**Fase 2 — Prototipo local**

- Escaneo de carpeta.
- Metadata con `ffprobe`.
- Export CSV/JSON.

**Fase 3 — Reporte PDF**

- Informe claro de ingesta, audios y matches sugeridos.

**Fase 4 — Interfaz web local**

- Selección de carpeta, progreso, tablas y exportación.

**Fase 5 — Transcripción básica**

- Preparación de audio y texto vinculado al archivo original.

**Fase 6 — Demo comercial + landing + beta**

- Demo de 2 minutos.
- Página de beta privada.
- Primeros usuarios externos.

**Fase futura**

- Waveform sync.
- Claqueta visual.
- Export XML/EDL.
- Integración CID.

## 21. Criterios de aceptación del MVP

Checklist:

- [ ] Escanea una carpeta real.
- [ ] Detecta vídeos.
- [ ] Detecta audios.
- [ ] Extrae metadata clave.
- [ ] Detecta timecode si existe.
- [ ] Sugiere matches por timecode.
- [ ] Sugiere matches secundarios por nombre/duración cuando no hay timecode.
- [ ] Genera CSV.
- [ ] Genera JSON.
- [ ] Genera PDF.
- [ ] No sube material a cloud.
- [ ] Puede mostrarse en una demo de 2 minutos.

## 22. Riesgos

- Diferentes cámaras escriben metadata de forma distinta.
- Timecode puede faltar, estar mal configurado o no ser comparable.
- Audio puede no tener BWF correcto.
- `ffprobe` puede no leer toda la metadata propietaria.
- Material real puede ser muy pesado y ralentizar escaneos.
- Transcripción puede ser lenta o costosa si no se acota bien.
- Instaladores Mac/Windows son fase posterior y pueden requerir soporte específico.
- Matches secundarios pueden generar falsos positivos si se presentan con demasiada confianza.

## 23. Non-goals

- No implementar SaaS.
- No implementar login.
- No implementar pagos.
- No implementar instalador.
- No subir material audiovisual.
- No modificar CID backend.
- No añadir endpoints.
- No tocar Docker.
- No tocar frontend SaaS.
- No prometer compatibilidad total con todos los flujos profesionales.
- No venderlo como sistema integral de postproducción.
- No automatizar decisiones editoriales sin revisión humana.
