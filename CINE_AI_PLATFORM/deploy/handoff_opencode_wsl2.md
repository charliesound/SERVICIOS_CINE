# Handoff Bridge: Docker Windows -> WSL2 ComfyUI

## 1. Diagnóstico del Bridge
El patrón actual definido por `COMFYUI_BASE_URL=http://host.docker.internal:8188` es el patrón más estable y estándar que soporta Docker Desktop en Windows operando bajo la integración de WSL2. Esto asume correctamente que WSL2 funciona como un subsistema en localhost expuesto a la red interna de vSwitch de Windows y el DNS interno de Docker enruta `host.docker.internal` al host subyacente.

## 2. Decisión Técnica Cerrada
### Patrón Requerido:
1. **WSL2 ComfyUI (Host)**: ComfyUI DEBE ejecutarse con el flag `--listen 0.0.0.0` (o `--listen`). *Explicación: Si arranca por defecto en `127.0.0.1`, WSL2 no enrutará el tráfico que provenga de la red externa al localhost interno de la distribución WSL2. Solo escuchando en `0.0.0.0`, el host Windows puede capturar la asignación del puerto.*
2. **Windows OS**: Escucha nativamente en `127.0.0.1:8188` (puerto capturado desde WSL2).
3. **Contenedor API**: Llama a `http://host.docker.internal:8188`. El engine de Docker resuelve esto hacia la IP pasarela de Windows que, a su vez, conecta internamente con la escucha proxy de WSL2.

> [!NOTE]
> **Es el patrón correcto y cerrado.** Es extremadamente estable siempre y cuando se respete el binding `0.0.0.0` dentro del runner de WSL2.

## 3. Lista de Archivos Aplicados
Solo se debió modificar un archivo para dar soporte de auditoría cruzada al bridge a nivel de host VS a nivel de container:
- **`infra/scripts/smoke-private.ps1`**:
  - Modificado: Ahora efectúa un `Invoke-RestMethod` nativo hacia `127.0.0.1:8188` en el host local **antes** del intento del contenedor.
  - Esto valida primero si Windows es capaz de ver la app en WSL2, y luego si Docker es capaz de verla a través de `host.docker.internal`, aislando dónde falla el túnel.

## 4. Prioridad de Aplicación (OpenCode)
1. Iniciar **manualmente** ComfyUI en WSL2 asegurando explícitamente arrancar con:
   ```bash
   python main.py --listen 0.0.0.0
   ```
2. Ejecutar `deploy/start-private.ps1` para instanciar el entorno.
3. Ejecutar `infra/scripts/smoke-private.ps1`
4. Comprobar que en el output final las variables reflejan integridad de conexión, específicamente el valor nuevo de `comfyui_wsl_bridge = OK`.
5. **Aceptación y finalización**: Si ese script devuelve todo en verde o con status lines "OK", el patrón está sellado; bajo ninguna circunstancia se debe dockerizar ComfyUI o alterar la red.
