# SERVICIOS_CINE - Scripts de Despliegue

> Estado: documentacion legacy orientada a scripts manuales en Windows.
> El flujo operativo actual recomendado usa Docker en WSL2.
> Consulta `README_WSL2.md`, `DOCKER.md` y `docs/DOCUMENTACION_VIGENTE.md`.

## Scripts Disponibles

### En Laptop (Desarrollo)

| Script | Proposito |
|--------|-----------|
| `setup.bat` | Instalar todas las dependencias |
| `start_backend.bat` | Iniciar backend FastAPI |
| `start_frontend.bat` | Iniciar frontend React |
| `preflight_check.bat` | Verificar que todo esta listo |
| `preflight_check.ps1` | Verificacion avanzada (PowerShell) |
| `smoke_producer_persistence.py` | Smoke reproducible de Producer Sprint 7 |
| `smoke_review_delivery_persistence.py` | Smoke reproducible de Reviews y Delivery Sprint 7 |
| `smoke_sprint13_rc.py` | Smoke reproducible de cierre Sprint 13 |
| `smoke_restart_recovery.py` | Smoke basico de reinicio y recovery |
| `build_frontend_wsl.sh` | Build frontend reproducible desde WSL |

### En Servidor (Produccion)

| Script | Proposito |
|--------|-----------|
| `copiar_al_servidor.ps1` | Copiar proyecto de disco externo a interno |
| `arranque_servidor.ps1` | Arrancar todos los servicios |
| `arranque_servidor.bat` | Wrapper para arranque_servidor.ps1 |

## Flujo de Despliegue en Servidor

### 1. Copiar archivos (una sola vez)
```
.\copiar_al_servidor.bat
```
Preguntara por disco origen y destino.

### 2. Primera vez: Instalar dependencias
```
cd D:\SERVICIOS_CINE
.\setup.bat
```

### 3. Verificar preflight
```
.\preflight_check.bat
```

### 4. Arrancar servicios
```
.\arranque_servidor.bat
```

## Uso Avanzado

### arrancar_servidor.ps1 con parametros
```powershell
# Con rutas de ComfyUI (opcional)
.\arranque_servidor.ps1 -ComfyUIStill "C:\ComfyUI\still" -ComfyUIVideo "C:\ComfyUI\video"

# Sin modo demo
.\arranque_servidor.ps1 -NoDemo

# Skip preflight check
.\arranque_servidor.ps1 -SkipPreflight

# Automatico (sin confirmaciones)
.\arranque_servidor.ps1 -Auto
```

### copiar_al_servidor.ps1 con parametros
```powershell
# Especificar origen y destino
.\copiar_al_servidor.ps1 -Origen "E:\SERVICIOS_CINE" -Destino "D:\SERVICIOS_CINE"

# Automatico
.\copiar_al_servidor.ps1 -Auto
```

### preflight_check.ps1 con parametros
```powershell
# Verbose output
.\preflight_check.ps1 -Verbose

# Auto-fix missing dependencies
.\preflight_check.ps1 -Fix
```

## Archivos Creados

El script de copia creara esta estructura:

```
D:\SERVICIOS_CINE\
├── src\                    # Backend FastAPI
├── src_frontend\           # Frontend React  
├── docs\                   # Documentacion
├── handoff\                # Sesiones
├── setup.bat               # Instalacion
├── start_backend.bat       # Iniciar backend
├── start_frontend.bat      # Iniciar frontend
├── preflight_check.bat     # Verificacion
├── copiar_al_servidor.ps1  # Copia servidor
└── arranque_servidor.ps1   # Arranque completo
```

## Notas

- Los scripts .ps1 requieren PowerShell 5.1+
- Los scripts .bat usan cmd.exe
- Backend y Frontend se abren en ventanas separadas
- ComfyUI debe estar corriendo manualmente (fuera de Docker)
