# Hardening y Primer Arranque (PRIVATE PACK)

Antes de levantar el stack privado por primera vez en el ordenador de casa, debes establecer llaves criptográficas reales y asegurar la persistencia mínima del entorno.

El archivo que orquesta toda la infraestructura es `.env.private`, que no se versiona por seguridad.

## 1. Secretos Obligatorios (Checklist de Seguridad)
Renombra el archivo `.env.private.example` a `.env.private` y sustituye los siguientes placeholders estáticos por llaves complejas generadas, por ejemplo, mediante un gestor de contraseñas:

- `N8N_ENCRYPTION_KEY`: UUID o cadena alfanumérica larga aleatoria. N8N usa esto para cifrar las credenciales de los webhooks y las integraciones. **[!] Si lo pierdes, pierdes acceso a las credenciales guardadas en N8N.**
- `AUTH_BOOTSTRAP_USERS`: Semilla del primer administrador. Se recomienda fuertemente asignar una contraseña compleja en vez de contraseñas estáticas por defecto.
  - Formato estricto: `correo:contraseña:rol` (Ej: `admin@cine.local:SuperSecureP@ssW0rd:admin`)

## 2. Checklist de Primer Arranque (Home PC)

### Paso 1: Configurar el Entorno
- [ ] Conecta el disco duro externo al ordenador de casa.
- [ ] Ejecuta `Copy-Item .env.private.example .env.private`
- [ ] Abre `.env.private` y **reemplaza** los passwords y keys descritos en la sección superior.

### Paso 2: Encender el Bridge Físico Externo
- [ ] Inicia y conecta **Tailscale** en la máquina Windows para asegurar enrutamiento.
- [ ] Abre WSL2 y ejecuta el script de levantado de ComfyUI: `.\deploy\start-comfy-wsl.ps1`
- [ ] Valida que el puente responde al DNS de Windows: `.\infra\scripts\check-comfy-bridge.ps1`

### Paso 3: Orquestación Cero
- [ ] Arranca el core del entorno invocando el boot general: `.\deploy\start-private.ps1`
- [ ] Monitoriza el asentamiento inicial de directorios mapeados: `.\deploy\status-private.ps1`
- [ ] Valida el E2E usando el chequeo maestro: `.\infra\scripts\smoke-private.ps1`

### Paso 4: Cierre del Bootstrap
Si el status es OK y los checks pasan, la infraestructura está lista.
*(Nota: Si N8N pide configuración inicial, entra al dominio privado definido en Tailscale y establece la cuenta maestre por la Web UI).*
