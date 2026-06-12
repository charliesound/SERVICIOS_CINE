# AILink Marketing Leads — n8n + PostgreSQL + Private CRM Spec v1

## 1. Objetivo

Este documento define la arquitectura futura para captar interesados en AILink Sync Dialogue desde una landing pública, procesarlos con n8n, guardarlos en PostgreSQL y gestionarlos más adelante desde un CRM privado sencillo.

La finalidad es preparar el programa de captación pasiva de junio a septiembre sin construir todavía infraestructura innecesaria.

Esta fase no implementa workflows reales de n8n, no crea tablas, no crea migraciones, no toca frontend, backend, CID SaaS, formulario real, CRM real, pagos, Docker, runtime ni configuración.

## 2. Decisión de arquitectura

Arquitectura recomendada:

Landing pública / formulario beta → n8n recibe el lead → n8n valida y normaliza datos → PostgreSQL guarda el lead → CRM privado permite revisar y gestionar leads.

Responsabilidades:

- Landing: presenta AILink Sync Dialogue y recoge intención de beta.
- n8n: automatiza recepción, validación, confirmación y avisos.
- PostgreSQL: almacena los leads de forma estructurada.
- CRM privado: permite ver, filtrar, editar estado y registrar seguimiento.
- CID: queda separado y no participa en esta primera captación.

## 3. Diferencia entre n8n, PostgreSQL y CRM

PostgreSQL es la base de datos.

n8n es el orquestador.

El CRM privado es el panel de gestión.

PostgreSQL guarda nombre, email, organización, tipo de lead, estado y consentimiento.

n8n recibe el formulario, valida datos, guarda el lead y envía avisos.

El CRM privado permite consultar leads, cambiar estado, añadir notas y exportar CSV.

## 4. Separación con CID

AILink Marketing Leads debe mantenerse separado de CID.

Reglas:

- No mezclar leads de marketing con usuarios reales de CID.
- No mezclar beta testers con cuentas SaaS.
- No usar datos de leads para consumo de créditos IA.
- No crear proyectos CID automáticamente desde leads.
- No conectar esta captación con billing.
- No usar tablas core de CID para leads comerciales.

Relación futura:

- Un lead cualificado puede convertirse más adelante en beta tester.
- Un beta tester puede convertirse más adelante en usuario CID.
- Esa conversión debe ser explícita y no automática en esta fase.

## 5. Tabla conceptual `marketing_leads`

Campos recomendados:

| Campo | Uso |
|---|---|
| id | Identificador interno |
| created_at | Fecha de alta |
| updated_at | Última actualización |
| source | landing, manual, linkedin, email, evento |
| name | Nombre de contacto |
| email | Email de contacto |
| organization | Escuela, productora o empresa |
| profile_type | escuela, productora, postproduccion, montador, dit, otro |
| tools_used | DaVinci, Avid, Premiere, otros |
| main_problem | Problema principal antes de montaje |
| wants_september_beta | Interés en pruebas de septiembre |
| consent_contact | Consentimiento para contacto |
| consent_marketing | Consentimiento opcional para novedades |
| privacy_version | Versión legal aceptada |
| status | Estado del lead |
| priority | alta, media, baja |
| notes | Notas internas |
| no_contactar | Bloqueo de contacto |
| last_contacted_at | Último contacto |
| next_action_at | Próxima acción prevista |

## 6. Estados del lead

Estados recomendados:

- nuevo
- pendiente_revision
- cualificado
- interesado_septiembre
- contactado
- respondio
- demo_agendada
- beta_aprobada
- no_interesado
- no_contactar
- descartado

Reglas:

- Todo lead entra como nuevo.
- Si falta consentimiento de contacto, no se debe usar comercialmente.
- Si `no_contactar` es verdadero, n8n no debe enviar campañas ni recordatorios.
- La cualificación debe ser manual al inicio.
- La selección para beta debe ser manual.

## 7. Workflow n8n futuro: captura de lead

Workflow conceptual:

1. Recibir lead desde formulario o webhook.
2. Validar campos mínimos.
3. Validar email.
4. Validar consentimiento de contacto.
5. Normalizar `profile_type`.
6. Crear registro en PostgreSQL.
7. Evitar duplicados por email.
8. Enviar confirmación al interesado.
9. Enviar aviso interno.
10. Devolver mensaje de gracias.

No debe hacer:

- Crear cuenta CID.
- Crear proyecto CID.
- Cobrar.
- Pedir material audiovisual.
- Pedir datos sensibles.
- Enviar campañas sin consentimiento.
- Clasificar automáticamente como beta_aprobada.

## 8. Workflow n8n futuro: resumen semanal

Workflow conceptual:

1. Ejecutarse una vez por semana.
2. Consultar leads nuevos.
3. Separar por tipo de perfil.
4. Contar interesados en septiembre.
5. Listar leads pendientes de revisión.
6. Enviar resumen interno.
7. No contactar automáticamente a leads sin revisión.

Salida interna recomendada:

- nuevos esta semana
- interesados en septiembre
- escuelas
- productoras
- postproducción
- montadores/DIT
- pendientes de revisar
- leads con no_contactar

## 9. Workflow n8n futuro: preparación de septiembre

Workflow manual:

1. Filtrar `wants_september_beta`.
2. Filtrar prioridad alta y media.
3. Excluir `no_contactar`.
4. Excluir leads sin consentimiento.
5. Exportar CSV.
6. Preparar contacto manual.
7. Registrar respuestas en CRM privado.

## 10. CRM privado futuro

El CRM privado debe ser simple.

Funciones mínimas:

- Ver lista de leads.
- Buscar por nombre, email u organización.
- Filtrar por estado.
- Filtrar por tipo de perfil.
- Filtrar interesados en septiembre.
- Editar estado.
- Editar prioridad.
- Añadir notas.
- Marcar no_contactar.
- Ver fecha de alta.
- Ver último contacto.
- Exportar CSV.

No debe ser todavía:

- CRM comercial completo.
- Sistema de ventas.
- Sistema de campañas masivas.
- Plataforma de email marketing.
- Sustituto de CID.
- Panel público.

## 11. Formulario futuro de landing

Campos mínimos:

- Nombre.
- Email.
- Organización.
- Perfil.
- Problema principal.
- Herramientas que usa.
- Interés en probar en septiembre.
- Consentimiento de contacto.
- Consentimiento opcional de novedades.
- Aceptación de política de privacidad.

Texto de seguridad:

No envíes material audiovisual ni archivos de clientes. Esta lista es solo para solicitar acceso a la beta privada y recibir contacto sobre AILink Sync Dialogue.

## 12. Confirmación al usuario

Mensaje de confirmación recomendado:

Gracias por apuntarte a la lista de beta privada de AILink Sync Dialogue.

Hemos recibido tu solicitud. Durante los próximos meses seleccionaremos perfiles concretos para demos controladas y pruebas en septiembre. No necesitamos que envíes material audiovisual en esta fase.

## 13. Aviso interno

Aviso interno recomendado:

Nuevo lead AILink Sync Dialogue.

Datos mínimos:

- nombre
- email
- organización
- perfil
- problema principal
- interés septiembre
- origen
- estado inicial

No incluir datos sensibles.

## 14. Duplicados

Regla recomendada:

- El email debe ser el identificador principal para evitar duplicados.
- Si entra un email ya existente, actualizar `updated_at`, `source` adicional y notas.
- No crear registros duplicados salvo decisión manual.
- Si el lead estaba en `no_contactar`, no reactivarlo automáticamente.

## 15. RGPD operativo básico

Principios:

- Recoger solo datos necesarios.
- Informar de finalidad.
- Pedir consentimiento de contacto.
- Mantener consentimiento de novedades separado.
- Permitir baja o no_contactar.
- No pedir material sensible.
- No mezclar leads con usuarios SaaS.
- No conservar leads inútiles indefinidamente.
- No usar los datos para fines distintos a la beta sin consentimiento.

## 16. Roadmap recomendado

Fase 1 actual:

- Spec n8n + PostgreSQL + CRM privado.
- Sin implementación.

Fase 2 futura:

- Crear esquema técnico de tabla `marketing_leads`.
- Definir validaciones.
- Definir contrato CSV.

Fase 3 futura:

- Implementar workflow n8n local o de staging.

Fase 4 futura:

- Conectar formulario real de landing.

Fase 5 futura:

- Crear CRM privado mínimo.

Fase 6 futura:

- Preparar campaña manual de septiembre.

## 17. No-goals

Esta fase no hace:

- No implementa n8n real.
- No crea tablas reales.
- No crea migraciones.
- No implementa CRM.
- No implementa landing real.
- No implementa formulario real.
- No implementa email real.
- No conecta PostgreSQL real.
- No toca CID.
- No toca billing.
- No toca frontend/backend.
- No toca Docker.
- No toca runtime.
- No toca configuración.
- No hace scraping.
- No hace campañas automáticas.

## 18. Criterios de aceptación

Esta fase se considera válida si:

- Explica la diferencia entre n8n, PostgreSQL y CRM.
- Define arquitectura landing → n8n → PostgreSQL → CRM.
- Mantiene separación con CID.
- Define tabla conceptual `marketing_leads`.
- Define estados de lead.
- Define workflow de captura.
- Define workflow semanal.
- Define workflow de preparación de septiembre.
- Define funciones mínimas del CRM privado.
- Define campos del formulario futuro.
- Define confirmación al usuario.
- Define aviso interno.
- Define reglas de duplicados.
- Define RGPD operativo básico.
- Define roadmap.
- Define no-goals.
- No implementa runtime.
