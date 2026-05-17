# CID Breakdown - Backend Enforcement Sprint 3

## Resumen ejecutivo

Se aplico enforcement backend quirurgico para el modulo `breakdown` usando `require_module_access("breakdown")` solo en endpoints con ownership claro de Breakdown.

Resultado:
- Se protege acceso comercial por plan para endpoints de desglose.
- Se mantiene intacto el contrato API (paths, payloads, responses, codigos existentes).
- No se toca Script Analysis Pro, Budget Lite ni Project Core fuera de su estado actual.

## Endpoints protegidos

Se aplico dependencia a nivel endpoint en `src/routes/intake_routes.py`:

- `GET /api/projects/{project_id}/breakdown/scenes`
- `GET /api/projects/{project_id}/breakdown/departments`

Motivo:
- Router mixto (`/api/projects`) contiene endpoints de `script_analysis` y flujos compartidos.
- No corresponde router-level dependency para evitar enforcement accidental sobre endpoints no-breakdown.

## Endpoints no protegidos deliberadamente

### Script Analysis Pro (ownership script_analysis)
- `POST /api/projects/{project_id}/intake/script`
- `POST /api/projects/{project_id}/analysis/run`
- `GET /api/projects/{project_id}/analysis/summary`
- `GET /api/projects/{project_id}/analysis/export`
- `POST /api/projects/{project_id}/analyze`

Motivo:
- Ya usan `require_module_access("script_analysis")` o pertenecen al flujo de Script Analysis.

### Budget Lite (ownership budget_lite)
- `/api/projects/{project_id}/budgets/*`

Motivo:
- Ya tiene enforcement router-level con `require_module_access("budget_lite")`.

### Project Core / Shared
- Rutas de proyecto, dashboard y jobs en `project_routes.py`.

Motivo:
- Ownership no-breakdown o compartido; fuera del alcance del commit.

## Comportamiento esperado de bloqueo (403)

Cuando un plan no incluye `module_breakdown` y el usuario no es admin/global admin:

- Status: `403`
- Detail:
  - `code: MODULE_ACCESS_BLOCKED`
  - `module: breakdown`
  - `plan: <plan_normalizado>`
  - `reason: <locked_reason>`

Admins y global admins mantienen bypass segun `module_access.py`.

## Relacion con `module_breakdown` en planes

`module_breakdown` esta habilitado en `creator` y `producer` (y por herencia comercial en escalones superiores), no en `demo/free`.

Con este cambio:
- `demo/free` quedan correctamente bloqueados para endpoints de Breakdown (excepto bypass admin/global admin).
- planes con feature habilitada mantienen acceso.

## Relacion con Script Analysis Pro

Breakdown sigue dependiendo de datos producidos por Script Analysis (`production_breakdowns.breakdown_json`), pero ahora su consumo por API queda desacoplado comercialmente mediante feature flag propia.

Esto preserva la cadena:

`Script Analysis Pro -> Breakdown -> Budget Lite`

sin alterar contratos ni persistencia.

## Riesgos conocidos

- Endpoints Breakdown viven en `intake_routes.py` (router mixto): futuras adiciones requieren revisar ownership antes de aplicar nuevas dependencias.
- No existe export propio de Breakdown todavia; solo enforcement de lectura actual.
- Cobertura de tests de Breakdown aun es minima y concentrada en enforcement.

## Siguiente commit recomendado

Implementar export dedicado de Breakdown:

- Endpoint sugerido: `GET /api/projects/{project_id}/breakdown/export?format=json|csv|md`
- Servicio nuevo: `breakdown_export_service.py`
- Tests de formato, auth/tenant y enforcement `module_breakdown`.
