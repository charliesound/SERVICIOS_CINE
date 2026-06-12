# AILink Marketing Leads — PostgreSQL Schema Contract v1

## 1. Objetivo

Este documento define el contrato lógico del futuro esquema PostgreSQL para gestionar leads de marketing de AILink Sync Dialogue.

La finalidad es fijar qué datos se guardarán, cómo se separarán de CID SaaS, qué estados tendrá un lead, cómo se registrará el consentimiento y qué eventos mínimos se necesitarán para operar una beta privada de forma ordenada.

Esta fase es documental y de contrato. No crea tablas físicas, no crea migraciones reales, no implementa backend, no implementa frontend, no implementa CRM, no implementa formularios, no implementa workflows de n8n y no modifica runtime.

## 2. Alcance

Incluido:

- Modelo lógico de datos para leads.
- Tablas futuras recomendadas.
- Campos obligatorios y opcionales.
- Estados operativos del lead.
- Registro de consentimiento.
- Registro de eventos de contacto.
- Separación entre marketing leads y CID SaaS.
- Reglas de privacidad y minimización de datos.
- Criterios de aceptación para una futura implementación.

Excluido:

- Creación real de tablas.
- Migraciones reales.
- Código de backend.
- Código de frontend.
- Panel CRM real.
- Workflows reales de n8n.
- Conexión con formularios reales.
- Pagos.
- Automatizaciones de email.
- Integración con CID SaaS.

## 3. Separación con CID

Los leads de marketing pertenecen a una capa separada de AILinkCinema.

No deben mezclarse con:

- Usuarios reales de CID SaaS.
- Organizaciones de CID.
- Billing de CID.
- Créditos IA de CID.
- Jobs IA de CID.
- Datos internos de proyectos audiovisuales.
- Material audiovisual del cliente.
- Guiones, documentos de producción o assets de rodaje.

Convertir un lead en cliente de CID será una operación futura, explícita y trazable.

## 4. Arquitectura conceptual futura

Landing o formulario beta recibe el interés.

n8n recibe, valida y normaliza el lead.

PostgreSQL guarda el lead, el consentimiento y el evento inicial.

El CRM privado permite revisar, cualificar y dar seguimiento.

n8n actúa como orquestador de entrada. PostgreSQL actúa como fuente de verdad. El CRM privado actúa como interfaz operativa.

## 5. Tablas lógicas futuras

Tablas recomendadas:

- marketing_leads
- marketing_lead_consents
- marketing_lead_events
- marketing_lead_notes

Estas tablas deben vivir fuera del dominio operativo de CID SaaS.

## 6. Tabla marketing_leads

Tabla principal de interesados.

Campos recomendados:

- id
- created_at
- updated_at
- source
- status
- priority
- full_name
- email
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
- notes_summary
- last_contact_at
- next_follow_up_at
- owner
- do_not_contact
- consent_reference

Campos obligatorios mínimos:

- id
- created_at
- updated_at
- source
- status
- full_name
- email
- consent_reference

## 7. Origen del lead

Valores recomendados para source:

- landing_beta_form
- manual_linkedin
- manual_email
- manual_event
- manual_referral
- manual_existing_contact
- other

No se recomienda scraping automático como fuente inicial. Conviene priorizar consentimiento, contexto y contacto cualitativo.

## 8. Tipo de organización

Valores recomendados para organization_type:

- film_school
- production_company
- postproduction_company
- editor
- sound_professional
- director
- producer
- freelancer
- distributor
- other

## 9. Área de interés

Valores recomendados para interest_area:

- sync_dialogue
- call_sheet
- script_pitch
- cid_full_platform
- ai_workflow_consulting
- unknown

## 10. Estados del lead

Estados recomendados:

- new
- qualified
- contacted
- demo_scheduled
- demo_done
- beta_candidate
- beta_active
- not_now
- not_fit
- do_not_contact
- converted
- archived

## 11. Prioridad del lead

Valores recomendados para priority:

- high
- medium
- low
- unknown

Prioridad alta:

- Tiene proyecto próximo.
- Pertenece a escuela, productora o equipo con necesidad real.
- Tiene problema claro de sincronía, ingesta, montaje o workflow.
- Acepta demo.
- Puede dar feedback profesional.

## 12. Tabla marketing_lead_consents

Registra el consentimiento asociado al lead.

Campos recomendados:

- id
- lead_id
- created_at
- consent_type
- consent_text_version
- accepted
- accepted_at
- source
- ip_hash
- user_agent_summary
- legal_basis
- withdrawn_at
- withdrawal_reason

Tipos de consentimiento recomendados:

- beta_contact
- commercial_updates
- privacy_policy_acceptance
- manual_contact_permission

El consentimiento comercial debe estar separado del consentimiento necesario para responder a una solicitud beta.

## 13. Tabla marketing_lead_events

Guarda el historial operativo del lead.

Campos recomendados:

- id
- lead_id
- created_at
- event_type
- event_source
- actor
- summary
- metadata_json

Tipos de evento recomendados:

- lead_created
- lead_updated
- consent_recorded
- status_changed
- priority_changed
- manual_email_sent
- manual_call_done
- manual_linkedin_message_sent
- demo_requested
- demo_scheduled
- demo_completed
- feedback_received
- follow_up_scheduled
- do_not_contact_set
- converted_to_customer
- archived

## 14. Tabla marketing_lead_notes

Guarda notas manuales del CRM privado.

Campos recomendados:

- id
- lead_id
- created_at
- updated_at
- author
- note_type
- body
- visibility

Tipos de nota:

- qualification
- demo
- feedback
- follow_up
- internal

Las notas deben servir para seguimiento comercial y cualificación, no para almacenar información sensible innecesaria.

## 15. Reglas de privacidad

No guardar:

- Material audiovisual.
- Enlaces a material privado del cliente.
- Guiones.
- Contratos.
- Documentos de producción.
- Datos bancarios.
- Datos de facturación.
- Documentos de identidad.
- Información personal sensible innecesaria.

Guardar solo datos útiles para responder al interesado, cualificar el lead, preparar una demo, medir interés real, gestionar baja o no contacto y convertir manualmente en cliente futuro si procede.

## 16. Normalización de email

Reglas recomendadas:

- Trim de espacios.
- Conversión a minúsculas.
- Validación de formato básico.
- Unicidad lógica por email normalizado.
- No crear duplicado si el mismo email vuelve a entrar.
- Registrar evento nuevo si el lead ya existía.

## 17. Duplicados

Si llega un lead con email ya existente:

- No debe crearse un segundo lead activo por defecto.
- Debe añadirse un evento lead_updated.
- Debe actualizarse updated_at.
- Debe conservarse el historial anterior.
- Debe revisarse si cambia interés, proyecto o consentimiento.

## 18. Relación con n8n

n8n podrá usar este contrato para recibir formulario, validar campos mínimos, normalizar email, detectar duplicados, insertar o actualizar lead, insertar consentimiento, insertar evento inicial y notificar internamente un nuevo lead cualificado.

n8n no debe ser el CRM principal ni la fuente de verdad. La fuente de verdad será PostgreSQL.

## 19. Relación con CRM privado

El CRM privado futuro deberá permitir:

- Ver leads por estado.
- Filtrar por prioridad.
- Filtrar por tipo de organización.
- Ver historial de eventos.
- Añadir notas.
- Cambiar estado.
- Programar seguimiento.
- Marcar do_not_contact.
- Exportar listado operativo si hace falta.

El CRM privado no debe acceder a datos internos de CID SaaS salvo que una fase futura defina una conversión explícita y segura.

## 20. Índices lógicos recomendados

Índices recomendados para futura implementación:

- marketing_leads.email
- marketing_leads.status
- marketing_leads.priority
- marketing_leads.source
- marketing_leads.organization_type
- marketing_leads.created_at
- marketing_leads.next_follow_up_at
- marketing_lead_events.lead_id
- marketing_lead_events.created_at
- marketing_lead_consents.lead_id
- marketing_lead_notes.lead_id

## 21. Reglas de retención

Reglas recomendadas:

- Lead activo: conservar mientras exista relación comercial o interés razonable.
- Lead not_now: revisar periódicamente.
- Lead do_not_contact: conservar dato mínimo para no volver a contactar.
- Lead archived: conservar solo el mínimo necesario.
- Solicitud de baja: registrar retirada y bloquear nuevo contacto.

La política exacta deberá revisarse antes de activar captación real.

## 22. Criterios de aceptación de una futura implementación

Una implementación futura deberá cumplir:

- Crear tablas separadas del dominio CID.
- No introducir dependencias con billing, créditos o jobs IA.
- No pedir datos innecesarios.
- Registrar consentimiento separado.
- Registrar evento inicial.
- Evitar duplicados por email normalizado.
- Permitir do_not_contact.
- Permitir trazabilidad de cambios de estado.
- Mantener PostgreSQL como fuente de verdad.
- Permitir operación manual antes de automatizar ventas.

## 23. Próximas fases recomendadas

Fases posibles:

- AILINK.MARKETING.LEADS.N8N.WORKFLOW.CONTRACT.PHASE3
- AILINK.MARKETING.LEADS.CRM.PRIVATE.UI.SPEC.PHASE3
- AILINK.MARKETING.LEADS.DB.MIGRATION.PHASE3

La recomendación es no crear todavía migraciones reales hasta cerrar el contrato de workflow n8n y el diseño operativo del CRM privado.

## 24. Resumen ejecutivo

Este contrato define una base PostgreSQL futura para leads de AILinkCinema separada de CID SaaS.

El sistema debe permitir captar interesados de forma pasiva, registrar consentimiento, cualificar leads, preparar demos y operar una beta privada sin mezclar marketing con producción, facturación, créditos IA o datos internos de clientes.

La prioridad es mantener el sistema simple, legalmente prudente, trazable y preparado para crecer sin convertir n8n en un CRM improvisado.
