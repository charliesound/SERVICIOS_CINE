# RUNTIME HANDOFF: HOME PC DEPLOYMENT

Este documento es la guía estricta de ejecución para levantar el entorno Private Pack una vez el disco externo esté fisicamente conectado al ordenador de casa.

## Orden Exacto de Ejecución

Abre una consola PowerShell con permisos elevados y ejecuta en orden:

1. **Bootstrap del Motor Gráfico (ComfyUI via WSL2)**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\deploy\start-comfy-wsl.ps1 -ComfyPath "/home/<USUARIO>/ComfyUI"
   ```
   * **Salida Esperada:** WSL arranca, entorno virtual Python activado. El log termina mostrando `To see the GUI go to: http://0.0.0.0:8188`. (El proceso queda bloqueando la consola, déjalo abierto).

2. **Validación del Puente 1: Host a WSL2**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\infra\scripts\check-comfy-bridge.ps1 -SkipContainerCheck
   ```
   * **Salida Esperada:** Todos los outputs de host_probe en verde (`HTTP 200 OK`). Confirmación de que Windows alcanza a WSL2.

3. **Bootstrap del Clúster Privado (Docker Compose)**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\deploy\start-private.ps1
   ```
   * **Salida Esperada:** Creación de redes (si no existen), montado de volúmenes persistentes y el log `Container cine-private-api-1  Started` para api, web, n8n y qdrant. Termina con exit code 0.

4. **Validación del Puente 2: Contenedor a WSL2**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\infra\scripts\check-comfy-bridge.ps1
   ```
   * **Salida Esperada:** Ambos probes (Host local y Contenedor API temporal) retornan `True` en verde. Significa que la API empaquetada puede ver el motor de IA.

5. **Prueba End-to-End Segura**
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\infra\scripts\smoke-private.ps1
   ```
   * **Salida Esperada:** Reporte consolidado en verde que indica: `files_ok=True`, `compose_config_ok=True`, `comfyui_bridge_ok=True`, `api_health_ok=True` (o un error de certificado temporal pero resolviendo la IP de Tailscale correctamente).

---

## Troubleshooting Guide (Qué revisar si falla)

### Si falla `start-comfy-wsl.ps1`
- **Causa probable:** WSL2 no está arrancado, Python local no está en el PATH de la distro de Linux, o la ruta de acceso al directorio de ComfyUI está mal escrita.
- **Acción:** Abre Ubuntu/WSL2 manualmente, navega a la carpeta e intenta levantar ComfyUI con `python main.py --listen 0.0.0.0`. Observa los errores de dependencias.

### Si falla `check-comfy-bridge.ps1`
- **Si falla el `host_probe` (Windows):** ComfyUI no configuró la bandera `--listen 0.0.0.0` y solo escucha dentro del localhost de WSL2. Alternativa: el Firewall de Windows Defender bloquea el puerto 8188 desde redes públicas.
- **Si falla el `container_probe` (Docker):** El Docker Engine no está enrutando correctamente `host.docker.internal` al host local de Windows, o la integración WSL2 Engine de Docker Desktop está desconectada. Revisa la UI de Docker Desktop > Settings > Resources > WSL Integration.

### Si falla `start-private.ps1`
- **Causa probable:** Docker Daemon apagado. Conflictos de puertos en Windows (Típicamente el puerto `80` chocando con *System*, *IIS*, o *Skype*). Rutas de persistencia del `.env.private` inválidas en el nuevo Host (Asegúrate de que la unidad montada sea efectivamente `X:\`).
- **Acción:** Lanza manualmente `docker compose --env-file .env.private -f docker-compose.private.yml config` para auditar la sintaxis, o `docker ps` para ver puertos colisionados.

### Si falla `smoke-private.ps1`
- **Causa probable:** La URL suministrada en `PRIVATE_BASE_URL` no resuelve al servicio de Nginx. La VPN de Tailscale no está conectada o está baneando el ICMP local.
- **Acción:** Pide a Tailscale tu IP real en la VPN. Haz un ping manual. Comprueba los logs nativos de la API para ver si la base de datos sqlite está corrupta o atascada por permisos:
  ```powershell
  docker logs cine-private-api
  docker logs cine-private-nginx
  ```
