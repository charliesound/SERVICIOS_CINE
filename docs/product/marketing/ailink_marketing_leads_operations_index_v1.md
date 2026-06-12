# AILink Marketing Leads — Operations Index v1

## 1. Objetivo

Este documento cierra el bloque documental inicial de marketing leads para AILink Sync Dialogue.

La finalidad es dejar un índice operativo de lo ya decidido, qué piezas existen, qué no debe implementarse todavía y cuándo tendría sentido activar infraestructura real de captación, n8n, PostgreSQL y CRM privado.

Esta fase es documental e índice operativo. No implementa n8n real, no implementa CRM real, no crea frontend, no crea backend, no crea formulario real, no crea tablas reales, no crea migraciones, no toca Docker, no toca runtime, no toca configuración y no modifica CID SaaS.

## 2. Estado estable del bloque

El bloque marketing leads queda formado por cuatro contratos previos:

- Phase1: arquitectura Landing/Formulario → n8n → PostgreSQL → CRM privado.
- Phase2: contrato lógico del esquema PostgreSQL de leads.
- Phase3: contrato lógico del workflow n8n.
- Phase4: especificación funcional del CRM privado.

Este documento actúa como mapa de lectura y cierre operativo antes de volver al producto AILink Sync Dialogue.

## 3. Documentos incluidos

### 3.1 Phase1 — Arquitectura general

Archivo:

- docs/product/marketing/ailink_marketing_leads_n8n_postgres_crm_spec_v1.md

Define:

- Captación pasiva de leads.
- Separación entre marketing leads y CID SaaS.
- Arquitectura conceptual Landing/Formulario → n8n → PostgreSQL → CRM privado.
- n8n como orquestador.
- PostgreSQL como base de datos de leads.
- CRM privado como panel manual futuro.

### 3.2 Phase2 — Contrato PostgreSQL

Archivo:

- docs/product/marketing/ailink_marketing_leads_db_schema_contract_v1.md

Define:

- marketing_leads.
- marketing_lead_consents.
- marketing_lead_events.
- marketing_lead_notes.
- Campos mínimos.
- Estados del lead.
- Consentimiento.
- Eventos.
- Privacidad.
- Normalización de email.
- Duplicados.
- Relación con n8n y CRM privado.

### 3.3 Phase3 — Contrato workflow n8n

Archivo:

- docs/product/marketing/ailink_marketing_leads_n8n_workflow_contract_v1.md

Define:

- Entrada esperada desde landing o formulario.
- Validación de campos mínimos.
- Normalización de email.
- Detección de duplicados.
- Registro de consentimiento.
- Registro de eventos.
- Notificación interna.
- Manejo seguro de errores.
- Límites de n8n como orquestador, no CRM.

### 3.4 Phase4 — CRM privado

Archivo:

- docs/product/marketing/ailink_marketing_leads_crm_private_ui_spec_v1.md

Define:

- Dashboard privado.
- Lista de leads.
- Detalle de lead.
- Filtros.
- Búsqueda.
- Notas manuales.
- Eventos.
- Seguimiento.
- Consentimiento.
- Vista de septiembre.
- Seguridad.
- Separación con CID SaaS.
- Relación con PostgreSQL y n8n.

## 4. Decisiones cerradas

Decisiones aprobadas:

- No contactar escuelas de forma fuerte antes de septiembre.
- Junio, julio y agosto se orientan a captación pasiva y desarrollo de producto.
- Septiembre será el momento natural para demos y pruebas controladas.
- n8n encaja como orquestador, no como CRM principal.
- PostgreSQL será la fuente de verdad de leads.
- El CRM privado será la interfaz manual para operar leads.
- CID SaaS debe permanecer separado del sistema de marketing leads.
- No se debe mezclar marketing con billing, créditos IA, AI Jobs, proyectos audiovisuales ni material de clientes.

## 5. Qué no debe implementarse todavía

No implementar todavía:

- Workflow real de n8n.
- Webhook real.
- JSON importable de n8n.
- Credenciales reales.
- Formulario real conectado.
- CRM real.
- Frontend del CRM.
- Backend del CRM.
- Migraciones reales.
- Tablas reales.
- Automatización de emails.
- Campañas masivas.
- Scraping.
- Integración con CID SaaS.
- Conversión automática de lead a cliente.
- Pagos.
- Docker.
- Runtime.
- Configuración.

Motivo: todavía falta validar interés real con producto demostrable y señal comercial suficiente.

## 6. Condiciones para activar n8n real

n8n real debería activarse solo cuando se cumplan varias condiciones:

- Landing o formulario beta con texto revisado.
- Política de privacidad y consentimiento preparados.
- Producto demo suficientemente claro.
- CTA público definido.
- Necesidad real de capturar más leads de los que se pueden gestionar manualmente.
- Criterios de cualificación ya probados.
- Decisión clara sobre dónde vivirá el CRM privado.
- Decisión clara sobre base PostgreSQL real de marketing leads.
- No mezclar nunca con base operativa de CID SaaS.

## 7. Condiciones para activar CRM real

CRM real debería activarse cuando:

- Existan leads suficientes para que una hoja manual sea incómoda.
- Haya demos programadas.
- Haya necesidad de seguimiento semanal.
- Sea importante registrar notas, eventos y estados con disciplina.
- Se acerque septiembre y haga falta priorizar escuelas, productoras y leads calientes.
- Ya se haya decidido si el CRM vive dentro del repo actual o como herramienta interna separada.

## 8. Riesgos de avanzar demasiado pronto

Riesgos:

- Construir infraestructura antes de tener producto enseñable.
- Convertir n8n en CRM improvisado.
- Perder tiempo con frontend interno antes de captar feedback real.
- Crear migraciones prematuras.
- Mezclar datos de marketing con CID SaaS.
- Añadir obligaciones legales antes de tener flujo público revisado.
- Automatizar contacto sin suficiente contexto.
- Desviar foco de AILink Sync Dialogue.

## 9. Checklist de septiembre

Antes de contactar escuelas, productoras o leads calientes en septiembre, revisar:

- Demo local de AILink Sync Dialogue funcionando.
- Guion de demo comercial de 5 a 7 minutos.
- Landing revisada.
- CTA beta claro.
- Texto legal mínimo revisado.
- Formulario o mecanismo de contacto decidido.
- Mensajes manuales de contacto preparados.
- Lista inicial de contactos priorizada.
- Criterios de lead high, medium y low revisados.
- Sistema manual o CRM mínimo para seguimiento.
- Calendario de demos.
- Plantilla de feedback post-demo.

## 10. Checklist de producto antes de marketing fuerte

Antes de invertir más en captación, AILink Sync Dialogue debe poder mostrar:

- Escaneo local de carpeta.
- Detección de archivos de vídeo y audio.
- Lectura de metadata cuando esté disponible.
- Sugerencias de matching.
- Reporte HTML o equivalente.
- Demo end-to-end reproducible.
- Explicación clara de límites actuales.
- Mensaje comercial honesto.
- Qué resuelve hoy.
- Qué se probará en beta.
- Qué no hace todavía.

## 11. Orden recomendado desde este punto

Orden recomendado:

1. Cerrar este índice operativo.
2. Parar marketing leads técnico por ahora.
3. Volver a AILink Sync Dialogue producto y demo.
4. Preparar demo readiness.
5. Revisar landing y mensaje cuando la demo esté más sólida.
6. Activar formulario o n8n solo si ya hay algo claro que enseñar.
7. Preparar CRM real solo cuando haya volumen de leads o demos.

## 12. Fase siguiente recomendada

La siguiente fase recomendada es:

- AILINK.PRODUCT.SYNC_DIALOGUE.DEMO.READINESS.PHASE7

Objetivo futuro:

- Auditar si la demo actual está lista para enseñar.
- Identificar huecos comerciales.
- Separar prototipo, beta y promesa futura.
- Preparar una demo de 5 a 7 minutos.
- Preparar checklist de revisión antes de enseñar a terceros.

## 13. Resumen ejecutivo

El bloque marketing leads ya tiene suficiente contrato para no improvisar.

La decisión recomendada es no implementar todavía n8n, CRM ni base real de leads.

La prioridad vuelve a ser producto: mejorar AILink Sync Dialogue como demo vendible y beta privada seria.

Marketing debe acompañar al producto, no adelantarse a él.
