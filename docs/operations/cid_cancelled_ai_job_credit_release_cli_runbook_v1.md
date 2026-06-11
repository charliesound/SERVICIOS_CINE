# CID Cancelled AI Job Credit Release — CLI Runbook v1

## 1. Título y alcance

Este runbook documenta la operación manual/interna de reconciliación de créditos
reservados en AI Jobs cancelados mediante la CLI interna:

    scripts/ops/reconcile_cancelled_ai_job_credit_releases.py

**Qué es**: una herramienta de operaciones (ops) que ejecuta `process_cancelled_ai_job_credit_releases(...)` para un tenant concreto, liberando los créditos que quedaron retenidos tras la cancelación de un AI Job.

**Qué NO es**:
- No es un endpoint público.
- No es un scheduler automático.
- No es un worker real.
- No es una cola de mensajes.
- No expone control de release al cliente.

**Relación con la API pública**: `POST /api/v1/ai-jobs/{job_id}/cancel` solo registra la intención de cancelación. La liberación operativa de créditos se realiza internamente con esta CLI (o con mecanismos futuros — scheduler, endpoint admin, worker). El cliente no puede forzar ni conocer el release.

## 2. Preconditions / requisitos previos

- Ejecutar desde `/opt/SERVICIOS_CINE`.
- Activar el entorno virtual: `source .venv/bin/activate`.
- `DATABASE_URL` debe estar configurado en el entorno operativo.
- **No imprimir ni registrar `DATABASE_URL`** en logs, salida, capturas de pantalla ni documentación.
- `organization_id` debe ser explícito y verificado antes de ejecutar.
- **Siempre ejecutar `--dry-run` primero** antes de una ejecución real.
- No existe modo global/all-tenants. Cada ejecución es estrictamente por tenant.

## 3. Comandos de uso

### Dry-run (humano)

```bash
python scripts/ops/reconcile_cancelled_ai_job_credit_releases.py \
    --organization-id <organization_id> \
    --max-items 50 \
    --dry-run
```

### Dry-run (JSON)

```bash
python scripts/ops/reconcile_cancelled_ai_job_credit_releases.py \
    --organization-id <organization_id> \
    --max-items 50 \
    --dry-run \
    --json
```

### Ejecución real (humano)

```bash
python scripts/ops/reconcile_cancelled_ai_job_credit_releases.py \
    --organization-id <organization_id> \
    --max-items 50
```

### Ejecución real (JSON)

```bash
python scripts/ops/reconcile_cancelled_ai_job_credit_releases.py \
    --organization-id <organization_id> \
    --max-items 50 \
    --json
```

### Con identificador de operador

```bash
python scripts/ops/reconcile_cancelled_ai_job_credit_releases.py \
    --organization-id <organization_id> \
    --max-items 50 \
    --requested-by ops-manual-<initials> \
    --dry-run \
    --json
```

## 4. Flujo operativo recomendado

Seguir estos pasos en orden para cada tenant:

| Paso | Acción |
|------|--------|
| 1 | Confirmar el `organization_id` del tenant objetivo. Verificar dos fuentes (admin panel + DB). |
| 2 | Ejecutar dry-run con `--json`. |
| 3 | Revisar los counters: `scanned_count`, `processed_count`, `dry_run` (debe ser `true`). |
| 4 | Revisar `per_job_results` para cada candidato: `error_category` debe ser `dry_run_eligible`. |
| 5 | Si `dry_run` es `true` y `processed_count > 0` y no hay señales peligrosas, ejecutar sin `--dry-run`. |
| 6 | Revisar el exit code al finalizar. |
| 7 | Si se usó `--json`, guardar la salida como evidencia operativa (ej. `ops-run-<org>-<date>.json`). |
| 8 | Si `failed_count > 0`, no repetir a ciegas. Revisar la causa (sección 10). |

## 5. Interpretación de contadores

La CLI reporta los siguientes counters (provenientes de `AIJobAsyncCancelCreditReleaseReconciliationResult`):

| Contador | Significado operativo |
|----------|----------------------|
| `scanned_count` | Número total de jobs cancelados examinados en la BD para este tenant. |
| `processed_count` | Jobs candidatos que pasaron los filtros y fueron procesados (equivale a "eligible count"). |
| `released_count` | Jobs en los que se ejecutó la liberación contable (`release_performed = true`). |
| `skipped_count` | Jobs saltados por estado no válido o sin reserva (no requieren acción). |
| `failed_count` | Jobs con error durante el release. **Requiere revisión** si > 0. |
| `dry_run` | `true` si la ejecución fue en modo inspección; `false` si fue real. |

**Nota**: no existe `eligible_count` como campo separado. El equivalente operativo es `processed_count`.

## 6. Interpretación de resultados por job

Cada entrada en `per_job_results` incluye un `error_category` que clasifica el resultado individual:

| Categoría | Significado | Acción del operador |
|-----------|-------------|---------------------|
| `released_now` | Liberación ejecutada correctamente. Crédito devuelto al ledger. | OK. No requiere acción. |
| `idempotent_replay` | El job ya estaba liberado o el release es replay seguro. | OK. No requiere acción. |
| `dry_run_eligible` | Candidato detectado en dry-run. No hubo mutación. | Revisar y proceder con ejecución real si procede. |
| `skipped_already_released` | El job ya fue liberado previamente. | OK. No requiere acción. |
| `skipped_no_reservation` | El job cancelado no tiene reserva de créditos. | OK. No requiere acción. |
| `retryable_error` | Error transitorio durante el release. | Revisar logs. Posible reintento controlado con los mismos parámetros. |
| `terminal_error` | Error no recuperable (ej. inconsistencia contable). | **No reintentar**. Requiere análisis del ledger antes de cualquier acción. |
| `unexpected_error` | Error inesperado no clasificado. | **Parar y escalar**. No reintentar sin inspección. |

## 7. Exit codes

| Código | Significado |
|--------|-------------|
| 0 | Éxito completo: `failed_count == 0`. |
| 1 | Fallo parcial: `failed_count > 0` pero la ejecución completó el escaneo. |
| 2 | Error de argumentos o configuración (parámetros inválidos, `--max-items` fuera de rango, etc.). |
| 3 | Error inesperado estructural (excepción no manejada antes o durante la reconciliación). |

## 8. Checklist antes de ejecutar

- [ ] Estoy en `/opt/SERVICIOS_CINE`.
- [ ] `.venv` activo (`source .venv/bin/activate`).
- [ ] `DATABASE_URL` configurado en entorno seguro (no en `.env` local ni en la sesión del operador).
- [ ] `organization_id` verificado contra dos fuentes.
- [ ] No estoy usando un tenant equivocado (revisar si hay múltiples organizations similares).
- [ ] Se ha ejecutado dry-run primero.
- [ ] Se ha revisado la salida JSON del dry-run.
- [ ] Se ha confirmado que no se requiere modo global (no existe).
- [ ] Se acepta el `--max-items` elegido (máximo recomendado: 100; default: 50).

## 9. Checklist después de ejecutar

- [ ] Revisado exit code (0 esperado; 1 requiere revisión).
- [ ] Revisado `failed_count`.
- [ ] Revisados `per_job_results` con `error_category = terminal_error` o `unexpected_error`.
- [ ] Guardada salida JSON como evidencia operativa si procede.
- [ ] No se repite ejecución real si hay errores sin investigar.
- [ ] Si hay errores terminales o inesperados, escalar al equipo de backend/ledger.

## 10. Troubleshooting básico

| Problema | Acción recomendada |
|----------|-------------------|
| `DATABASE_URL` no configurado | Configurar la variable de entorno en el contexto operativo seguro. Verificar que la URL sea válida (`postgresql+asyncpg://...`). |
| `organization_id` incorrecto | Verificar el tenant en la base de datos. La CLI rechazará un ID que no exista o no tenga jobs cancelados, pero no valida el formato del ID. |
| `--max-items` inválido | Debe ser un entero >= 1. La CLI mostrará error de argparse si el valor es inválido. |
| `failed_count > 0` | Revisar `per_job_results`. Identificar si los errores son `retryable_error`, `terminal_error` o `unexpected_error`. No reintentar ciegamente. |
| `retryable_error` | Revisar logs del servicio y del ledger. Si el error fue transitorio (timeout, conexión), reintentar con los mismos parámetros. |
| `terminal_error` | **No reintentar**. Revisar el estado del job, la reserva y el ledger antes de cualquier acción. Escalar si es necesario. |
| `unexpected_error` | **Parar y escalar**. Error no clasificado que requiere inspección del código. |
| Salida JSON no parseable | Verificar que la salida completa se capturó (puede haber logs de error mezclados en stderr). Usar `2>/dev/null` para aislar stdout si es necesario. |
| Dry-run no muestra candidatos | Puede ser normal si no hay jobs cancelados con créditos pendientes. Verificar que el `organization_id` es correcto y que hay jobs en estado `cancelled` con reservas activas. |
| Dry-run muestra candidatos pero ejecución real no libera nada | Posible condición de carrera: otro proceso (scheduler, otra CLI) liberó los créditos entre el dry-run y la ejecución. Verificar counters: `idempotent_replay` indica que ya estaban liberados. |

## 11. Seguridad y límites

- **Per-tenant obligatorio**: la CLI opera exclusivamente por `--organization-id`. No existe flag `--all-tenants` ni `--global`.
- **No acepta flags peligrosos**: `--release-credits`, `--release-entry-id`, `--caller-key`, `--consume`, `--force`, `--all-organizations`, `--global`, `--tenant-all` no existen y serían rechazados por argparse.
- **No exponer secretos**: la CLI no imprime `DATABASE_URL`, credenciales ni tokens. No debe ejecutarse desde automatizaciones públicas ni desde la API pública.
- **No es un endpoint**: no debe ser llamada desde HTTP, webhook ni desde código no autorizado.
- **No sustituye scheduler/worker**: esta CLI es una herramienta manual de operaciones. No reemplaza la automatización futura (Phase 5B+).
- **No consumir créditos ni forzar settlement**: la CLI solo libera créditos reservados de jobs cancelados. No debe usarse para consumir créditos, forzar settlements manuales ni modificar el ledger fuera del flujo de cancelación.

## 12. Relación con fases futuras

Este runbook documenta la operación manual segura previa a las siguientes fases, que no están implementadas todavía:

- **Phase 5B**: scheduler interno con lock operacional (`pg_advisory_lock`), periodicidad configurable, métricas por tick y kill switch.
- **Phase 5C**: endpoint admin-only con autenticación admin independiente, rate limits y auditoría de acceso.
- **Phase 5D**: worker/background real conectado a cola, con dead letter, reintentos con backoff y escalabilidad horizontal.
- **Observabilidad avanzada**: dashboards de métricas por tenant, alertas sobre `failed_count > 0` y monitorización de candidatos no procesados.

Ninguna de estas fases está implementada en esta versión. El runbook actual es exclusivamente para operación manual segura.
