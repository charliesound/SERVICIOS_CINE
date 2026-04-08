# Deployment en Servidor - G:\SERVICIOS_CINE

## Pre-requisitos en el Servidor (Windows Server + WSL2)

### 1. Habilitar Hyper-V y WSL2
```powershell
# En PowerShell como Administrador
wsl --install
# Reiniciar el servidor
wsl --set-default-version 2
```

### 2. Habilitar Docker en WSL2
```bash
# En WSL2 (Ubuntu)
sudo apt update
sudo apt install -y docker.io docker-compose
sudo service docker start
# O mejor, instala Docker Desktop para Windows Server
```

### 3. Compartir unidad G$ (para copia desde laptop)
```powershell
# En PowerShell como Administrador en el servidor
New-SmbShare -Name "G$" -Path "G:\" -FullAccess "Administrators" -ReadAccess "Everyone"
```

### 4. Asegurar que G: existe
```powershell
# Crear unidad G si no existe
# En Disk Management o:
New-Partition -DriveLetter G -UseMaximumSize -AssignLetter
Format-Volume -DriveLetter G -FileSystem NTFS -NewFileSystemLabel "DATA"
```

## Copiar proyecto desde laptop

### Opcion 1: Por red (recomendado para archivos pequenos)
```powershell
# En el laptop
cd "D:\SERVICIOS_CINE\PROYECTO FINAL V1"
.\copiar_a_servidor.ps1 -ServidorIP "192.168.1.100"
```

### Opcion 2: Disco USB externo
1. Conecta el disco externo al servidor
2. Ejecuta `copiar_en_servidor.ps1`

## Estructura en el servidor

```
G:\
├─ SERVICIOS_CINE\
│   ├─ PROYECTO FINAL V1\      <- docker-compose, Caddy, setup
│   ├─ Web Ailink_Cinema\      <- Next.js CID App
│   ├─ CINE_AI_PLATFORM\       <- Python API + Web
│   └─ CID_SERVER\
│       └─ automation-engine\  <- Python FastAPI
└─ ComfyUI\                    <- Tu instalacion ComfyUI
```

## Ejecutar en el servidor

### Con el script (recomendado)
```powershell
cd "G:\SERVICIOS_CINE\PROYECTO FINAL V1"
.\setup.ps1
```

### Manual
```powershell
cd "G:\SERVICIOS_CINE\PROYECTO FINAL V1"
docker compose up -d --build
docker compose logs -f
```

## URLs de acceso

| Servicio | URL |
|---|---|
| CID App | http://TU_IP_LOCAL:8080 |
| CINE API | http://TU_IP_LOCAL:8080/api/cine |
| Automation Engine | http://TU_IP_LOCAL:8000 |

## Configurar Firewall (si es necesario)

```powershell
# Abrir puertos en Windows Server
New-NetFirewallRule -DisplayName "CID App" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
New-NetFirewallRule -DisplayName "Automation Engine" -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow
```

## ComfyUI en el servidor

Si ComfyUI esta en `G:\ComfyUI`:
1. Ejecútalo desde `G:\ComfyUI\run_cpu.bat` o `run_gpu.bat`
2. Asegúrate que corre en `http://0.0.0.0:8188`
3. El compose ya tiene `COMFYUI_BASE_URL=http://host.docker.internal:8188`

## Comandos utiles en el servidor

```powershell
# Ver estado
docker compose -f "G:\SERVICIOS_CINE\PROYECTO FINAL V1\docker-compose.yml" ps

# Ver logs
docker compose -f "G:\SERVICIOS_CINE\PROYECTO FINAL V1\docker-compose.yml" logs -f

# Reiniciar
docker compose -f "G:\SERVICIOS_CINE\PROYECTO FINAL V1\docker-compose.yml" restart

# Detener
docker compose -f "G:\SERVICIOS_CINE\PROYECTO FINAL V1\docker-compose.yml" down
```
