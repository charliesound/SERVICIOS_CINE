# AILink Sync Dialogue — Beta Leads Operations Runbook v1

## 1. Objetivo

Este runbook define cómo gestionar manualmente los interesados en la beta privada de AILink Sync Dialogue antes de implementar formulario real, CRM, Supabase, automatizaciones o base de datos de marketing.

La fase no implementa captación real. No crea formulario funcional. No conecta Supabase. No crea CRM. No envía emails automáticos. No modifica landing, frontend, backend, CID SaaS, Docker, runtime ni configuración.

El objetivo es que, cuando lleguen interesados desde LinkedIn, Facebook, email, llamada o contacto directo, exista un flujo claro, legalmente prudente y comercialmente útil para clasificarlos, responderles y preparar demos controladas.

## 2. Materiales de entrada

Materiales ya disponibles:

- docs/product/ailink_sync_dialogue_beta_form_spec_v1.md
- docs/product/legal/ailink_sync_dialogue_legal_web_texts_spec_v1.md
- docs/product/legal/ailink_sync_dialogue_landing_legal_integration_spec_v1.md
- docs/product/social/ailink_sync_dialogue_social_launch_pack_v1.md
- docs/product/video/ailink_sync_dialogue_demo_video_script_v1.md
- docs/product/video/ailink_sync_dialogue_demo_video_subtitles_readme_v1.md
- docs/product/video/ailink_sync_dialogue_demo_video_assembly_runbook_v1.md
- docs/product/landing/ailink_sync_dialogue_static_landing.html

## 3. Non-goals

Esta fase no debe:

- Implementar formulario.
- Implementar CRM.
- Implementar Supabase.
- Implementar base de datos de leads.
- Implementar automatizaciones.
- Implementar emails automáticos.
- Implementar tracking.
- Implementar cookies.
- Implementar pagos.
- Crear endpoints.
- Crear frontend nuevo.
- Tocar backend CID.
- Tocar runtime.
- Tocar Docker.
- Tocar archivos de configuración.
- Añadir dependencias.
- Publicar nada.

Resumen explícito de prohibiciones operativas:

- No implementar CRM.
- No implementar Supabase.
- No implementar formulario.
- No implementar automatizaciones.
- No implementar emails automáticos.
- No tocar runtime.
- No tocar frontend.
- No tocar backend.

## 4. Principio operativo

Durante la fase manual, los leads deben tratarse como contactos de beta privada, no como usuarios de producto final.

Cada lead debe tener:

- Origen.
- Fecha de entrada.
- Nombre.
- Email o vía de contacto.
- Tipo de organización.
- Rol.
- Interés principal.
- Nivel de encaje.
- Estado operativo.
- Próxima acción.
- Consentimiento o base de contacto disponible.
- Notas no sensibles.

No se debe pedir ni recibir material audiovisual real de terceros durante la captación inicial.

## 5. Orígenes de leads permitidos

Orígenes previstos:

- LinkedIn.
- Facebook.
- Email directo.
- Contacto telefónico iniciado por el interesado.
- Recomendación profesional.
- Escuela de cine contactada directamente.
- Productora contactada directamente.
- Formulario futuro de landing, cuando exista.
- Demo privada.

Cada origen debe registrarse de forma simple y trazable.

## 6. Estados operativos del lead

Estados recomendados:

- nuevo
- pendiente_respuesta
- cualificacion_inicial
- apto_beta
- beta_prioritaria
- beta_media
- beta_baja
- demo_propuesta
- demo_agendada
- demo_realizada
- esperando_feedback
- descartado
- no_contactar

Reglas:

- Un lead nuevo no debe quedarse sin próxima acción.
- Un lead descartado debe conservar motivo.
- Un lead no_contactar no debe recibir mensajes comerciales.
- Un lead demo_realizada debe tener nota de resultado.
- Un lead esperando_feedback debe tener fecha de seguimiento.

## 7. Criterios de cualificación

### 7.1 Encaje alto

Encaje alto:

- Escuela de cine con montaje, postproducción o producción audiovisual.
- Productora con flujo real de vídeo y audio separado.
- Equipo de postproducción con problemas de ingesta, metadata o sincronía.
- Usuario que trabaja con DaVinci Resolve, Avid, Premiere u otro editor profesional.
- Proyecto cercano en preparación o postproducción.
- Disposición a dar feedback concreto.
- Interés en beta de pago económica.

### 7.2 Encaje medio

Encaje medio:

- Profesional audiovisual individual.
- Creador con flujo pequeño pero real.
- Interés claro, pero sin proyecto cercano.
- Equipo que quiere verlo antes de probar.
- Contacto que puede recomendar la herramienta a otra persona.

### 7.3 Encaje bajo

Encaje bajo:

- Interés genérico sin relación con audiovisual.
- Petición de herramienta que no encaja con preparación de material.
- Persona que solo busca IA generativa de imagen o vídeo.
- Lead que exige producto final completo.
- Lead que quiere subir material sensible sin fase legal preparada.
- Lead que no acepta trabajar con caso controlado.

## 8. Datos mínimos a registrar manualmente

Campos mínimos:

- Fecha.
- Origen.
- Nombre.
- Organización.
- Rol.
- Email o canal de contacto.
- País/ciudad.
- Tipo de organización.
- Herramienta de edición usada.
- Problema principal.
- Trabaja con audio separado.
- Trabaja con timecode.
- Proyecto cercano.
- Interés en demo.
- Interés en beta de pago.
- Consentimiento de contacto beta.
- Consentimiento comercial, si existe.
- Estado operativo.
- Nivel de encaje.
- Próxima acción.
- Fecha de próxima acción.
- Notas.

## 9. Datos que no deben registrarse manualmente

No registrar:

- Material audiovisual.
- Enlaces a material sensible.
- Guiones completos.
- Contratos.
- Presupuestos.
- Datos bancarios.
- Documentos de identidad.
- Contraseñas.
- Accesos a discos.
- Datos de terceros no necesarios.
- Comentarios personales no relevantes.
- Información sensible sin necesidad clara.

## 10. Hoja manual temporal

Antes de tener CRM, se puede usar una hoja manual temporal.

Columnas recomendadas:

- lead_id
- created_at
- source
- name
- organization
- role
- email_or_contact
- country_city
- organization_type
- editing_tool
- has_separate_audio
- has_timecode
- main_problem
- upcoming_project
- demo_interest
- paid_beta_interest
- beta_contact_permission
- marketing_permission
- qualification_level
- status
- next_action
- next_action_date
- notes

Reglas:

- No guardar material audiovisual.
- No guardar secretos.
- No guardar datos innecesarios.
- No compartir la hoja públicamente.
- Limitar acceso a quien gestione la beta.
- Mantener una copia ordenada y revisable.
- Preparar migración futura a CRM o Supabase solo cuando se autorice.

## 11. Respuesta inicial recomendada

Objetivo:

- Confirmar recepción.
- Explicar que es beta privada.
- No prometer acceso inmediato.
- No pedir material audiovisual.
- Pedir solo contexto de workflow.

Plantilla base:

Hola, gracias por tu interés en AILink Sync Dialogue.

Ahora mismo estamos preparando una beta privada con casos controlados para escuelas, productoras y equipos de postproducción.

La herramienta está pensada para preparar material antes del montaje: detectar vídeo y audio, revisar metadata, sugerir posibles relaciones y generar salidas revisables.

Todavía no necesitamos que envíes material audiovisual. Lo primero es entender tu flujo de trabajo: qué editor usas, si trabajas con audio separado, si usas timecode y qué problema te gustaría resolver.

Revisaremos los perfiles y contactaremos con los casos que encajen mejor con esta fase de la beta.

## 12. Preguntas de cualificación

Preguntas recomendadas:

1. ¿Trabajas en escuela, productora, postproducción o como profesional independiente?
2. ¿Qué editor usas normalmente?
3. ¿Trabajas con audio separado de cámara?
4. ¿Tenéis timecode sincronizado en vuestros rodajes?
5. ¿Qué parte del proceso de ingesta o preparación de material os consume más tiempo?
6. ¿Tenéis algún proyecto cercano donde una demo controlada tenga sentido?
7. ¿Te interesaría una beta de bajo coste a cambio de feedback concreto?
8. ¿Preferirías ver primero una demo de 10–15 minutos?

## 13. Flujo operativo manual

Flujo recomendado:

1. Registrar lead.
2. Clasificar origen.
3. Enviar respuesta inicial.
4. Esperar datos básicos de cualificación.
5. Asignar nivel de encaje.
6. Definir estado operativo.
7. Proponer demo si encaja.
8. Registrar fecha de demo.
9. Realizar demo con material controlado.
10. Registrar feedback.
11. Decidir siguiente acción.
12. Marcar no_contactar si lo solicita.

## 14. Preparación de demo

Antes de una demo:

- Usar fixture o demo controlada.
- Revisar que no hay datos reales.
- Abrir report.html.
- Tener visibles media_files.csv y match_suggestions.csv.
- Tener claro qué limitaciones se van a explicar.
- No enseñar material privado.
- No prometer waveform sync.
- No prometer transcripción.
- No prometer claqueta visual.
- No prometer integración directa con editores.
- No pedir archivos del interesado.

## 15. Feedback posterior a demo

Preguntas recomendadas:

- ¿Qué parte te resultó más útil?
- ¿Qué salida revisarías primero: reporte, CSV o JSON?
- ¿Qué dato echas de menos?
- ¿Tu flujo usa más timecode, nombre de archivo, parte de sonido o claqueta?
- ¿Qué necesitarías para probarlo en un caso real controlado?
- ¿Pagarías una beta económica si resuelve parte del trabajo?
- ¿Qué integración futura sería prioritaria para ti?

## 16. Criterios para invitar a beta

Invitar primero a:

- Leads con proyecto cercano.
- Leads con flujo real de audio separado.
- Leads con posibilidad de dar feedback técnico.
- Leads que entienden que es beta.
- Leads que aceptan trabajar con material controlado.
- Leads que no exigen producto final cerrado.
- Leads que pueden validar valor comercial.

No invitar todavía a:

- Leads que necesitan garantías de producto final.
- Leads que piden subir material sensible sin marco preparado.
- Leads que necesitan integración NLE inmediata.
- Leads que buscan solo IA generativa visual.
- Leads que no aceptan limitaciones de beta.

## 17. Política no_contactar

Si una persona pide no recibir más mensajes:

- Marcar estado no_contactar.
- No volver a enviar comunicaciones comerciales.
- Conservar solo la información mínima necesaria para respetar esa preferencia.
- No reactivar sin nueva petición expresa de la persona.

## 18. Retención manual provisional

Hasta tener política definitiva:

- Revisar leads manuales periódicamente.
- Eliminar leads descartados que no aporten valor operativo.
- No conservar datos innecesarios.
- No conservar material audiovisual.
- No conservar notas sensibles.
- Preparar política final antes de CRM real.

## 19. Métricas manuales útiles

Métricas simples:

- Leads totales.
- Leads por origen.
- Leads de encaje alto.
- Demos propuestas.
- Demos realizadas.
- Feedback recibido.
- Interés en beta de pago.
- Objeciones frecuentes.
- Features más solicitadas.
- Sectores con más interés.

## 20. Separación AILink Sync Dialogue y CID

AILink Sync Dialogue debe gestionarse como herramienta independiente.

Reglas:

- No vender AILink Sync Dialogue como CID.
- No decir que hace todo lo que hará CID.
- No usar cuenta CID como requisito de beta.
- No mezclar leads beta con usuarios internos del SaaS CID.
- Se puede explicar que CID será el SaaS integral de AILinkCinema en una conversación separada.

## 21. Checklist semanal

Cada semana:

- Revisar leads nuevos.
- Marcar próximos seguimientos.
- Revisar no_contactar.
- Revisar demos pendientes.
- Resumir objeciones.
- Resumir features pedidas.
- Identificar 3 leads prioritarios.
- Decidir si hay que ajustar copy, demo o landing.
- No implementar automatizaciones sin fase específica.

## 22. Señales para pasar a CRM o Supabase real

Pasar a CRM o Supabase cuando:

- Haya volumen suficiente de leads.
- Exista formulario legalmente revisado.
- Exista criterio claro de permisos.
- Exista política de retención.
- Exista responsable de datos definido.
- Exista flujo de borrado/exportación.
- Exista necesidad real de seguimiento automatizado.
- La operación manual empiece a ser insuficiente.

## 23. Criterios de aceptación

Esta fase se considera válida si:

- Define estados operativos de leads.
- Define criterios de cualificación.
- Define datos mínimos a registrar.
- Define datos que no deben registrarse.
- Define hoja manual temporal.
- Incluye respuesta inicial recomendada.
- Incluye preguntas de cualificación.
- Define flujo manual.
- Define preparación de demo.
- Define feedback posterior.
- Define política no_contactar.
- Define métricas manuales.
- Mantiene separación AILink Sync Dialogue y CID.
- No implementa CRM.
- No implementa Supabase.
- No implementa formulario.
- No toca runtime.
- No toca frontend.
- No toca backend.
