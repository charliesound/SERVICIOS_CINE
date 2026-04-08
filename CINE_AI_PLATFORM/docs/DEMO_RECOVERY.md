# Demo Recovery Checklist

## Backend no responde
1. Verificar Docker Desktop
2. `docker compose --env-file .env.private -f docker-compose.private.yml ps`
3. `deploy/start-private.ps1` si necesario
4. Revisar logs: `deploy/logs-private.ps1 -Services api`

## ComfyUI no responde
1. Verificar WSL2: `wsl --list --running`
2. `check-comfy-bridge.ps1 -SkipContainerCheck`
3. Si ComfyUI cayo: `deploy/start-comfy-wsl.ps1 -ComfyPath "/home/<user>/ComfyUI"`
4. Re-validar bridge completo

## Tailscale no conecta
1. Verificar Tailscale en ambos extremos
2. Probar ping entre laptop y servidor
3. Fallback a local: usar `http://127.0.0.1` en el servidor
4. Si no hay alternativa, hacer demo solo con planner (sin render)

## Render tarda demasiado
1. Mostrar planificacion y grounding como resultado intermedio valido
2. Explicar que el render es asincrono
3. Mostrar resultados de una ejecucion previa si existen
4. No bloquear la demo esperando renders

## No llegan imagenes
1. Verificar jobs: `GET /api/render/jobs`
2. Revisar estado: failed/running/queued
3. Si todos failed: revisar ComfyUI y logs
4. Fallback: mostrar planificacion visual como storyboard textual
