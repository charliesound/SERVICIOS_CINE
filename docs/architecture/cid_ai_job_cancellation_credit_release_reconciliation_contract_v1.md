# CID AI Job Cancellation Credit Release Reconciliation Contract v1

## Estado

- Basado en HEAD `c2a3f60` (`test: harden CID AI job mock worker cancellation guard`).
- Documento previo a implementación.
- No cambia runtime.
- Define la futura operación interna/batch de reconciliación de releases pendientes.
- PostgreSQL-only.

## Problema

Ya existen las piezas principales para la cancelación segura de AI Jobs con créditos reservados:

- La API pública `POST /api/v1/ai-jobs/{job_id}/cancel` sólo expresa intención de cancelación.
- `AIJobAsyncOrchestrationService.request_cancel_ai_job(...)` marca `cancelled` o `cancel_requested` según el estado real del job.
- `AIJobAsyncOrchestrationService.release_cancelled_ai_job_reserved_credits(...)` libera créditos reservados de cancelación de forma tenant-scoped e idempotente.
- El guard del worker/mock impide ejecutar o consumir jobs en `cancel_requested`, `cancelled`, `release_pending` y `released`.
- El ledger valida que consume y release sean settlements mutuamente excluyentes por `reservation_entry_id`.

Falta una operación interna de reconciliación que localice jobs cancelados con reservas pendientes y ejecute el release de forma segura, reintentable y observable, sin depender de un request HTTP de usuario.

## Principio Principal

La reconciliación debe ser interna, tenant-safe, idempotente y no controlada por cliente.

Ningún payload público debe poder forzar release, elegir amount, elegir tenant, elegir idempotency key contable o saltarse la validación de estado real bajo lock.

## Operación Futura Propuesta

Nombre recomendado:

```text
process_cancelled_ai_job_credit_releases(...)
```

Ubicación futura recomendada:

- Servicio interno nuevo o método interno de orquestación, no ruta pública.
- Puede vivir junto a `AIJobAsyncOrchestrationService` si se mantiene pequeño, o en un servicio de reconciliación especializado si aparece lógica de selección/batch más amplia.

Inputs contractuales:

- `organization_id`: recomendado como obligatorio para modo tenant-scoped. Un modo global sólo debe existir para proceso interno privilegiado y debe seguir agrupando resultados por tenant.
- `max_items`: límite máximo de jobs a procesar por ejecución.
- `dry_run`: recomendado para inspección; si es `true`, no debe llamar al release interno ni mutar jobs.
- `statuses`: opcional y restringido a estados elegibles; por defecto debe usar el set seguro del contrato.
- `job_ids`: opcional para reparación interna dirigida, siempre validada por `organization_id`.
- `requested_by`: opcional para auditoría interna, no derivado de cliente público.
- `reason`: opcional para auditoría interna segura.

Límites recomendados:

- `max_items` debe tener un valor por defecto conservador.
- Debe existir un límite superior duro para evitar transacciones o recorridos demasiado largos.
- El selector no debe cargar payloads grandes ni metadata sensible innecesaria.

Retorno resumido recomendado:

- `scanned_count`
- `processed_count`
- `released_count`
- `skipped_count`
- `failed_count`
- `dry_run`
- `per_job_results`

Retorno por job recomendado:

- `job_id`
- `organization_id`
- `status_before`
- `status_after`
- `reservation_entry_id`
- `release_entry_id`
- `release_performed`
- `idempotent`
- `error_category`
- `message`

Esta fase no implementa la operación.

## Selector De Candidatos

El selector futuro debe incluir sólo jobs que cumplan todos los criterios seguros:

- `status` en `cancel_requested`, `cancelled` o `release_pending`.
- `reservation_entry_id` presente.
- `consume_entry_id` ausente.
- `release_entry_id` ausente.
- `consumed_credits == 0`.
- `reserved_credits > 0`.
- `organization_id` controlado por contexto interno confiable.

Estados incluidos:

- `cancel_requested`: elegible sólo porque el servicio interno actual lo acepta; el batch debe revalidar bajo lock y asumir que puede representar cancelación cooperativa pendiente.
- `cancelled`: elegible si mantiene `reservation_entry_id` y no tiene settlement de release/consume.
- `release_pending`: elegible para retry/reconciliación de release.

Estados excluidos:

- `created`
- `estimated`
- `credit_checked`
- `reserved`
- `queued`
- `running`
- `succeeded`
- `partial_succeeded`
- `failed`
- `consume_pending`
- `consumed`
- `released`
- `retry_pending`
- `expired`

Razones de exclusión principales:

- Sin reserva: no hay nada que liberar.
- No cancelado: no pertenece al camino de release por cancelación.
- Consume requerido o completado: no liberar créditos consumidos.
- Release ya completado: no duplicar settlement.
- Fallo/expiración: pertenecen a caminos de release distintos, no a cancelación.

No se implementan queries en esta fase.

## Tenant Boundary

Modo recomendado inicial:

- Procesamiento por `organization_id` explícita interna.

Modo global interno futuro:

- Permitido sólo para proceso interno privilegiado.
- Debe aplicar filtros por `organization_id` en cada job.
- Debe pasar el `organization_id` real y confiable a `release_cancelled_ai_job_reserved_credits(...)`.
- Debe registrar resultados agrupados por tenant.
- No debe mezclar resultados de tenants de forma que oculte errores o leakage.

Reglas:

- Nunca confiar en `organization_id` proveniente de cliente público.
- Cada llamada a `release_cancelled_ai_job_reserved_credits(...)` debe usar `organization_id + job_id`.
- Un job que no pertenece al tenant indicado debe producir resultado terminal tipo `job_not_found` o `tenant_mismatch` interno, sin filtrar existencia cross-tenant a superficies públicas.
- Logs y métricas deben incluir `organization_id`, pero no payload sensible.

## Locking Y Transacciones

El selector no debe bloquear muchas filas durante demasiado tiempo.

Patrón recomendado:

1. Seleccionar ids candidatos con filtros baratos, índice por `organization_id` y `status`, y `max_items`.
2. Procesar cada job con unidad transaccional clara.
3. Para cada job, llamar a `release_cancelled_ai_job_reserved_credits(...)`, que carga el job por `repository.get_for_update(organization_id, job_id)`.
4. Revalidar estado real y campos contables bajo lock.
5. Persistir resultado o error por job.

Orden de locks:

- Primero seleccionar ids sin sostener locks largos.
- Luego tomar lock del job específico.
- Dejar que el servicio interno y ledger validen la reserva y settlement.

Comportamiento ante job bloqueado:

- No esperar indefinidamente.
- Clasificar como retryable si el lock no se obtiene o hay timeout/deadlock.
- Continuar con otros jobs si el modo batch define continuar ante fallo por item.

Transacciones:

- Preferir transacción por job o lote pequeño explícito.
- Evitar una transacción única para todo el batch si puede mantener locks prolongados.
- No mezclar selección global, ledger settlement y auditoría de muchos jobs en una transacción larga.

## Idempotencia

La reconciliación debe ser segura ante rerun.

Garantías existentes que debe reutilizar:

- `release_entry_id` en `AIJob` es prueba primaria de settlement previo.
- `release_cancelled_ai_job_reserved_credits(...)` usa caller key determinista `cancel:<reservation_entry_id>`.
- `DuplicateIdempotencyKeyError` con `existing_entry_id` se reconcilia como replay idempotente.
- Duplicate idempotency sin `existing_entry_id` se transforma en error controlado.
- El ledger evita doble settlement de una misma reserva.
- El balance no debe mutar dos veces para el mismo release.

Reglas de reconciliación:

- Rerun sobre job ya `released` debe saltarse antes de llamar ledger.
- Rerun sobre job con `release_entry_id` debe clasificarse como `skipped_already_released` o `idempotent_replay` según se llame o no al servicio interno.
- Rerun sobre duplicate ledger válido debe contar como `idempotent_replay`.
- Job con `consume_entry_id` o `consumed_credits > 0` debe clasificarse como `skipped_consumed` o error terminal equivalente.
- Job sin `reservation_entry_id` debe clasificarse como `skipped_no_reservation`.
- Nunca aceptar `release_credits` desde input del batch para cancel-release.

## Categorías De Error Y Resultado

Categorías recomendadas:

- `released`: estado final ya liberado al observarlo.
- `skipped_no_reservation`: no existe reserva vinculada.
- `skipped_already_released`: `release_entry_id` ya existe o estado `released` ya está persistido.
- `skipped_consumed`: `consume_entry_id` existe o `consumed_credits > 0`.
- `skipped_not_eligible`: estado o campos no cumplen el contrato.
- `released_now`: el batch llamó release interno y creó settlement nuevo.
- `idempotent_replay`: el batch convergió sobre release ya existente sin mutar doble.
- `retryable_ledger_error`: fallo transitorio de gateway/ledger/DB antes de settlement verificable.
- `terminal_accounting_error`: inconsistencia contable no segura para retry automático.
- `unexpected_error`: error no clasificado que debe alertar.

Mapeo orientativo:

| Situación | Categoría |
|---|---|
| Release nuevo exitoso | `released_now` |
| Duplicate idempotency con `existing_entry_id` | `idempotent_replay` |
| Job sin `reservation_entry_id` | `skipped_no_reservation` |
| Job con `release_entry_id` | `skipped_already_released` |
| Job con consume persistido | `skipped_consumed` |
| Estado fuera de `cancel_requested`, `cancelled`, `release_pending` | `skipped_not_eligible` |
| Duplicate idempotency sin existing id | `terminal_accounting_error` |
| Timeout/deadlock/transient gateway | `retryable_ledger_error` |
| Excepción no clasificada | `unexpected_error` |

## Resultado Esperado

Objeto futuro recomendado:

```text
AIJobCancelCreditReleaseReconciliationResult
```

Campos de resumen:

- `scanned_count`
- `processed_count`
- `released_count`
- `skipped_count`
- `failed_count`
- `dry_run`
- `per_job_results`

Objeto por job recomendado:

- `job_id`
- `organization_id`
- `status_before`
- `status_after`
- `reservation_entry_id`
- `release_entry_id`
- `release_performed`
- `idempotent`
- `error_category`
- `message`

Semántica de contadores:

- `scanned_count`: jobs vistos por selector.
- `processed_count`: jobs sobre los que se intentó decisión bajo contrato.
- `released_count`: `released_now` más replays idempotentes que dejan estado released, si el contrato de métricas decide contarlos como liberados.
- `skipped_count`: no elegibles o ya resueltos.
- `failed_count`: errores retryables o terminales.

## Observabilidad

Logs mínimos por ejecución:

- `scanned_count`
- `processed_count`
- `released_count`
- `skipped_count`
- `failed_count`
- duración total
- modo `dry_run`
- `max_items`

Logs mínimos por job:

- `organization_id`
- `job_id`
- `reservation_entry_id`
- `release_entry_id`
- `status_before`
- `status_after`
- `release_performed`
- `idempotent`
- `error_category`
- duración por job si está disponible

Métricas recomendadas:

- Jobs escaneados.
- Releases realizados.
- Replays idempotentes.
- Skips por categoría.
- Fallos por categoría.
- Timeouts/deadlocks.
- Duración de batch.

No loguear:

- Secretos.
- Tokens.
- Headers completos.
- Payloads privados.
- Prompts completos.
- Metadata sensible de usuario o assets.

## API/Admin Boundary

No debe existir endpoint público para esta reconciliación.

Opciones futuras aceptables:

- CLI interna.
- Operación admin-only interna.
- Scheduler interno.

Si se implementa endpoint admin futuro:

- Debe ser permission-gated.
- Debe ser tenant-safe.
- Debe auditar caller interno/admin.
- No debe aceptar `release_credits` arbitrario.
- No debe aceptar flags equivalentes para forzar release desde cliente público.
- Debe delegar en la operación de reconciliación y esta a su vez en `release_cancelled_ai_job_reserved_credits(...)`.

La ruta pública `POST /api/v1/ai-jobs/{job_id}/cancel` debe seguir sin llamar a la reconciliación ni al release interno.

## Relación Con Worker/Mock Guard

El guard actual del worker/mock bloquea ejecución y settlement de success/failure cuando el job está en:

- `cancel_requested`
- `cancelled`
- `release_pending`
- `released`

Ese guard reduce el riesgo de consume tras cancelación, pero no sustituye la reconciliación.

La reconciliación debe asumir que todavía puede haber carreras:

- Un proceso de ejecución antiguo puede haber leído estado antes del guard.
- Un settlement de consume puede ganar la carrera antes de que el release tome lock.
- Un job puede cambiar de estado entre selección y procesamiento.

Por eso el batch debe validar estado real bajo lock y dejar que el ledger preserve settlement único por `reservation_entry_id`.

## Tests Requeridos Para Próxima Implementación

Tests mínimos de selector:

- Selector incluye sólo `cancel_requested`, `cancelled` y `release_pending` elegibles.
- Selector excluye `consumed`.
- Selector excluye `released`.
- Selector excluye jobs sin `reservation_entry_id`.
- Selector excluye `consume_entry_id` presente.
- Selector excluye `release_entry_id` presente.
- Selector excluye `consumed_credits > 0`.
- Selector respeta `organization_id`.
- Selector respeta `max_items`.

Tests mínimos de batch:

- Batch llama `release_cancelled_ai_job_reserved_credits(...)` una vez por job elegible.
- Un fallo en un job no aborta todo el batch si el contrato decide continuar.
- Duplicate replay se contabiliza como `idempotent_replay`.
- Gateway error queda como `retryable_ledger_error`.
- Duplicate sin `existing_entry_id` queda como `terminal_accounting_error`.
- Batch rerun no duplica ledger.
- `dry_run` no llama release ni muta jobs.
- Resultado resume `scanned_count`, `processed_count`, `released_count`, `skipped_count` y `failed_count`.
- `per_job_results` conserva `job_id`, `organization_id`, estados, `release_entry_id`, flags y categoría.

Tests mínimos de boundary:

- Tenant boundary por `organization_id`.
- Public cancel route sigue sin flags de release.
- Public cancel route sigue sin llamar worker/reconciliación/release interno.
- Worker/mock guard sigue pasando para estados protegidos.

Tests mínimos de concurrencia PostgreSQL:

- Dos reconciliadores no crean doble release para una reserva.
- Consume concurrente y release concurrente producen un solo settlement ganador.
- El perdedor recibe categoría controlada.
- `reserved_active` no muta dos veces.

## Riesgos

- Doble settlement si se bypassa `release_cancelled_ai_job_reserved_credits(...)`.
- Release después de consume si el selector no revalida bajo lock.
- Batch global sin tenant boundary explícito.
- Transacciones demasiado largas que mantengan locks y degraden otros workers.
- Acoplar admin/reconciliación a API pública.
- Ausencia de scheduler maduro para retry automático.
- Falta de observabilidad de retries y errores terminales.
- Clasificar `cancel_requested` como liberable antes de que la ejecución haya dejado de poder consumir.
- Exponer `release_credits` o idempotency keys al caller.

## Próxima Fase Recomendada

Próxima implementación pequeña recomendada:

```text
CID.SAAS.AI.JOB.CANCELLATION.CREDIT.RELEASE.RECONCILIATION.SERVICE.PHASE4B.IMPLEMENTATION.1
```

Alcance recomendado para esa fase:

- Implementar operación interna/batch sin scheduler real.
- Mantener API pública sin cambios.
- Usar exclusivamente `release_cancelled_ai_job_reserved_credits(...)` para settlement por cancelación.
- Empezar por modo tenant-scoped con `organization_id` explícita.
- Incluir `dry_run` si no aumenta el scope de forma significativa.
- Añadir tests unitarios de selector, resultado, idempotencia y errores.
- Añadir pruebas PostgreSQL de concurrencia antes de automatizar ejecución periódica.

Esta fase no implementa nada de lo anterior.
