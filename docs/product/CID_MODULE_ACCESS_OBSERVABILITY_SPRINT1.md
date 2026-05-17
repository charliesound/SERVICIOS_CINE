# CID Module Access Observability Sprint 1

## Resumen ejecutivo

Añadir logging estructurado y seguro al helper `require_module_access()` para que cada bloqueo modular emita un evento de log con contexto suficiente para diagnóstico de soporte, ventas y operaciones, sin cambiar contratos de API ni aplicar nuevo enforcement.

## Eventos de log

### MODULE_ACCESS_BLOCKED (WARNING)

Se emite cuando un usuario sin permisos de admin intenta acceder a un endpoint protegido por un módulo que no está en su plan.

```
event=MODULE_ACCESS_BLOCKED | module=pitch_deck | source=module_access_dependency | user_id=user-1 | organization_id=org-1 | role=user | is_admin=false | plan=free | locked_reason=plan_feature_missing | path=/api/projects/123/presentation/filmstrip | method=GET | request_id=abc123
```

### MODULE_ACCESS_GRANTED_BY_ADMIN (INFO)

Se emite cuando un admin o global_admin accede a un endpoint protegido, atravesando el bypass deliberado.

```
event=MODULE_ACCESS_GRANTED_BY_ADMIN | module=funding_grants | source=module_access_dependency | user_id=user-1 | organization_id=org-1 | role=admin | is_admin=true | path=/api/projects/123/funding/dossier | method=POST | request_id=def456
```

### MODULE_ACCESS_ERROR (WARNING)

Se emite cuando el module_key no existe en el catálogo o hay un error de resolución de plan.

```
event=MODULE_ACCESS_ERROR | module=unknown_module | source=module_access_dependency | user_id=user-1 | organization_id=org-1 | role=admin | is_admin=false | plan=free | locked_reason=module_not_found:unknown_module
```

## Campos incluidos

| Campo | Tipo | Origen | Obligatorio |
|---|---|---|---|
| `event` | string | Constante del código | Sí |
| `module` | string | Parámetro de `require_module_access()` | Sí |
| `source` | string | Siempre `module_access_dependency` | Sí |
| `user_id` | string | `TenantContext.user_id` | Sí |
| `organization_id` | string | `TenantContext.organization_id` | Sí |
| `role` | string | `TenantContext.role` | Sí |
| `is_admin` | string | `TenantContext.is_admin` | Sí |
| `plan` | string | Plan normalizado (solo en eventos con plan) | Condicional |
| `locked_reason` | string | Razón del bloqueo | Condicional |
| `path` | string | `request.url.path` | Sí (cuando request disponible) |
| `method` | string | `request.method` | Sí (cuando request disponible) |
| `request_id` | string | `request.state.request_id` del middleware | Sí (cuando middleware instalado) |

## Campos prohibidos (nunca loggeados)

- Tokens JWT o de acceso
- Payloads de request (body, query params con contenido sensible)
- Documentos, guiones o textos de análisis
- Emails (se usa `user_id` en su lugar)
- API Keys
- Secretos de sesión
- Headers de autorización

## Formato de log

```
%(asctime)s | %(levelname)-8s | %(name)s | event=EVENT_NAME | module=... | source=... | key=value | ...
```

Cada campo es `key=value` separado por ` | `, usando el logger `servicios_cine.module_access`.

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `src/dependencies/module_access.py` | +`_log_module_event()`, +inyección `Request`, +logging en cada punto de salida |
| `tests/unit/test_module_access_dependency.py` | +5 tests de logging con `caplog` |

## Tests

```
15 passed (5 nuevos de logging + 10 legacy)
```

Los tests verifican:
- MODULE_ACCESS_BLOCKED contiene `module` y `locked_reason`
- MODULE_ACCESS_BLOCKED contiene `user_id`, `organization_id`, `source`
- MODULE_ACCESS_BLOCKED contiene `path` y `method`
- MODULE_ACCESS_GRANTED_BY_ADMIN se loggea cuando admin accede
- MODULE_ACCESS_BLOCKED NO se loggea cuando admin accede

## Relación con soporte y venta modular

- Soporte puede diagnosticar por qué un usuario recibe 403 sin necesidad de reproducir el error.
- Ventas puede ver qué módulos están bloqueados con más frecuencia y en qué planes.
- Operaciones puede detectar picos de bloqueo que indiquen confusión en navegación o bugs de permiso.
- Los logs pueden alimentar dashboards de observabilidad (Grafana, ELK, etc.).

## Límites conocidos

- `request_id` solo se incluye si `request_id_middleware` está instalado en ese entorno.
- Los eventos `MODULE_ACCESS_ERROR` (module not found, catalog error) son raros en producción — el catálogo se valida en startup.
- No hay métricas (counters) todavía — solo logs. Un dashboard requeriría parsed de logs.
- Los tests con `caplog` verifican contenido del mensaje pero no el nivel de log exacto (se usa `set_level` para capturar).

## Siguiente commit recomendado

1. Añadir métricas Prometheus para bloqueos modulares (counter por module/plan/reason).
2. Dashboard sugerido para Grafana: bloqueos por módulo, por plan, por hora.
3. Incluir módulo bloqueado en response header `X-Module-Access: blocked` para debugging desde frontend (sin cambiar payload 403).
