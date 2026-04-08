# ARRANQUE EN SERVIDOR - SERVICIOS_CINE

> Nota: este documento describe un flujo antiguo de arranque manual en Windows.
> Para el despliegue actual en Ubuntu/WSL2 con Docker, usa `README_WSL2.md`.

## Preparacion del Disco

El disco externo contiene:
```
D:\SERVICIOS_CINE\
├── src\              # Backend FastAPI
├── src_frontend\     # Frontend React
├── handoff\         # Documentacion sesiones
├── docs\             # Documentacion general
├── CID_SERVER\       # (Heredado - no tocar)
├── CINE_AI_PLATFORM\ # (Heredado - no tocar)
├── PROYECTO FINAL V1\ # (Heredado - no tocar)
├── Web Ailink_Cinema\ # (Heredado - no tocar)
```

## Checklist Pre-Arranque

### 1. Dependencies en Servidor

Ejecutar `preflight_check.bat` o `preflight_check.ps1` para verificar:

- [ ] Python 3.10+
- [ ] pip
- [ ] Node.js 18+
- [ ] npm
- [ ] Puertos 8000, 3000 libres
- [ ] ComfyUI backends corriendo en 127.0.0.1:8188-8191

### 2. ComfyUI Backends

Asegurarse que los backends ComfyUI esten corriendo:

```bash
# Cada backend en su propia terminal o como servicio
python main.py --listen 0.0.0.0 --port 8188  # still
python main.py --listen 0.0.0.0 --port 8189  # video
python main.py --listen 0.0.0.0 --port 8190  # dubbing
python main.py --listen 0.0.0.0 --port 8191  # lab
```

Verificar:
```bash
curl http://127.0.0.1:8188/system_stats
curl http://127.0.0.1:8189/system_stats
curl http://127.0.0.1:8190/system_stats
curl http://127.0.0.1:8191/system_stats
```

## Arranque Rapido

### Paso 1: Backend
```bash
# Abrir terminal en D:\SERVICIOS_CINE
.\start_backend.bat
```

Verificar:
```bash
curl http://localhost:8000/health
curl http://localhost:8000/docs
```

### Paso 2: Frontend
```bash
# Nueva terminal
.\start_frontend.bat
```

Verificar:
```bash
curl http://localhost:3000
```

## Acceso desde Red Local

Para acceder desde otros equipos en la misma red:

1. Obtener IP del servidor:
```bash
ipconfig
# Buscar IPv4 de la red local, ej: 192.168.1.x
```

2. Acceder desde otro equipo:
```
Backend: http://192.168.1.x:8000
Frontend: http://192.168.1.x:3000
API Docs: http://192.168.1.x:8000/docs
```

## Configuracion de Backends

El archivo `src/config/instances.yml` esta configurado para:
- still: 127.0.0.1:8188
- video: 127.0.0.1:8189
- dubbing: 127.0.0.1:8190
- lab: 127.0.0.1:8191

## Inicializar Demo

Desde otra terminal:
```bash
cd src
curl -X POST http://localhost:8000/api/demo/quick-start
```

Credenciales demo:
| Plan | Email | Password |
|------|-------|----------|
| free | demo_free@servicios-cine.com | demo123 |
| studio | demo_studio@servicios-cine.com | demo123 |
| admin | admin@servicios-cine.com | admin123 |

## Resolucion de Problemas

### Backend no inicia
```bash
# Verificar puertos
netstat -ano | findstr ":8000"
```

### Frontend no conecta al backend
El proxy Vite esta configurado para redirigir `/api` a `:8000`. Verificar que backend esta corriendo.

### ComfyUI no responde
```bash
# Test directo
curl http://127.0.0.1:8188/system_stats
```

### Permisos en disco externo
Si hay problemas de permisos, ejecutar PowerShell como administrador.

## Estructura de Puertos

| Servicio | Puerto | Descripcion |
|----------|--------|-------------|
| Backend API | 8000 | FastAPI |
| Frontend | 3000 | Vite dev server |
| ComfyUI still | 8188 | Image generation |
| ComfyUI video | 8189 | Video generation |
| ComfyUI dubbing | 8190 | Voice/Audio |
| ComfyUI lab | 8191 | Experimental |

## Apagar

1. Ctrl+C en terminal del backend
2. Ctrl+C en terminal del frontend
3. Opcional: Cerrar instancias ComfyUI

## Siguiente Paso

Una vez funcionando localmente, ver `DOCKER.md` para容器izacion opcional.
