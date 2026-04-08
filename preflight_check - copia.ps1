# SERVICIOS_CINE - Preflight Check
# Verifica todas las dependencias necesarias para ejecutar el sistema
# Ejecutar antes de start_backend.bat y start_frontend.bat

param(
    [switch]$Verbose,
    [switch]$Fix
)

$ErrorActionPreference = "Continue"

function Write-Check {
    param([string]$Message, [string]$Status, [string]$Color)
    $spaces = " " * (40 - $Message.Length)
    Write-Host "[$Message]$spaces [$Status]" -ForegroundColor $Color
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SERVICIOS_CINE - Preflight Check" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$issues = @()
$warnings = @()

# Detectar si estamos en servidor o desarrollo
$isServer = $env:COMPUTERNAME -ne $env:USERNAME.ToUpper().Replace("-", "").Substring(0, [Math]::Min(15, $env:USERNAME.Length))
Write-Host "[INFO] Entorno: $(if ($isServer) { 'SERVIDOR' } else { 'DESARROLLO LOCAL' })" -ForegroundColor Gray
Write-Host ""

# ========================================
# 1. Python
# ========================================
Write-Host "--- Python ---" -ForegroundColor White
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Check "Python" "OK" "Green"
        if ($Verbose) { Write-Host "       $pythonVersion" -ForegroundColor Gray }
    } else {
        Write-Check "Python" "NO ENCONTRADO" "Red"
        $issues += "Python no instalado"
    }
} catch {
    Write-Check "Python" "NO ENCONTRADO" "Red"
    $issues += "Python no instalado"
}

# ========================================
# 2. pip
# ========================================
Write-Host ""
Write-Host "--- pip ---" -ForegroundColor White
try {
    $pipVersion = pip --version 2>&1 | Select-Object -First 1
    if ($LASTEXITCODE -eq 0) {
        Write-Check "pip" "OK" "Green"
        if ($Verbose) { Write-Host "       $pipVersion" -ForegroundColor Gray }
    } else {
        Write-Check "pip" "NO ENCONTRADO" "Red"
        $issues += "pip no instalado"
    }
} catch {
    Write-Check "pip" "NO ENCONTRADO" "Red"
    $issues += "pip no instalado"
}

# ========================================
# 3. Python Dependencies
# ========================================
Write-Host ""
Write-Host "--- Python Dependencies ---" -ForegroundColor White
Set-Location "$PSScriptRoot\src" -ErrorAction SilentlyContinue
$deps = @("fastapi", "uvicorn", "aiohttp", "pyyaml", "pydantic", "email_validator")
$missingDeps = @()
$installedDeps = @()

foreach ($dep in $deps) {
    $result = python -c "import $($dep -replace '-', '_')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        $installedDeps += $dep
    } else {
        $missingDeps += $dep
    }
}

if ($missingDeps.Count -eq 0) {
    Write-Check "Python deps" "OK" "Green"
    if ($Verbose) { Write-Host "       $($installedDeps -join ', ')" -ForegroundColor Gray }
} else {
    Write-Check "Python deps" "FALTAN" "Yellow"
    Write-Host "       Faltan: $($missingDeps -join ', ')" -ForegroundColor Yellow
    $warnings += "Instalar con: pip install -r requirements.txt"
    if ($Fix) {
        Write-Host "       [AUTO-FIX] Instalando..." -ForegroundColor Cyan
        pip install -r requirements.txt --quiet
        if ($LASTEXITCODE -eq 0) {
            Write-Check "Python deps" "INSTALADO" "Green"
        }
    }
}

# Volver al directorio original
Set-Location $PSScriptRoot

# ========================================
# 4. Node.js
# ========================================
Write-Host ""
Write-Host "--- Node.js ---" -ForegroundColor White
try {
    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Check "Node.js" "OK" "Green"
        if ($Verbose) { Write-Host "       $nodeVersion" -ForegroundColor Gray }
    } else {
        Write-Check "Node.js" "NO ENCONTRADO" "Red"
        $issues += "Node.js no instalado"
    }
} catch {
    Write-Check "Node.js" "NO ENCONTRADO" "Red"
    $issues += "Node.js no instalado"
}

# ========================================
# 5. npm
# ========================================
Write-Host ""
Write-Host "--- npm ---" -ForegroundColor White
try {
    $npmVersion = npm --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Check "npm" "OK" "Green"
        if ($Verbose) { Write-Host "       v$npmVersion" -ForegroundColor Gray }
    } else {
        Write-Check "npm" "NO ENCONTRADO" "Red"
        $issues += "npm no instalado"
    }
} catch {
    Write-Check "npm" "NO ENCONTRADO" "Red"
    $issues += "npm no instalado"
}

# ========================================
# 6. Frontend Dependencies
# ========================================
Write-Host ""
Write-Host "--- Frontend Dependencies ---" -ForegroundColor White
Set-Location "$PSScriptRoot\src_frontend" -ErrorAction SilentlyContinue
if (Test-Path "node_modules") {
    Write-Check "node_modules" "OK" "Green"
} else {
    Write-Check "node_modules" "NO EXISTE" "Yellow"
    $warnings += "Ejecutar: cd src_frontend && npm install"
    if ($Fix) {
        Write-Host "       [AUTO-FIX] Instalando..." -ForegroundColor Cyan
        npm install 2>&1 | Out-Null
        if (Test-Path "node_modules") {
            Write-Check "node_modules" "INSTALADO" "Green"
        }
    }
}
Set-Location $PSScriptRoot

# ========================================
# 7. Puertos
# ========================================
Write-Host ""
Write-Host "--- Puertos ---" -ForegroundColor White
$ports = @(
    @{name="Backend"; port=8000},
    @{name="Frontend"; port=3000},
    @{name="ComfyUI still"; port=8188},
    @{name="ComfyUI video"; port=8189},
    @{name="ComfyUI dubbing"; port=8190},
    @{name="ComfyUI lab"; port=8191}
)

$portsInfo = @()
foreach ($p in $ports) {
    $connection = Test-NetConnection -ComputerName 127.0.0.1 -Port $p.port -WarningAction SilentlyContinue -ErrorAction SilentlyContinue
    if ($connection.TcpTestSucceeded) {
        $portsInfo += "$($p.name)=$($p.port)"
    }
}

if ($portsInfo.Count -eq 0) {
    Write-Check "Puertos" "LIBRES" "Green"
    Write-Host "       Ningun servicio en uso" -ForegroundColor Gray
} else {
    Write-Check "Puertos" "EN USO" "Yellow"
    foreach ($info in $portsInfo) {
        Write-Host "       - $info" -ForegroundColor Yellow
    }
}

# ========================================
# 8. ComfyUI Backends
# ========================================
Write-Host ""
Write-Host "--- ComfyUI Backends ---" -ForegroundColor White
$backends = @(
    @{name="still"; port=8188; desc="Imagenes"},
    @{name="video"; port=8189; desc="Video"},
    @{name="dubbing"; port=8190; desc="Voz/Audio"},
    @{name="lab"; port=8191; desc="Experimental"}
)

$backendsOk = @()
$backendsFail = @()

foreach ($backend in $backends) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$($backend.port)/system_stats" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendsOk += "$($backend.name)($($backend.port))"
            Write-Host "  $($backend.name.PadRight(10)) $($backend.desc.PadRight(15)) [OK]" -ForegroundColor Green
        } else {
            $backendsFail += $backend.name
            Write-Host "  $($backend.name.PadRight(10)) $($backend.desc.PadRight(15)) [ERROR]" -ForegroundColor Red
        }
    } catch {
        $backendsFail += $backend.name
        Write-Host "  $($backend.name.PadRight(10)) $($backend.desc.PadRight(15)) [NO RESPONDE]" -ForegroundColor Red
    }
}

if ($backendsOk.Count -eq 0) {
    $warnings += "ComfyUI backends no detectados - necesarios para renderizado"
}

# ========================================
# 9. Configuracion
# ========================================
Write-Host ""
Write-Host "--- Configuracion ---" -ForegroundColor White
Set-Location $PSScriptRoot

if (Test-Path "src\config\instances.yml") {
    Write-Check "instances.yml" "OK" "Green"
} else {
    Write-Check "instances.yml" "FALTA" "Red"
    $issues += "Archivo de configuracion no encontrado"
}

if (Test-Path "src\config\plans.yml") {
    Write-Check "plans.yml" "OK" "Green"
} else {
    Write-Check "plans.yml" "FALTA" "Red"
    $issues += "Archivo de planes no encontrado"
}

# ========================================
# RESUMEN
# ========================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "RESUMEN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

if ($issues.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "  [OK] Todo listo!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  Ejecutar en terminal 1:" -ForegroundColor White
    Write-Host "    .\start_backend.bat" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Ejecutar en terminal 2:" -ForegroundColor White
    Write-Host "    .\start_frontend.bat" -ForegroundColor Gray
}
else {
    if ($issues.Count -gt 0) {
        Write-Host "  [PROBLEMAS]" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "    - $issue" -ForegroundColor Red
        }
        Write-Host ""
    }

    if ($warnings.Count -gt 0) {
        Write-Host "  [ADVERTENCIAS]" -ForegroundColor Yellow
        foreach ($warning in $warnings) {
            Write-Host "    - $warning" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    if ($issues.Count -gt 0) {
        Write-Host "  Corregir problemas antes de continuar" -ForegroundColor Red
        Write-Host "  Ver: docs\GUIA_DESPLIEGUE_SERVIDOR.md" -ForegroundColor Gray
    }
    else {
        Write-Host "  Listo para arrancar (con advertencias)" -ForegroundColor Yellow
        Write-Host "  Ejecutar: .\start_backend.bat && .\start_frontend.bat" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
