# AILink Sync Dialogue — Landing Legal Integration Spec v1

## 1. Objetivo

Este documento define cómo integrar legalmente el bloque de formulario beta, privacidad, cookies, consentimientos y disclaimers dentro de una futura landing real de AILink Sync Dialogue.

No implementa la landing real. No implementa formulario, CRM, Supabase, tracking, cookies ni envío de emails.

El objetivo es dejar un contrato documental claro para que la futura implementación no improvise textos legales, consentimientos ni comportamiento de captación de datos.

## 2. Estado actual de partida

Ya existen documentos y piezas previas:

- docs/product/landing/ailink_sync_dialogue_static_landing.html
- docs/product/landing/ailink_sync_dialogue_static_landing_README.md
- docs/product/ailink_sync_dialogue_beta_form_spec_v1.md
- docs/product/legal/ailink_sync_dialogue_legal_web_texts_spec_v1.md
- docs/product/social/ailink_sync_dialogue_social_launch_pack_v1.md
- docs/product/video/ailink_sync_dialogue_demo_video_script_v1.md
- docs/product/video/ailink_sync_dialogue_demo_video_subtitles_readme_v1.md

La landing estática actual es una pieza exportable y revisable. No envía datos, no contiene JavaScript, no tiene tracking y no incluye formulario real.

## 3. Alcance

Esta fase define:

- Dónde colocar el formulario beta.
- Qué textos legales deben aparecer cerca del formulario.
- Qué checkboxes deben existir.
- Qué consentimientos deben separarse.
- Qué textos deben enlazarse.
- Qué placeholders legales deben completarse.
- Qué comportamiento debe evitarse.
- Qué debe auditarse antes de publicar.
- Qué criterios deben cumplirse antes de activar captación real.

## 4. Non-goals

Esta fase no debe:

- Implementar HTML real nuevo.
- Modificar la landing estática existente.
- Implementar formulario funcional.
- Implementar Supabase.
- Implementar CRM.
- Implementar backend.
- Implementar endpoints.
- Implementar JavaScript.
- Implementar tracking.
- Implementar cookies.
- Implementar email automático.
- Implementar pagos.
- Tocar .env.
- Tocar Docker.
- Tocar CID SaaS.
- Añadir dependencias.
- Publicar nada.

## 5. Principio de integración legal

La landing futura debe separar claramente:

1. Información comercial del producto.
2. Información de beta/prototipo.
3. Información básica de privacidad.
4. Aceptación de política de privacidad.
5. Permiso de contacto beta.
6. Consentimiento opcional para comunicaciones comerciales.
7. Información de cookies.
8. Aviso legal completo.

No deben mezclarse consentimientos distintos en una sola casilla.

## 6. Ubicación recomendada del formulario

El formulario debe aparecer en una sección específica con identificador beta-form.

Ubicación recomendada:

- Después del bloque “Beta privada”.
- Antes del FAQ final.
- Con un CTA desde el hero: “Solicitar acceso beta”.
- Con un CTA final que vuelva al mismo bloque.

Motivo:

- El usuario entiende primero el producto.
- Ve que es beta.
- Ve limitaciones.
- Después decide si quiere dejar sus datos.

## 7. Estructura recomendada del bloque beta

La sección debe contener este orden:

1. Título.
2. Texto corto de contexto.
3. Aviso de beta privada.
4. Aviso de no subir material audiovisual.
5. Formulario.
6. Primera capa RGPD.
7. Checkboxes.
8. Enlaces legales.
9. Mensaje de no garantía de acceso.
10. Mensaje de éxito tras envío.

## 8. Texto introductorio del formulario

Texto recomendado:

Solicita acceso a la beta privada de AILink Sync Dialogue.

La beta está pensada para escuelas, productoras y equipos de postproducción que quieran probar la herramienta con casos controlados.

Completar el formulario no garantiza acceso inmediato. Revisaremos las solicitudes según el perfil, el caso de uso y la fase actual de la beta.

No subas ni envíes material audiovisual. Solo necesitamos información sobre tu flujo de trabajo.

## 9. Campos del formulario

Campos obligatorios:

- Nombre.
- Email.
- Empresa o escuela.
- Rol.
- País/ciudad.
- Software de montaje.
- Trabajo con audio separado.
- Trabajo con timecode.
- Principal problema actual al preparar material.
- Permiso de contacto beta.
- Aceptación de política de privacidad.

Campos opcionales:

- Volumen aproximado de material por proyecto.
- Interés en beta de pago.
- Aceptación de demo de 10–15 minutos.
- Comunicaciones comerciales.
- Comentarios adicionales.

## 10. Primera capa RGPD en la landing

La primera capa RGPD debe estar visible antes del botón de envío o justo encima de los checkboxes.

Texto base:

Responsable: PENDIENTE_RELLENAR.

Finalidad: gestionar tu solicitud de acceso a la beta privada de AILink Sync Dialogue, valorar si tu perfil encaja con la fase actual y contactar contigo en relación con la beta.

Legitimación: consentimiento de la persona interesada.

Destinatarios: no se cederán datos a terceros salvo obligación legal o proveedores necesarios para gestionar formulario, email, CRM o alojamiento.

Derechos: puedes acceder, rectificar y suprimir tus datos, así como ejercer otros derechos reconocidos por la normativa de protección de datos escribiendo a PENDIENTE_RELLENAR.

Información adicional: consulta la política de privacidad completa.

## 11. Checkboxes obligatorios

### 11.1 Permiso de contacto beta

Texto:

Autorizo a AILinkCinema a contactarme sobre mi solicitud de acceso a la beta privada de AILink Sync Dialogue.

Reglas:

- Obligatorio.
- No premarcado.
- Separado de comunicaciones comerciales.
- Guardar versión del texto aceptado.
- Guardar fecha/hora de aceptación cuando se implemente el formulario real.

### 11.2 Aceptación de política de privacidad

Texto:

He leído y acepto la política de privacidad de AILinkCinema.

Reglas:

- Obligatorio.
- No premarcado.
- Debe enlazar a la política de privacidad.
- No sustituye a la primera capa RGPD.

## 12. Checkbox opcional de comunicaciones comerciales

Texto:

Quiero recibir novedades sobre AILink Sync Dialogue, futuras herramientas de AILinkCinema y comunicaciones relacionadas con la beta.

Reglas:

- Opcional.
- No premarcado.
- No bloquea el envío si no se acepta.
- Debe poder retirarse.
- Debe registrarse separado del contacto beta.

## 13. Enlaces legales mínimos

La landing real debe incluir enlaces visibles a:

- Aviso legal.
- Política de privacidad.
- Política de cookies o información de no tracking.
- Contacto legal o privacidad.

Ubicaciones recomendadas:

- Footer.
- Primera capa del formulario.
- Bloque de cookies si existe.
- Mensaje de confirmación o email de confirmación.

## 14. Cookies y tracking

### 14.1 Escenario sin tracking

Si no hay analítica, píxeles, embeds externos ni cookies no técnicas:

Esta página no utiliza cookies analíticas, publicitarias ni de seguimiento. Si en el futuro incorporamos analítica o servicios de terceros, actualizaremos esta información y solicitaremos consentimiento cuando corresponda.

Requisito:

- Verificar técnicamente que no se instalan cookies no técnicas.

### 14.2 Escenario con analítica futura

Si se añade analítica:

- Debe existir banner o mecanismo de consentimiento.
- Debe existir opción de aceptar.
- Debe existir opción de rechazar.
- Debe existir opción de configurar.
- Aceptar y rechazar deben tener visibilidad equivalente.
- La analítica no debe cargarse antes del consentimiento si requiere consentimiento.

## 15. Mensaje de éxito del formulario

Texto recomendado:

Gracias por solicitar acceso a la beta privada de AILink Sync Dialogue.

Hemos recibido tu solicitud. Revisaremos los perfiles periódicamente y te contactaremos si tu caso encaja con la fase actual.

Completar el formulario no garantiza acceso inmediato.

No envíes material audiovisual todavía. Si avanzamos, te indicaremos los pasos siguientes.

## 16. Mensaje de error del formulario

Errores mínimos:

- Email inválido.
- Campo obligatorio vacío.
- Checkboxes obligatorios no aceptados.
- Error temporal de envío.
- Error de consentimiento.

Los mensajes deben ser claros y no técnicos.

## 17. Datos que deben registrarse en implementación futura

Cuando exista formulario real, se recomienda registrar:

- Nombre.
- Email.
- Empresa o escuela.
- Rol.
- País/ciudad.
- Software de montaje.
- Audio separado.
- Timecode.
- Problema principal.
- Interés en beta de pago.
- Aceptación de demo.
- Permiso de contacto beta.
- Aceptación de privacidad.
- Consentimiento comercial opcional.
- Fecha/hora de envío.
- Versión de textos legales.
- Origen de la landing.
- UTM si se decide usar campañas.
- IP solo si asesoría legal confirma necesidad y base adecuada.
- User agent solo si asesoría legal confirma necesidad y base adecuada.

## 18. Datos que no deben pedirse

No pedir:

- Subida de vídeo.
- Subida de audio.
- Enlaces a material audiovisual sensible.
- Guiones completos.
- Contratos de producción.
- Presupuestos.
- DNI/NIF del solicitante.
- Teléfono obligatorio.
- Dirección postal.
- Datos bancarios.
- Tarjeta.
- Contraseña.
- Acceso a editores de montaje.
- Acceso a discos del usuario.

## 19. Integración futura con Supabase o CRM

Antes de guardar datos en Supabase, CRM u otra base:

- Definir responsable del tratamiento.
- Definir proveedor.
- Revisar contrato de encargado de tratamiento.
- Definir región de almacenamiento.
- Revisar transferencias internacionales.
- Definir política de retención.
- Definir exportación/borrado de datos.
- Definir acceso interno mínimo.
- Registrar versión de consentimientos.
- Evitar mezclar leads de marketing con base de datos core de CID.

## 20. Relación con CID

AILink Sync Dialogue es una herramienta independiente de AILinkCinema.

La landing debe evitar confusión:

- No decir que AILink Sync Dialogue es CID.
- No usar “CID” como nombre de la herramienta independiente.
- No usar “Intelligence” en el nombre de la herramienta independiente.
- Sí puede mencionar que CID será el SaaS integral de AILinkCinema en una sección separada si procede.
- No debe requerirse cuenta CID para solicitar la beta de AILink Sync Dialogue.

## 21. Relación con el vídeo demo

Si la landing incorpora vídeo demo:

- El vídeo debe mantener el mensaje de beta privada.
- No debe pedir material audiovisual.
- No debe prometer waveform sync.
- No debe prometer transcripción.
- No debe prometer detección de claqueta visual.
- No debe prometer integración directa con editores.
- Debe usar assets auditados o material autorizado.
- Debe evitar datos reales.

## 22. Checklist antes de activar formulario real

Antes de activar el formulario:

- Completar todos los PENDIENTE_RELLENAR.
- Revisar aviso legal.
- Revisar política de privacidad.
- Revisar cookies reales.
- Validar textos con asesoría legal.
- Confirmar que no hay casillas premarcadas.
- Confirmar que no se pide material audiovisual.
- Confirmar que el consentimiento comercial es opcional.
- Confirmar que aceptar privacidad y contacto beta son casillas separadas.
- Confirmar que el envío no funciona si faltan consentimientos obligatorios.
- Confirmar que se registra versión de textos aceptados.
- Confirmar que el mensaje de éxito no pide archivos.
- Confirmar que los datos no se mezclan con la base core de CID.
- Confirmar que existe procedimiento de borrado/exportación de leads.
- Confirmar que no hay tracking sin consentimiento cuando sea necesario.

## 23. Tests recomendados para implementación futura

Cuando se implemente la landing real, añadir tests que verifiquen:

- Existe id beta-form.
- Existen enlaces a aviso legal, privacidad y cookies.
- Los checkboxes obligatorios no están premarcados.
- El checkbox comercial es opcional.
- El envío falla sin privacidad.
- El envío falla sin contacto beta.
- El envío puede continuar sin consentimiento comercial.
- El texto “No subas ni envíes material audiovisual” es visible.
- No hay llamadas a tracking antes de consentimiento.
- No hay URLs de CRM hardcodeadas en cliente si no procede.
- No hay secretos en frontend.
- No hay rutas locales del sistema.

## 24. Criterios de aceptación

La fase se considera válida si:

- Define estructura legal del formulario en landing.
- Separa consentimientos.
- Incluye primera capa RGPD.
- Incluye cookies sin tracking y cookies futuras con analítica.
- Incluye mensaje de éxito.
- Incluye datos a registrar en futura implementación.
- Incluye datos que no deben pedirse.
- Incluye relación con Supabase/CRM sin implementar nada.
- Incluye relación con CID sin confundir marca.
- Incluye checklist antes de activar formulario real.
- No toca runtime.
- No modifica landing existente.
