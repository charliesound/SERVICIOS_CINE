# SERVICIOS_CINE - Restart Services
# Reinicia todos los servicios de forma ordenada

param(
    [switch]$Force,
    [switch]$Docker
)

$ErrorActionPreference = "Continue"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

function Stop-ProcessByPort($port) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        $proc = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
        if ($proc) {
            Write-Host "  Deteniendo proceso en puerto $port (PID: $($proc.Id))" -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force
        }
    }
}

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  AILinkCinema - Reiniciando Servicios" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

if ($Docker) {
    Write-Host "[INFO] Modo Docker seleccionado" -ForegroundColor Cyan
    Write-Host ""
    
    Set-Location $projectRoot
    
    Write-Host "[1/3] Deteniendo contenedores..." -ForegroundColor Yellow
    docker-compose down
    
    Write-Host "[2/3] Reconstruyendo..." -ForegroundColor Yellow
    docker-compose build
    
    Write-Host "[3/3] Iniciando servicios..." -ForegroundColor Yellow
    docker-compose up -d
    
    Write-Host ""
    Write-Host "[OK] Servicios Docker iniciados" -ForegroundColor Green
    Write-Host "     Frontend: http://localhost:3000" -ForegroundColor Gray
    Write-Host "     Backend:  http://localhost:8000" -ForegroundColor Gray
}
else {
    Write-Host "[1/5] Deteniendo servicios existentes..." -ForegroundColor Yellow
    
    $ports = @(8000, 3000)
    foreach ($port in $ports) {
        Stop-ProcessByPort $port
    }
    
    Write-Host "[2/5] Verificando Python..." -ForegroundColor Gray
    python --version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Python no disponible" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[3/5] Verificando Node.js..." -ForegroundColor Gray
    node --version 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Node.js no disponible" -ForegroundColor Red
        exit 1
    }
    
    Write-Host "[4/5] Iniciando backend..." -ForegroundColor Yellow
    $backendDir = Join-Path $projectRoot "src"
    Start-Process "cmd.exe" -ArgumentList "/c cd /d `"$backendDir`" && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload" -WindowStyle Normal
    
    Write-Host "[5/5] Iniciando frontend..." -ForegroundColor Yellow
    $frontendDir = Join-Path $projectRoot "src_frontend"
    
    if (-not (Test-Path (Join-Path $frontendDir "node_modules"))) {
        Write-Host "     Instalando dependencias..." -ForegroundColor Gray
        Set-Location $frontendDir
        npm install
    }
    
    Start-Process "cmd.exe" -ArgumentList "/c cd /d `"$frontendDir`" && npm run dev -- --host 0.0.0.0 --port 3000" -WindowStyle Normal
}

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Servicios reiniciados!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Esperando 5 segundos para verificación..." -ForegroundColor Gray
Start-Sleep -Seconds 5

$backendOk = $false
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $backendOk = $true
    }
} catch {}

if ($backendOk) {
    Write-Host "[OK] Backend respondiendo" -ForegroundColor Green
} else {
    Write-Host "[WARN] Backend no responde aún" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Accesos:" -ForegroundColor Cyan
Write-Host "  Local:   http://localhost:3000" -ForegroundColor White
Write-Host "  Tailscale: http://100.121.83.126 (oailinkcinema)" -ForegroundColor White
Write-Host ""