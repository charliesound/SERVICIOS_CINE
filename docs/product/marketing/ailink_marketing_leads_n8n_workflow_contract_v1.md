# AILink Marketing Leads — n8n Workflow Contract v1

## 1. Objetivo

Este documento define el contrato lógico del futuro workflow n8n para captar leads de marketing de AILink Sync Dialogue.

La finalidad es fijar cómo debe comportarse n8n cuando reciba un lead desde una landing o formulario beta: validar campos, normalizar datos, detectar duplicados, registrar consentimiento, crear eventos operativos y notificar internamente.

Esta fase es documental y de contrato. No crea workflows reales de n8n, no crea JSON importable en n8n, no llama webhooks reales, no crea credenciales, no toca PostgreSQL real, no crea tablas, no crea migraciones, no implementa backend, no implementa frontend, no implementa CRM, no toca Docker, no toca runtime y no modifica CID SaaS.

## 2. Relación con fases anteriores

Este contrato depende de:

- AILINK.MARKETING.LEADS.N8N.POSTGRES.CRM.SPEC.PHASE1
- AILINK.MARKETING.LEADS.DB.SCHEMA.CONTRACT.PHASE2

La Phase1 definió la arquitectura conceptual: Landing/Formulario, n8n, PostgreSQL y CRM privado.

La Phase2 definió el contrato lógico de datos: marketing_leads, marketing_lead_consents, marketing_lead_events y marketing_lead_notes.

Esta Phase3 define la operación lógica de n8n sin implementar el workflow real.

## 3. Principio general

n8n debe actuar como orquestador de entrada, no como CRM y no como fuente de verdad.

La fuente de verdad será PostgreSQL.

El CRM privado será la interfaz de gestión manual.

n8n solo debe recibir, validar, normalizar, enrutar, registrar y notificar.

## 4. Flujo lógico esperado

Flujo conceptual:

1. Recibir lead desde landing o formulario beta.
2. Validar campos mínimos.
3. Normalizar email.
4. Clasificar fuente del lead.
5. Preparar payload interno.
6. Consultar si el email ya existe.
7. Insertar o actualizar lead lógico.
8. Registrar consentimiento.
9. Registrar evento operativo.
10. Notificar internamente.
11. Devolver respuesta segura al formulario.
12. Registrar errores sin exponer información sensible.

## 5. Entrada esperada

El formulario o landing deberá enviar un payload lógico con estos campos mínimos:

- full_name
- email
- source
- beta_contact_consent
- privacy_policy_acceptance

Campos opcionales recomendados:

- phone
- organization_name
- organization_type
- role
- country
- city
- language
- interest_area
- current_tools
- main_problem
- upcoming_project
- project_timing
- demo_interest
- beta_interest
- message

## 6. Validación de campos mínimos

n8n deberá rechazar o marcar como inválido cualquier lead sin:

- Nombre.
- Email.
- Fuente.
- Aceptación de política de privacidad.
- Consentimiento necesario para contacto beta.

La validación no debe pedir datos innecesarios.

El workflow futuro debe responder con un mensaje genérico y seguro. No debe exponer nombres de tablas, credenciales, errores SQL, rutas internas ni detalles del servidor.

## 7. Normalización de email

n8n debe normalizar el email antes de consultar PostgreSQL.

Reglas:

- Eliminar espacios al principio y al final.
- Convertir a minúsculas.
- Validar formato básico.
- Rechazar emails vacíos.
- No asumir que dos emails visualmente parecidos pertenecen a la misma persona salvo coincidencia exacta normalizada.

La normalización debe coincidir con el contrato de PostgreSQL definido en Phase2.

## 8. Fuente del lead

Valores válidos de source:

- landing_beta_form
- manual_linkedin
- manual_email
- manual_event
- manual_referral
- manual_existing_contact
- other

Para el flujo automático inicial, la fuente principal prevista será landing_beta_form.

Los contactos manuales pueden registrarse más adelante desde CRM privado o flujo interno controlado.

## 9. Consentimiento

El workflow debe separar claramente:

- Consentimiento para responder a una solicitud beta.
- Aceptación de política de privacidad.
- Consentimiento para comunicaciones comerciales futuras.

El consentimiento comercial no debe estar preaceptado.

Si no hay consentimiento beta o aceptación de privacidad, el lead no debe entrar como lead contactable.

Debe registrarse un evento de consentimiento asociado al lead.

## 10. Duplicados

Si el email normalizado no existe:

- Crear lead lógico.
- Registrar consentimiento.
- Registrar evento lead_created.
- Notificar nuevo lead.

Si el email normalizado ya existe:

- No crear un segundo lead activo por defecto.
- Actualizar datos permitidos si procede.
- Registrar evento lead_updated.
- Registrar nuevo consentimiento si hay nueva aceptación o cambio de versión.
- Notificar actualización de lead existente solo si aporta información nueva relevante.

## 11. Estados iniciales

El estado inicial recomendado es new.

El workflow puede proponer priority unknown o medium según la información recibida, pero la cualificación final debe ser manual desde CRM privado.

No debe marcar automáticamente beta_active, converted ni demo_done.

## 12. Priorización inicial

n8n puede asignar una prioridad preliminar.

Reglas recomendadas:

- high: proyecto próximo, problema claro, demo solicitada y perfil profesional útil.
- medium: interés real pero sin urgencia.
- low: curiosidad genérica.
- unknown: datos insuficientes.

La prioridad automática no sustituye la revisión humana.

## 13. Eventos operativos mínimos

Cada entrada válida debe generar al menos:

- lead_created o lead_updated.
- consent_recorded.
- source_recorded.

Eventos adicionales posibles:

- demo_requested.
- follow_up_scheduled.
- priority_suggested.
- validation_failed.
- duplicate_detected.
- notification_sent.
- notification_failed.

## 14. Notificación interna

El workflow futuro puede notificar internamente cuando llegue un lead válido.

Canales posibles futuros:

- Email interno.
- Mensaje interno en n8n.
- Registro para CRM privado.
- Notificación manual revisable.

La notificación no debe incluir datos sensibles innecesarios.

La notificación debe incluir:

- Nombre.
- Email.
- Organización si existe.
- Tipo de organización si existe.
- Área de interés.
- Problema principal resumido.
- Proyecto próximo si existe.
- Prioridad sugerida.
- Enlace futuro al lead en CRM privado cuando exista.

## 15. Manejo de errores

El workflow debe distinguir:

- Error de validación.
- Error de duplicado controlado.
- Error de PostgreSQL.
- Error de notificación.
- Error inesperado.

Las respuestas al usuario deben ser genéricas.

Los errores internos deben registrarse como eventos o logs internos, sin exponer credenciales, rutas, tokens ni detalles técnicos al formulario público.

## 16. Seguridad y privacidad

El workflow no debe:

- Guardar material audiovisual.
- Pedir subida de archivos.
- Guardar guiones.
- Guardar contratos.
- Guardar documentos de identidad.
- Guardar datos bancarios.
- Guardar datos de facturación.
- Mezclar leads con usuarios CID.
- Escribir en tablas de CID SaaS.
- Usar credenciales hardcodeadas.
- Enviar datos a servicios externos no aprobados.

## 17. Relación con PostgreSQL

PostgreSQL será la fuente de verdad.

n8n solo debe ejecutar operaciones lógicas equivalentes a:

- Buscar lead por email normalizado.
- Insertar lead si no existe.
- Actualizar lead si existe.
- Insertar consentimiento.
- Insertar evento.
- Registrar errores operativos cuando proceda.

La implementación real de queries queda fuera de esta fase.

## 18. Relación con CRM privado

El CRM privado será el lugar donde se revisan leads.

n8n no debe convertirse en panel comercial.

n8n no debe ser el lugar principal para cambiar estados manuales, añadir notas o gestionar seguimiento diario.

El CRM privado futuro deberá leer la información que n8n deje en PostgreSQL.

## 19. Respuesta al formulario

La respuesta pública al usuario debe ser simple:

- Confirmación si el lead se ha recibido correctamente.
- Mensaje genérico si hay error.
- Sin detalles técnicos.
- Sin promesas comerciales cerradas.
- Sin indicar que el usuario ya existía en la base de datos.

Ejemplo conceptual de respuesta positiva:

Gracias. Hemos recibido tu solicitud de acceso beta. Revisaremos tu perfil y te contactaremos si encaja con la fase actual de pruebas.

## 20. Observabilidad mínima futura

El workflow futuro debería permitir saber:

- Cuántos leads entraron.
- Cuántos fueron válidos.
- Cuántos fallaron por validación.
- Cuántos eran duplicados.
- Cuántos generaron notificación.
- Cuántos fallaron por error interno.

Estos contadores no se implementan en esta fase.

## 21. Criterios de aceptación de una futura implementación

Una implementación futura del workflow deberá cumplir:

- No usar n8n como CRM.
- No usar n8n como fuente de verdad.
- Validar campos mínimos.
- Normalizar email.
- Detectar duplicados por email normalizado.
- Registrar consentimiento separado.
- Registrar evento inicial.
- No crear leads contactables sin consentimiento.
- No escribir en tablas de CID SaaS.
- No guardar datos sensibles innecesarios.
- No exponer errores internos al usuario.
- No incluir credenciales en el repo.
- Permitir operación manual antes de automatizar ventas.

## 22. Límites de esta fase

Esta fase no incluye:

- Workflow real de n8n.
- Export JSON de n8n.
- Webhook real.
- Credenciales.
- Variables de entorno.
- Conexión PostgreSQL real.
- Tablas reales.
- Migraciones.
- CRM privado real.
- Landing real.
- Formulario real.
- Backend.
- Frontend.
- Docker.
- Runtime.
- CID SaaS.

## 23. Próximas fases recomendadas

Después de este contrato, las siguientes fases posibles son:

- AILINK.MARKETING.LEADS.CRM.PRIVATE.UI.SPEC.PHASE4
- AILINK.MARKETING.LEADS.N8N.WORKFLOW.DRY.RUN.SPEC.PHASE4
- AILINK.MARKETING.LEADS.DB.MIGRATION.CONTRACT.PHASE4

La recomendación es especificar el CRM privado antes de implementar workflow real, para evitar automatizar un flujo que luego no se pueda operar bien.

## 24. Resumen ejecutivo

Este contrato define cómo debe comportarse n8n dentro del sistema de captación pasiva de leads de AILink Sync Dialogue.

n8n recibirá leads, validará campos, normalizará email, detectará duplicados, registrará consentimiento, registrará eventos y notificará internamente.

La operación comercial seguirá siendo manual y prudente hasta tener señales reales de interés, demos y feedback.
