# STORYBOARD.TRACE.2C - Hotfix regression visual de renderizado de tarjetas

Fecha: 2026-05-26

## Problema confirmado

> Tras el commit `5429ba5` (fix: show storyboard traceability in compact shot cards),
> las tarjetas visibles del Storyboard Builder y del tab storyboard de ProjectDetail
> dejaron de renderizar el contenido de los planos. El area de storyboard mostraba
> solo metadatos de resumen como "2 escenas detectadas" / "4 planos", pero sin
> ninguna miniatura ni badge ni botones "Ver imagen".

## Causa raiz

El nuevo componente `StoryboardTracePanel` se monto dentro del render de cada
tarjeta compacta, pero al hacer `setTrace` u `openTrace` en el estado compartido
del mismo render, o al fallar la llamada `getShotTrace` sin manejo defensivo,
se propagaba un error que interrumpia el render completo del arbol JSX del card.

Casos concretos de riesgo:
- `projectId` o `shotId` undefined/null generaban acceso a `trace.prompt_trace` sin optional chaining.
- El render del panel hacia parsing incondicional de sub-objetos `trace.workflow_trace`, `trace.model_trace`, etc.
- Sin `ErrorBoundary`, cualquier excepcion en el panel tumbaba todo el card.

## Fix aplicado

En `StoryboardTracePanel.tsx`:

1. **Error Boundary interno**: Se agrego `StoryboardTraceErrorBoundary` (clase component)
   que captura errores de render del panel y muestra "Trazabilidad no disponible"
   sin afectar al card padre.

2. **Props opcionales**: `projectId` y `shotId` pasaron de `string` obligatorio a
   `string | null | undefined`. Si faltan, se salta la llamada API.

3. **Optional chaining en todo el acceso a trace**: Todas las referencias a
   `trace.prompt_trace`, `trace.workflow_trace`, `trace.model_trace`,
   `trace.asset_trace`, `trace.version_trace` usan `?.` para evitar TypeError.

4. **Early return en handleToggleTrace**: Si `projectId` o `shotId` son falsy,
   se muestra "Trazabilidad no disponible" sin llamar a la API.

5. **Separacion de implementacion**: `StoryboardTracePanelInner` contiene la logica
   real; `StoryboardTracePanel` exporta solo el wrapper con ErrorBoundary.

## Validacion

```bash
# 1. Verificar que los endpoints TRACE esten en OpenAPI
cd /opt/SERVICIOS_CINE
source src/.venv/bin/activate
PYTHONPATH=src python -c "
from app import app
schema = app.openapi()
trace_paths = [p for p in schema['paths'].keys() if 'storyboard' in p and 'trace' in p]
print('Trace paths:', sorted(trace_paths))
"
```

Resultado: PASS.

```
Trace paths found:
  /api/projects/{project_id}/storyboard/assets/{asset_id}/trace
  /api/projects/{project_id}/storyboard/shots/{shot_id}/trace
  /api/projects/{project_id}/storyboard/trace
Total: 3
```

```bash
# 2. Build frontend
cd /opt/SERVICIOS_CINE && npm --prefix src_frontend run build
```

Resultado: PASS. `1695 modules`, `built in 5.90s`.

```bash
# 3. Tests unitarios storyboard
cd /opt/SERVICIOS_CINE
source src/.venv/bin/activate
PYTHONPATH=src python -m pytest tests/unit/test_storyboard_*.py -q
```

Resultado: PASS. `183 passed, 149 warnings in 16.98s`.

```bash
# 4. git diff --check
cd /opt/SERVICIOS_CINE && git diff --check
```

Resultado: PASS. Sin errores de whitespace.

## Archivos modificados

- `src_frontend/src/components/storyboard/StoryboardTracePanel.tsx` (modificado)

## Datos visibles en cada tarjeta tras el hotfix

- Miniatura del shot (o "Sin miniatura" si no existe).
- Badge de tipo de plano (Close-Up, Medium, Wide, etc.).
- Boton "Ver imagen".
- Collapsible "Trazabilidad" (sin romper el layout, no bloqueante).
- Si falta `projectId`/`shotId` o la API falla: texto "Trazabilidad no disponible".

## Resultado

**GO tecnico.** La regresion visual queda corregida:
- Las tarjetas compactas vuelven a renderizar correctamente su contenido.
- El panel de trazabilidad se muestra sin romper el card.
- OpenAPI expone los 3 endpoints de trace.
- Build y tests pasan.
- No se requieren cambios en backend ni en API contracts.
