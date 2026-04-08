# SERVICIOS_CINE - Arranque Completo del Servidor
# Este script inicia todos los servicios necesarios

param(
    [string]$ComfyUIStill = "",
    [string]$ComfyUIVideo = "",
    [string]$ComfyUIDubbing = "",
    [string]$ComfyUILab = "",
    [switch]$SkipPreflight,
    [switch]$NoDemo,
    [switch]$Auto
)

$ErrorActionPreference = "Continue"

# Colores
function Write-Section { param([string]$Text) 
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host $Text -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

function Write-Step { param([string]$Text)
    Write-Host "[ETAPA] $Text" -ForegroundColor Yellow
}

# Banner
Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SERVICIOS_CINE - Arranque Servidor   ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Cyan

# Detectar IP local
$localIP = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "Loopback" -and $_.IPAddress -notmatch "^127" }).IPAddress | Select-Object -First 1
if (-not $localIP) { $localIP = "localhost" }

Write-Host ""
Write-Host "[INFO] IP del servidor: $localIP" -ForegroundColor Gray

# ========================================
# PASO 1: Preflight
# ========================================
Write-Section "PASO 1: Verificacion de Pre-Flight"

if (-not $SkipPreflight) {
    & "$PSScriptRoot\preflight_check.ps1"
    
    Write-Host ""
    Write-Host "Continuar con el arranque? (S/N): " -NoNewline -ForegroundColor White
    if (-not $Auto) {
        $confirm = Read-Host
        if ($confirm -ne "S" -and $confirm -ne "s") {
            Write-Host "[CANCELADO]" -ForegroundColor Red
            exit 0
        }
    }
}

# ========================================
# PASO 2: ComfyUI Backends
# ========================================
Write-Section "PASO 2: ComfyUI Backends"

# Si no se proporcionan rutas, verificar si ya estan corriendo
$backendsRequeridos = @(
    @{name="still"; port=8188; path=$ComfyUIStill},
    @{name="video"; port=8189; path=$ComfyUIVideo},
    @{name="dubbing"; port=8190; path=$ComfyUIDubbing},
    @{name="lab"; port=8191; path=$ComfyUILab}
)

$backendsIniciados = @()
$backendsYaCorriendo = @()

foreach ($backend in $backendsRequeridos) {
    $testResult = Test-NetConnection -ComputerName 127.0.0.1 -Port $backend.port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($testResult.TcpTestSucceeded) {
        $backendsYaCorriendo += $backend.name
        Write-Host "  $($backend.name.PadRight(10)) [$($backend.port)] - YA CORRIENDO" -ForegroundColor Green
    }
}

Write-Host ""

# Si se proporcionan rutas y no estan corriendo, iniciarlos
if (-not $Auto) {
    Write-Host "[INFO] Para iniciar ComfyUI manualmente:" -ForegroundColor Gray
    foreach ($backend in $backendsRequeridos) {
        if ($backend.path) {
            Write-Host "  cd $($backend.path)" -ForegroundColor Gray
            Write-Host "  python main.py --listen 127.0.0.1 --port $($backend.port)" -ForegroundColor Gray
            Write-Host ""
        }
    }
}

# ========================================
# PASO 3: Backend
# ========================================
Write-Section "PASO 3: Backend API"

$backendRunning = Test-NetConnection -ComputerName 127.0.0.1 -Port 8000 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
if ($backendRunning.TcpTestSucceeded) {
    Write-Host "[INFO] Backend ya esta corriendo en puerto 8000" -ForegroundColor Green
}
else {
    Write-Host "[INFO] Iniciando backend..." -ForegroundColor Yellow
    
    # Verificar dependencias
    Set-Location "$PSScriptRoot\src"
    $depsOk = $true
    foreach ($dep in @("fastapi", "uvicorn", "aiohttp")) {
        $result = python -c "import $dep" 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Host "  [ERROR] $dep no instalado" -ForegroundColor Red
            $depsOk = $false
        }
    }
    
    if ($depsOk) {
        # Iniciar backend en una nueva ventana
        Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d `"$PSScriptRoot\src`" && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload && pause" -WindowStyle Normal
        Write-Host "[OK] Backend iniciado en nueva ventana" -ForegroundColor Green
        Write-Host "      Esperando que este listo..." -ForegroundColor Gray
        Start-Sleep -Seconds 3
    }
    else {
        Write-Host "[ERROR] Faltan dependencias. Ejecutar: pip install -r requirements.txt" -ForegroundColor Red
    }
    
    Set-Location $PSScriptRoot
}

# Verificar backend
Write-Host ""
Write-Host "[INFO] Verificando backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        Write-Host "[OK] Backend responde correctamente" -ForegroundColor Green
    }
} catch {
    Write-Host "[ADVERTENCIA] Backend no responde aun. Verificar manualmente." -ForegroundColor Yellow
}

# ========================================
# PASO 4: Frontend
# ========================================
Write-Section "PASO 4: Frontend"

$frontendRunning = Test-NetConnection -ComputerName 127.0.0.1 -Port 3000 -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
if ($frontendRunning.TcpTestSucceeded) {
    Write-Host "[INFO] Frontend ya esta corriendo en puerto 3000" -ForegroundColor Green
}
else {
    Write-Host "[INFO] Verificando node_modules..." -ForegroundColor Yellow
    
    Set-Location "$PSScriptRoot\src_frontend"
    if (-not (Test-Path "node_modules")) {
        Write-Host "  Instalando dependencias de npm..." -ForegroundColor Yellow
        npm install 2>&1 | Out-Null
    }
    
    # Iniciar frontend en una nueva ventana
    Start-Process -FilePath "cmd.exe" -ArgumentList "/c cd /d `"$PSScriptRoot\src_frontend`" && npm run dev -- --host 0.0.0.0 && pause" -WindowStyle Normal
    Write-Host "[OK] Frontend iniciado en nueva ventana" -ForegroundColor Green
    
    Set-Location $PSScriptRoot
}

# ========================================
# PASO 5: Demo Mode
# ========================================
if (-not $NoDemo) {
    Write-Section "PASO 5: Modo Demo"
    
    Start-Sleep -Seconds 2
    
    Write-Host "[INFO] Inicializando modo demo..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8000/api/demo/quick-start" -Method POST -TimeoutSec 10 -ErrorAction SilentlyContinue
        Write-Host "[OK] Demo inicializado" -ForegroundColor Green
        
        if ($response.status -eq "ready") {
            Write-Host "  Usuarios creados: $($response.users_created)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "[AVISO] No se pudo inicializar demo automaticamente" -ForegroundColor Yellow
        Write-Host "  Ejecutar manualmente: curl -X POST http://localhost:8000/api/demo/quick-start" -ForegroundColor Gray
    }
}

# ========================================
# RESUMEN
# ========================================
Write-Section "ARRANQUE COMPLETADO"

Write-Host ""
Write-Host "  ACCESO DESDE ESTE SERVIDOR:" -ForegroundColor White
Write-Host "  ---------------------------" -ForegroundColor Gray
Write-Host "  Frontend:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend:   http://localhost:8000" -ForegroundColor Cyan
Write-Host "  API Docs:  http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "  ACCESO DESDE OTRO EQUIPO:" -ForegroundColor White
Write-Host "  ---------------------------" -ForegroundColor Gray
Write-Host "  Frontend:  http://$localIP`:3000" -ForegroundColor Cyan
Write-Host "  Backend:   http://$localIP`:8000" -ForegroundColor Cyan
Write-Host "  API Docs:  http://$localIP`:8000/docs" -ForegroundColor Cyan
Write-Host ""

if (-not $NoDemo) {
    Write-Host "  CREDENCIALES DEMO:" -ForegroundColor White
    Write-Host "  ------------------" -ForegroundColor Gray
    Write-Host "  Admin:     admin@servicios-cine.com / admin123" -ForegroundColor Yellow
    Write-Host "  Free:      demo_free@servicios-cine.com / demo123" -ForegroundColor Yellow
    Write-Host "  Studio:    demo_studio@servicios-cine.com / demo123" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "  COMFYUI BACKENDS:" -ForegroundColor White
Write-Host "  -----------------" -ForegroundColor Gray
Write-Host "  Still:     http://127.0.0.1:8188" -ForegroundColor Yellow
Write-Host "  Video:     http://127.0.0.1:8189" -ForegroundColor Yellow
Write-Host "  Dubbing:   http://127.0.0.1:8190" -ForegroundColor Yellow
Write-Host "  Lab:       http://127.0.0.1:8191" -ForegroundColor Yellow
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Verificar servicios en: docs\GUIA_DESPLIEGUE_SERVIDOR.md" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
