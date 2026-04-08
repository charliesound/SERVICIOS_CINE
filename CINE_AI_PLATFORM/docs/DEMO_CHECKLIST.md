# Demo Checklist

## Infraestructura
- [ ] Ordenador de casa encendido y accesible
- [ ] Docker Desktop corriendo
- [ ] WSL2 disponible
- [ ] ComfyUI arrancado en WSL2
- [ ] Tailscale conectado en laptop y servidor
- [ ] Stack privado arriba

## Validacion tecnica
- [ ] `smoke-private.ps1` pasa sin errores
- [ ] `check-comfy-bridge.ps1` reporta host y container OK
- [ ] Endpoint `/api/health` responde 200
- [ ] Endpoint `/api/health/details` reporta ComfyUI reachable
- [ ] Token de demo valido

## Caso de demo
- [ ] `examples/demo_screenplay_01.txt` existe y es legible
- [ ] El guion se carga correctamente
- [ ] Se ha probado una ejecucion completa antes de la demo real

## Presentacion
- [ ] Navegador abierto en el panel web
- [ ] Secuencia de presentacion preparada
- [ ] Explicacion comercial breve preparada
