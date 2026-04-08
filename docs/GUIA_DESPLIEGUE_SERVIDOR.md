# GUIA DE DESPLIEGUE EN SERVIDOR - SERVICIOS_CINE

> Nota: esta guia describe un despliegue anterior orientado a Windows/disco local.
> Para la configuracion actual en Ubuntu/WSL2 con Docker y Tailscale, consulta `README_WSL2.md` y `README_TAILSCALE.md`.

## Resumen del Procedimiento

Este documento describe el procedimiento para:
1. Copiar el proyecto del disco externo al disco interno del servidor
2. Instalar dependencias en el servidor
3. Arrancar los servicios

---

## ARQUITECTURA DE RED

```
┌─────────────────────────────────────────────────────────────┐
│                        SERVIDOR (Casa)                       │
│                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌───────────────┐  │
│   │  ComfyUI    │    │  ComfyUI    │    │  ComfyUI      │  │
│   │  still      │    │  video      │    │  dubbing/lab  │  │
│   │  :8188      │    │  :8189      │    │  :8190-8191   │  │
│   └──────┬──────┘    └──────┬──────┘    └───────┬───────┘  │
│          │                   │                    │           │
│          └───────────────────┼────────────────────┘        │
│                              │                              │
│                     ┌────────▼────────┐                     │
│                     │  SERVICIOS_CINE │                     │
│                     │     backend     │                     │
│                     │    :8000        │                     │
│                     └────────┬────────┘                     │
│                              │                              │
│                     ┌────────▼────────┐                     │
│                     │  SERVICIOS_CINE │                     │
│                     │    frontend     │                     │
│                     │    :3000        │                     │
│                     └─────────────────┘                     │
└─────────────────────────────────────────────────────────────┘
                              │
                              │ Red local
                              ▼
                   ┌─────────────────────┐
                   │   Cliente (Laptop)  │
                   │  http://IP:3000     │
                   └─────────────────────┘
```

---

## PASO 1: COPIAR AL SERVIDOR

### Opcion A: Desde disco externo (Windows)

1. Conectar disco externo al servidor
2. Copiar carpeta `SERVICIOS_CINE` al disco interno

```powershell
# Ejemplo: Copiar de E:\ a D:\
Copy-Item -Path "E:\SERVICIOS_CINE" -Destination "D:\SERVICIOS_CINE" -Recurse -Force
```

### Opcion B: Usando el script (ejecutar en SERVIDOR)

```powershell
# En el servidor, crear y ejecutar:
.\copiar_al_servidor.ps1
```

El script pedira:
- Ruta origen (disco externo)
- Ruta destino (disco interno)

---

## PASO 2: VERIFICAR ESTRUCTURA

En el servidor, verificar que la carpeta contiene:

```
D:\SERVICIOS_CINE\
├── src\                    # Backend FastAPI
│   ├── app.py
│   ├── requirements.txt
│   ├── config\
│   │   ├── instances.yml   # 127.0.0.1:8188-8191
│   │   └── plans.yml
│   ├── routes\
│   └── services\
├── src_frontend\           # Frontend React
│   ├── package.json
│   ├── src\
│   └── ...
├── docs\                   # Documentacion
├── handoff\                # Sesiones OpenCode
├── setup.bat               # Script de instalacion
├── start_backend.bat       # Arrancar backend
├── start_frontend.bat      # Arrancar frontend
└── preflight_check.bat     # Verificar dependencias
```

---

## PASO 3: INSTALAR DEPENDENCIAS

### Opcion A: Script automatico

```powershell
cd D:\SERVICIOS_CINE
.\setup.bat
```

### Opcion B: Manual

#### Python dependencies
```powershell
cd D:\SERVICIOS_CINE\src
pip install -r requirements.txt
```

#### Node dependencies
```powershell
cd D:\SERVICIOS_CINE\src_frontend
npm install
```

---

## PASO 4: ARRANCAR COMFYUI BACKENDS

Los backends ComfyUI deben estar corriendo ANTES de iniciar SERVICIOS_CINE.

```powershell
# Terminal 1: Still (8188)
cd C:\ruta\a\ComfyUI_still
python main.py --listen 127.0.0.1 --port 8188

# Terminal 2: Video (8189)
cd C:\ruta\a\ComfyUI_video
python main.py --listen 127.0.0.1 --port 8189

# Terminal 3: Dubbing (8190)
cd C:\ruta\a\ComfyUI_dubbing
python main.py --listen 127.0.0.1 --port 8190

# Terminal 4: Lab (8191)
cd C:\ruta\a\ComfyUI_lab
python main.py --listen 127.0.0.1 --port 8191
```

Verificar que respondan:
```powershell
# Cada una debe devolver JSON con system_stats
curl http://127.0.0.1:8188/system_stats
curl http://127.0.0.1:8189/system_stats
curl http://127.0.0.1:8190/system_stats
curl http://127.0.0.1:8191/system_stats
```

---

## PASO 5: VERIFICAR PREFLIGHT

```powershell
cd D:\SERVICIOS_CINE
.\preflight_check.ps1
```

Debe mostrar:
```
[1/7] Checking Python... OK
[2/7] Checking pip... OK
[3/7] Checking Python dependencies... OK
[4/7] Checking Node.js... OK
[5/7] Checking npm... OK
[6/7] Checking ports... All free
[7/7] Checking ComfyUI backends... OK: still, video, dubbing, lab
```

---

## PASO 6: ARRANCAR SERVICIOS_CINE

### Terminal 1: Backend
```powershell
cd D:\SERVICIOS_CINE
.\start_backend.bat
```

Verificar:
```powershell
curl http://localhost:8000/health
# {"status":"healthy"}

curl http://localhost:8000/api/ops/status
# { "overall_status": "healthy", ... }
```

### Terminal 2: Frontend
```powershell
cd D:\SERVICIOS_CINE
.\start_frontend.bat
```

Verificar:
```powershell
curl http://localhost:3000
```

---

## PASO 7: ACCESO DESDE RED LOCAL

### Obtener IP del servidor
```powershell
ipconfig
# Buscar: IPv4 . . . . . . . . . . : 192.168.x.x
```

### Acceder desde laptop
```
Frontend: http://192.168.x.x:3000
Backend:  http://192.168.x.x:8000
API Docs: http://192.168.x.x:8000/docs
```

---

## INICIALIZAR MODO DEMO

```powershell
curl -X POST http://localhost:8000/api/demo/quick-start
```

Credenciales demo:

| Plan | Email | Password |
|------|-------|----------|
| Free | demo_free@servicios-cine.com | demo123 |
| Creator | demo_creator@servicios-cine.com | demo123 |
| Studio | demo_studio@servicios-cine.com | demo123 |
| Enterprise | demo_enterprise@servicios-cine.com | demo123 |
| Admin | admin@servicios-cine.com | admin123 |

---

## ESTRUCTURA DE PUERTOS

| Servicio | Puerto | Descripcion |
|----------|--------|-------------|
| Backend API | 8000 | FastAPI - todas las operaciones |
| Frontend | 3000 | Vite dev server |
| ComfyUI still | 8188 | Generacion de imagenes |
| ComfyUI video | 8189 | Generacion de video |
| ComfyUI dubbing | 8190 | Voz y audio |
| ComfyUI lab | 8191 | Experimental |

---

## CONFIGURACION DE BACKENDS

El archivo `src/config/instances.yml` esta configurado para:

```yaml
backends:
  still:
    host: "127.0.0.1"  # ComfyUI en el mismo servidor
    port: 8188
  video:
    host: "127.0.0.1"
    port: 8189
  dubbing:
    host: "127.0.0.1"
    port: 8190
  lab:
    host: "127.0.0.1"
    port: 8191
```

**Importante**: Se usa `127.0.0.1` porque los backends ComfyUI corren en el MISMO servidor, fuera de Docker.

---

## RESOLUCION DE PROBLEMAS

### Backend no inicia
```powershell
# Verificar que el puerto 8000 este libre
netstat -ano | findstr ":8000"

# Si hay algo, matar el proceso:
taskkill /PID <numero> /F
```

### Frontend no conecta al backend
Verificar que el backend esta corriendo y que CORS permite el origen.

### ComfyUI no responde
```powershell
# Test directo
curl http://127.0.0.1:8188/system_stats

# Si no responde, verificar que ComfyUI esta corriendo
# y que esta escuchando en 127.0.0.1 (no solo localhost)
```

### Python no encuentra modulos
```powershell
cd D:\SERVICIOS_CINE\src
pip install -r requirements.txt
```

### npm install falla
```powershell
cd D:\SERVICIOS_CINE\src_frontend
npm cache clean --force
npm install
```

---

## APAGAR SERVICIOS

1. Ctrl+C en terminal del frontend
2. Ctrl+C en terminal del backend
3. Opcional: Cerrar instancias ComfyUI

---

## NOTAS IMPORTANTES

1. **Disco externo es SOLO transporte** - El proyecto se ejecuta desde disco interno
2. **ComfyUI fuera de Docker** - Los backends usan `127.0.0.1` porque corren en el host
3. **Bind a 0.0.0.0** - Backend y frontend se bindean a todas las interfaces para acceso de red
4. **Puerto 8000 y 3000** - Deben estar libres antes de arrancar

---

## SIGUIENTE PASO

Una vez funcionando localmente, ver `DOCKER.md` para consideraciones de containerizacion opcional.
