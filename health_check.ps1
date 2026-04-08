# SERVICIOS_CINE - Health Check para Servidor
# Ejecutar cada 5 minutos para monitoreo

param(
    [switch]$Json,
    [switch]$AutoFix
)

$ErrorActionPreference = "Continue"

function Get-ServiceStatus($name, $port) {
    $result = @{
        name = $name
        port = $port
        status = "unknown"
        response_time = 0
        error = $null
    }
    
    try {
        $sw = [Diagnostics.Stopwatch]::StartNew()
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:$port/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        $sw.Stop()
        
        $result.status = "healthy"
        $result.response_time = $sw.ElapsedMilliseconds
    }
    catch {
        $result.status = "unhealthy"
        $result.error = $_.Exception.Message
    }
    
    return $result
}

function Get-ComfyUIBackendStatus($port, $name) {
    $result = @{
        name = $name
        port = $port
        status = "unknown"
        devices = @()
    }
    
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:$port/system_stats" -TimeoutSec 5 -ErrorAction Stop
        $result.status = "healthy"
        
        if ($response.devices) {
            $result.devices = $response.devices
        }
    }
    catch {
        $result.status = "offline"
    }
    
    return $result
}

$services = @(
    @{name="Backend"; port=8000},
    @{name="Frontend"; port=3000}
)

$backends = @(
    @{name="still"; port=8188},
    @{name="video"; port=8189},
    @{name="dubbing"; port=8190},
    @{name="lab"; port=8191}
)

$results = @{
    timestamp = (Get-Date).ToString("o")
    services = @()
    backends = @()
    overall_status = "healthy"
}

foreach ($svc in $services) {
    $status = Get-ServiceStatus $svc.name $svc.port
    $results.services += $status
    
    if ($status.status -ne "healthy") {
        $results.overall_status = "degraded"
    }
}

foreach ($be in $backends) {
    $status = Get-ComfyUIBackendStatus $be.port $be.name
    $results.backends += $status
    
    if ($status.status -ne "healthy") {
        $results.overall_status = "degraded"
    }
}

if ($Json) {
    $results | ConvertTo-Json -Depth 3
}
else {
    Write-Host ""
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host "  SERVICIOS_CINE - Health Check" -ForegroundColor Cyan
    Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Timestamp: $($results.timestamp)" -ForegroundColor Gray
    Write-Host ""
    
    Write-Host "--- Servicios ---" -ForegroundColor White
    foreach ($s in $results.services) {
        $color = if ($s.status -eq "healthy") { "Green" } else { "Red" }
        $time = if ($s.response_time -gt 0) { " ($($s.response_time)ms)" } else { "" }
        Write-Host "  $($s.name.PadRight(15)) $($s.port)$time" -ForegroundColor $color
    }
    Write-Host ""
    
    Write-Host "--- ComfyUI Backends ---" -ForegroundColor White
    foreach ($b in $results.backends) {
        $color = if ($b.status -eq "healthy") { "Green" } elseif ($b.status -eq "offline") { "Yellow" } else { "Red" }
        Write-Host "  $($b.name.PadRight(10)) [$($b.port)] $($b.status)" -ForegroundColor $color
    }
    Write-Host ""
    
    $statusColor = if ($results.overall_status -eq "healthy") { "Green" } else { "Yellow" }
    Write-Host "Estado General: $($results.overall_status)" -ForegroundColor $statusColor
    Write-Host ""
    
    if ($AutoFix -and $results.overall_status -ne "healthy") {
        Write-Host "[AUTO-FIX] Iniciando servicios..." -ForegroundColor Cyan
        
        if ($results.services[0].status -ne "healthy") {
            Start-Process "cmd.exe" -ArgumentList "/c cd /d `"$PSScriptRoot\src`" && python -m uvicorn app:app --host 0.0.0.0 --port 8000" -WindowStyle Hidden
        }
        
        if ($results.services[1].status -ne "healthy") {
            Start-Process "cmd.exe" -ArgumentList "/c cd /d `"$PSScriptRoot\src_frontend`" && npm run dev -- --host 0.0.0.0" -WindowStyle Hidden
        }
        
        Write-Host "[OK] Servicios iniciados, verificar en 30s" -ForegroundColor Green
    }
}