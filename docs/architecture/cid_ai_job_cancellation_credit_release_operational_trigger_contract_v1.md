# CID AI Job Cancellation Credit Release Operational Trigger Contract v1

## Estado

- Basado en HEAD `51aeb69` (`test: harden CID AI job cancellation release reconciliation`).
- Documento previo a implementación.
- No cambia runtime.
- Define opciones futuras para disparar `process_cancelled_ai_job_credit_releases(...)`.
- PostgreSQL-only.

## Problema

La reconciliación interna ya existe como servicio:

- `AIJobAsyncOrchestrationService.process_cancelled_ai_job_credit_releases(...)`
- `AIJobAsyncOrchestrationService.release_cancelled_ai_job_reserved_credits(...)`
- `AIJobRepository.list_cancelled_credit_release_candidates(...)`

Todas las piezas de selección, validación, release contable y reporting están implementadas y testeadas. Sin embargo, no existe todavía un mecanismo operativo que dispare la reconciliación periódicamente o bajo demanda.

Hay que decidir cómo activarla sin exponer control de release al cliente y sin acoplar la operación interna a la API pública existente.

## Principio Principal

La ejecución debe ser:

- **Interna**: nunca iniciada por payload de cliente público.
- **Auditada**: cada ejecución debe registrar `requested_by`, `organization_id`, resultado y duración.
- **Tenant-safe**: siempre por `organization_id` explícito confiable.
- **Idempotente**: rerun seguro sin doble settlement.
- **Observable**: métricas y logs por ejecución, por tenant, por categoría de error.
- **No controlada por cliente**: `organization_id`, `release_credits`, `caller_key` y flags de release no deben venir de cliente público.

## Opciones De Disparo

### A) CLI Interna Manual

**Descripción**: script mantenible tipo `python -m scripts.ops.reconcile_cancelled_ai_job_credit_releases` que ejecuta la reconciliación para un `organization_id` concreto.

**Ventajas**:
- Implementación mínima: llamada directa a `process_cancelled_ai_job_credit_releases(...)`.
- Segura para primera operación: no expone HTTP, no depende de scheduler.
- `dry_run` disponible sin riesgo.
- Fácil de auditar (log + salida JSON).
- No requiere infraestructura nueva.

**Riesgos**:
- Depende de operador humano; no automatiza recuperación nocturna.
- No escala a muchos tenants sin scripting externo.
- Sin scheduler, los créditos de jobs cancelados quedan retenidos hasta ejecución manual.
- El operador debe tener acceso al entorno runtime y a las credenciales de base de datos.

**Uso recomendado**: primera fase operativa (Phase 5A).

### B) Endpoint Admin-Only Interno

**Descripción**: endpoint HTTP interno/admin (no público, no accesible desde Internet) que recibe `organization_id`, `max_items` y `dry_run`, y ejecuta la reconciliación.

**Ventajas**:
- Integrable con panel de operaciones futuro.
- El servicio ya corre dentro del proceso FastAPI; añadir un router admin separado es técnicamente trivial.
- `requested_by` puede derivarse del contexto de autenticación admin.
- Logging y métricas centralizados.

**Riesgos**:
- Superficie HTTP nueva que debe protegerse con permisos fuertes.
- Riesgo de exposición accidental si el router admin no está bien aislado de la API pública.
- Requiere definir autenticación admin/ops, rate limits, auditoría de acceso.
- El cliente interno (panel/scripts) sigue siendo un caller HTTP; si el panel está comprometido, el endpoint es accesible.

**No implementar todavía** sin contrato de admin/ops que defina:
- Cómo se autentica un caller admin vs cliente normal.
- Qué permisos mínimos son necesarios.
- Cómo se audita cada invocación.
- Cómo se rate-limit para evitar abuso desde panel comprometido.
- Cómo se aísla del router público (sub-app FastAPI separada, prefijo `/internal/admin/`, middleware específico).

### C) Scheduler Interno

**Descripción**: tarea programada (cron, schedule library, Celery Beat, APScheduler) que ejecuta la reconciliación periódicamente para todos los tenants o para una lista configurada.

**Ventajas**:
- Automatización completa: los créditos retenidos se liberan sin intervención manual.
- Frecuencia configurable: permite definir ventanas de procesamiento (minuto, hora, diario).
- Puede iterar sobre tenants automáticamente usando una lista de organizaciones activas.

**Riesgos**:
- Dos ticks del scheduler pueden solaparse si el procesamiento tarda más que el intervalo.
- Sin lock operacional, dos réplicas del scheduler pueden ejecutar la misma reconciliación simultáneamente.
- Observabilidad: si falla silenciosamente, los créditos quedan retenidos sin alarma.
- Retry sin backoff ni ventana puede generar loops apretados sobre errores transitorios.
- El despliegue del scheduler requiere coordinación con el ciclo de release del backend.
- La lógica para obtener la lista de tenants activos no existe todavía.

**No implementar todavía** hasta tener:
- Lock operacional probado (advisory lock PostgreSQL o lock externo).
- Métricas de tick, duración, errores y capacidad de kill switch.
- Ventana de retry y backoff definidos.
- Lista de tenants o mecanismo de discovery.
- Pruebas de concurrencia que demuestren que dos schedulers no producen doble settlement.

### D) Worker/Background Real Conectado a Cola

**Descripción**: worker asíncrono que procesa mensajes de una cola (RabbitMQ, Redis RQ, Celery) donde se encolan peticiones de reconciliación por `organization_id`.

**Ventajas**:
- Diseño escalable: los workers pueden escalar horizontalmente.
- Desacoplamiento: el trigger y la ejecución están separados por cola.
- Retry nativo: la cola reintenta mensajes fallidos con backoff.
- Dead letter: errores terminales van a cola de inspección.

**Riesgos**:
- La cola aún no está madura en el proyecto; introducirla sólo para reconciliación es premature.
- Idempotencia distribuida: el mismo mensaje puede entregarse dos veces; el consumidor debe ser idempotente (el servicio ya lo es, pero hay que validarlo bajo entrega duplicada).
- Observabilidad: métricas de cola (depth, age, retries, dead letter) son necesarias.
- Complejidad operativa: la cola requiere despliegue, monitoreo y mantenimiento.

**Posponer** hasta que exista un worker real en el proyecto con cola operativa y monitoreo.

## Recomendación

Secuencia recomendada de implementación progresiva:

| Fase | Mecanismo | Cuándo |
|---|---|---|
| **Phase 5A** | CLI interna manual per-tenant | Inmediato: primera operación segura sin exposición HTTP |
| **Phase 5B** | Scheduler interno con lock operacional | Después de tener observabilidad, métricas, lock PostgreSQL probado y kill switch |
| **Phase 5C** | Endpoint admin-only (si existe panel Ops) | Después de contrato de admin/ops con permisos fuertes y aislamiento de router |
| **Phase 5D** | Worker/cola real | Cuando exista worker real con cola operativa y monitoreo |

No saltar fases. Cada fase debe demostrar estabilidad antes de pasar a la siguiente.

La CLI es la puerta de entrada más segura porque:
- No añade superficie de red.
- No requiere autenticación de servicio adicional.
- El operador controla tenant, dry_run y salida.
- Es trivial de auditar: logs + stdout.

## Contrato De CLI Futura

El siguiente contrato describe una CLI futura sin implementarla:

```text
python -m scripts.ops.reconcile_cancelled_ai_job_credit_releases \
    --organization-id <id> \
    [--max-items 50] \
    [--dry-run] \
    [--requested-by "ops-user"]
```

### Parámetros

| Parámetro | Obligatorio | Default | Descripción |
|---|---|---|---|
| `--organization-id` | Sí | — | Tenant obligatorio. Sin batch global sin organización explícita. |
| `--max-items` | No | `50` | Máximo de jobs a procesar. Capa interna a 100. |
| `--dry-run` | No | `False` | Modo inspección; no muta jobs ni llama ledger. |
| `--requested-by` | No | `"cli"` | Identificador del operador para auditoría. |

### Salida

Salida JSON a `stdout` al finalizar:

```json
{
  "organization_id": "org-xxx",
  "dry_run": false,
  "scanned_count": 50,
  "processed_count": 50,
  "released_count": 45,
  "skipped_count": 3,
  "failed_count": 2,
  "duration_seconds": 1.23,
  "per_job_results": [
    {
      "job_id": "job-001",
      "organization_id": "org-xxx",
      "error_category": "released_now",
      "release_entry_id": "rel-entry-001",
      ...
    }
  ]
}
```

Si `failed_count > 0`, el script debe producir **exit code no cero** (documentado abajo).

### Exit Codes

| Código | Significado |
|---|---|
| `0` | Éxito completo: `failed_count == 0`. |
| `1` | Fallo parcial: `failed_count > 0` pero no hay error inesperado. |
| `2` | Error de parámetros: `--organization-id` faltante o inválido. |
| `3` | Error inesperado durante la ejecución del script (antes de llamar al servicio). |
| `≥ 10` | Error de conexión/entorno (base de datos no disponible, etc.). |

### Logs

- Cada ejecución debe loguear: `organization_id`, `dry_run`, `max_items`, resultados agregados, duración.
- Cada job debe loguear: `job_id`, `error_category`, `release_entry_id`, `release_performed`, `status_before`, `status_after`.
- No loguear: secretos, tokens, payloads de usuario, prompts, metadata sensible.

### Seguridad

- No debe ejecutarse como root ni con permisos de superusuario de base de datos.
- No debe leer `.env` de entorno de producción desde contexto inseguro.
- No debe aceptar `organization_id` desde variable de entorno no validada.
- `requested_by` debe ser trazable a un operador real o alias conocido.

## Contrato De Endpoint Admin-Only Futuro

El siguiente contrato describe un posible endpoint admin sin implementarlo:

```text
POST /internal/admin/ai-jobs/reconcile-cancelled-credits
```

### Request Body

```json
{
  "organization_id": "org-xxx",
  "max_items": 50,
  "dry_run": false,
  "requested_by": "ops-panel"
}
```

### Requisitos de Permiso

- Middleware de autenticación admin independiente del middleware de cliente público.
- `organization_id` controlado por el contexto del admin, no por el payload del cliente.
- Rechazar si el caller no tiene rol `admin` u `operator`.
- Rate limit por caller, no por tenant (un admin no debe saturar el sistema accidentalmente).

### Prohibiciones

- No aceptar campos `release_credits`, `caller_key`, `reservation_entry_id` ni ninguna flag de release arbitraria.
- No aceptar `organization_id` que no corresponda al contexto autenticado del admin (el admin autenticado puede operar sobre múltiples tenants, pero cada petición debe declarar un solo `organization_id` explícito).

### Audit Log

Cada petición debe registrar:

- `caller_id`
- `organization_id`
- `dry_run`
- `max_items`
- Timestamp
- Resultado (scanned, released, failed, etc.)
- Si ocurrió error, detalles a nivel de job sin exponer secretos.

### Aislamiento de Router

- Debe montarse en una sub-app FastAPI separada (e.g., `app.mount("/internal/admin", admin_router)`) o en un prefijo que el proxy inverso (nginx/Caddy) pueda bloquear para tráfico externo.
- Debe tener su propio middleware de autenticación, independiente del `require_write_permission` de la API pública.
- No debe aparecer en la documentación OpenAPI pública.

## Contrato De Scheduler Futuro

El siguiente contrato describe un scheduler futuro sin implementarlo.

### Frecuencia Recomendada

- Intervalo inicial: cada 5 minutos.
- `max_items` por tick: `50`.
- Ajustable por configuración, no por payload.

### Evitar Solapamiento

- Usar `pg_advisory_lock` con una key determinista (e.g., `hash("reconcile_cancelled_credits:<organization_id>")`).
- Si el lock no se obtiene en `N` segundos, saltar ese tick y loguear.
- No esperar indefinidamente.

### Lock Operacional

- Cada tenant debe tener su propio lock para que la reconciliación de un tenant no bloquee la de otro.
- Si se ejecuta batch global (todas las organizaciones), cada tenant debe procesarse secuencialmente o con lock independiente por tenant.
- Dos réplicas del scheduler no deben poder ejecutar el mismo tenant simultáneamente.

### Métricas por Tick

- `scanned_count`, `processed_count`, `released_count`, `skipped_count`, `failed_count`.
- `duration_seconds`.
- `dry_run` (flag, no métrica de health).
- `organization_id` como tag/label.
- `tick_timestamp`.
- Error categories como contadores.

### Retry y Backoff

- Si el tick falla completamente (no parcial), reintentar con backoff exponencial: `1 min, 2 min, 4 min, 8 min, max 1 hour`.
- Si el tick tiene `failed_count > 0` pero completó el escaneo, no reintentar automáticamente; loguear y alertar.
- `terminal_error` en per-job no debe reintentarse; requiere inspección operativa.

### Kill Switch

- Configuración remota (variable de entorno o flag en DB) para deshabilitar el scheduler globalmente o por tenant.
- Si está deshabilitado, el scheduler debe loguear "disabled" y saltar sin ejecutar.

### Modo Dry-Run / Monitoring

- El scheduler debe soportar un modo "monitoring" donde ejecuta la selección sin llamar al release y loguea los candidatos.
- Esto permite validar la configuración antes de activar releases automáticos.

## Tenant Boundary

- La primera versión operativa (CLI) debe ser per-tenant: `--organization-id` obligatorio.
- Ningún mecanismo (CLI, endpoint, scheduler) debe aceptar `organization_id` desde un contexto no confiable.
- El batch global (sin `organization_id`) es aceptable **sólo** como modo interno privilegiado, y debe:
  - Recibir una lista explícita de organizaciones desde configuración interna o discovery controlado.
  - Procesar cada organización de forma aislada.
  - Reportar resultados agregados sin mezclar contadores entre tenants.
  - No exponer datos cross-tenant.
- Cada ejecución (independientemente del trigger) debe registrar `organization_id`.
- Todos los resultados por job deben mantener `organization_id` correcto.

## Idempotencia Y Concurrencia

Garantías existentes:

- `process_cancelled_ai_job_credit_releases(...)` ya es idempotente por job.
- `release_entry_id` es prueba primaria de settlement previo.
- El ledger rechaza doble settlement para la misma `reservation_entry_id`.
- El caller key determinista `cancel:<reservation_entry_id>` evita duplicados contables.

Riesgos operacionales:

| Situación | Riesgo | Mitigación |
|---|---|---|
| CLI duplicada por error del operador | Bajo | El servicio es idempotente; rerun cuenta `idempotent_replay`. |
| Scheduler + CLI simultáneos | Medio | `get_for_update` serializa por job; el perdedor continúa sin doble release. |
| Dos schedulers mismos parámetros | Medio | Lock operacional por organización. |
| Endpoint admin duplicado | Bajo | Idempotencia del servicio; rate limit evita ráfagas. |
| CLI durante ventana de scheduler | Medio | Lock operacional recomendado; sin lock, `get_for_update` protege cada job pero ambos procesan la misma lista de candidatos (el segundo encuentra todo ya `released` o skip). |

Recomendación: no implementar scheduler sin lock operacional probado. La CLI y el endpoint admin pueden coexistir sin lock porque la idempotencia del servicio los hace seguros, aunque ineficientes (el segundo procesa jobs que el primero ya liberó).

## Observabilidad

### Logs por Ejecución (Trigger-Independiente)

Toda ejecución debe loguear:

- `trigger_type`: `"cli"`, `"admin_endpoint"`, `"scheduler"`.
- `organization_id`.
- `dry_run`.
- `max_items`.
- `scanned_count`, `processed_count`, `released_count`, `skipped_count`, `failed_count`.
- `duration_seconds`.
- `requested_by`.
- `exit_code` o `http_status`.

### Logs por Job

- `job_id`.
- `organization_id`.
- `reservation_entry_id`.
- `release_entry_id`.
- `status_before`, `status_after`.
- `release_performed`.
- `idempotent`.
- `error_category`.

### Métricas

| Métrica | Tags | Descripción |
|---|---|---|
| `reconcile.jobs.scanned` | `org` | Jobs vistos por selector |
| `reconcile.jobs.released` | `org` | Releases realizados |
| `reconcile.jobs.idempotent` | `org` | Replays idempotentes |
| `reconcile.jobs.skipped` | `org`, `category` | Skips por categoría |
| `reconcile.jobs.failed` | `org`, `category` | Fallos por categoría |
| `reconcile.duration` | `org`, `trigger` | Duración del batch |
| `reconcile.errors` | `org`, `category` | Errores inesperados |

### No Loguear

- Secretos, tokens, API keys.
- Headers completos de request.
- Payloads privados de usuario.
- Prompts completos.
- Metadata sensible de assets o proyectos.

## Seguridad Y Permisos

- Sólo operadores/admin internos pueden ejecutar la reconciliación.
- Usuarios de proyecto normales (cliente público) no deben tener acceso.
- El principio de mínimo privilegio aplica: el trigger debe ejecutarse con el rol de base de datos mínimo necesario para la operación.
- Auditoría de quién ejecutó:
  - CLI: `--requested-by` obligatorio o derivado del usuario del sistema.
  - Endpoint admin: `caller_id` del token de autenticación admin.
  - Scheduler: `requested_by = "scheduler"`.
- Trazabilidad: `requested_by` debe propagarse a `AIJobAsyncCancelCreditReleaseReconciliationRequest.requested_by`.

## Failure Model

### Fallo Parcial

- `failed_count > 0` no debe ocultarse.
- CLI exit code no cero si `failed_count > 0`.
- Endpoint admin debe devolver HTTP `200` (la operación se completó) con `failed_count > 0` en body, pero el monitor de health debe alertar.
- Scheduler: loguear y alertar; no reintentar automáticamente el mismo batch.

### Retry Manual Seguro

- La idempotencia del servicio garantiza que rerun es seguro.
- El operador puede retry con los mismos parámetros sin riesgo de doble settlement.
- `dry_run` disponible para verificar estado antes de rerun.

### Errores No Recuperables

- `unexpected_error`: requiere inspección; no reintentar automáticamente.
- `terminal_error` (e.g., `AIJobAsyncAccountingError`): no debe reintentarse ciegamente; requiere revisión de ledger.
- `skipped_consumed`: indica que el job fue consumido después de la cancelación; es esperado y no requiere acción.

## Relación Con API Pública

- `POST /api/v1/ai-jobs/{job_id}/cancel` sigue siendo sólo intención de cancelación.
- No debe añadir flags `release_credits`, `release_pending`, `release_required` ni ningún campo que permita a un cliente forzar release.
- No debe exponer `process_cancelled_ai_job_credit_releases(...)` directa ni indirectamente.
- El cliente no debe poder saber si un job tiene créditos reservados pendientes de release.
- La existencia de la reconciliación interna es un detalle de implementación; no debe mencionarse en la documentación de API pública.

## Tests Requeridos Para Futura Implementación

### CLI

- `--organization-id` obligatorio; error si falta.
- `--dry-run` lista candidatos sin mutar ni llamar ledger.
- `--max-items` respeta cap máximo y floor.
- `--max-items` default correcto.
- Salida JSON contiene todos los campos del resultado.
- Exit code `0` si `failed_count == 0`.
- Exit code `1` si `failed_count > 0`.
- Exit code `2` si parámetros inválidos.
- Llama `process_cancelled_ai_job_credit_releases(...)` con la `organization_id` correcta.

### Admin Endpoint

- Rechaza callers sin rol admin/operator.
- Rechaza `organization_id` que no corresponda al contexto autenticado.
- Rechaza campos extra no permitidos (extra="forbid").
- Acepta `dry_run`.
- Rate limit aplica.
- Audit log registra caller, org, resultado.
- No aparece en OpenAPI pública.

### Scheduler

- No solapa ejecuciones por `organization_id` cuando lock operacional está activo.
- Salta tick si lock no se obtiene.
- Respeta `max_items` por tick.
- Backoff exponencial en fallo completo.
- Kill switch deshabilita ejecución.
- Modo monitoring no llama release.
- Métricas registradas correctamente.

## Riesgos

| Riesgo | Severidad | Mitigación |
|---|---|---|
| Exposición accidental de endpoint admin a Internet | Alta | Router aislado, proxy inverso bloquea `/internal/`, revisión de security scan. |
| Batch global sin control tenant | Alta | `organization_id` obligatorio en CLI; endpoint admin rechaza payload sin org; scheduler itera por tenant con lock individual. |
| Doble ejecución concurrente sin lock | Media | Idempotencia del servicio protege contra doble settlement; ineficiencia aceptable en CLI, mitigación con lock en scheduler. |
| Falta de observabilidad: release falla silenciosamente | Alta | Métricas y logs por tick; exit code no cero en CLI; health check en endpoint admin. |
| Dependencia manual indefinida | Media | CLI como primera fase; scheduler planificado como Phase 5B. |
| Scheduler sin lock operacional | Alta | No implementar scheduler hasta tener lock probado. |
| Endpoint admin sin permisos fuertes | Alta | No implementar endpoint admin sin middleware de autenticación admin independiente. |
| Mezclar release con cancel HTTP público | Crítica | Prohibido por contrato; el endpoint público cancel no debe llamar release ni reconciliación. |

## Próxima Fase Recomendada

Se proponen dos caminos:

### Opción 1: Contrato CLI Detallado

```text
CID.SAAS.AI.JOB.CANCELLATION.CREDIT.RELEASE.OPERATIONAL.CLI.CONTRACT.AUDIT.1
```

Refinar el contrato de la CLI antes de implementar: revisar parámetros, salida, exit codes y seguridad.

### Opción 2: Implementación CLI Directa

```text
CID.SAAS.AI.JOB.CANCELLATION.CREDIT.RELEASE.OPERATIONAL.CLI.PHASE5A.IMPLEMENTATION.1
```

Implementar la CLI interna sin scheduler, sin endpoint admin, sin cambios en API pública.

**Recomendación personal**: Opción 2 si el contrato actual se considera suficientemente detallado. Opción 1 si hay dudas sobre la interfaz CLI, la localización del script (`scripts/`, `src/scripts/`, `src/commands/`) o la convención de exit codes.

Esta fase no implementa CLI, endpoint, scheduler, worker, cola ni ningún cambio de runtime.
