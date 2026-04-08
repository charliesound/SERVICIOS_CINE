$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " SERVICIOS_CINE - PREFLIGHT DEL SERVIDOR " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$srcDir = Join-Path $projectRoot "src"
$frontDir = Join-Path $projectRoot "src_frontend"

function Test-Cmd($cmd, $args = @()) {
    try {
        & $cmd @args *> $null
        return $true
    } catch {
        return $false
    }
}

function Test-PortFree($port) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    return ($null -eq $conn)
}

function Test-Http($url) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 3
        return $true
    } catch {
        return $false
    }
}

Write-Host ""
Write-Host "[1] Verificando estructura del proyecto..." -ForegroundColor Yellow
$requiredPaths = @(
    $projectRoot,
    $srcDir,
    $frontDir,
    (Join-Path $srcDir "app.py"),
    (Join-Path $srcDir "requirements.txt"),
    (Join-Path $srcDir "config\config.yaml"),
    (Join-Path $srcDir "config\instances.yml"),
    (Join-Path $srcDir "config\plans.yml"),
    (Join-Path $frontDir "package.json")
)

foreach ($p in $requiredPaths) {
    if (Test-Path $p) {
        Write-Host "  [OK] $p" -ForegroundColor Green
    } else {
        Write-Host "  [FALTA] $p" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "[2] Verificando herramientas..." -ForegroundColor Yellow

if (Test-Cmd "python" @("--version")) {
    $pyv = python --version
    Write-Host "  [OK] Python: $pyv" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Python no está disponible en PATH." -ForegroundColor Red
}

if (Test-Cmd "pip" @("--version")) {
    $pipv = pip --version
    Write-Host "  [OK] pip: $pipv" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] pip no está disponible en PATH." -ForegroundColor Red
}

if (Test-Cmd "node" @("--version")) {
    $nodev = node --version
    Write-Host "  [OK] Node.js: $nodev" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Node.js no está disponible en PATH." -ForegroundColor Red
}

if (Test-Cmd "npm" @("--version")) {
    $npmv = npm --version
    Write-Host "  [OK] npm: $npmv" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] npm no está disponible en PATH." -ForegroundColor Red
}

Write-Host ""
Write-Host "[3] Verificando dependencias Python mínimas..." -ForegroundColor Yellow
try {
    python -c "import fastapi, yaml, uvicorn, aiohttp, httpx; print('deps OK')" | Out-Null
    Write-Host "  [OK] Dependencias Python mínimas disponibles." -ForegroundColor Green
} catch {
    Write-Host "  [ERROR] Faltan dependencias Python. Ejecuta: pip install -r src\requirements.txt" -ForegroundColor Red
}

Write-Host ""
Write-Host "[4] Verificando puertos del servidor..." -ForegroundColor Yellow
$ports = @(8000,3000,8188,8189,8190,8191)

foreach ($port in $ports) {
    if (Test-PortFree $port) {
        Write-Host "  [LIBRE] Puerto $port" -ForegroundColor Green
    } else {
        Write-Host "  [OCUPADO] Puerto $port" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[5] Verificando conectividad local a backends IA..." -ForegroundColor Yellow
$backendUrls = @(
    "http://127.0.0.1:8188",
    "http://127.0.0.1:8189",
    "http://127.0.0.1:8190",
    "http://127.0.0.1:8191"
)

foreach ($url in $backendUrls) {
    if (Test-Http $url) {
        Write-Host "  [OK] Responde: $url" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] No responde ahora: $url" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[6] Resumen final" -ForegroundColor Yellow
Write-Host "  - Proyecto raíz: $projectRoot"
Write-Host "  - Backend: $srcDir"
Write-Host "  - Frontend: $frontDir"
Write-Host ""
Write-Host "Siguiente orden recomendado:" -ForegroundColor Cyan
Write-Host "  1. Arrancar backends IA (8188-8191) si no están activos"
Write-Host "  2. Ejecutar .\start_backend.bat"
Write-Host "  3. Ejecutar .\start_frontend.bat"
Write-Host "  4. Probar desde el servidor: http://127.0.0.1:8000/health"
Write-Host "  5. Probar desde el laptop: http://IP_DEL_SERVIDOR:3000"
Write-Host ""
Write-Host "Preflight completado." -ForegroundColor Cyan