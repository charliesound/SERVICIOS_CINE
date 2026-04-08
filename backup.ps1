# SERVICIOS_CINE - Script de Backup
# Realiza backup de datos y configuración

param(
    [string]$BackupPath = "",
    [switch]$IncludeData,
    [switch]$Compress
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupName = "ailinkcinema_backup_$timestamp"

if (-not $BackupPath) {
    $BackupPath = Join-Path $projectRoot "backups"
}

if (-not (Test-Path $BackupPath)) {
    New-Item -ItemType Directory -Path $BackupPath -Force | Out-Null
}

$backupDir = Join-Path $BackupPath $backupName
New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "  AILinkCinema - Backup" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$items = @(
    @{name="src/config"; desc="Configuración"},
    @{name="src/services"; desc="Servicios"},
    @{name="src/routes"; desc="Rutas API"},
    @{name="src/schemas"; desc="Esquemas"},
    @{name="src_frontend/src"; desc="Frontend src"},
    @{name="Caddyfile"; desc="Caddy config"},
    @{name="docker-compose.yml"; desc="Docker compose"},
    @{name=".env"; desc="Environment"}
)

if ($IncludeData) {
    $items += @(
        @{name="logs"; desc="Logs"},
        @{name="data"; desc="Data"}
    )
}

$totalItems = $items.Count
$currentItem = 0

foreach ($item in $items) {
    $currentItem++
    $source = Join-Path $projectRoot $item.name
    
    if (Test-Path $source) {
        $percent = [math]::Round(($currentItem / $totalItems) * 100)
        Write-Host "[$percent%] Copiando $($item.desc)..." -ForegroundColor Gray
        
        $dest = Join-Path $backupDir $item.name
        Copy-Item -Path $source -Destination $dest -Recurse -Force
    }
    else {
        Write-Host "[SKIP] $($item.name) no existe" -ForegroundColor Yellow
    }
}

if ($Compress) {
    Write-Host ""
    Write-Host "Comprimiendo backup..." -ForegroundColor Yellow
    
    $zipPath = "$backupDir.zip"
    Compress-Archive -Path $backupDir -DestinationPath $zipPath -Force
    
    $size = (Get-Item $zipPath).Length / 1MB
    Write-Host "[OK] Backup comprimido: $zipPath ($([math]::Round($size, 2)) MB)" -ForegroundColor Green
    
    Remove-Item -Path $backupDir -Recurse -Force
    $finalPath = $zipPath
}
else {
    $finalPath = $backupDir
}

Write-Host ""
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host "  Backup completado!" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════" -ForegroundColor Green
Write-Host ""
Write-Host "Ubicación: $finalPath" -ForegroundColor White
Write-Host ""
Write-Host "Para restaurar:" -ForegroundColor Cyan
Write-Host "  1. Extraer si está comprimido" -ForegroundColor Gray
Write-Host "  2. Copiar carpetas al proyecto" -ForegroundColor Gray
Write-Host "  3. Reiniciar servicios" -ForegroundColor Gray
Write-Host ""