# AILink Marketing Leads — Private CRM UI Spec v1

## 1. Objetivo

Este documento define la especificación funcional del futuro CRM privado para gestionar leads de marketing de AILink Sync Dialogue.

La finalidad es diseñar una interfaz operativa mínima para revisar leads, cualificarlos, cambiar estados, añadir notas, programar seguimiento y preparar demos sin mezclar marketing con CID SaaS.

Esta fase es documental y de especificación. No implementa CRM real, no implementa frontend, no implementa backend, no crea rutas, no crea componentes React, no crea tablas, no crea migraciones, no crea workflow n8n, no toca PostgreSQL real, no toca Docker, no toca runtime, no toca configuración y no modifica CID SaaS.

## 2. Relación con fases anteriores

Este documento se apoya en:

- AILINK.MARKETING.LEADS.N8N.POSTGRES.CRM.SPEC.PHASE1
- AILINK.MARKETING.LEADS.DB.SCHEMA.CONTRACT.PHASE2
- AILINK.MARKETING.LEADS.N8N.WORKFLOW.CONTRACT.PHASE3

La Phase1 definió la arquitectura general de captación de leads.

La Phase2 definió el contrato lógico PostgreSQL.

La Phase3 definió el comportamiento lógico esperado de n8n.

Esta Phase4 define cómo se operarán manualmente esos leads desde un CRM privado futuro.

## 3. Principio general

El CRM privado debe ser una herramienta interna de operación comercial.

No debe ser una parte pública de la landing.

No debe ser CID SaaS.

No debe acceder a proyectos audiovisuales de clientes.

No debe acceder a billing, créditos IA, jobs IA, guiones, materiales, assets ni documentos internos de producción.

Debe servir para decidir qué leads merecen demo, seguimiento o beta.

## 4. Usuarios previstos

Usuarios internos previstos:

- Juan Carlos / operador principal.
- Futuro colaborador comercial si existe.
- Futuro administrador interno si se necesita.

No hay necesidad inicial de multiusuario complejo.

La primera versión puede asumir uso interno restringido, pero debe diseñarse pensando en permisos futuros.

## 5. Objetivos operativos del CRM

El CRM privado debe permitir:

- Ver leads recibidos.
- Filtrar leads por estado.
- Filtrar leads por prioridad.
- Filtrar por tipo de organización.
- Filtrar por área de interés.
- Revisar detalle de un lead.
- Ver consentimiento asociado.
- Ver historial de eventos.
- Añadir notas manuales.
- Cambiar estado.
- Cambiar prioridad.
- Programar próximo seguimiento.
- Marcar do_not_contact.
- Preparar demos de septiembre.
- Mantener separación con CID SaaS.

## 6. Pantallas mínimas futuras

Pantallas recomendadas:

- Dashboard privado.
- Lista de leads.
- Detalle de lead.
- Vista de notas.
- Vista de eventos.
- Vista de seguimiento.
- Vista de configuración mínima.

No hace falta un CRM complejo al inicio.

## 7. Dashboard privado

El dashboard debe mostrar una visión rápida del estado comercial.

Métricas recomendadas:

- Leads nuevos.
- Leads cualificados.
- Leads contactados.
- Demos solicitadas.
- Demos programadas.
- Demos realizadas.
- Beta candidates.
- Beta active.
- Leads not_now.
- Leads do_not_contact.
- Próximos seguimientos.
- Leads de alta prioridad.

El dashboard no debe mostrar información sensible innecesaria.

## 8. Lista de leads

La lista de leads debe ser la pantalla principal de trabajo.

Columnas recomendadas:

- Nombre.
- Email.
- Organización.
- Tipo de organización.
- Rol.
- Área de interés.
- Estado.
- Prioridad.
- Fuente.
- Fecha de creación.
- Último contacto.
- Próximo seguimiento.
- Consentimiento beta.
- do_not_contact.

La lista debe priorizar claridad y rapidez.

## 9. Filtros mínimos

Filtros recomendados:

- status.
- priority.
- organization_type.
- interest_area.
- source.
- created_at range.
- next_follow_up_at.
- demo_interest.
- beta_interest.
- do_not_contact.
- country.
- language.

Los filtros iniciales más importantes son status, priority, organization_type, interest_area y next_follow_up_at.

## 10. Búsqueda

La búsqueda debe permitir localizar leads por:

- Nombre.
- Email.
- Organización.
- Rol.
- Problema principal.
- Notas internas.

La búsqueda no debe depender de indexación compleja en primera versión.

## 11. Detalle de lead

La ficha de lead debe mostrar:

- Datos básicos.
- Organización.
- Rol.
- Contacto.
- Estado.
- Prioridad.
- Fuente.
- Área de interés.
- Herramientas actuales.
- Problema principal.
- Proyecto próximo.
- Timing del proyecto.
- Interés en demo.
- Interés en beta.
- Consentimientos.
- Eventos.
- Notas.
- Próximo seguimiento.
- Marcador do_not_contact.

La ficha debe permitir entender rápido si el lead merece contacto o demo.

## 12. Acciones principales

Acciones mínimas:

- Cambiar status.
- Cambiar priority.
- Añadir nota.
- Programar seguimiento.
- Marcar demo_scheduled.
- Marcar demo_done.
- Marcar beta_candidate.
- Marcar beta_active.
- Marcar not_now.
- Marcar not_fit.
- Marcar do_not_contact.
- Archivar lead.

Las acciones deben registrar evento operativo.

## 13. Estados editables

Estados operativos:

- new.
- qualified.
- contacted.
- demo_scheduled.
- demo_done.
- beta_candidate.
- beta_active.
- not_now.
- not_fit.
- do_not_contact.
- converted.
- archived.

Cambios sensibles:

- do_not_contact debe requerir confirmación.
- converted debe requerir confirmación.
- beta_active debe ser manual.
- archived debe ser reversible o registrarse con nota.

## 14. Prioridad editable

Prioridades:

- high.
- medium.
- low.
- unknown.

La prioridad puede venir sugerida por n8n, pero la decisión final debe ser humana.

El CRM debe mostrar claramente si la prioridad fue sugerida o revisada manualmente.

## 15. Notas manuales

Tipos de nota:

- qualification.
- demo.
- feedback.
- follow_up.
- internal.

Las notas deben ser útiles para operación comercial.

No deben almacenar material audiovisual, guiones, contratos, documentos personales, datos bancarios ni información sensible innecesaria.

## 16. Eventos

El CRM debe mostrar eventos del lead.

Eventos relevantes:

- lead_created.
- lead_updated.
- consent_recorded.
- status_changed.
- priority_changed.
- manual_email_sent.
- manual_call_done.
- manual_linkedin_message_sent.
- demo_requested.
- demo_scheduled.
- demo_completed.
- feedback_received.
- follow_up_scheduled.
- do_not_contact_set.
- converted_to_customer.
- archived.

Los eventos ayudan a no perder contexto y evitan depender de memoria manual.

## 17. Seguimiento

El CRM debe permitir programar follow-up.

Campos recomendados:

- next_follow_up_at.
- follow_up_reason.
- follow_up_channel.
- follow_up_status.

Canales posibles:

- email.
- phone.
- LinkedIn.
- video_call.
- in_person.
- other.

El objetivo es preparar septiembre con una lista clara de leads calientes.

## 18. Consentimiento y privacidad

El CRM debe mostrar el estado de consentimiento.

Debe distinguir:

- Consentimiento para contacto beta.
- Aceptación de política de privacidad.
- Consentimiento comercial futuro.

El CRM debe permitir ver si el contacto está permitido.

Si do_not_contact está activo, el CRM debe bloquear acciones comerciales.

## 19. Vista de septiembre

Para la estrategia actual, el CRM debe permitir una vista útil para septiembre.

Vista recomendada:

- Leads high priority.
- Leads de escuelas.
- Leads de productoras.
- Leads con demo_interest.
- Leads con upcoming_project.
- Leads con next_follow_up_at próximo.
- Leads beta_candidate.

Esta vista debe ayudar a decidir a quién contactar primero cuando llegue septiembre.

## 20. Seguridad

El CRM privado debe estar protegido.

Requisitos futuros:

- Acceso privado.
- Autenticación.
- No exposición pública.
- Sin datos sensibles innecesarios.
- Sin credenciales en repo.
- Sin acceso a CID SaaS salvo contrato futuro.
- Sin acceso a materiales de clientes.
- Logs prudentes.

## 21. Separación con CID SaaS

El CRM privado no debe:

- Leer proyectos CID.
- Modificar organizaciones CID.
- Leer billing CID.
- Leer créditos IA.
- Leer AI Jobs.
- Leer guiones.
- Leer documentos de producción.
- Leer assets audiovisuales.
- Crear usuarios CID automáticamente.

La conversión de lead a cliente será una fase futura explícita.

## 22. Relación con PostgreSQL

El CRM futuro leerá de PostgreSQL.

Operaciones lógicas futuras:

- Listar leads.
- Leer detalle de lead.
- Actualizar status.
- Actualizar priority.
- Añadir nota.
- Añadir evento.
- Programar seguimiento.
- Marcar do_not_contact.

Esta fase no implementa queries reales.

## 23. Relación con n8n

n8n alimentará leads y eventos iniciales.

El CRM revisará esos leads.

n8n no debe reemplazar al CRM.

El CRM no debe depender de abrir n8n para operar comercialmente.

## 24. Exportación operativa

Una versión futura podría permitir exportar listados operativos.

Exportaciones permitidas:

- CSV interno de leads filtrados.
- Lista de demos previstas.
- Lista de seguimientos.
- Lista de beta candidates.

No exportar datos sensibles innecesarios.

No exportar material audiovisual ni documentos privados.

## 25. Métricas comerciales mínimas

Métricas recomendadas:

- Total leads.
- Leads nuevos por semana.
- Leads cualificados.
- Leads contactados.
- Demos programadas.
- Demos realizadas.
- Beta candidates.
- Beta active.
- Conversión manual futura.
- Motivos frecuentes de interés.
- Tipos de organización más interesados.

Estas métricas deben apoyar decisiones, no crear burocracia.

## 26. Primera versión recomendada

Primera versión mínima futura:

- Login privado.
- Lista de leads.
- Filtros básicos.
- Detalle de lead.
- Cambio de estado.
- Cambio de prioridad.
- Notas.
- Seguimiento.
- do_not_contact.
- Eventos básicos.

No incluir todavía:

- Automatización avanzada.
- Envío masivo de emails.
- Scraping.
- Integración CID.
- Billing.
- Roles complejos.
- Campañas comerciales complejas.

## 27. Criterios de aceptación de una implementación futura

Una implementación futura deberá cumplir:

- No mezclar CRM de leads con CID SaaS.
- No exponer CRM públicamente.
- Mostrar lista de leads.
- Mostrar detalle de lead.
- Permitir filtros principales.
- Permitir cambios de status.
- Permitir cambios de priority.
- Permitir notas manuales.
- Permitir seguimiento.
- Respetar do_not_contact.
- Mostrar consentimiento.
- Registrar eventos.
- No guardar datos sensibles innecesarios.
- No incluir credenciales en el repo.
- No depender de n8n como panel operativo.

## 28. Límites de esta fase

Esta fase no incluye:

- CRM real.
- Frontend real.
- Backend real.
- Rutas reales.
- Componentes React.
- API.
- Queries SQL.
- Migraciones.
- Tablas reales.
- Workflow n8n real.
- Formulario real.
- Landing real.
- Docker.
- Runtime.
- Configuración.
- CID SaaS.

## 29. Próximas fases recomendadas

Después de esta fase, las siguientes opciones son:

- AILINK.MARKETING.LEADS.CRM.PRIVATE.DATA.FLOW.CONTRACT.PHASE5
- AILINK.MARKETING.LEADS.N8N.WORKFLOW.DRY.RUN.SPEC.PHASE5
- AILINK.MARKETING.LEADS.DB.MIGRATION.CONTRACT.PHASE5
- Volver a AILink Sync Dialogue producto/demos

La recomendación es no implementar CRM real hasta decidir si se hará dentro del repo actual, en un frontend separado o como herramienta interna mínima.

## 30. Resumen ejecutivo

Este documento especifica el CRM privado mínimo para operar leads de AILink Sync Dialogue.

El CRM debe ayudar a revisar, filtrar, cualificar, anotar y seguir leads manualmente.

La prioridad es mantener el flujo simple, privado, seguro y separado de CID SaaS.
