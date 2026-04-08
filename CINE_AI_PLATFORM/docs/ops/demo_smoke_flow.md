# Smoke flow manual de demo remota

## Contexto
Uso real con laptop + hotspot (o acceso por Tailscale/Cloudflare) sobre stack WSL.

## Preparacion
Definir URL de demo:

```bash
export DEMO_URL="http://localhost:8080"
```

## Orden exacto de comprobaciones

1) UI base (`/`) - esperado: 200 en 1-3 s

```bash
curl -I "$DEMO_URL/"
```

2) Health API - esperado: `ok=true` en <1 s

```bash
curl -s "$DEMO_URL/api/health"
```

3) Estado operativo - esperado: `ok=true` en <1 s

```bash
curl -s "$DEMO_URL/api/ops/status"
```

4) Health details - esperado: respuesta en 1-3 s (depende timeout ComfyUI)

```bash
curl -s "$DEMO_URL/api/health/details"
```

5) Storage summary - esperado: `ok=true` en <1 s

```bash
curl -s "$DEMO_URL/api/storage/summary"
```

6) Flujo UI minimo - esperado total: 30-90 s
- abrir app
- cargar proyecto demo
- navegar escena
- abrir/editar shot

## Criterios de exito/fallo
- Exito minimo:
  - UI carga
  - `/api/health` y `/api/storage/summary` en `ok=true`
- Exito completo:
  - ademas `comfyui.reachable=true`
- Fallo critico:
  - `/api/health` no responde o `ok=false`

## Fallback sin ComfyUI
Si `comfyui.reachable=false`:
1. continuar demo con editor/storage
2. evitar acciones dependientes de render
3. mostrar `api/ops/status` como evidencia de modo degradado controlado

## Tiempo total objetivo
- Smoke tecnico: 2-4 min
- Demo operativa inicial: <=10 min desde arranque
