# CID AI Job Cancellation Worker Release Path Contract v1

## Estado

- Basado en HEAD `24f89e6` (`docs: add CID AI job cancellation credit release orchestration contract`).
- Documento previo a implementación.
- No cambia runtime.
- Define el futuro camino interno para procesar cancelaciones pendientes y liberar créditos de forma segura.
- PostgreSQL-only.

## Problema

La cancelación pública y el release interno ya existen como piezas separadas:

- Endpoint público: `POST /api/v1/ai-jobs/{job_id}/cancel`.
- Servicio de cancelación: `AIJobAsyncOrchestrationService.request_cancel_ai_job(...)`.
- Servicio interno de release: `AIJobAsyncOrchestrationService.release_cancelled_ai_job_reserved_credits(...)`.

Falta definir el componente interno que detectará trabajos cancelados o pendientes de release y ejecutará `release_cancelled_ai_job_reserved_credits(...)` sin depender del request HTTP. Ese componente debe evitar doble settlement, respetar el tenant boundary, no consumir trabajos cancelados y dejar un camino de retry seguro ante errores parciales.

## Principio Principal

El cliente nunca debe controlar el release.

El worker/background path debe ser:

- Tenant-safe.
- Idempotente.
- Auditable.
- Reintentable.
- Basado en estado persistido y no en flags de payload público.
- Compatible con settlement mutualmente excluyente entre consume y release.

## Estados De Entrada

Estados reales relevantes definidos en `src/services/ai_job_status_service.py`:

### Debe Procesar

El worker/background path de release por cancelación debe considerar candidatos en:

- `cancel_requested`: cancelación solicitada para un job reservado, en cola o en ejecución. Requiere confirmar que la ejecución no va a consumir antes de liberar.
- `release_pending`: release requerido o en progreso; estado natural para retries.
- `cancelled` con `reservation_entry_id` presente y `release_entry_id` ausente: compatible con el flujo actual si un job ya quedó cancelado pero aún no liquidado.

### Debe Ignorar O Rechazar

El worker/background path de release por cancelación debe ignorar o rechazar:

- `created`: no hay reserva que liberar.
- `estimated`: no hay reserva que liberar.
- `credit_checked`: no hay reserva que liberar.
- `reserved`: todavía no hay intención de cancelación.
- `queued`: ejecutable, pero no cancelado.
- `running`: ejecución activa o no finalizada.
- `succeeded`: pertenece al camino de consume.
- `partial_succeeded`: pertenece al camino de consume.
- `failed`: pertenece al camino genérico de release por fallo, no al release por cancelación.
- `consume_pending`: consume en curso o requerido.
- `consumed`: settlement de consumo ya completado.
- `released`: settlement de release ya completado.
- `retry_pending`: política de retry de ejecución, no de release por cancelación.
- `expired`: pertenece al camino de expiración, no al release por cancelación.

Gap actual: `release_cancelled_ai_job_reserved_credits(...)` acepta `cancel_requested`, `cancelled` y `release_pending`. El worker futuro debe decidir si procesa `cancel_requested` directamente o si primero exige una finalización explícita de ejecución cancelada. Para `running`, el contrato más seguro es no liberar hasta que la ejecución haya dejado de poder consumir.

## Criterios De Selección

El selector futuro de candidatos debe estar definido por contrato antes de escribir queries.

Debe incluir sólo jobs que cumplan:

- `organization_id` acotado por tenant o contexto interno confiable.
- `status` en `cancel_requested`, `cancelled` o `release_pending`.
- `reservation_entry_id` presente.
- `consume_entry_id` ausente.
- `release_entry_id` ausente.
- `consumed_credits == 0`.
- `reserved_credits > 0`.

Debe excluir:

- Jobs sin reserva.
- Jobs con consume ya persistido.
- Jobs con release ya persistido.
- Jobs fuera del `organization_id` autorizado para el proceso.
- Jobs en estados de éxito, fallo no cancelatorio, expiración o retry de ejecución.

Retry y batch, cuando existan, deben respetar:

- Ventanas de retry para evitar loops apretados sobre errores transitorios.
- Límite de batch fijo y auditable.
- Orden estable por antigüedad o prioridad definida.
- Procesamiento por job aislado para que un error no mantenga locks largos sobre todo el lote.

No se implementan queries en esta fase.

## Operación Interna

Nombre recomendado para la operación futura:

```text
process_cancelled_ai_job_credit_releases(...)
```

Responsabilidades:

- Recibir contexto interno confiable, no payload público.
- Seleccionar candidatos tenant-scoped o procesar una lista tenant-scoped validada.
- Cargar cada job con lock antes de decidir.
- Revalidar estado y campos contables después del lock.
- Llamar a `release_cancelled_ai_job_reserved_credits(...)` como única ruta de release por cancelación.
- No duplicar lógica de ledger.
- No construir releases parciales desde input externo.
- Registrar resultado por job.
- Continuar con el siguiente job cuando el contrato de batch decida que el error de un job no aborta todo el lote.
- Dejar retry seguro ante error transitorio.

Resultado mínimo por job:

- `job_id`.
- `organization_id`.
- Estado antes y después.
- Si se realizó release.
- Si fue replay/idempotente.
- `release_entry_id` si existe.
- Categoría de error si falló.
- Indicador retryable/terminal.

## Transacciones Y Locking

El release por cancelación debe apoyarse en locks de fila y settlement transaccional.

Requisitos:

- Usar `repository.get_for_update(organization_id, job_id)` o equivalente para mutar un job.
- Mantener la decisión final y la llamada al servicio interno dentro de una unidad transaccional clara por job.
- Evitar mezclar demasiados jobs en una transacción larga.
- Preferir una transacción por job o grupos pequeños con límites explícitos.
- Revalidar `status`, `reservation_entry_id`, `consume_entry_id`, `release_entry_id`, `consumed_credits` y `reserved_credits` después de tomar el lock.
- No hacer read-modify-write sólo desde un adapter HTTP.
- No mantener locks mientras se hacen tareas ajenas al settlement del job.

Orden de locks recomendado:

1. Seleccionar ids candidatos con filtros tenant-scoped y límite de batch.
2. Para cada candidato, tomar lock del `AIJob`.
3. Revalidar elegibilidad.
4. Ejecutar release interno, que a su vez valida ledger/reservation linkage.
5. Persistir `release_entry_id`, `released_credits` y estado final.

Comportamiento ante job bloqueado por otro proceso:

- No esperar indefinidamente.
- Saltar o fallar ese job como retryable, según la capacidad transaccional que se implemente.
- Registrar diagnóstico mínimo sin exponer payload sensible.

Comportamiento ante worker de ejecución intentando consumir a la vez:

- Consume y release son settlement mutuamente excluyente por `reservation_entry_id`.
- El worker de ejecución debe revalidar que el job no está en `cancel_requested`, `cancelled` o `release_pending` antes de consumir.
- Si consume gana la carrera, el release por cancelación debe fallar como terminal para esa reserva.
- Si release gana la carrera, un consume posterior debe fallar como conflicto de estado/ledger.

## Idempotencia

El worker/background path debe ser seguro ante rerun.

Reglas:

- El mismo `reservation_entry_id` debe producir el mismo `caller_key` interno: `cancel:<reservation_entry_id>`.
- `release_entry_id` es prueba primaria de settlement previo en el `AIJob`.
- Si `release_entry_id` ya existe, no llamar de nuevo al ledger.
- Si el ledger devuelve duplicate idempotency con `existing_entry_id`, reconciliar mediante el servicio interno y persistir el entry id.
- Si no hay `reservation_entry_id`, tratar como no-op idempotente.
- Si el job ya está `released`, tratar como no-op siempre que `release_entry_id` esté presente.
- Si el job tiene `consume_entry_id` o `consumed_credits > 0`, nunca convertir el caso en release.
- No aceptar amount ni idempotency key desde cliente para este camino.

No debe existir doble release porque:

- El job se bloquea con `get_for_update`.
- La operación usa `release_cancelled_ai_job_reserved_credits(...)`.
- El ledger valida settlement único por `reservation_entry_id`.
- El caller key interno es determinístico.

## Errores Y Retry

Categorías esperadas:

| Categoría | Ejemplo | Retry | Resultado esperado |
|---|---|---|---|
| `job_not_found` | El job ya no existe o no corresponde al tenant | Terminal para ese item | Registrar y continuar. |
| `tenant_mismatch` | `organization_id` no coincide | Terminal y alerta si proviene de selector interno | No filtrar existencia cross-tenant. |
| `ineligible_state` | Estado no permitido para release por cancelación | Terminal salvo cambio posterior de estado | No llamar ledger. |
| `consumption_detected` | `consume_entry_id` presente o `consumed_credits > 0` | Terminal | No liberar créditos consumidos. |
| `duplicate_without_existing_entry` | Duplicate idempotency sin `existing_entry_id` | No automático | Registrar inconsistencia contable y alertar. |
| `ledger_or_gateway_failure` | Error del gateway contable | Retryable si no hay `release_entry_id` | Mantener estado retryable. |
| `db_timeout_or_transient` | Timeout, deadlock, conexión transitoria | Retryable | Reintentar con backoff. |
| `unexpected_error` | Excepción no clasificada | Retryable limitado y alerta | No marcar release exitoso. |

Cuándo dejar `release_pending`:

- Si el job ya estaba en `release_pending` y falla el ledger antes de `release_entry_id`.
- Si el worker futuro decide mover `cancelled -> release_pending` antes del release y luego ocurre un fallo transitorio.

Cuándo no mover a otro estado:

- No inventar estados nuevos.
- `retry_pending` existe, pero pertenece al retry de ejecución y no debe reutilizarse automáticamente para errores de release por cancelación sin nuevo contrato.
- Si los estados actuales no bastan para distinguir retries contables, el gap debe documentarse antes de modificar modelos.

Diagnóstico mínimo:

- Categoría de error.
- Job y tenant afectados.
- Estado antes/después.
- Si se llamó o no al ledger.
- Si el error es retryable.
- Conteo de intentos sólo si existe o se agrega en una fase futura.

## Observabilidad

Logs mínimos por job:

- `job_id`.
- `organization_id`.
- `reservation_entry_id`.
- `release_entry_id`.
- `status_before`.
- `status_after`.
- `release_performed`.
- `idempotent`.
- `error_category`.
- `retryable`.
- `retry_count` si existe o se añade en una fase futura.

Métricas recomendadas:

- Candidatos escaneados.
- Jobs elegibles.
- Jobs liberados.
- Jobs idempotentes.
- Jobs saltados por estado.
- Jobs bloqueados por consumo.
- Errores retryables.
- Errores terminales.

No loguear:

- Secretos.
- Tokens.
- Headers completos.
- Payloads privados de usuario.
- Prompts completos o datos sensibles de assets.

## API Boundary

La ruta pública `POST /api/v1/ai-jobs/{job_id}/cancel`:

- No llama este worker directamente.
- No acepta `release_credits`.
- No acepta `release_pending`.
- No acepta `release_required`.
- No acepta `organization_id` en body ni query.
- No acepta flags equivalentes para forzar release.
- No expone endpoint público de release por cancelación.

Cualquier operación manual futura debe ser:

- Interna/admin-only.
- Tenant-safe.
- Auditable.
- Sin control de amount desde cliente público.
- Sin bypass de `release_cancelled_ai_job_reserved_credits(...)`.

## Relación Con Worker/Mock Actual

`src/services/ai_job_worker_mock_service.py` existe como executor backend-only de pruebas/operación mock con modos:

- `success`: encola, arranca, marca éxito, marca `consume_pending` y consume créditos.
- `failure`: encola, arranca, marca fallo, marca `release_pending` y llama `release_ai_job_credits(...)`.
- `cancel`: exige un job ya en `cancel_requested`, marca `cancelled`, marca `release_pending` y llama `release_ai_job_credits(...)`.

`src/services/ai_job_worker_mock_execution_service.py` envuelve ese worker con persistencia de `AIJobExecutionAttempt`, fingerprint e idempotencia por `execution_attempt_id`.

Auditoría del estado actual:

- El mock procesa AI Jobs ejecutables y settlements simulados.
- El modo `cancel` ya exige `cancel_requested` en V1.
- El modo `cancel` usa el release genérico `release_ai_job_credits(...)`, no el release interno específico de cancelación `release_cancelled_ai_job_reserved_credits(...)`.
- El modo `success` no debe consumir un job que ya esté `cancel_requested`, `cancelled` o `release_pending`; si el flujo actual aún no lo blinda, conviene implementar ese guard antes de automatizar release por cancelación.
- El wrapper de attempts protege replay de ejecución, pero no sustituye la idempotencia contable de release por cancelación.

Riesgos actuales a proteger con tests futuros:

- Worker/mock de éxito consumiendo un job con cancelación ya solicitada.
- Dos procesos intentando settle la misma reserva por consume y release.
- Modo `cancel` divergiendo del servicio `release_cancelled_ai_job_reserved_credits(...)`.
- Replay de attempt reconstruyendo resultado terminal sin validar estado contable más amplio.

Antes de un worker/background real, conviene hacer un guard pequeño para que ningún worker de ejecución consuma `cancel_requested` o `release_pending`.

## Estrategia Recomendada

Estrategia recomendada por seguridad y menor riesgo:

### Phase 4A: Guard Del Worker/Mock

Implementar primero un guard para que el worker/mock no consuma jobs en:

- `cancel_requested`
- `cancelled`
- `release_pending`
- `released`

Justificación:

- Reduce el riesgo de carrera consume-vs-release antes de automatizar el release.
- Es pequeño y verificable.
- No requiere scheduler ni cola.

### Phase 4B: Reconciliación Interna/Batch Sin Scheduler Real

Agregar una operación interna tipo `process_cancelled_ai_job_credit_releases(...)` que procese un batch explícito o selector interno controlado.

Justificación:

- Permite probar selección, locking, idempotencia y errores sin introducir una cola madura.
- Mantiene la ruta pública sin cambios.
- Reusa `release_cancelled_ai_job_reserved_credits(...)`.

### Phase 4C: Worker/Background Real O Scheduler

Conectar la operación batch a un worker/background real cuando haya garantías operativas suficientes.

Justificación:

- Evita acoplar release contable al request HTTP.
- Permite retry y observabilidad dedicados.
- Mantiene el control interno del release.

No se recomienda iniciar por un endpoint público ni por lógica de release dentro de la ruta pública de cancelación.

## Tests Requeridos Para Próxima Implementación

Tests mínimos de selector:

- El selector sólo incluye `cancel_requested`, `cancelled` y `release_pending` elegibles.
- El selector exige `reservation_entry_id` presente.
- El selector excluye `consume_entry_id` presente.
- El selector excluye `release_entry_id` presente.
- El selector excluye `consumed_credits > 0`.
- El selector aplica `organization_id` como tenant boundary.
- El selector respeta límite de batch.

Tests mínimos de batch/reconciliación:

- Batch no procesa jobs consumidos.
- Batch no duplica release en rerun.
- Job con `release_entry_id` se salta como idempotente.
- Error de gateway deja retry seguro sin `release_entry_id`.
- Un job fallido no aborta todo el batch si el contrato de batch decide continuar.
- Duplicate idempotency con `existing_entry_id` reconcilia.
- Duplicate idempotency sin `existing_entry_id` produce error controlado.
- Job sin reserva es no-op idempotente.

Tests mínimos de worker/mock:

- Worker/mock no consume `cancel_requested`.
- Worker/mock no consume `cancelled`.
- Worker/mock no consume `release_pending`.
- Modo `cancel` de worker/mock no bypassa reglas de cancel-release cuando se conecte al nuevo servicio.
- Replay de attempt terminal no llama de nuevo al worker.

Tests mínimos de API boundary:

- La API pública sigue rechazando `release_credits`.
- La API pública sigue rechazando `release_pending`.
- La API pública sigue rechazando `release_required`.
- La API pública sigue rechazando `organization_id` en body/query.
- La ruta pública cancel sigue sin llamar `release_cancelled_ai_job_reserved_credits(...)`.
- No aparece endpoint público de release por cancelación.

Tests mínimos de concurrencia PostgreSQL:

- Dos procesos de release para la misma reserva producen un solo `credit_release`.
- Consume y release concurrentes para la misma reserva producen un único settlement ganador.
- El perdedor recibe error controlado.
- `reserved_active` se decrementa una sola vez.
- Tenant mismatch no puede liberar reserva de otro tenant.

## Límites Explícitos

Esta fase no implementa:

- Worker real.
- Scheduler.
- Cola.
- Endpoint público.
- Endpoint interno/admin.
- Cambios de modelos.
- Cambios de rutas.
- Cambios de servicios.
- Cambios de tests.
- Cancellation attempts.
- Integración externa.

## Próxima Fase Recomendada

Siguiente fase pequeña recomendada:

```text
CID.SAAS.AI.JOB.CANCELLATION.WORKER.CANCELLED.GUARD.IMPLEMENTATION.1
```

Objetivo:

- Impedir que el worker/mock consuma jobs con cancelación ya solicitada o release en curso.
- Mantener API pública sin cambios.
- Añadir tests unitarios enfocados para `cancel_requested`, `cancelled` y `release_pending`.

Fase posterior recomendada:

```text
CID.SAAS.AI.JOB.CANCELLATION.CREDIT.RELEASE.RECONCILIATION.SERVICE.PHASE4.IMPLEMENTATION.1
```

Objetivo:

- Implementar operación interna/batch de reconciliación sin scheduler real.
- Reusar exclusivamente `release_cancelled_ai_job_reserved_credits(...)` para settlement por cancelación.
- Añadir tests de selector, idempotencia, error y concurrencia PostgreSQL.
