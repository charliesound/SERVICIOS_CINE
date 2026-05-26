# STORYBOARD.TRACE.2 - UI visibility fix

Fecha: 2026-05-26

## Problema confirmado

La trazabilidad existia en `ShotCard.tsx`, pero en la UI visible principal no siempre se renderizaba ese componente.

- `StoryboardBuilderPage.tsx` usa `ShotCard`, pero solo dentro del bloque colapsable `Detalles de planos`.
- Las tarjetas visibles de `StoryboardBuilderPage.tsx` usan renders compactos internos para `filmstrip` y `contact_sheet`.
- La evidencia visual reportada coincide tambien con el render compacto de `ProjectDetailPage.tsx`, que muestra `Sin miniatura`, badge de tipo de plano y `Ver imagen`.

## Fix aplicado

- Se creo `src_frontend/src/components/storyboard/StoryboardTracePanel.tsx` como panel reutilizable.
- `ShotCard.tsx` ahora reutiliza `StoryboardTracePanel` en lugar de tener la logica duplicada.
- `StoryboardBuilderPage.tsx` monta `StoryboardTracePanel` en las tarjetas visibles de:
  - `Filmstrip horizontal`
  - `Contact sheet grid`
- `ProjectDetailPage.tsx` monta `StoryboardTracePanel` en las tarjetas compactas visibles del tab storyboard.

## Endpoint llamado desde la tarjeta visible

`StoryboardTracePanel` llama bajo demanda:

```ts
storyboardApi.getShotTrace(projectId, shotId)
```

El panel esta montado directamente en las tarjetas visibles compactas, por lo que el endpoint `GET /api/projects/{project_id}/storyboard/shots/{shot_id}/trace` se llama desde la tarjeta real cuando el usuario abre `Trazabilidad`.

## Datos visibles en cada tarjeta

El collapsible `Trazabilidad` muestra:

- Prompt resumido.
- Workflow key y workflow profile.
- Fallback de workflow.
- Modelo/checkpoint.
- Seed, steps, cfg y sampler si existen.
- `render_job_id`.
- `media_asset_id`.
- Version actual e indicios de versiones anteriores.
- Boton `Copiar prompt`.
- Boton `Ver detalle tecnico`.

Si falta informacion se muestra `No disponible`.

## Seguridad

- No se anaden rutas fisicas al frontend.
- El panel consume exclusivamente el endpoint trace ya sanitizado.
- Las imagenes siguen usando endpoints autenticados de storyboard shot image/thumbnail.

## Validacion

```bash
cd /opt/SERVICIOS_CINE/src_frontend && npm run build
```

Resultado: PASS. Vite build completo. Persisten warnings existentes de dynamic import/chunk size.

```bash
source .venv/bin/activate && PYTHONPATH=src python -m pytest tests/unit/test_storyboard_*.py -q
```

Resultado: PASS. `183 passed, 149 warnings in 18.82s`.

```bash
grep -R -l 'Trazabilidad' /opt/SERVICIOS_CINE/src_frontend/dist /opt/SERVICIOS_CINE/Dockerfile* /opt/SERVICIOS_CINE/compose*.yml 2>/dev/null
```

Resultado: PASS. Encontrado en:

- `/opt/SERVICIOS_CINE/src_frontend/dist/assets/index-CWmtzy1L.js`

```bash
git diff --check
```

Resultado: PASS. Solo warnings de LF/CRLF reportados por Git.

## Resultado

GO tecnico para commit: la trazabilidad ahora es visible en las tarjetas reales del Storyboard Builder y del tab storyboard compacto, sin exponer rutas internas y sin romper build/tests.
