# Directiva Técnica: Ruteo de Alertas por Tipo y Severidad

## 1. Objetivo
Establecer un mecanismo de decisión centralizado y configurable que enrute las alertas emitidas por la plataforma hacia los canales de notificación adecuados (Slack, Telegram, Webhook) basándose en atributos clave como la severidad (`severity`) y la categoría/tipo de evento (`type`).

## 2. Problema que Resuelve
Actualmente la plataforma cuenta con capacidades integradas para enviar alertas multicanal, pero carece de un sistema de filtrado condicional inteligente. Esto genera problemas de *alert fatigue* (fatiga de alertas) donde notificaciones de baja relevancia saturan canales críticos, o alertas urgentes (ej. fallo grave en pipeline de renderizado) pueden perderse. El ruteo dinámico garantiza que los equipos y flujos de automatización (vía n8n) reciban únicamente la información accionable y de forma puntual.

## 3. Modelo de Datos Recomendado para Routing Rules
Dado el stack de **Supabase (PostgreSQL)**, se recomienda añadir tablas relacionales para administrar las "Reglas de Ruteo" a nivel de proyecto u organización SaaS.

**Tabla: `alert_routing_rules`**
- `id` (UUID, PK)
- `project_id` (UUID, FK a Project - Nullable si es configuración global)
- `name` (String) - Nombre de la regla (ej. "Producción: Solo Críticos a Telegram")
- `match_type` (Enum Array / Text Array) - Tipos de evento (ej. `['render_failed', 'auth_issue', '*']`)
- `match_severity` (Enum Array / Text Array) - Niveles (ej. `['critical', 'error']`)
- `target_channels` (JSONB) - Rutas de entrega (ej. `[{ "channel": "slack", "webhook_id": "uuid" }, { "channel": "n8n_webhook", "url": "https..." }]`)
- `is_enabled` (Boolean, Default: true)
- `created_at` / `updated_at` (Timestamps)

## 4. Reglas Mínimas de Matching por Type y Severity
Se debe seguir esta taxonomía mínima en el código para categorizar eventos:

**Severidad (`severity`):**
- `info`: Eventos informativos exitosos de negocio (ej. "Exportación OTX inciada").
- `warning`: Problemas no bloqueantes (ej. "Falta de espacio en disco detectada").
- `error`: Fallos que afectan operaciones puntuales (ej. "Error procesando webhook de ComfyUI").
- `critical`: Fallos catastróficos u operativos que detienen flujos de producción.

**Tipos (`type`):**
- `system`: Infraestructura, integraciones externas (Supabase, disco, red).
- `auth`: Actividad de seguridad, roles o accesos anómalos.
- `job`: Cargas de trabajo asíncronas de la plataforma (Pipelines, Generación, Importaciones).
- `business`: Notificaciones de métricas o negocio SaaS.

*Mecánica:* Si una alerta definida como `[type: job, severity: critical]` es originada, el router consultará las reglas y activará únicamente aquellos canales donde figure esta combinación. 

## 5. Estrategia para Evitar Envíos Duplicados (Deduplicación)
1. **Ventanas de Debouncing / Rate Limiting:**
   - Generar un "fingerprint" del evento usando: `hash(project_id + type + severity + target_entity_id)`.
   - Utilizar una tabla transitoria (ej. `alert_locks`) en Supabase con lógica de TTL, o caché. Si un evento con el mismo fingerprint se repite en menos de 5-15 minutos, se omite el ruteo hacia el canal, se incrementa un counter en la DB (para saber que la regla "absorbió" el error continuo) sin molestar a los usuarios en Telegram o Slack.
2. **Acumulación (Batching):** En futuras fases, encolar los ruteos de tipo `warning` para enviarse como resumen y no en tiempo real.

## 6. Trazabilidad Mínima del Ruteo Aplicado
Para debug interno y paneles de Observability, todo dictamen del router debe generar un log.

**Tabla: `alert_delivery_logs`**
- `id` (UUID)
- `alert_event_id` (UUID - ID de la alerta/evento raw original)
- `routing_rule_id` (UUID, opcional - Regla que validó el envío)
- `channel` (String - "slack", "telegram", "webhook")
- `status` (Enum - `success`, `failed`, `skipped_duplicate`, `filtered`)
- `response_payload` (JSONB - Respuesta/HTTP status del canal de destino)
- `dispatched_at` (Timestamp)

## 7. Integración Recomendada en UI
Se encapsulará bajo la sección de Administrador (Settings > Alertas):
- **Dashboard de Reglas:** Utilizando `DataTable` de Shadcn para visibilidad de reglas activas/inactivas.
- **Constructor de Routing (Formulario Modal):** 
  - Usando `Select` múlti-opción para definir arrays de `type` y `severity`.
  - Formularios dinámicos (con `react-hook-form` + `zod`) para añadir `n` canales por regla.
  - Botón "Test Rule" que envía un "dummy payload" al backend para validar el endpoint y la credencial/URL.
- **Log de Envíos:** Una vista *Read-Only* conectada a `alert_delivery_logs` con filtros por Estado, permitiendo solucionar problemas a los sysadmins.

## 8. Criterios de Aceptación
1. El motor ignora las notificaciones que no cumplen con los parámetros definidos en las reglas de un usuario (`filtered`).
2. Las alertas en ráfaga provenientes del mismo origen se reducen utilizando la clave de debouncing (No al *Spam multicanal*).
3. Todo intento o acción filtrada se graba en la base de datos de trazabilidad.
4. El envío de notificaciones multicanal no retrasa transacciones del usuario, lográndose mediante procesos push en background (Servicios Externos o Webhooks propios ejecutando asíncronamente).

## 9. Riesgos
- **Latencia Transaccional:** Ejecutar el cruce de reglas e inserciones HTTP síncronamente al emitir la alerta, degradando tiempos de respuesta de la API principal. 
  *(Mitigación: Disparar el router de alertas y salidas usando Supabase Edge Functions con triggers `.after_insert()` sobre la tabla original de alertas, o enviarlo mediante enrutador n8n asíncrono).*
- **Infinite Loops (Bucles Infinitos):** El canal de reporte webhooks falla, genera un error crítico, el cual gatilla el enrutador de webhooks que vuelve a fallar.
  *(Mitigación: Implementar guardrails en el código excluyendo explícitamente eventos catalogados como `[type: internal_routing_error]` para rutear fuera del mismo sistema que ha fallado).*

## 10. Siguiente Evolución Recomendada
- **Reglas basadas en Ponderaciones Extra (Payload Matching):** Permitir JSONPaths avanzados (ej. "Route_to_Telegram: Solo si `alert.payload.cost > $100`").
- **Escalation Policies (Políticas de Escalamiento):** Implementar la capacidad de Acknowledgement. Si una alerta `critical` en Slack no interactúa con un botón de "Tomar caso", pasados 15 minutos el sistema la eleva mediante otra regla (ej. llamando a un webhook n8n adicional para Pageduty/Llamadas telefónicas).
