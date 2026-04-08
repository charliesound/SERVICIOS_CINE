<#
.SYNOPSIS
    Setup automatico para el ecosistema CID + CINE_AI_PLATFORM integrado.
.DESCRIPTION
    Verifica dependencias, configura variables de entorno, levanta contenedores
    y valida que todos los servicios respondan correctamente.
#>

param(
    [switch]$SkipBuild,
    [switch]$SkipHealthCheck,
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$PROJECT_ROOT = Split-Path -Parent $PSScriptRoot
$COMPOSE_DIR = $PSScriptRoot

$actualDrive = (Get-Location).Drive.Name
if ($actualDrive -ne "G" -and (Test-Path "G:\SERVICIOS_CINE\PROYECTO FINAL V1")) {
    $COMPOSE_DIR = "G:\SERVICIOS_CINE\PROYECTO FINAL V1"
    $PROJECT_ROOT = "G:\SERVICIOS_CINE"
    Write-Host "[INFO] Detectada unidad G:, ajustando rutas..." -ForegroundColor Cyan
}

function Write-Step { param([string]$Msg) Write-Host "`n>>> $Msg" -ForegroundColor Cyan }
function Write-Success { param([string]$Msg) Write-Host "    [OK] $Msg" -ForegroundColor Green }
function Write-Warn { param([string]$Msg) Write-Host "    [WARN] $Msg" -ForegroundColor Yellow }
function Write-Fail { param([string]$Msg) Write-Host "    [FAIL] $Msg" -ForegroundColor Red }
function Write-Info { param([string]$Msg) Write-Host "    $Msg" -ForegroundColor Gray }

$totalSteps = 6
$currentStep = 0

# ─────────────────────────────────────────────
# PASO 1: Verificar dependencias del sistema
# ─────────────────────────────────────────────
$currentStep++
Write-Step "($currentStep/$totalSteps) Verificando dependencias del sistema"

$errors = 0

$docker = Get-Command docker -ErrorAction SilentlyContinue
if (-not $docker) {
    Write-Fail "Docker no encontrado. Instala Docker Desktop desde https://docker.com"
    $errors++
} else {
    Write-Success "Docker encontrado: $(docker --version 2>&1)"
}

$compose = Get-Command docker -ErrorAction SilentlyContinue
if (-not $compose) {
    Write-Fail "docker compose no disponible"
    $errors++
} else {
    $composeVersion = docker compose version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker Compose: $composeVersion"
    } else {
        Write-Warn "docker compose version fallo, verificando con docker-compose..."
        $legacyVersion = docker-compose --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Docker Compose (legacy): $legacyVersion"
        } else {
            Write-Fail "docker compose no disponible"
            $errors++
        }
    }
}

$dockerRunning = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Docker no esta corriendo. Inicia Docker Desktop."
    $errors++
} else {
    Write-Success "Docker daemon esta corriendo"
}

if ($errors -gt 0) {
    Write-Host "`nCorrige los errores antes de continuar." -ForegroundColor Red
    exit 1
}

# ─────────────────────────────────────────────
# PASO 2: Verificar estructura de carpetas
# ─────────────────────────────────────────────
$currentStep++
Write-Step "($currentStep/$totalSteps) Verificando estructura de carpetas"

$requiredPaths = @(
    @{ Path = "$PROJECT_ROOT\CID_SERVER\automation-engine"; Label = "CID_SERVER/automation-engine" },
    @{ Path = "$PROJECT_ROOT\CINE_AI_PLATFORM"; Label = "CINE_AI_PLATFORM" },
    @{ Path = "$PROJECT_ROOT\Web Ailink_Cinema"; Label = "Web Ailink_Cinema" },
    @{ Path = "$PROJECT_ROOT\PROYECTO FINAL V1"; Label = "PROYECTO FINAL V1" }
)

foreach ($item in $requiredPaths) {
    if (Test-Path $item.Path) {
        Write-Success "$($item.Label) existe"
    } else {
        Write-Fail "$($item.Label) no encontrado en: $($item.Path)"
        $errors++
    }
}

$requiredFiles = @(
    @{ Path = "$PROJECT_ROOT\CID_SERVER\automation-engine\Dockerfile"; Label = "automation-engine Dockerfile" },
    @{ Path = "$PROJECT_ROOT\CID_SERVER\automation-engine\app\main.py"; Label = "automation-engine main.py" },
    @{ Path = "$PROJECT_ROOT\CINE_AI_PLATFORM\Dockerfile.cine"; Label = "CINE_AI_PLATFORM Dockerfile.cine" },
    @{ Path = "$PROJECT_ROOT\CINE_AI_PLATFORM\apps\api\src\app.py"; Label = "CINE_AI_PLATFORM app.py" },
    @{ Path = "$PROJECT_ROOT\CINE_AI_PLATFORM\apps\web\Dockerfile"; Label = "CINE_AI_PLATFORM web Dockerfile" },
    @{ Path = "$PROJECT_ROOT\Web Ailink_Cinema\Dockerfile"; Label = "Web Ailink_Cinema Dockerfile" },
    @{ Path = "$PROJECT_ROOT\Web Ailink_Cinema\next.config.ts"; Label = "Web Ailink_Cinema next.config.ts" },
    @{ Path = "$PROJECT_ROOT\Web Ailink_Cinema\package.json"; Label = "Web Ailink_Cinema package.json" },
    @{ Path = "$PROJECT_ROOT\PROYECTO FINAL V1\docker-compose.yml"; Label = "PROYECTO FINAL V1 docker-compose.yml" },
    @{ Path = "$PROJECT_ROOT\PROYECTO FINAL V1\Caddyfile"; Label = "PROYECTO FINAL V1 Caddyfile" },
    @{ Path = "$PROJECT_ROOT\PROYECTO FINAL V1\.env"; Label = "PROYECTO FINAL V1 .env" },
    @{ Path = "$PROJECT_ROOT\PROYECTO FINAL V1\env\cid.env"; Label = "PROYECTO FINAL V1 env/cid.env" },
    @{ Path = "$PROJECT_ROOT\PROYECTO FINAL V1\env\cine.env"; Label = "PROYECTO FINAL V1 env/cine.env" }
)

foreach ($item in $requiredFiles) {
    if (Test-Path $item.Path) {
        Write-Success "$($item.Label)"
    } else {
        Write-Fail "$($item.Label) no encontrado"
        $errors++
    }
}

if ($errors -gt 0) {
    Write-Host "`nArchivos faltantes detectados. Verifica la estructura." -ForegroundColor Red
    exit 1
}

# ─────────────────────────────────────────────
# PASO 3: Configurar variables de entorno
# ─────────────────────────────────────────────
$currentStep++
Write-Step "($currentStep/$totalSteps) Configurando variables de entorno"

$envFile = "$COMPOSE_DIR\.env"
$cidEnvFile = "$COMPOSE_DIR\env\cid.env"
$cineEnvFile = "$COMPOSE_DIR\env\cine.env"
$automationEnvFile = "$PROJECT_ROOT\CID_SERVER\automation-engine\.env"

$needsSetup = $false

if (-not (Test-Path $envFile)) {
    Write-Warn ".env principal no existe, creando desde ejemplo..."
    if (Test-Path "$COMPOSE_DIR\.env.example") {
        Copy-Item "$COMPOSE_DIR\.env.example" $envFile
    } else {
        @"
NEXT_PUBLIC_SUPABASE_URL=https://tu-proyecto.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=tu_anon_key_aqui
SUPABASE_SERVICE_ROLE_KEY=tu_service_role_key_aqui
CINEMA_API_URL=http://localhost:8080/api/cine
AUTOMATION_ENGINE_URL=http://automation-engine:8000
N8N_WEBHOOK_URL=
FOLLOWUP_SEND_MODE=simulated
"@ | Out-File -FilePath $envFile -Encoding UTF8
    }
    $needsSetup = $true
}

function Test-EnvVar {
    param([string]$File, [string]$VarName, [string]$Placeholder = "REEMPLAZAR")
    if (-not (Test-Path $File)) { return $false }
    $content = Get-Content $File -Raw
    $value = ([regex]::Match($content, "(?m)^$VarName=(.*)$")).Groups[1].Value.Trim()
    return $value -and $value -ne "" -and $value -ne $Placeholder
}

$supabaseUrlSet = Test-EnvVar $envFile "NEXT_PUBLIC_SUPABASE_URL"
$supabaseKeySet = Test-EnvVar $envFile "NEXT_PUBLIC_SUPABASE_ANON_KEY"
$cidSupabaseSet = Test-EnvVar $cidEnvFile "NEXT_PUBLIC_SUPABASE_URL"
$cidKeySet = Test-EnvVar $cidEnvFile "NEXT_PUBLIC_SUPABASE_ANON_KEY"

if (-not $supabaseUrlSet -or -not $supabaseKeySet) {
    Write-Warn "NEXT_PUBLIC_SUPABASE_URL o NEXT_PUBLIC_SUPABASE_ANON_KEY no estan configurados en .env"
    Write-Info "1. Crea tu proyecto en https://supabase.com"
    Write-Info "2. Ve a Project Settings > API y copia las claves"
    Write-Info "3. Edita: $envFile"
    Write-Info "4. Edita: $cidEnvFile"
    $needsSetup = $true
} else {
    Write-Success "Credenciales Supabase configuradas"
}

$cinemaUrlSet = Test-EnvVar $envFile "CINEMA_API_URL"
if (-not $cinemaUrlSet) {
    Write-Warn "CINEMA_API_URL no esta configurado en .env"
    $needsSetup = $true
} else {
    Write-Success "CINEMA_API_URL configurado"
}

if ($needsSetup) {
    Write-Host "`nCompletaste la configuracion de .env? Presiona cualquier tecla cuando estes listo..." -ForegroundColor Yellow
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}

# ─────────────────────────────────────────────
# PASO 4: Verificar ComfyUI (opcional)
# ─────────────────────────────────────────────
$currentStep++
Write-Step "($currentStep/$totalSteps) Verificando ComfyUI"

$comfyuiUrl = "http://127.0.0.1:8188/system_stats"
try {
    $response = Invoke-WebRequest -Uri $comfyuiUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
    if ($response.StatusCode -eq 200) {
        Write-Success "ComfyUI respondiendo en http://127.0.0.1:8188"
    } else {
        Write-Warn "ComfyUI respondio con status $($response.StatusCode) - los renders no funcionaran"
    }
} catch {
    Write-Warn "ComfyUI no esta corriendo en http://127.0.0.1:8188"
    Write-Info "Inicia ComfyUI para habilitar la generacion de imagenes"
    Write-Info "Opcional: Agrega ComfyUI como servicio en docker-compose.yml si lo tienes en container"
}

# ─────────────────────────────────────────────
# PASO 5: Construir y levantar contenedores
# ─────────────────────────────────────────────
$currentStep++
Write-Step "($currentStep/$totalSteps) Construyendo y levantando contenedores"

Push-Location $COMPOSE_DIR

try {
    $composeCmd = "docker"
    $useLegacy = $false

    $null = docker compose version 2>&1
    if ($LASTEXITCODE -ne 0) {
        $composeCmd = "docker-compose"
        $null = & docker-compose --version 2>&1
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "docker compose ni docker-compose disponibles"
            Pop-Location
            exit 1
        }
        $useLegacy = $true
    }

    Write-Info "Usando: $composeCmd"

    if (-not $SkipBuild) {
        Write-Info "Deteniendo contenedores anteriores..."
        if ($useLegacy) {
            docker-compose down --remove-orphans 2>&1 | Out-Null
        } else {
            docker compose down --remove-orphans 2>&1 | Out-Null
        }

        Write-Info "Construyendo imagenes (puede tardar 5-15 minutos la primera vez)..."
        if ($useLegacy) {
            docker-compose build 2>&1 | ForEach-Object { Write-Info $_ }
        } else {
            docker compose build 2>&1 | ForEach-Object { Write-Info $_ }
        }
        if ($LASTEXITCODE -ne 0) {
            Write-Fail "Build fallo"
            Pop-Location
            exit 1
        }
        Write-Success "Build completado"
    }

    Write-Info "Levantando contenedores..."
    if ($useLegacy) {
        docker-compose up -d 2>&1 | ForEach-Object { Write-Info $_ }
    } else {
        docker compose up -d 2>&1 | ForEach-Object { Write-Info $_ }
    }
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "docker compose up fallo"
        Pop-Location
        exit 1
    }
    Write-Success "Contenedores levantados"

} finally {
    Pop-Location
}

# ─────────────────────────────────────────────
# PASO 6: Verificar salud de servicios
# ─────────────────────────────────────────────
$currentStep++
Write-Step "($currentStep/$totalSteps) Verificando salud de servicios"

Start-Sleep -Seconds 5

function Test-Service {
    param(
        [string]$Name,
        [string]$Url,
        [int]$ExpectedStatus = 200,
        [int]$TimeoutSec = 15
    )
    Write-Info "Verificando $Name..."
    $attempt = 0
    while ($attempt -lt $TimeoutSec) {
        try {
            $response = Invoke-WebRequest -Uri $Url -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            if ($response.StatusCode -eq $ExpectedStatus) {
                Write-Success "$Name respondio ($($response.StatusCode))"
                return $true
            }
        } catch {
        }
        $attempt += 2
        Start-Sleep -Seconds 2
    }
    Write-Warn "$Name no respondio en ${TimeoutSec}s - puede necesitar mas tiempo para iniciar"
    return $false
}

$localIP = "localhost"
$results = @{
    "Caddy (CID Web)" = (Test-Service "Caddy (CID Web)" "http://$localIP`:8080" 200)
    "CINE API" = (Test-Service "CINE API" "http://$localIP`:8080/api/cine/health" 200)
    "Automation Engine" = (Test-Service "Automation Engine" "http://$localIP`:8000/health" 200)
}

# ─────────────────────────────────────────────
# Resumen final
# ─────────────────────────────────────────────
Write-Host "`n" -NoNewline
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  RESUMEN DE LA INSTALACION" -ForegroundColor Cyan
Write-Host "══════════════════════════════════════════════" -ForegroundColor Cyan

Write-Host "`n  URLs de acceso:" -ForegroundColor White
Write-Host "  ┌─────────────────────────────────────────────┐" -ForegroundColor Gray
Write-Host "  │  CID / App Web:     http://$localIP`:8080     │" -ForegroundColor White
Write-Host "  │  CINE API:          http://$localIP`:8080/api/cine  │" -ForegroundColor White
Write-Host "  │  Automation Engine: http://$localIP`:8000     │" -ForegroundColor White
Write-Host "  └─────────────────────────────────────────────┘" -ForegroundColor Gray

Write-Host "`n  Credenciales de prueba CINE_AI_PLATFORM:" -ForegroundColor White
Write-Host "  ┌─────────────────────────────────────────────┐" -ForegroundColor Gray
Write-Host "  │  admin:    admin@cine.local / CHANGE_ME      │" -ForegroundColor Yellow
Write-Host "  │  editor:   editor@cine.local / editor1234   │" -ForegroundColor Yellow
Write-Host "  │  viewer:   viewer@cine.local / viewer1234    │" -ForegroundColor Yellow
Write-Host "  └─────────────────────────────────────────────┘" -ForegroundColor Gray

Write-Host "`n  Comandos utiles:" -ForegroundColor White
Write-Host "  Ver logs:    docker compose -f '$COMPOSE_DIR\docker-compose.yml' logs -f" -ForegroundColor Gray
Write-Host "  Detener:     docker compose -f '$COMPOSE_DIR\docker-compose.yml' down" -ForegroundColor Gray
Write-Host "  Reiniciar:  docker compose -f '$COMPOSE_DIR\docker-compose.yml' restart" -ForegroundColor Gray
Write-Host "  Status:     docker compose -f '$COMPOSE_DIR\docker-compose.yml' ps" -ForegroundColor Gray

$failedServices = $results.Values | Where-Object { -not $_ }
if ($failedServices.Count -gt 0) {
    Write-Host "`n  Algunos servicios no estan listos. Revisando logs..." -ForegroundColor Yellow
    Write-Host "  Los servicios pueden necesitar 30-60 segundos extra para iniciar." -ForegroundColor Yellow
}

Write-Host "`n" -NoNewline
