# CID AI Job Cancellation Credit Release — Scheduler Contract v1

## 1. Título y alcance

Este documento define el contrato futuro de un scheduler interno para ejecutar
automáticamente la reconciliación de créditos reservados en AI Jobs cancelados.

**Qué es esta fase**: solo documentación. Define el diseño, las restricciones de
seguridad, la cadencia, el anti-solape, la iteración de tenants, la política de
errores y los criterios de aceptación del scheduler futuro.

**Qué NO es esta fase**:
- No implementa scheduler.
- No implementa endpoint admin, worker real, cola real ni cambios de runtime.
- No añade dependencias.
- No cambia modelos, ledger, rutas, frontend, Docker, Alembic ni tests.

**Mecanismo operativo actual**: la CLI manual sigue siendo el único mecanismo
disponible hoy (ver runbook en `docs/operations/cid_cancelled_ai_job_credit_release_cli_runbook_v1.md`).

## 2. Estado actual

Ya existen los siguientes componentes:

| Componente | Ubicación |
|------------|-----------|
| Servicio interno de reconciliación | `AIJobAsyncOrchestrationService.process_cancelled_ai_job_credit_releases(...)` |
| Servicio interno de release | `AIJobAsyncOrchestrationService.release_cancelled_ai_job_reserved_credits(...)` |
| Selector de candidatos | `AIJobRepository.list_cancelled_credit_release_candidates(...)` |
| CLI interna manual | `scripts/ops/reconcile_cancelled_ai_job_credit_releases.py` |
| Runbook operativo | `docs/operations/cid_cancelled_ai_job_credit_release_cli_runbook_v1.md` |
| Contrato de disparo operativo | `docs/architecture/cid_ai_job_cancellation_credit_release_operational_trigger_contract_v1.md` |

## 3. Objetivo del scheduler futuro

El scheduler deberá:

- Ejecutar reconciliaciones internas de forma periódica y automática.
- Operar por tenant (`organization_id`).
- Respetar `max_items` por ejecución.
- Evitar solapamiento entre ticks.
- Ser idempotente (rerun seguro sin doble settlement).
- No exponer capacidades de release al cliente.
- No consumir créditos ni forzar settlements manuales.
- No saltarse las invariantes de seguridad del servicio interno.
- Poder ser desactivado remotamente (kill switch).
- Generar observabilidad suficiente para detectar fallos silenciosos.

## 4. Non-goals

- No sustituye la API pública de cancelación (`POST /api/v1/ai-jobs/{job_id}/cancel`).
- No añade endpoint público.
- No añade endpoint admin en esta fase.
- No implementa worker real.
- No implementa cola de mensajes.
- No cambia modelos, ledger, rutas, frontend, Docker ni Alembic.
- No permite `all-tenants` sin control operativo explícito.
- No añade modo `force`, `global`, `consume` ni flags peligrosos equivalentes.
- No sustituye la CLI manual (la CLI sigue siendo el mecanismo de respaldo).

## 5. Boundary de seguridad

- El scheduler no debe recibir `organization_id` desde cliente ni desde fuente no confiable.
- Si itera tenants, debe hacerlo desde una fuente interna controlada (lista explícita habilitada o consulta interna de organizaciones activas con filtro de estado).
- Cada ejecución debe llamar al servicio con `organization_id` explícito.
- No debe llamar directamente al ledger (ninguna función de `CreditLedgerService`).
- No debe llamar directamente a `release_cancelled_ai_job_reserved_credits(...)` por fuera de `process_cancelled_ai_job_credit_releases(...)`, salvo justificación futura documentada y aprobada.
- No debe importar rutas públicas (nada de `src/routes/`).
- No debe imprimir `DATABASE_URL`, credenciales, tokens ni secretos.
- No debe usar configuración alternativa (`.env` local, archivos de configuración externos no controlados).
- No debe tener flags peligrosos equivalentes a `--force`, `--global`, `--consume`, `--release-entry-id`, `--caller-key` público.

## 6. Cadencia propuesta

Cadencia inicial conservadora:

- **Intervalo**: cada 5 o 15 minutos en entorno operativo.
- **`max_items` por tenant**: 50 (default), cap interno a 100.
- **Backoff en errores repetidos**: si el tick falla completamente, reintentar en el siguiente intervalo (no apilar ticks). Si falla N veces consecutivas, duplicar intervalo hasta un máximo de 1 hora.
- **Kill switch**: configuración interna (variable de entorno o flag en DB) para deshabilitar el scheduler globalmente o por tenant. Si está deshabilitado, el scheduler debe loguear "disabled" y saltar sin ejecutar.
- **Modo dry-run**: el scheduler puede tener un modo "monitoring" que ejecuta la selección sin llamar al release y loguea los candidatos, para validación operativa antes de activar releases automáticos. Este modo no debe ser el modo normal de producción.

No añadir configuración real todavía. Esta cadencia es contractual y se ajustará en Phase 5B.2.

## 7. Anti-solape / locking

El scheduler debe evitar ejecuciones simultáneas que procesen el mismo tenant:

| Requisito | Descripción |
|-----------|-------------|
| Un scheduler activo por entorno | Una sola instancia del scheduler debe ejecutarse en cada entorno (producción, staging). |
| Lock distribuido | Usar `pg_advisory_lock` con una key determinista (ej. `hash("scheduler:reconcile_cancelled_credits")`). |
| Lock por tenant | Cada tenant debe tener su propio lock para que la reconciliación de un tenant no bloquee la de otro. Key: `hash("scheduler:reconcile_cancelled_credits:<org_id>")`. |
| TTL del lock | Timeout máximo de retención del lock (ej. 5 minutos). Si se excede, el lock se libera automáticamente (riesgo aceptado de doble ejecución solo si el procesamiento excede el TTL, lo cual es improbable con `max_items <= 100`). |
| Liberación segura | Liberar el lock en bloque `finally` o `try/finally`. Nunca dejar locks huérfanos. |
| Lock no adquirido | Si el lock ya existe, saltar ese tenant/tick limpiamente y loguear. No esperar indefinidamente. |
| Múltiples réplicas | Dos réplicas del scheduler no deben poder ejecutar el mismo tenant simultáneamente. El lock PostgreSQL lo garantiza. |

No implementar lock todavía. Este contrato define los requisitos; la implementación se hará en Phase 5B.3.

## 8. Tenant iteration segura

Alternativas futuras para determinar qué tenants procesar:

| Alternativa | Descripción |
|-------------|-------------|
| Lista explícita | Lista interna/controlada de `organization_id` habilitados para scheduler. Máximo control operativo. |
| Consulta interna | Selector de organizaciones activas con filtro de estado (ej. `is_active = true`). Menos mantenimiento manual pero requiere validación adicional. |
| Híbrida | Lista explícita como fuente primaria; consulta interna como respaldo si la lista está vacía. |

Requisitos por tenant:
- Batch por tenant: un tick itera tenants secuencialmente.
- Límite total por ciclo: si hay muchos tenants, limitar el número máximo procesados por tick.
- Límite por tenant: `max_items` aplica individualmente.
- Orden estable: mismo orden de procesamiento en cada tick (ej. alfabético por `organization_id`).
- No mezclar resultados entre tenants: cada ejecución es independiente.
- Observabilidad por tenant: métricas y logs separados por `organization_id`.

**Recomendación para primera implementación (Phase 5B.2)**: lista interna explícita de tenants habilitados. Nunca aceptar `all-tenants` desde cliente ni desde configuración externa no validada.

## 9. Resultado esperado por ejecución

El scheduler recibirá el resultado de `process_cancelled_ai_job_credit_releases(...)`, que expone los siguientes counters (definidos en `AIJobAsyncCancelCreditReleaseReconciliationResult`):

| Counter | Tipo | Descripción |
|---------|------|-------------|
| `scanned_count` | `int` | Jobs cancelados examinados en la BD para este tenant. |
| `processed_count` | `int` | Jobs candidatos que pasaron filtros y fueron procesados. |
| `released_count` | `int` | Jobs con `release_performed = true`. |
| `skipped_count` | `int` | Jobs saltados por estado no válido o sin reserva. |
| `failed_count` | `int` | Jobs con error durante el release. |
| `dry_run` | `bool` | `true` si el scheduler está en modo monitoring. |
| `per_job_results` | `list[...]` | Resultados individuales por job. |

No existen `eligible_count`, `idempotent_count` ni `dry_run_count` como campos separados. El equivalente operativo de `eligible_count` es `processed_count`. La idempotencia y dry-run se interpretan por `error_category` en `per_job_results`.

## 10. Categorías por job

El scheduler debe manejar cada `error_category` según la siguiente política:

| Categoría | Clasificación | Acción del scheduler |
|-----------|---------------|----------------------|
| `released_now` | success | Registrar counter. No requiere acción adicional. |
| `idempotent_replay` | success/no-op seguro | Registrar counter. No requiere acción. |
| `dry_run_eligible` | informativo | No debería aparecer en ejecución normal (solo en modo monitoring). Registrar y continuar. |
| `skipped_already_released` | success | Registrar y continuar. |
| `skipped_no_reservation` | success | Registrar y continuar. |
| `retryable_error` | warning | Registrar. El job podrá reintentarse en el siguiente ciclo (el servicio es idempotente). |
| `terminal_error` | error | Registrar. **No reintentar**. Requiere intervención operativa. Incrementar contador de alerta. |
| `unexpected_error` | critical | Registrar. Marcar el ciclo con error. Alertar inmediatamente. No reintentar sin inspección. |

## 11. Error policy / retry policy

- **Errores por job**: no deben tumbar todo el ciclo. El scheduler debe continuar procesando los jobs restantes del mismo tenant y los demás tenants.
- **Errores estructurales**: sí deben abortar el ciclo (ej. error de conexión a BD, lock no adquirido, excepción no manejada en el scheduler).
- **`failed_count > 0`**: debe generar señal operativa (log, métrica, alerta).
- **`retryable_error`**: puede reintentarse en ciclos posteriores (el servicio es idempotente).
- **`terminal_error`**: requiere intervención. No reintentar automáticamente.
- **`unexpected_error`**: requiere alerta inmediata. No reintentar sin inspección.
- **Límite de reintentos**: backoff exponencial si el tick falla completamente. No repetir en bucle cerrado.
- **Dead cycle detection**: si N ticks consecutivos fallan (threshold configurable), desactivar scheduler automáticamente y alertar.

## 12. Observabilidad

Campos mínimos que debe registrar el scheduler por tick:

| Campo | Descripción |
|-------|-------------|
| `scheduler_run_id` | Identificador único del tick. |
| `organization_id` | Tenant procesado. |
| `max_items` | Límite de items configurado. |
| `started_at` | Timestamp de inicio. |
| `finished_at` | Timestamp de fin. |
| `duration_ms` | Duración total del tick. |
| `scanned_count` | Jobs examinados. |
| `processed_count` | Jobs procesados. |
| `released_count` | Jobs liberados. |
| `skipped_count` | Jobs saltados. |
| `failed_count` | Jobs con error. |
| `per_job_category_summary` | Resumen de categorías (`released_now: N`, `terminal_error: M`, ...). |
| `error_category` | `"none"`, `"partial"`, `"structural"`. |
| `requested_by` | `"scheduler"` o identificador interno equivalente. |
| `dry_run` | `true` si el scheduler está en modo monitoring. |
| `lock_acquired` | `true`/`false`. |

No implementar logging nuevo todavía. Este contrato define el esquema futuro.

## 13. Seguridad operativa

- No exponer salida con secretos, `DATABASE_URL`, credenciales ni tokens.
- No imprimir `DATABASE_URL` en logs, stdout, métricas ni alertas.
- No permitir ejecución del scheduler desde automatización pública (webhooks externos, API pública).
- No permitir que usuarios finales disparen release a través del scheduler.
- No ejecutar scheduler con permisos de superusuario de BD ni con rol de mayor privilegio del necesario.
- Toda ejecución debe quedar trazable: `scheduler_run_id`, `organization_id`, timestamps, resultado.
- Mantener separación estricta entre cancelación pública y reconciliación interna: el scheduler nunca debe leer ni modificar el estado de cancelación; solo opera sobre jobs ya cancelados.

## 14. Relación con la CLI

- La CLI sigue siendo la herramienta manual de operación y diagnóstico.
- El scheduler futuro debe reutilizar la misma operación interna de servicio (`process_cancelled_ai_job_credit_releases(...)`), no duplicar lógica de reconciliación.
- La CLI sirve como mecanismo de respaldo si el scheduler falla o está desactivado.
- El runbook de CLI sigue siendo válido para diagnóstico y ejecución controlada.
- Los tests de la CLI ya cubren el contrato de integración con el servicio; los tests del scheduler deben enfocarse en tick, lock, iteración y observabilidad, no en duplicar los tests de reconciliación.

## 15. Propuesta de fases futuras

Secuencia recomendada de implementación progresiva para Phase 5B:

| Subfase | Objetivo | Entregable |
|---------|----------|------------|
| **5B.1** | Tests/contract del scheduler | Tests de unidad del scheduler sin runtime real (simular tick, lock, iteración). |
| **5B.2** | Implementación mínima | Scheduler interno desactivado por defecto (kill switch en `False`). Solo activable por configuración explícita. |
| **5B.3** | Locking anti-solape | Integración con `pg_advisory_lock` (adapter aislado). Tests de lock. |
| **5B.4** | Observabilidad y alertas | Métricas por tick, logs estructurados, alerta en `failed_count > 0` y errores estructurales. |

Fases posteriores (no parte de Phase 5B):

| Fase | Objetivo |
|------|----------|
| **Phase 5C** | Endpoint admin-only (si realmente se necesita y existe panel Ops). |
| **Phase 5D** | Integración con worker/background real o cola madura. |

## 16. Riesgos

| Riesgo | Severidad | Mitigación |
|--------|-----------|------------|
| Doble ejecución concurrente del mismo tenant | Media | Lock por tenant con `pg_advisory_lock`. Tests de concurrencia. |
| Tenant equivocado (producción vs. staging, tenant A vs. tenant B) | Alta | Lista explícita de tenants habilitados. Validación en cada tick. |
| Bucle de retries sin límite | Media | Backoff exponencial en fallo completo. Dead cycle detection. |
| Liberar créditos de un job ya consumido | Baja | El servicio ya verifica estado del job y reserva. Idempotente. |
| Ocultar errores terminales (avanzar sin detectar) | Alta | `terminal_error` counter separado. Alerta si > 0. |
| Convertir operación interna en pública accidentalmente | Crítica | El scheduler no tiene interfaz HTTP. No hay endpoint público. |
| Scheduler demasiado agresivo (intervalo < duración de procesamiento) | Media | Lock anti-solape. Skip si lock existe. |
| Falta de observabilidad: release falla silenciosamente | Alta | Logs estructurados por tick. Métricas. Alerta configurable. |
| Locks huérfanos después de crash | Baja | `pg_advisory_lock` se libera al cerrar sesión PostgreSQL. TTL adicional como safeguard. |
| Mezcla de resultados entre tenants | Media | Cada tenant ejecuta su propio `process_cancelled_ai_job_credit_releases(...)`. Resultados no se mezclan. |

## 17. Criterios de aceptación para futura implementación

Checklist que debe cumplir la implementación del scheduler:

- [ ] No expone endpoint público ni acepta `organization_id` desde cliente.
- [ ] No llama directamente al ledger.
- [ ] `organization_id` explícito por ejecución; no hay modo `all-tenants` sin control.
- [ ] `max_items` limitado y con cap interno.
- [ ] Anti-solape cubierto con `pg_advisory_lock` (global + por tenant).
- [ ] Logs estructurados con campos mínimos de observabilidad.
- [ ] Errores categorizados por job (`retryable`, `terminal`, `unexpected`).
- [ ] Tests de tenant boundary: tenant A no afecta tenant B.
- [ ] Tests de lock: lock adquirido, lock no adquirido, lock liberado.
- [ ] Tests de idempotencia: rerun del mismo tick produce mismos resultados.
- [ ] Tests de `failed_count` > 0: no aborta ciclo.
- [ ] Tests de no secretos: `DATABASE_URL` no aparece en salida ni logs.
- [ ] Tests de no flags peligrosos: scheduler no acepta `--force`, `--global`, `--consume`.
- [ ] Guards PASS: DB regression guard and WSL repo guard.
- [ ] Kill switch funcional: desactivado por defecto; activación explícita requiere configuración.
