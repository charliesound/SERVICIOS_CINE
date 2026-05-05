# CID INTERNAL TEST MODE

## 1. Proposito

CID Internal Test Mode permite a un admin real o a un email interno en whitelist probar una experiencia simulada de acceso premium dentro de rutas internas aisladas.

## 2. Variables de entorno

- `CID_INTERNAL_TEST_MODE_ENABLED=false`
- `CID_INTERNAL_TESTER_EMAILS=email1@example.com,email2@example.com`
- `CID_INTERNAL_TEST_PLAN=enterprise`

Notas:
- El valor por defecto es seguro: `CID_INTERNAL_TEST_MODE_ENABLED=false`.
- `CID_INTERNAL_TEST_PLAN` solo acepta `demo`, `free`, `creator`, `producer`, `studio` o `enterprise`.
- Si `CID_INTERNAL_TESTER_EMAILS` esta vacio, solo un admin real puede acceder.

## 3. Seguridad

- No altera `get_tenant_context()`.
- No concede `enterprise` o `admin` globalmente.
- Solo opera bajo `/api/dev/cid-test/*`.
- Requiere flag explicita.
- Requiere admin real o email en whitelist.
- Registra `logger.warning` cuando el modo se usa.

## 4. Endpoints disponibles

- `GET /api/dev/cid-test/status`
- `POST /api/dev/cid-test/simulate-access`
- `POST /api/dev/cid-test/simulate-demo-project`
- `POST /api/dev/cid-test/run-full-pipeline`

Todos los endpoints son simulados y no persisten cambios.

## 5. Limitaciones

- No genera tokens.
- No crea usuarios.
- No modifica planes reales.
- No crea proyectos reales.
- No ejecuta jobs reales ni llama servicios externos reales.

## 6. Riesgos mitigados

- Se elimina el override global sobre `get_tenant_context()`.
- Se evita elevar permisos en endpoints normales.
- El router solo se registra cuando `CID_INTERNAL_TEST_MODE_ENABLED=true`.
- El acceso queda limitado a rutas internas de desarrollo.

## 7. No usar en produccion publica

Este modo existe solo para QA interno y validacion controlada. No debe exponerse en despliegues publicos abiertos ni utilizarse como sustituto de pagos, RBAC real o tooling administrativo formal.
