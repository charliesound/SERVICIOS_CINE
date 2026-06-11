# CID AI Job Cancellation Credit Release — Scheduler Locking Contract v1

## 1. Título y alcance

Este documento define el contrato futuro de locking anti-solape para el scheduler
interno que ejecuta la reconciliación de créditos reservados en AI Jobs cancelados.

**Qué es esta fase**: solo documentación. Define el diseño, la estrategia de locking,
los niveles de lock, la política de errores y los criterios de aceptación del locking
futuro.

**Qué NO es esta fase**:
- No implementa locks.
- No activa scheduler runtime.
- No añade endpoint admin, worker real, cola, cron ni startup hook.
- No modifica el adapter, la CLI, el orchestration service, el repository ni el ledger.
- No añade dependencias.
- No cambia modelos, rutas, frontend, Docker, Alembic ni tests.

## 2. Estado actual

Ya existen los siguientes componentes:

| Componente | Ubicación |
|------------|-----------|
| Adapter scheduler | `AIJobCancellationCreditReleaseSchedulerService.run_tick(...)` |
| Servicio de reconciliación | `AIJobAsyncOrchestrationService.process_cancelled_ai_job_credit_releases(...)` |
| CLI manual | `scripts/ops/reconcile_cancelled_ai_job_credit_releases.py` |
| Runbook CLI | `docs/operations/cid_cancelled_ai_job_credit_release_cli_runbook_v1.md` |
| Contrato scheduler | `docs/architecture/cid_ai_job_cancellation_credit_release_scheduler_contract_v1.md` |
| Contrato de disparo | `docs/architecture/cid_ai_job_cancellation_credit_release_operational_trigger_contract_v1.md` |

**No existe locking real todavía.** El adapter actual confía en la idempotencia del
servicio interno para evitar doble settlement, pero sin lock dos ticks pueden
procesar el mismo tenant simultáneamente, generando trabajo duplicado.

## 3. Problema que resuelve el locking

Sin locking, ocurren los siguientes problemas:

| Problema | Impacto |
|----------|---------|
| Dos procesos ejecutando el scheduler a la vez | Ambos procesan la misma lista de candidatos; el segundo encuentra todo ya liberado (idempotent). Ineficiente pero seguro. |
| Dos ticks solapados en el mismo proceso | El segundo tick itera tenants que el primero ya procesó. Trabajo duplicado sin valor. |
| Dos réplicas procesando el mismo tenant | Cada réplica escanea, procesa y commitea los mismos jobs. La idempotencia protege, pero duplica carga en DB y ledger. |
| Doble release intentado simultáneamente | El ledger lo rechaza (idempotency key), pero genera errores en logs y ruido operativo. |
| Commits concurrentes sobre el mismo job | `SELECT FOR UPDATE` serializa, pero la transacción perdedora descubre que el estado cambió y lo registra como skip. |
| Métricas duplicadas | Cada tick reporta `scanned_count`, `released_count`, etc. Solapamiento infla métricas sin releases reales. |
| Ruido operativo | El operador ve dos ticks que reportan candidatos, pero el segundo encuentra 0 releases. Confusión en alertas. |
| Retry loops | Si un tick falla y se reintenta mientras el anterior sigue ejecutándose, hay 2N ticks compitiendo. |

**El servicio interno de release es idempotente, pero el locking**:
- Reduce presión sobre DB y ledger.
- Elimina ruido operativo.
- Garantiza que cada tenant se procese una sola vez por tick.
- Hace que las métricas por tick sean fiables.

## 4. Principios del locking

- **PostgreSQL será la autoridad del lock** — `pg_try_advisory_lock` o `pg_advisory_lock`.
  No depender de memoria de proceso, filesystem locks ni locks locales por instancia.
- **Non-blocking preferido** — `pg_try_advisory_lock`. Si el lock no se adquiere,
  skip limpio. No esperar indefinidamente.
- **Lock siempre liberado** — asociado a session PostgreSQL. Al cerrar la conexión,
  el lock se libera automáticamente. Usar `try/finally` como safeguard adicional.
- **Lock observable** — toda adquisición, fallo o liberación debe registrarse en
  métrica/log (sin secretos).
- **Lock no expone secretos** — las keys del lock son deterministas, no contienen
  `DATABASE_URL`, credenciales ni datos sensibles.
- **Lock no es seguridad** — el lock es mecanismo de concurrencia, no mecanismo de
  autorización ni de tenant isolation. Todos los checks de tenant boundary ya están
  en el adapter.

## 5. Estrategia recomendada

**Nivel 1 (obligatorio)**: Lock por tenant mediante `pg_try_advisory_lock`.

```text
key = hash("scheduler:cancelled-credit-release:<organization_id>")
```

Cada tenant habilitado intenta adquirir su lock antes de abrir la sesión de
procesamiento. Si el lock no se adquiere, el tenant se salta (`skipped_locked`)
y el tick continúa con el siguiente.

**Nivel 2 (evaluar)**: Lock global de tick mediante `pg_try_advisory_lock`.

```text
key = hash("scheduler:cancelled-credit-release:tick")
```

Si el lock global no se adquiere, todo el tick se salta. Previene que dos
réplicas ejecuten ticks simultáneamente.

La primera implementación debe usar al menos lock por tenant. El lock global
se evaluará después si hay evidencia de múltiples réplicas activas.

## 6. Lock global

| Aspecto | Descripción |
|---------|-------------|
| Cuándo se usaría | En entornos con múltiples réplicas del scheduler (producción con escalado horizontal). |
| Qué protege | Evita que dos réplicas ejecuten el mismo tick a la vez. |
| Key conceptual | `hash("scheduler:cancelled-credit-release:tick")` |
| Ventajas | Simplifica la concurrencia entre réplicas. Un solo tick activo en todo el cluster. |
| Riesgos | Si el tick falla y el lock está retenido, el siguiente tick no se ejecuta hasta que el lock se libere (por TTL o cierre de conexión). |
| Lock no adquirido | Tick skipped completo. No error terminal. Se reintenta en el siguiente intervalo. |
| Métrica futura | `global_lock_acquired: bool` |

**Decisión**: skip limpio si el lock global no se adquiere. El tick no debe
marcarse como fallo; debe registrarse como evento operativo.

## 7. Lock por tenant

| Aspecto | Descripción |
|---------|-------------|
| Cuándo se usaría | Siempre que el scheduler esté activo. |
| Qué protege | Evita que dos ticks (mismo scheduler o réplicas) procesen el mismo `organization_id` simultáneamente. |
| Key conceptual | `hash("scheduler:cancelled-credit-release:<org_id>")` |
| Ventajas | Granularidad por tenant. Un tenant lento no bloquea a los demás. |
| Riesgos | Si hay muchos tenants, cada uno requiere una llamada `pg_try_advisory_lock`. |
| Lock no adquirido | Ese tenant se salta. El tick continúa con los siguientes. |
| Contador futuro | `skipped_locked_tenant_count` en el resultado del tick. |

**Comportamiento**:
- El lock por tenant se intenta adquirir antes de abrir la sesión de procesamiento.
- Si no se adquiere: `skipped_locked_tenant_count += 1`, continuar.
- No marcar como fallo de negocio.
- Registrar `lock_acquired=false` para ese tenant.
- Si se adquiere: procesar tenant, commit/rollback, liberar lock (cierre de sesión).

## 8. Session ownership

- El adapter actual abre una sesión por tenant habilitado.
- Si se implementa lock por tenant, el lock debe adquirirse dentro de la misma
  sesión (o al menos dentro de una sesión controlada cuyo ciclo de vida sea
  explícito).
- **Opción A**: lock session separada — una sesión mínima solo para `pg_try_advisory_lock`,
  luego la sesión de procesamiento. Separación clara pero dos conexiones.
- **Opción B**: misma sesión — el lock se adquiere en la sesión que se usará para
  procesar. El lock se libera al cerrar la sesión (commit/rollback + close).
- **Recomendación**: Opción B (misma sesión). El lock se adquiere al inicio de la
  sesión, antes de llamar a `process_cancelled_ai_job_credit_releases(...)`. Si el
  lock falla, no hay sesión de procesamiento. Si se adquiere, la sesión se usa
  para procesar y se cierra al final (commit o rollback).
- El commit/rollback del procesamiento debe ocurrir antes de cerrar la sesión.
  El lock se libera al cerrar la sesión PostgreSQL (no es necesario `pg_advisory_unlock`
  explícito, pero es buena práctica llamarlo en `finally`).

**Contrato actual del adapter**: una sesión por tenant.
**Contrato futuro con lock**: misma sesión por tenant, lock adquirido al inicio.

## 9. Transaction boundary

| Tipo | Descripción | Recomendación |
|------|-------------|---------------|
| Session-level advisory lock | El lock dura mientras la sesión PostgreSQL esté abierta. Se libera al cerrar la conexión o con `pg_advisory_unlock`. | **Recomendado**. El lock sobrevive a commits/rollbacks dentro de la sesión. Seguro para el caso de uso: si hay un commit exitoso, el lock sigue retenido hasta cerrar la sesión (evitando que otro tick procese el mismo tenant hasta que la sesión termine). |
| Transaction-level advisory lock | El lock dura solo dentro de la transacción actual. Se libera al hacer commit o rollback. | No recomendado para este caso: si el procesamiento de un tenant involucra múltiples transacciones (futuro), el lock se perdería entre ellas. |

**Recomendación**: session-level `pg_try_advisory_lock`. El lock se adquiere al
inicio de la sesión (antes del procesamiento) y se libera al cerrar la sesión.

**Riesgo**: si el proceso crashea sin cerrar la sesión, PostgreSQL libera el lock
automáticamente al detectar la conexión rota. No hay locks huérfanos permanentes.

## 10. Comportamiento cuando el lock no se adquiere

- **No bloquear**: usar `pg_try_advisory_lock`, no `pg_advisory_lock`.
- **No reintentar en bucle cerrado**: si el lock no se adquiere, registrar y continuar.
  El próximo tick lo reintentará.
- **No tumbar el tick completo** (salvo lock global si está implementado):
  el fallo de lock por tenant solo afecta a ese tenant.
- **Marcar tenant como skipped/locked**: `skipped_locked_tenant_count` incrementado.
- **Registrar evento**: `lock_acquired=false`, `organization_id`, `lock_key`.
- **No abrir procesamiento de release**: si el lock no se adquiere, no se llama a
  `process_cancelled_ai_job_credit_releases(...)` para ese tenant.
- **Cerrar la sesión del lock**: si se abrió una sesión para intentar el lock y no
  se adquirió, cerrarla limpiamente.

## 11. Error policy

| Escenario | Clasificación | Acción |
|-----------|---------------|--------|
| Error adquiriendo lock global | Estructural (no retryable en el mismo tick) | Tick skipped. Alerta. Reintento en siguiente intervalo. |
| Error adquiriendo lock por tenant | Transitorio (retryable en siguiente tick) | Tenant skipped. Registrar. Sin alerta a menos que sea persistente. |
| Error liberando lock (pg_advisory_unlock falla) | Bajo | La sesión se cerrará; PostgreSQL libera el lock. Registrar warning. |
| Error en procesamiento tras adquirir lock | Según categoría del error (retryable/terminal/unexpected) | Rollback de la sesión. Cerrar sesión (lock liberado). |
| Error en rollback tras fallo de procesamiento | Estructural | Cerrar sesión (libera lock). Alerta. |
| Error en commit tras procesamiento exitoso | Estructural | Cerrar sesión sin commit (libera lock). Reintentar en siguiente tick. |
| Lock no adquirido por falta de conexión DB | Estructural | Tick falla. Alerta inmediata. |

**Retryable**: error adquiriendo lock por tenant (reintentar en siguiente tick).
**No retryable en mismo tick**: lock global no adquirido, error de conexión DB.
**Alerta requerida**: error estructural, error en commit, error en rollback.

## 12. Observabilidad mínima futura

Campos que debe registrar el tick scheduler cuando el locking esté implementado:

| Campo | Descripción |
|-------|-------------|
| `scheduler_run_id` | Identificador único del tick. |
| `organization_id` | Tenant procesado o intentado. |
| `lock_key` | Key del lock (global o por tenant). |
| `lock_scope` | `"global"` \| `"tenant"`. |
| `lock_acquired` | `true` / `false`. |
| `lock_wait_ms` | Tiempo de espera para adquirir el lock (0 si non-blocking). |
| `lock_skipped` | `true` si el tenant/tick se saltó por lock no adquirido. |
| `skipped_locked_tenant_count` | Número de tenants saltados por lock. |
| `started_at` | Timestamp de inicio del tick/tenant. |
| `finished_at` | Timestamp de fin. |
| `duration_ms` | Duración total. |
| `error_category` | `"none"`, `"lock_failure"`, `"partial"`, `"structural"`. |
| `error_message` | Sanitizado (sin secretos). |

No implementar logging nuevo todavía.

## 13. Seguridad

- No imprimir `DATABASE_URL`, connection strings ni credenciales en ningún mensaje
  relacionado con locks.
- No incluir `organization_id` peligroso (`*`, `all`, `all-tenants`, `global`) sin
  validar (el adapter ya lo valida).
- No aceptar `all`/`global`/`*` desde cliente (el adapter ya lo rechaza).
- No crear endpoint público de locking.
- No permitir que un cliente dispare locks ni libere locks manualmente.
- No usar lock como autorización ni como mecanismo de tenant boundary.
- Lock es mecanismo de concurrencia, no mecanismo de seguridad.
- Las keys del lock (`hash("...")`) no deben contener secretos ni datos sensibles.

## 14. Relación con el adapter actual

- El adapter actual (`AIJobCancellationCreditReleaseSchedulerService`) ya valida
  el request completo antes de mutar (`_validate_tick_request`).
- El adapter actual usa una sesión por tenant habilitado.
- El adapter actual no está activo en runtime.
- El locking futuro debe integrarse sin romper el contrato de tests actual
  (82 tests que cubren kill switch, validación, iteración, errores, sanitización).
- El locking futuro debe añadirse como un servicio/adapter aislado (lock manager
  PostgreSQL inyectable), no como lógica mezclada con rutas o con el orchestration service.
- El adapter no debe importar `AsyncSessionLocal`, `DATABASE_URL`, rutas ni FastAPI.
- El lock manager debe ser aislable y testeable con mocks.

## 15. Relación con CLI

- La CLI manual (`scripts/ops/reconcile_cancelled_ai_job_credit_releases.py`)
  no necesita lock para operación manual controlada.
- En el futuro, si la CLI y el scheduler pueden operar a la vez, ambos deberían
  respetar el mismo lock por tenant, o al menos el servicio interno de release
  debe proteger la sección crítica (ya es idempotente).
- La CLI sigue siendo el fallback operativo. Si el scheduler falla o está
  desactivado, la CLI permite ejecutar reconciliación manual sin depender del
  estado del lock.
- El runbook de CLI debe advertir si el scheduler está activo (futuro):
  "Si el scheduler está habilitado, la CLI y el scheduler pueden competir
  por los mismos tenants. Verificar que no haya un tick activo antes de
  ejecutar la CLI manual."

## 16. Relación con idempotencia

- El locking **no sustituye la idempotencia** del servicio de release.
- `release_cancelled_ai_job_reserved_credits(...)` usa `caller_key` determinista
  (`cancel:<reservation_entry_id>`) que hace que el ledger rechace doble settlement.
- El locking reduce concurrencia, ruido y presión, pero no debe ser la única garantía.
- Si se pierde el lock o hay un crash, el siguiente tick (o la CLI manual) debe
  poder rerun sin riesgo de doble settlement gracias a la idempotencia.
- **Relación**: idempotencia es la última línea de defensa; locking es la primera.
  Ambas deben coexistir.

## 17. Criterios de aceptación para futura implementación

Checklist que debe cumplir la implementación del locking:

- [ ] No activa scheduler runtime.
- [ ] No expone endpoint público ni acepta `organization_id` desde cliente.
- [ ] No llama directamente al ledger.
- [ ] Lock no bloqueante (`pg_try_advisory_lock`).
- [ ] Lock por tenant implementado.
- [ ] Lock global evaluado y documentado (implementado o pospuesto con justificación).
- [ ] Si lock no se adquiere, skip limpio del tenant/tick — no error terminal.
- [ ] No hay procesamiento de release sin lock si locking está habilitado.
- [ ] Session ownership clara (misma sesión para lock y procesamiento).
- [ ] Commit/rollback seguro: rollback ante fallo, commit solo si éxito, cierre de sesión en `finally`.
- [ ] `skipped_locked_tenant_count` en resultado del tick.
- [ ] Logs/metrics sanitizados (sin `DATABASE_URL`, sin credenciales).
- [ ] Tests de lock adquirido.
- [ ] Tests de lock no adquirido.
- [ ] Tests de tenant A no bloquea tenant B (locks independientes).
- [ ] Tests de dos ejecuciones concurrentes sobre el mismo tenant.
- [ ] Tests de rollback con lock activo.
- [ ] Tests de no secretos en mensajes de error de lock.
- [ ] Guards PASS.

## 18. Riesgos

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Lock huérfano por crash | Baja | PostgreSQL libera locks al cerrar la conexión. No hay locks permanentes. |
| Bloqueo indefinido por lock blocking | Media | Usar `pg_try_advisory_lock` en lugar de `pg_advisory_lock`. Non-blocking. |
| Falsa sensación de seguridad (confiar solo en lock) | Media | El lock no sustituye idempotencia. Documentar y testear ambas capas. |
| Doble procesamiento si key mal derivada | Alta | Key determinista estable: `hash("scheduler:cancelled-credit-release:<org_id>")`. Revisar en code review. |
| Key collision (dos entidades diferentes misma key hash) | Baja | Usar hash con prefijo textual único. La probabilidad de colisión es insignificante. |
| Mezclar tenants (lock de tenant A protege tenant B) | Alta | Cada lock usa `organization_id` en la key. Validar en tests. |
| Rollback incorrecto que deja datos inconsistentes | Media | El adapter captura excepción, hace rollback y cierra sesión. Si rollback falla, la sesión se cierra igual (PostgreSQL hace rollback implícito). |
| Commit sin lock (lock perdido entre adquisición y procesamiento) | Baja | El lock está asociado a la sesión; no se pierde dentro de la misma sesión. |
| Lock global demasiado amplio que serializa todo | Media | Lock por tenant como granularidad principal. Lock global como opt-in solo si hay evidencia de múltiples réplicas. |
| Lock demasiado granular que no protege contra réplicas | Media | Lock por tenant protege contra réplicas para ese tenant. Lock global es protección adicional. |
| Pérdida de observabilidad: lock falla silenciosamente | Alta | `lock_acquired`, `lock_wait_ms`, `skipped_locked_tenant_count` en todo resultado. |
| Scheduler y CLI compitiendo por el mismo lock | Media | Ambos usarían la misma key de lock. El que no adquiere el lock, skip. La CLI no implementa lock todavía; documentar en runbook. |

## 19. Fases futuras recomendadas

| Subfase | Objetivo | Entregable |
|---------|----------|------------|
| **5B.2A** | Lock adapter contract/tests | Tests de unidad del lock manager PostgreSQL (simulado con mock) sin runtime real. |
| **5B.2B** | Implementación aislada de lock manager | Clase `PostgresAdvisoryLockManager` o similar, usando `pg_try_advisory_lock`. Sin runtime activation. Sin startup hook. |
| **5B.2C** | Integración con scheduler adapter | El lock manager se inyecta en `AIJobCancellationCreditReleaseSchedulerService`. Comportamiento: intentar lock por tenant antes de procesar. |
| **5B.2D** | Observabilidad del lock | `skipped_locked_tenant_count`, `lock_acquired`, `lock_wait_ms` en `TickResult`. Tests de observabilidad. |
| **5B.3** | Scheduler interno | Scheduler desactivado por defecto (kill switch `false`). Lock manager integrado. Sin startup hook todavía. |
| **5B.4** | Activación controlada | Startup hook opcional. Activación en staging primero. Monitoreo antes de producción. |

## 20. Non-goals

- No implementar locking real en esta fase.
- No modificar el scheduler adapter.
- No modificar la CLI.
- No modificar el orchestration service.
- No modificar el repository.
- No modificar el ledger.
- No tocar Docker.
- No tocar `.env`.
- No tocar Alembic.
- No añadir endpoint admin.
- No añadir startup hook.
- No añadir cron.
- No añadir worker real.
- No añadir cola.
- No añadir dependencias nuevas al proyecto.
